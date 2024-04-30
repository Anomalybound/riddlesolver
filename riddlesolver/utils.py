import re

from datetime import datetime
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
