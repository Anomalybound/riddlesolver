import re
from datetime import datetime

import requests
from dateutil.parser import parse

from constants import DATE_FORMAT


def parse_date(date_string):
    """
    Parses a date string and returns a datetime object.

    Args:
        date_string (str): The date string to parse.

    Returns:
        datetime: The parsed datetime object.
    """
    return datetime.strptime(date_string, DATE_FORMAT)


def calculate_days_between_dates(start_date, end_date):
    """
    Calculates the number of days between two dates.

    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.

    Returns:
        int: The number of days between the two dates.
    """
    if isinstance(start_date, str):
        start_date = parse(start_date)
    if isinstance(end_date, str):
        end_date = parse(end_date)
    return (end_date - start_date).days


def format_date(date):
    """
    Formats a datetime object into a string representation.

    Args:
        date (datetime): The datetime object to format.

    Returns:
        str: The formatted date string.
    """
    if isinstance(date, str):
        date = parse(date)
    return date.strftime(DATE_FORMAT)


def handle_error(error):
    """
    Handles errors and exceptions gracefully.

    Args:
        error (Exception): The error message to display or log.
    """
    raise error


def validate_arguments(repo_path, start_date, end_date):
    """
    Validates the provided arguments.

    Args:
        repo_path (str): The repository path or URL.
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    if not repo_path:
        raise ValueError("Repository path or URL is required.")
    if start_date > end_date:
        raise ValueError("Start date cannot be greater than end date.")


def get_repository_type(repo_path):
    """
    Determines the type of repository based on the provided repository path.

    Args:
        repo_path (str): The repository path or URL.

    Returns:
        str: The repository type (github, gitlab, local, or remote).
    """
    if repo_path.startswith(("https://github.com/", "http://github.com/", "git@github.com:")):
        return "github"
    elif repo_path.startswith(("https://gitlab.com/", "http://gitlab.com/", "git@gitlab.com:")):
        return "gitlab"
    elif repo_path.startswith(("https://", "http://", "git@")):
        return "remote"
    else:
        return "local"


def extract_owner_repo(github_link):
    """
    Extracts the owner and repository name from a GitHub link.
    Args:
        github_link: The GitHub link in the format "https://github.com/owner/repo" or
        "git@github.com:owner/repo.git". or "https://github.com/owner/repo.git"

    Returns:
        str: The owner and repository name in the format "owner/repo".
    """
    # Define regular expression patterns
    https_pattern = r'https?://github\.com/([^/]+)/([^/]+)'
    ssh_pattern = r'git@github\.com:([^/]+)/([^/]+)\.git'

    # Try matching with HTTPS pattern
    match = re.match(https_pattern, github_link)
    if match:
        owner, repo = match.groups()
        return f'{owner}/{repo}'

    # Try matching with SSH pattern
    match = re.match(ssh_pattern, github_link)
    if match:
        owner, repo = match.groups()
        return f'{owner}/{repo}'

    # If no match found, return None
    return None


def remove_duplicated_commits(commits):
    """
    Removes duplicated commits from the list of commits.

    Args:
        commits (list): The list of commits.

    Returns:
        list: The list of unique commits.
    """

    unique_commits = []
    # Sort by author, and move 'main' branch to the beginning
    commits = sorted(
        commits,
        key=lambda x: (x['author'], x['branch'] != 'main'),
    )

    # if there is a main branch in the list, move it to the front
    # TODO: hardcoded 'main' branch name for now, actually we need a way to find out which branch is the earliest
    # branch in the list, and we order the branches by the created date
    main_branch = 'main'
    for commit in commits:
        if commit['branch'] == main_branch:
            commits.remove(commit)
            commits.insert(0, commit)
            break

    for commit_object in commits:
        messages = commit_object['commit_messages']
        for message in messages:
            sha = message['sha']
            if sha not in unique_commits:
                unique_commits.append(sha)
            else:
                message['removed'] = True

        messages = [message for message in messages if not message.get('removed')]
        commit_object['commit_messages'] = messages

    # remove commit objects with no commit messages
    commits = [commit_object for commit_object in commits if commit_object['commit_messages']]
    return commits


def get_base_branch_map(repo_path, start_date, end_date, access_token, author=None):
    """
    Get the base branch for each branch in a GitHub repository.
    Args:
        repo_path: owner/repo format
        start_date: The start date of the date range.
        end_date: The end date of the date range.
        access_token: GitHub access token
        author: The author name or email.

    Returns:
        dict: A dictionary mapping each branch to its base branch.
        dict: A dictionary mapping each branch to its commits, for caching.
    """
    # Set the base URL for the GitHub API
    base_url = f'https://api.github.com/repos/{repo_path}'
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    commit_params = {
        "since": start_date.isoformat(),
        "until": end_date.isoformat(),
    }

    if author:
        commit_params["author"] = author

    # Fetch the list of branches in the repository
    branches_url = f'{base_url}/branches'
    branches_response = requests.get(branches_url, headers=headers)
    branches = [branch['name'] for branch in branches_response.json()]

    base_branch_map = {}
    branch_commits_caches = {}

    for branch in branches:
        # Fetch the list of commits for the current branch
        branch_url = f'{base_url}/commits?sha={branch}'
        branch_response = requests.get(branch_url, headers=headers, params=commit_params)
        branch_commits = branch_response.json()
        branch_commit_hashes = [commit['sha'] for commit in branch_commits]
        branch_commits_caches[branch] = branch_commits

        # Find the base branch for the current branch
        base_branch = None
        base_branch_commits = []
        for other_branch in branches:
            if other_branch != branch:
                other_branch_url = f'{base_url}/commits?sha={other_branch}'
                if other_branch in branch_commits_caches:
                    other_branch_commits = branch_commits_caches[other_branch]
                else:
                    other_branch_response = requests.get(other_branch_url, headers=headers, params=commit_params)
                    other_branch_commits = other_branch_response.json()
                other_branch_commit_hashes = [commit['sha'] for commit in other_branch_commits]
                common_commits = set(branch_commit_hashes) & set(other_branch_commit_hashes)
                if len(common_commits) > len(base_branch_commits):
                    base_branch = other_branch
                    base_branch_commits = other_branch_commits

        base_branch_map[branch] = base_branch

    return base_branch_map, branch_commits_caches


def get_all_unique_commits(repo_path, base_branch_map, commits_caches, start_date, end_date, access_token, author=None):
    """
    Get the unique commits for each branch in a GitHub repository.
    Args:
        repo_path: owner/repo format
        base_branch_map: A dictionary mapping each branch to its base branch.
        commits_caches: A dictionary mapping each branch to its commits, for caching. Could be empty.
        start_date: The start date of the date range.
        end_date: The end date of the date range.
        access_token: GitHub access token
        author: The author name or email.

    Returns:
        dict: A dictionary mapping each branch to its unique commits.
    """
    # Set the base URL for the GitHub API
    base_url = f'https://api.github.com/repos/{repo_path}'
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    commit_params = {
        "since": start_date.isoformat(),
        "until": end_date.isoformat(),
    }

    if author:
        commit_params["author"] = author

    unique_commits_map = {}

    for branch, base_branch in base_branch_map.items():
        # Fetch the list of commits for the current branch
        if branch in commits_caches:
            branch_commits = commits_caches[branch]
        else:
            query_url = f'{base_url}/commits?sha={branch}'
            branch_response = requests.get(query_url, headers=headers, params=commit_params)
            branch_commits = branch_response.json()

        if not base_branch:
            unique_commits_map[branch] = branch_commits
            continue

        # Fetch the list of commits for the base branch
        if base_branch in commits_caches:
            base_branch_commits = commits_caches[base_branch]
        else:
            query_url = f'{base_url}/commits?sha={base_branch}'
            base_branch_response = requests.get(query_url, headers=headers, params=commit_params)
            base_branch_commits = base_branch_response.json()

        # Find the unique commits on the current branch
        unique_commits = [commit for commit in branch_commits if commit not in base_branch_commits]

        unique_commits_map[branch] = unique_commits

    return unique_commits_map


def get_base_branch_map_local(repo, start_date, end_date, author=None):
    """
    Get the base branch for each branch in a local repository.
    Args:
        repo: The local repository object.
        start_date: The start date of the date range.
        end_date: The end date of the date range.
        author: The author name or email.

    Returns:
        dict: A dictionary mapping each branch to its base branch.
    """
    base_branch_map = {}

    # Fetch remote branches
    repo.remotes.origin.fetch()

    for ref in repo.remotes.origin.refs:
        branch = ref.name.split('/')[-1]
        branch_commits = list(repo.iter_commits(ref, author=author))
        branch_commits = [commit for commit in branch_commits if
                          start_date <= commit.committed_datetime.replace(tzinfo=None) <= end_date]

        base_branch = None
        base_branch_commits = []
        for other_ref in repo.remotes.origin.refs:
            other_branch = other_ref.name.split('/')[-1]
            if other_branch != branch:
                other_branch_commits = list(repo.iter_commits(other_ref, author=author))
                other_branch_commits = [commit for commit in other_branch_commits if
                                        start_date <= commit.committed_datetime.replace(tzinfo=None) <= end_date]
                common_commits = set(branch_commits) & set(other_branch_commits)
                if len(common_commits) > len(base_branch_commits):
                    base_branch = other_branch
                    base_branch_commits = other_branch_commits

        base_branch_map[branch] = base_branch

    return base_branch_map


def get_all_unique_commits_local(repo, base_branch_map, start_date, end_date, author=None):
    """
    Get the unique commits for each branch in a local repository.
    Args:
        repo: The local repository object.
        base_branch_map: A dictionary mapping each branch to its base branch.
        start_date: The start date of the date range.
        end_date: The end date of the date range.
        author: The author name or email.

    Returns:
        dict: A dictionary mapping each branch to its unique commits.
    """
    unique_commits_map = {}

    # Fetch remote branches
    repo.remotes.origin.fetch()

    for branch, base_branch in base_branch_map.items():
        # ignore HEAD branch
        if branch == 'HEAD':
            continue

        for branch_ref in repo.remotes.origin.refs:
            if branch_ref.name.split('/')[-1] == branch:
                branch_commits = list(repo.iter_commits(branch_ref, author=author))
                branch_commits = [commit for commit in branch_commits if
                                  start_date <= commit.committed_datetime.replace(tzinfo=None) <= end_date]

                if not base_branch or base_branch not in repo.remotes.origin.refs:
                    unique_commits_map[branch] = branch_commits
                    continue

                base_branch_ref = repo.remotes.origin.refs[base_branch]
                base_branch_commits = list(repo.iter_commits(base_branch_ref, author=author))
                base_branch_commits = [commit for commit in base_branch_commits if
                                       start_date <= commit.committed_datetime.replace(tzinfo=None) <= end_date]

                unique_commits = [commit for commit in branch_commits if commit not in base_branch_commits]

                unique_commits_map[branch] = unique_commits

    return unique_commits_map
