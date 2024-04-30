import os
import shutil

import requests
from git import Repo
from datetime import datetime, timedelta

from riddlesolver.config import get_config_value
from riddlesolver.utils import extract_owner_repo


def fetch_commits(repo_path, start_date, end_date, branch=None, author=None, access_token=None, repo_type=None):
    """
    Fetches commits from a repository within the specified date range.

    Args:
        repo_path (str): The repository path or URL.
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.
        access_token (str): The access token for authentication.
        repo_type (str): The repository type (github, gitlab, local, remote).

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """
    if repo_type == "github":
        if not access_token:
            raise ValueError("GitHub access token is required.")
        repo_path_result = extract_owner_repo(repo_path)
        if not repo_path_result:
            raise ValueError(f"Invalid GitHub repository link: {repo_path}")
        return fetch_commits_from_github(repo_path_result, start_date, end_date, branch, author, access_token)
    elif repo_type == "gitlab":
        # GitLab is not implemented yet
        return fetch_commits_from_remote(repo_path, start_date, end_date, branch, author)
    elif repo_type == "local":
        return fetch_commits_from_local(repo_path, start_date, end_date, branch, author)
    elif repo_type == "remote":
        return fetch_commits_from_remote(repo_path, start_date, end_date, branch, author)


def fetch_commits_from_github(repo_path, start_date, end_date, branch=None, author=None, access_token=None):
    """
    Fetches commits from a GitHub repository.

    Args:
        repo_path (str): The repository path in the format "owner/repo".
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.
        access_token (str): The GitHub access token for authentication.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """

    results = []
    list_branches_url = f"https://api.github.com/repos/{repo_path}/branches"
    list_commits_url = f"https://api.github.com/repos/{repo_path}/commits"
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

    response = requests.get(list_branches_url, headers=headers)
    response.raise_for_status()

    branches = response.json()

    for fetched_branch in branches:
        branch_name = fetched_branch["name"]
        # If branch is specified, filter by branch name
        if branch and branch_name != branch:
            continue

        commit_params.update({"sha": branch_name})
        response = requests.get(list_commits_url, headers=headers, params=commit_params)
        response.raise_for_status()

        commits = response.json()

        # group commits by author
        commits_by_author = {}
        for commit in commits:
            author = commit["commit"]["author"]["name"]
            if author not in commits_by_author:
                commits_by_author[author] = []
            commits_by_author[author].append(commit)

        for author, commits in commits_by_author.items():
            # Ignore branches with no commits
            if len(commits) <= 0:
                continue

            end_date = commits[0]["commit"]["author"]["date"]
            start_date = commits[-1]["commit"]["author"]["date"]
            messages = [commit["commit"]["message"] for commit in commits]

            # unified results
            results.append({
                "branch": branch_name,
                "author": author,
                "start_date": start_date,
                "end_date": end_date,
                "commit_messages": messages
            })

    return results


def fetch_commits_from_local(repo_path, start_date, end_date, branch=None, author=None):
    """
    Fetches commits from a local repository.

    Args:
        repo_path (str): The local repository path.
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """
    repo = Repo(repo_path)
    results = []

    for local_branch in repo.branches:
        branch_name = local_branch.name

        # If branch is specified, filter by branch name
        if branch is not None and branch_name != branch:
            continue

        # Iterate over commits in the branch
        commits = repo.iter_commits(branch_name)

        # filter commits by date and author
        filtered_commits = []
        for commit in commits:
            commit_date = datetime.fromtimestamp(commit.committed_date)
            if start_date <= commit_date <= end_date:
                if author is None or commit.author.email == author or commit.author.name == author:
                    filtered_commits.append(commit)

        # group commits by author
        commits_by_author = {}
        for commit in filtered_commits:
            author = commit.author.name
            if author not in commits_by_author:
                commits_by_author[author] = []
            commits_by_author[author].append(commit)

        for author, commits in commits_by_author.items():
            if len(commits) < 0:
                continue

            end_date = commits[0].committed_datetime
            start_date = commits[-1].committed_datetime
            messages = [commit.message for commit in commits]

            # unified results
            results.append({
                "branch": branch_name,
                "author": author,
                "start_date": start_date,
                "end_date": end_date,
                "commit_messages": messages
            })

    return results


def fetch_commits_from_remote(repo_url, start_date, end_date, branch=None, author=None, config=None):
    """
    Fetches commits from a remote repository.

    Args:
        repo_url (str): The remote repository URL.
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.
        config (dict): The configuration dictionary.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """
    if config is None:
        config = {}

    cache_dir = get_config_value(config, "general", "cache_dir")
    if cache_dir is None:
        cache_dir = os.path.expanduser("~/.cache/repo_cache")

    cache_duration = get_config_value(config, "general", "cache_duration")
    if cache_duration is None:
        cache_duration = 7  # Default cache duration of 7 days
    else:
        cache_duration = int(cache_duration)

    repo_name = repo_url.split("/")[-1].split(".")[0]
    repo_cache_dir = os.path.join(cache_dir, repo_name)

    if os.path.exists(repo_cache_dir):
        # Check if the cached repository is still valid
        cache_timestamp = datetime.fromtimestamp(os.path.getmtime(repo_cache_dir))
        cache_expiry = cache_timestamp + timedelta(days=cache_duration)
        if cache_expiry > datetime.now():
            # Use the cached repository
            repo = Repo(repo_cache_dir)
        else:
            # Cache has expired, remove the cached repository
            shutil.rmtree(repo_cache_dir)
            repo = None
    else:
        repo = None

    if repo is None:
        # Clone the remote repository and cache it
        os.makedirs(cache_dir, exist_ok=True)
        repo = Repo.clone_from(repo_url, repo_cache_dir, no_checkout=True, depth=1)  # Clone with minimal history
        repo.git.fetch(all=True)  # Fetch all branches and tags

    # Fetch the commits using the same logic as fetch_commits_from_local()
    results = fetch_commits_from_local(repo_cache_dir, start_date, end_date, branch, author)

    return results
