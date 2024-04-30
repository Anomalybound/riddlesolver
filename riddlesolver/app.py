import argparse
import configparser
import os
import tempfile
import openai
import requests

from collections import defaultdict
from dateutil.parser import parse
from datetime import datetime, timedelta
from pathlib import Path
from git import Repo, InvalidGitRepositoryError, GitCommandError

# Template for the configuration file
CONFIG_TEMPLATE = """
[openai]
api_key = YOUR_API_KEY
model = gpt-3.5-turbo
base_url = https://api.openai.com/v1

[general]
verbose = False
batch_size = 50

[github]
access_token = YOUR_GITHUB_ACCESS_TOKEN
"""

# Template for the prompt to be sent to the OpenAI API
PROMPT_TEMPLATE = """
You are a helpful assistant that summarizes Git commit messages for the branch "{branch_name}" in a clear, concise, and standardized manner.

Please provide a summary of the following Git commit messages:

{commit_messages}

Format the summary as follows:
1. 📝 Summary:
   - In a single sentence, capture the overall purpose and changes made in these commits.
   - Follow the Git commit message pattern: Use the imperative mood, capitalize the first letter, and omit the period at the end.
   - Example: "✨ Add new feature for user authentication"

2. 🔍 Key Changes:
   - 🌟 Feature: Describe any new features or enhancements added
   - 🛠️ Refactor: Mention any significant refactoring or code improvements
   - 🐛 Fix: Note any bug fixes or issue resolutions
   - 📚 Docs: Highlight any updates to documentation
   - 🚀 Perf: Indicate any performance optimizations
   - 🧪 Test: Mention any additions or modifications to tests
   - 🎨 Style: Note any changes related to styling or UI improvements
   - 🔧 Chore: Describe any build process, dependency, or configuration updates
   Add more bullet points as needed, using gitmoji to categorize the changes.

3. 💡 Insights:
   - Provide any additional insights or observations about the commits
   - Mention any potential impact or benefits of the changes
   - Add any relevant notes or suggestions for future improvements

Please ensure the summary adheres to the gitmoji conventions and the Git commit message pattern. Use markdown formatting for clarity and structure.
""".strip()


def get_openai_summary(commit_messages, branch_name, model, openai_api_key, base_url):
    """
    Retrieve a summary of the given commit messages using the OpenAI API.

    Args:
        commit_messages (str): The commit messages to summarize.
        branch_name (str): The name of the branch associated with the commits.
        model (str): The OpenAI model to use for generating the summary.
        openai_api_key (str): The API key for accessing the OpenAI API.
        base_url (str): The base URL of the OpenAI API.

    Returns:
        str: The generated summary of the commit messages, or None if an error occurs.
    """
    client = openai.Client(api_key=openai_api_key, base_url=base_url)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": PROMPT_TEMPLATE.format(branch_name=branch_name, commit_messages=commit_messages)
            }]
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            print("OpenAI API returned an empty response.")
            return None
    except openai.RateLimitError:
        print("OpenAI API request exceeded rate limit.")
        return None
    except openai.AuthenticationError:
        print("OpenAI API authentication failed. Please check your API key.")
        return None
    except openai.APIError as e:
        print(f"OpenAI API Error: {str(e)}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def fetch_commits_from_github_repo(repo_path, start_date, end_date, access_token, branch=None, author=None):
    """
    Fetch commits from a GitHub repository within the specified date range using the GitHub REST API.

    Args:
        repo_path (str): The repository path in the format "owner/repo".
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        access_token (str): The GitHub Access Token for authentication.
        branch (str, optional): The branch to fetch commits from. If not provided, the default branch is used.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.

    Returns:
        tuple: A tuple containing the list of commit objects within the specified date range and the list of branch names.
    """
    url = f"https://api.github.com/repos/{repo_path}/commits"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    params = {
        "since": start_date.isoformat(),
        "until": end_date.isoformat(),
        "sha": branch
    }
    if author:
        params["author"] = author

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    commits = response.json()

    branch_names = []
    if branch:
        branch_names.append(branch)
    else:
        # Fetch the list of branches from the repository
        branches_url = f"https://api.github.com/repos/{repo_path}/branches"
        branches_response = requests.get(branches_url, headers=headers)
        branches_response.raise_for_status()
        branches = branches_response.json()
        branch_names = [branch["name"] for branch in branches]

    print(f"Fetched {len(commits)} commits from {repo_path}")
    return commits, branch_names


def fetch_commits_from_remote_repo(repo_url, start_date, end_date, clone_dir=None, branch=None, author=None):
    """
    Fetch commits from a remote repository within the specified date range.

    Args:
        repo_url (str): The URL of the remote repository.
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        clone_dir (str, optional): The directory to clone the repository into. If not provided, a temporary directory is used.
        branch (str, optional): The branch to fetch commits from. If not provided, all branches are considered.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.

    Returns:
        tuple: A tuple containing the list of commit objects within the specified date range and the list of branch names.
    """
    try:
        if clone_dir is None:
            temp_dir = tempfile.gettempdir()
            repo_name = os.path.basename(repo_url).replace(".git", "")
            repo_dir = os.path.join(temp_dir, repo_name)
            commits, branch_names = get_commits_from_cloned_repo(repo_dir, repo_url, start_date, end_date, branch, author)
        else:
            repo_dir = os.path.join(clone_dir, os.path.basename(repo_url).replace(".git", ""))
            commits, branch_names = get_commits_from_cloned_repo(repo_dir, repo_url, start_date, end_date, branch, author)

        print(f"Fetched {len(commits)} commits from {repo_url}")
        return commits, branch_names
    except GitCommandError as e:
        print(f"Error cloning repository: {str(e)}")
        return [], []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], []


def get_commits_from_cloned_repo(repo_dir, repo_url, start_date, end_date, branch, author):
    """
    Fetch commits from a cloned repository within the specified date range.

    Args:
        repo_dir (str): The directory where the repository is cloned.
        repo_url (str): The URL of the repository.
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        branch (str, optional): The branch to fetch commits from. If not provided, all branches are considered.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.

    Returns:
        tuple: A tuple containing the list of commit objects within the specified date range and the list of branch names.
    """
    try:
        if os.path.exists(repo_dir):
            print(f"Repository already exists at {repo_dir}. Fetching commits...")
            repo = Repo(repo_dir)
            repo.git.fetch(all=True)  # Fetch all branches and tags
        else:
            print(f"Cloning {repo_url} to {repo_dir}")
            repo = Repo.clone_from(repo_url, repo_dir, no_checkout=True, depth=1)  # Clone with minimal history
            repo.git.fetch(all=True)  # Fetch all branches and tags

        if branch and branch not in repo.heads:
            print(f"Branch '{branch}' not found in the repository.")
            return [], []

        commits, branch_names = fetch_commits_from_repo(repo, start_date, end_date, branch, author)
        return commits, branch_names
    except GitCommandError as e:
        print(f"Error fetching commits: {str(e)}")
        return [], []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], []


def fetch_commits_from_repo(repo, start_date, end_date, branch=None, author=None):
    """
    Fetch commits from a repository within the specified date range.

    Args:
        repo (git.Repo): The Git repository object.
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        branch (str, optional): The branch to fetch commits from. If not provided, all branches are considered.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.

    Returns:
        tuple: A tuple containing the list of commit objects within the specified date range and the list of branch names.
    """
    commits = []
    branch_names = []

    for branch in repo.branches:
        branch_name = branch.name
        branch_names.append(branch_name)

        for commit in repo.iter_commits(branch_name):
            commit_date = datetime.fromtimestamp(commit.committed_date)
            if start_date <= commit_date <= end_date:
                if author is None or commit.author.email == author or commit.author.name == author:
                    commits.append(commit)

    return commits, branch_names


def fetch_commits_from_local_repo(repo_path, start_date, end_date, branch=None, author=None):
    """
    Fetch commits from a local repository within the specified date range.

    Args:
        repo_path (str): The path to the local repository.
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        branch (str, optional): The branch to fetch commits from. If not provided, all branches are considered.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.

    Returns:
        tuple: A tuple containing the list of commit objects within the specified date range and the list of branch names.
    """
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        return [], []
    return fetch_commits_from_repo(repo, start_date, end_date, branch, author)



def generate_commit_summary(repo_path, start_date, end_date, openai_api_key, model, base_url, verbose, batch_size,
                            silent=False, branch=None, author=None, output_file=None, access_token=None):
    """
    Generate a summary of the commits in a repository within the specified date range.

    Args:
        repo_path (str): The path or URL of the repository.
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        openai_api_key (str): The API key for accessing the OpenAI API.
        model (str): The OpenAI model to use for generating the summary.
        base_url (str): The base URL of the OpenAI API.
        verbose (bool): Whether to enable verbose output.
        batch_size (int): The number of commits to process in each batch.
        silent (bool, optional): Whether to run in silent mode without interactive prompts. Defaults to False.
        branch (str, optional): The branch to fetch commits from. If not provided, the default branch is used.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.
        output_file (str, optional): The path to save the summary as a markdown file. If not provided, the summary is printed to the console.
        access_token (str, optional): The GitHub Access Token for authentication. Required for GitHub repositories.
    """
    if repo_path is None:
        raise ValueError("Repository path is required.")

    if repo_path.startswith(("https://github.com/", "http://github.com/", "git@github.com:")):
        if access_token is None:
            raise ValueError("GitHub Access Token is required for GitHub repositories.")
        repo_owner, repo_name = repo_path.rstrip("/").split("/")[-2:]
        repo_path = f"{repo_owner}/{repo_name}"
        commits, branch_names = fetch_commits_from_github_repo(repo_path, start_date, end_date, access_token, branch,
                                                               author)
    else:
        is_remote_repo = repo_path.startswith(("https://", "http://", "git@"))
        if is_remote_repo:
            if silent:
                clone_dir = os.getcwd()
                commits, branch_names = fetch_commits_from_remote_repo(repo_path, start_date, end_date, clone_dir,
                                                                       branch, author)
            else:
                clone_dir = input(
                    f"Enter the directory to clone {repo_path} (leave blank for current directory): ") or os.getcwd()
                commits, branch_names = fetch_commits_from_remote_repo(repo_path, start_date, end_date, clone_dir,
                                                                       branch, author)
        else:
            commits, branch_names = fetch_commits_from_local_repo(repo_path, start_date, end_date, branch, author)

    if not commits:
        print("No commits found within the specified date range.")
        return

    if verbose:
        print(f"Commit summary from {start_date} to {end_date}:")
        print("=" * 50)

    commit_batches = defaultdict(lambda: defaultdict(list))
    processed_commits = set()

    for commit in commits:
        commit_id = commit["sha"] if isinstance(commit, dict) else commit.hexsha
        if commit_id in processed_commits:
            continue

        for branch_name in branch_names:
            if branch is None or branch_name == branch:
                if isinstance(commit, dict):
                    commit_batches[commit["commit"]["author"]["email"]][branch_name].append(commit)
                else:
                    commit_batches[commit.author.email][branch_name].append(commit)
                processed_commits.add(commit_id)

    output = []
    for author_email, branch_commits in commit_batches.items():
        for branch_name, commit_messages in branch_commits.items():
            batched_commits = [commit_messages[i:i + batch_size] for i in range(0, len(commit_messages), batch_size)]

            for batch in batched_commits:
                actual_batch_size = len(batch)

                # Get the start and end dates of the batch
                if isinstance(batch[0], dict):
                    actual_start_date = parse(batch[0]["commit"]["author"]["date"])
                    actual_end_date = parse(batch[-1]["commit"]["author"]["date"])
                else:
                    actual_start_date = datetime.fromtimestamp(batch[0].committed_date)
                    actual_end_date = datetime.fromtimestamp(batch[-1].committed_date)

                commit_messages = [c["commit"]["message"] if isinstance(c, dict) else c.message for c in batch]

                duration = (actual_end_date - actual_start_date).days
                summary = get_openai_summary("\n".join(commit_messages), branch_name, model, openai_api_key, base_url)
                if summary:
                    output.append(f"Author: {author_email}")
                    output.append(f"Branch: {branch_name}")
                    output.append(f"Period: {actual_start_date} to {actual_end_date} ({duration} days)")
                    output.append(f"Summary of {actual_batch_size} commits:")
                    output.append(summary)
                    output.append("-" * 50)
                else:
                    output.append(f"Failed to generate summary for author: {author_email}, branch: {branch_name}")
                    output.append("-" * 50)

    if output_file:
        try:
            with open(output_file, "w") as file:
                file.write("\n".join(output))
            print(f"Summary saved to {output_file}")
        except IOError as e:
            print(f"Error writing to output file: {str(e)}")
    else:
        print("\n".join(output))

    if verbose:
        print("=" * 50)


def get_config_dir():
    """
    Get the directory path for storing the configuration file.

    Returns:
        pathlib.Path: The directory path for storing the configuration file.
    """
    home_dir = Path.home()
    config_dir = home_dir / ".riddlesolver"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_path(config_path=None):
    """
    Get the path to the configuration file.

    Args:
        config_path (str, optional): The path to the configuration file. If not provided, the default path is used.

    Returns:
        pathlib.Path: The path to the configuration file.
    """
    if config_path:
        return Path(config_path)
    else:
        home_dir = Path.home()
        config_dir = home_dir / ".riddlesolver"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.ini"


def create_config_file(config_path):
    """
    Create the configuration file if it doesn't exist.

    Args:
        config_path (pathlib.Path): The path to the configuration file.
    """
    if not config_path.exists():
        with open(config_path, "w") as file:
            file.write(CONFIG_TEMPLATE.strip())
        print(f"Created configuration file: {config_path}")
    else:
        print(f"Configuration file already exists: {config_path}")


def set_config_value(config_path, section, key, value):
    """
    Set a value in the configuration file.

    Args:
        config_path (pathlib.Path): The path to the configuration file.
        section (str): The section in the configuration file.
        key (str): The key in the configuration section.
        value (str): The value to set for the key.
    """
    config = configparser.ConfigParser()
    config.read(config_path)

    if section not in config:
        config.add_section(section)

    config.set(section, key, value)

    with open(config_path, "w") as file:
        config.write(file)

    print(f"Updated configuration: [{section}] {key} = {value}")


def clone_repository(repo_url, clone_dir=None):
    """
    Clone a Git repository from the given URL.

    Args:
        repo_url (str): The URL of the remote repository.
        clone_dir (str, optional): The directory to clone the repository into. If not provided, a temporary directory is used.

    Returns:
        str: The path to the cloned repository.
    """
    try:
        if clone_dir is None:
            temp_dir = tempfile.gettempdir()
            repo_name = os.path.basename(repo_url).replace(".git", "")
            repo_dir = os.path.join(temp_dir, repo_name)
        else:
            repo_dir = os.path.join(clone_dir, os.path.basename(repo_url).replace(".git", ""))

        if os.path.exists(repo_dir):
            print(f"Repository already exists at {repo_dir}. Fetching updates...")
            repo = Repo(repo_dir)
            repo.git.fetch(all=True)  # Fetch all branches and tags
        else:
            print(f"Cloning {repo_url} to {repo_dir}")
            repo = Repo.clone_from(repo_url, repo_dir, no_checkout=True, depth=1)  # Clone with minimal history
            repo.git.fetch(all=True)  # Fetch all branches and tags

        return repo_dir
    except GitCommandError as e:
        print(f"Error cloning repository: {str(e)}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def get_commits(repo_path, start_date, end_date, branch=None, author=None):
    """
    Retrieve commits from a Git repository within the specified date range.

    Args:
        repo_path (str): The path to the Git repository.
        start_date (datetime): The start date of the commit range (inclusive).
        end_date (datetime): The end date of the commit range (inclusive).
        branch (str, optional): The branch to fetch commits from. If not provided, all branches are considered.
        author (str, optional): The email or name of the author to filter commits by. If not provided, all authors are considered.

    Returns:
        list: A list of commit objects within the specified date range.
    """
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        raise

    return fetch_commits_from_repo(repo, start_date, end_date, branch, author)


def summarize_commits(commit_messages, branch_name, model, openai_api_key, base_url):
    """
    Generate a summary of the given commit messages using the OpenAI API.

    Args:
        commit_messages (list): A list of commit message strings.
        branch_name (str): The name of the branch associated with the commits.
        model (str): The OpenAI model to use for generating the summary.
        openai_api_key (str): The API key for accessing the OpenAI API.
        base_url (str): The base URL of the OpenAI API.

    Returns:
        str: The generated summary of the commit messages.
    """
    summary = get_openai_summary("\n".join(commit_messages), branch_name, model, openai_api_key, base_url)
    if summary:
        return summary
    else:
        raise Exception("Failed to generate summary")


def save_summary(summary, output_file):
    """
    Save the commit summary to a file.

    Args:
        summary (str): The commit summary to save.
        output_file (str): The path to save the summary as a markdown file.

    Returns:
        None
    """
    try:
        with open(output_file, "w") as file:
            file.write(summary)
        print(f"Summary saved to {output_file}")
    except IOError as e:
        print(f"Error writing to output file: {str(e)}")
        raise


def main():
    """
    The main entry point of the program.
    """
    now = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description="RiddleSolver - A Git Commit(Riddles) Summarizer!")
    parser.add_argument("repo", nargs="?", help="Repository path, URL, or 'owner/repo' for GitHub repositories")
    parser.add_argument("-s", "--start-date", default=week_ago, help="Start date (YYYY-MM-DD)")
    parser.add_argument("-e", "--end-date", default=now, help="End date (YYYY-MM-DD)")
    parser.add_argument("-c", "--config", default=None, help="Path to the configuration file")
    parser.add_argument("--silent", action="store_true", help="Run in silent mode without interactive prompts")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    parser.add_argument("-d", "--days", type=int,
                        help="Number of days to include in the summary (e.g., -d 2 for the last 2 days)")
    parser.add_argument("-w", "--weeks", type=int,
                        help="Number of weeks to include in the summary (e.g., -w 1 for the last week)")
    parser.add_argument("-m", "--months", type=int,
                        help="Number of months to include in the summary (e.g., -m 3 for the last 3 months)")
    parser.add_argument("-b", "--branch", default=None, help="Branch name to analyze commits from")
    parser.add_argument("-a", "--author", default=None, help="Author's email or name to filter commits by")
    parser.add_argument("-o", "--output", default=None, help="Path to save the summary as a markdown file")
    parser.add_argument("command", nargs="?", choices=["config"],
                        help="Subcommand to execute (e.g., 'config' to set configuration values)")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for the subcommand")
    args = parser.parse_args()

    config_path = get_config_path(args.config)
    create_config_file(config_path)

    if args.command == "config":
        if len(args.args) == 3:
            section, key, value = args.args
            set_config_value(config_path, section, key, value)
        else:
            print("Usage: riddlesolver config <section> <key> <value>")
        return

    config = configparser.ConfigParser()
    config.read(config_path)
    openai_api_key = config.get("openai", "api_key")
    model = config.get("openai", "model")
    base_url = config.get("openai", "base_url")
    verbose = args.verbose or config.getboolean("general", "verbose", fallback=False)
    batch_size = config.getint("general", "batch_size", fallback=50)
    access_token = config.get("github", "access_token", fallback=None)

    if args.repo is None:
        parser.error("Repository path or URL is required.")
    if args.days:
        if args.days <= 0:
            parser.error("Number of days must be a positive integer.")
        start_date = datetime.now() - timedelta(days=args.days)
        end_date = datetime.now()
    elif args.weeks:
        if args.weeks <= 0:
            parser.error("Number of weeks must be a positive integer.")
        start_date = datetime.now() - timedelta(weeks=args.weeks)
        end_date = datetime.now()
    elif args.months:
        if args.months <= 0:
            parser.error("Number of months must be a positive integer.")
        start_date = datetime.now() - timedelta(days=args.months * 30)  # Approximate month as 30 days
        end_date = datetime.now()
    else:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    try:
        generate_commit_summary(args.repo, start_date, end_date, openai_api_key, model, base_url, verbose, batch_size,
                                args.silent, args.branch, args.author, args.output, access_token)
    except configparser.Error as e:
        print(f"Error in configuration file: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
