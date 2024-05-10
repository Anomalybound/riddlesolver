import os
import shutil
import logging
from datetime import datetime, timedelta

from dateutil.parser import parse
from git import Repo, InvalidGitRepositoryError

from riddlesolver.config import get_config_value
from riddlesolver.utils import (
    extract_owner_repo, get_base_branch_map, get_all_unique_commits,
    get_base_branch_map_local, get_all_unique_commits_local, get_all_commits
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_commits(repo_path, start_date, end_date, branch=None, author=None, access_token=None, repo_type=None,
                  config=None, cache_dir=None):
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
        config (ConfigParser): The configuration dictionary.
        cache_dir (str): The cache directory.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """
    if repo_type == "github":
        if not access_token:
            logger.warning(f'There is no access token for {repo_path}, pulling remote commits without authentication.')
            return fetch_commits_from_remote(repo_path, start_date, end_date, branch, author, config, cache_dir)
        repo_path_result = extract_owner_repo(repo_path)
        if not repo_path_result:
            logger.error(f"Invalid GitHub repository link: {repo_path}")
            raise ValueError(f"Invalid GitHub repository link: {repo_path}")
        return fetch_commits_from_github(repo_path_result, start_date, end_date, branch, author, access_token)
    elif repo_type == "gitlab":
        # GitLab is not implemented yet
        return fetch_commits_from_remote(repo_path, start_date, end_date, branch, author, config)
    elif repo_type == "local":
        return fetch_commits_from_local(repo_path, start_date, end_date, branch, author)
    elif repo_type == "remote":
        return fetch_commits_from_remote(repo_path, start_date, end_date, branch, author, config)


def fetch_commits_from_github(repo_path, start_date, end_date, branch=None, author=None, access_token=None,
                              unique_commits=False):
    """
    Fetches commits from a GitHub repository.

    Args:
        repo_path (str): The repository path in the format "owner/repo".
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.
        access_token (str): The GitHub access token for authentication.
        unique_commits (bool): Whether to fetch unique commits.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """

    results = []

    logger.info(f'Collecting unique commits from {repo_path}...')

    if unique_commits:
        base_branch_map, caches = get_base_branch_map(repo_path=repo_path, start_date=start_date, end_date=end_date,
                                                      access_token=access_token, author=author)
        commits = get_all_unique_commits(repo_path=repo_path, base_branch_map=base_branch_map, commits_caches=caches,
                                         start_date=start_date, end_date=end_date, access_token=access_token,
                                         author=author)
    else:
        commits = get_all_commits(repo_path=repo_path, start_date=start_date, end_date=end_date,
                                  access_token=access_token,
                                  author=author)

    for unique_commit_pair in commits.items():
        branch_name = unique_commit_pair[0]
        commits = unique_commit_pair[1]

        # If branch is specified, filter by branch name
        if branch and branch_name != branch:
            continue

        # group commits by author
        commits_by_author = {}
        for commit in commits:
            author = commit["commit"]["author"]["name"]
            if author not in commits_by_author:
                commits_by_author[author] = []
            commits_by_author[author].append(commit)

        for author, commits in commits_by_author.items():

            # sort commits by date
            commits = sorted(commits, key=lambda x: x["commit"]["author"]["date"], reverse=True)

            # convert string date to datetime
            for commit in commits:
                commit["commit"]["author"]["date"] = parse(commit["commit"]["author"]["date"]).replace(tzinfo=None)

            # filter out commits outside the date range
            commits = [commit for commit in commits if
                       start_date <= commit["commit"]["author"]["date"] <= end_date]

            # Ignore branches with no commits
            if len(commits) <= 0:
                continue

            end_date = commits[0]["commit"]["author"]["date"]
            start_date = commits[-1]["commit"]["author"]["date"]
            messages = [{"messages": commit["commit"]["message"], "sha": commit["sha"]} for commit in commits]

            # unified results
            results.append({
                "branch": branch_name,
                "author": author,
                "start_date": start_date,
                "end_date": end_date,
                "commit_messages": messages
            })

    logger.info(f'Fetched {len(results)} unique commits from {repo_path}.')
    return results


def fetch_commits_from_local(repo_path, start_date, end_date, branch=None, author=None, unique_commits=False):
    """
    Fetches commits from a local repository.

    Args:
        repo_path (str): The local repository path.
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.
        unique_commits (bool): Whether to fetch unique commits.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """
    try:
        repo = Repo(repo_path)
        results = []

        if unique_commits:
            # Get the base branch map and unique commits for local repository
            base_branch_map = get_base_branch_map_local(repo, start_date, end_date, author)
            commits = get_all_unique_commits_local(repo, base_branch_map, start_date, end_date, author)
        else:
            commits = {}
            remote_branches = repo.git.branch('-r').split('\n')
            for remote_branch in remote_branches:
                remote_branch = remote_branch.strip()
                if remote_branch.contains("HEAD"):
                    continue

                branch_commits = list(repo.iter_commits(remote_branch, author=author))

                # sort commits by date
                branch_commits = sorted(branch_commits, key=lambda x: x.committed_datetime, reverse=True)

                # filter out commits outside the date range
                branch_commits = [commit for commit in branch_commits if
                                  start_date <= commit.committed_datetime.replace(tzinfo=None) <= end_date]
                commits[remote_branch] = branch_commits

        for branch_name, commits in commits.items():
            # If branch is specified, filter by branch name
            if branch:
                # remove "origin/" prefix
                stripped_branch_name = branch_name.split("/", 1)[1]
                if stripped_branch_name != branch:
                    continue

            # group commits by author
            commits_by_author = {}
            for commit in commits:
                author = commit.author.name
                if author not in commits_by_author:
                    commits_by_author[author] = []
                commits_by_author[author].append(commit)

            for author, commits in commits_by_author.items():
                if len(commits) < 0:
                    continue

                end_date = commits[0].committed_datetime
                start_date = commits[-1].committed_datetime
                messages = [{"messages": commit.message, "sha": commit.hexsha} for commit in commits]

                # unified results
                results.append({
                    "branch": branch_name,
                    "author": author,
                    "start_date": start_date,
                    "end_date": end_date,
                    "commit_messages": messages
                })

        logger.info(f'Fetched {len(results)} commits from local repository: {repo_path}.')
        return results
    except InvalidGitRepositoryError:
        logger.error(f"Invalid Git repository: {repo_path}")
        raise ValueError(f"Invalid Git repository: {repo_path}")


def fetch_commits_from_remote(repo_url, start_date, end_date, branch=None, author=None, config=None, cache_dir=None):
    """
    Fetches commits from a remote repository.

    Args:
        repo_url (str): The remote repository URL.
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        branch (str): The branch name.
        author (str): The author name or email.
        config (configparser.ConfigParser): The configuration to save.
        cache_dir (str): The cache directory.

    Returns:
        list: stores the branch, author, datetime ranges and the commits
    """

    if config:
        cache_dir = config.get("general", "cache_dir") if not cache_dir else cache_dir
        cache_duration = config.get("general", "cache_duration")
    else:
        cache_dir = get_config_value("general", "cache_dir") if not cache_dir else cache_dir
        cache_duration = get_config_value("general", "cache_duration")

    if not cache_duration:
        cache_duration = 7
        logger.warning(f"Cache duration not specified. Using default value: {cache_duration} days.")

    if not cache_dir or not os.path.exists(cache_dir):
        cache_dir = os.path.expanduser("~/.cache/repo_cache")
        cache_dir = os.path.normpath(cache_dir)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Created cache directory: {cache_dir}")
        else:
            logger.info(f"Using cache directory: {cache_dir}")

    repo_name = repo_url.split("/")[-1].split(".")[0]
    repo_cache_dir = os.path.join(cache_dir, repo_name)

    if os.path.exists(repo_cache_dir):
        # Check if the cached repository is still valid
        cache_timestamp = datetime.fromtimestamp(os.path.getmtime(repo_cache_dir))
        cache_expiry = cache_timestamp + timedelta(days=cache_duration)
        if cache_expiry > datetime.now():
            # Use the cached repository
            repo = Repo(repo_cache_dir)
            logger.info(f"Using cached repository: {repo_cache_dir}")
        else:
            # Cache has expired, remove the cached repository
            shutil.rmtree(repo_cache_dir)
            logger.info(f"Cache expired. Removing cached repository: {repo_cache_dir}")
            repo = None
    else:
        repo = None

    if repo is None:
        # Clone the remote repository and cache it
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Cloning remote repository: {repo_url}")
        repo = Repo.clone_from(repo_url, repo_cache_dir, no_checkout=True,
                               filter='blob:none')  # Clone with minimal history
        repo.git.fetch(all=True)  # Fetch all branches and tags
        logger.info(f"Cloned repository cached at: {repo_cache_dir}")
    else:
        # Fetch the latest changes in the repository
        repo.git.fetch(all=True)
        logger.info(f"Fetched latest changes from remote repository: {repo_url}")

    # Fetch the commits using the same logic as fetch_commits_from_local()
    results = fetch_commits_from_local(repo_cache_dir, start_date, end_date, branch, author)

    logger.info(f'Fetched {len(results)} commits from remote repository: {repo_url}.')
    return results