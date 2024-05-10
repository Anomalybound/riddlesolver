import argparse
from riddlesolver import __version__

from datetime import datetime, timedelta

from config import load_config_from_file, save_config_to_file, get_config_value, set_config_value, grant_github_auth
from constants import DEFAULT_SETTINGS
from repository import fetch_commits
from summary import generate_commit_summary
from utils import parse_date, handle_error, validate_arguments, get_repository_type


def main():
    config = load_config_from_file()
    args = parse_arguments()

    if args.command == "config":
        if len(args.config_args) == 3:
            section, key, value = args.config_args
            set_config_value(section, key, value)
            save_config_to_file(config)
            print(f"Configuration updated: [{section}] {key} = {value}")
        else:
            print("Invalid number of arguments for 'config' command.")
            print("Usage: riddlesolver -c config <section> <key> <value>")
        return

    if args.command == "grant-auth":
        grant_github_auth()
        save_config_to_file(config)
        print("GitHub authentication granted.")
        return

    if args.command == "version" or args.version:
        print(f"Riddlesolver version {get_version()}")
        return

    if not args.repo:
        print("Please provide a repository path or URL.")
        return

    repo_path = args.repo
    start_date, end_date = get_date_range(args)
    branch = args.branch
    author = args.author
    output_file = args.output

    try:
        validate_arguments(repo_path, start_date, end_date)
        repo_type = get_repository_type(repo_path)
        access_token = get_config_value(repo_type, "access_token")
        batched_commits = fetch_commits(repo_path, start_date, end_date, branch, author, access_token, repo_type)
        branch = f" on branch '{branch}'" if branch else ""
        author = f" by '{author}'" if author else ""
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        print(f"Start generating commits summary ({start_date} to {end_date}){branch}{author}:")
        generate_commit_summary(batched_commits, config, output_file)
    except Exception as e:
        handle_error(e)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Commit Summary Generator")
    parser.add_argument("repo", nargs="?", help="Repository path or URL")
    parser.add_argument("-s", "--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("-e", "--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("-d", "--days", type=int, help="Number of days to include in the summary")
    parser.add_argument("-w", "--weeks", type=int, help="Number of weeks to include in the summary")
    parser.add_argument("-m", "--months", type=int, help="Number of months to include in the summary")
    parser.add_argument("-b", "--branch", help="Branch name")
    parser.add_argument("-a", "--author", help="Author name or email")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-c", "--command", choices=["config", "grant-auth", "version"], help="Command to execute")
    parser.add_argument("config_args", nargs="*", help="Arguments for the 'config' command")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    return parser.parse_args()


def get_date_range(args):
    if args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    elif args.weeks:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=args.weeks)
    elif args.months:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.months * 30)  # Approximate month as 30 days
    elif args.start_date and args.end_date:
        start_date = parse_date(args.start_date)
        end_date = parse_date(args.end_date)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DEFAULT_SETTINGS["default_date_range"])
    return start_date, end_date


def get_version():
    return __version__


if __name__ == "__main__":
    main()
