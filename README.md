# RiddleSolver 🎩🔍

[English](README.md) | [简体中文](README.zh-CN.md)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://badge.fury.io/py/riddlesolver.svg)](https://badge.fury.io/py/riddlesolver)
[![Last Commit](https://img.shields.io/github/last-commit/AnomalyBound/riddlesolver)](https://github.com/AnomalyBound/riddlesolver/commits)

[![Code Size](https://img.shields.io/github/languages/code-size/AnomalyBound/riddlesolver)](https://github.com/AnomalyBound/riddlesolver)
[![Downloads](https://img.shields.io/pypi/dm/riddlesolver)](https://pypi.org/project/riddlesolver/)

Ladies and gentlemen, boys and girls, gather around for the most extraordinary, mind-bending, and side-splitting Git commit summarizer you've ever witnessed! 🤯🎪 Introducing... RiddleSolver! 🎭

RiddleSolver is like a magical genie 🧞‍ that grants your wish to understand the cryptic riddles known as Git commits. With a wave of its virtual wand 🪄, RiddleSolver conjures up clear, concise, and standardized summaries of your Git commit messages, leaving you in awe and amazement! 🎆

## ✨ Features

- 🔮 Unravels the mysteries of Git commits and reveals their true purpose with mind-blowing insights
- 🎯 Fetches only the unique commits dedicated to a certain branch, eliminating the hassle of overlapping commits
- 🌿 Works its magic on both local repositories and remote GitHub repositories (no cloning required!)
- 📅 Grants you the power to specify a custom date range, so you can focus on the commits that matter most
- 🧙‍♂️ Enables you to summon commits by a specific author or branch, giving you full control over your analysis
- 🔧 Bestows upon you the power to set configuration values using the intuitive config command
- 🔑 Allows you to grant GitHub authentication effortlessly using the magical grant-auth command
- 📦 Serves as a versatile development toolkit, providing a well-structured API for seamless integration into your projects
- 🎨  Comes with a bonus Streamlit app, offering a delightful and intuitive user interface for commit analysis

## 🧪 Installation

To unleash the power of RiddleSolver, simply recite the following incantation in your terminal:

```bash
pip install --upgrade riddlesolver
```

And voila! The genie is now at your command! 🧞️✨

## 📖 Usage

### Summoning the Genie

To summon the RiddleSolver genie and unravel the riddles of your Git commits, use the following command:

```bash
riddlesolver <repo> [options]
```

Replace `<repo>` with the path to your local repository, the URL of a remote repository, or the owner/repo format for GitHub repositories.

### Options 🎛️

- `-s`, `--start-date`: Specify the start date of the commit range (YYYY-MM-DD)
- `-e`, `--end-date`: Specify the end date of the commit range (YYYY-MM-DD)
- `-d`, `--days`: Specify the number of days to include in the summary (e.g., `-d 2` for the last 2 days)
- `-w`, `--weeks`: Specify the number of weeks to include in the summary (e.g., `-w 1` for the last week)
- `-m`, `--months`: Specify the number of months to include in the summary (e.g., `-m 3` for the last 3 months)
- `-b`, `--branch`: Specify the branch name to focus the genie's powers on
- `-a`, `--author`: Specify the author's email or name to filter commits by
- `-o`, `--output`: Specify the path to save the genie's wisdom as a markdown file
- `-c`, `--command`: Execute a command (`config` or `grant-auth`)

⚠️ **IMPORTANT**: When using RiddleSolver with GitHub remote repositories, you have two options:

1. Use the `grant-auth` command to grant the necessary permissions and utilize the GitHub API for fetching commits. 

2. If you choose not to grant authentication, RiddleSolver will still work and fetch commits without using the GitHub API.

### Configuring the Genie

To customize the genie's behavior and grant it access to the OpenAI API, use the mystical `config` subcommand:

```bash
riddlesolver config <section> <key> <value>
```

For example, to set the OpenAI API key:

```bash
riddlesolver config openai api_key YOUR_API_KEY
```

The genie will store its secrets in the sacred scroll located at `~/.riddlesolver/config.ini`.

### Examples 🌟

Summon the genie to unravel the riddles of a local repository:

```bash
riddlesolver /path/to/local/repo
```

Summon the genie to decipher the commits of a remote repository within a specific date range:

```bash
riddlesolver https://github.com/owner/repo -s 2023-01-01 -e 2023-01-31
```

Summon the genie to uncover the riddles of a specific branch:

```bash
riddlesolver /path/to/local/repo -b feature-branch
```

Summon the genie to expose the commits by a specific author:

```bash
riddlesolver owner/repo -a john@example.com
```

Summon the genie to capture its wisdom in a markdown file:

```bash
riddlesolver /path/to/local/repo -o summary.md
```

Grant GitHub authentication to the genie:

```bash
riddlesolver --command grant-auth
```

**🛠️ Development Toolkit**
---------------------------

RiddleSolver not only serves as a command-line tool but also provides a well-structured API for developers to integrate its functionality into their own projects. You can use RiddleSolver as a development toolkit to fetch commits, generate summaries, and save the summaries to files.

### **API Functions**

1.  `fetch_commits(repo_path, start_date, end_date, branch=None, author=None, access_token=None, repo_type=None)`: Fetches commits from a repository within the specified date range, optionally filtered by branch and author. If `access_token` is provided and `repo_type` is set to `"github"`, it will use the GitHub API to fetch commits. Otherwise, it will fetch commits without using the API. Returns a list of commit objects.
    
2.  `generate_summary(commit_batches, config)`: Generates a summary of commit batches using the OpenAI API. Returns the generated summary as a string.
    
3.  `save_summary_to_file(summary, output_file)`: Saves the commit summary to a file at the specified output path.
    

### **Example Usage**

Here's an example of how you can use RiddleSolver as a development toolkit in your own project:

```python
from riddlesolver import fetch_commits, generate_summary, save_summary_to_file
from riddlesolver.config import load_config_from_file
from datetime import datetime

repo_path = "https://github.com/username/repo.git"
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
branch = "main"
author = "john@example.com"
access_token = "YOUR_ACCESS_TOKEN"
repo_type = "github"
output_file = "summary.md"

config = load_config_from_file()
batched_commits = fetch_commits(repo_path, start_date, end_date, branch, author, access_token, repo_type)
summary = generate_summary(batched_commits, config)
save_summary_to_file(summary, output_file)
```

## 🔧 Configuration

The genie's secrets are stored in the sacred scroll located at `~/.riddlesolver`. Here's a glimpse of what it contains:

```ini
[openai]
api_key = your_openai_api_key
model = gpt-3.5-turbo
base_url = https://api.openai.com/v1

[general]
cache_dir = ~/.cache/repo_cache
cache_duration = 7

[github]
access_token = your_github_access_token
```

- `api_key`: Replace `INPUT YOUR API KEY` with your OpenAI API key (the genie needs it to work its magic!)
- `model`: Specify the OpenAI model for the genie to use (default: `gpt-3.5-turbo`)
- `base_url`: Specify the base URL for the OpenAI API (default: `https://api.openai.com/v1`)
- `cache_dir`: Specify the directory where the genie stores its cached repositories (default: `~/.cache/repo_cache`)
- `cache_duration`: Specify the number of days the genie should keep the cached repositories (default: `7`)
- `access_token`: Provide your GitHub access token to grant the genie access to your repositories (leave empty if not required)

## 🤝 Contributing

If you wish to contribute to the genie's power and make it even more extraordinary, please open an issue or submit a pull request on the [GitHub repository](https://github.com/AnomalyBound/riddlesolver). The genie appreciates all the help it can get!

## 📜 License

RiddleSolver is released under the [MIT License](https://opensource.org/licenses/MIT), granting you the power to use, modify, and distribute the genie as you see fit.

## 🙏 Acknowledgements

The genie would like to express its gratitude to the mighty OpenAI for granting it the power of language understanding and generation. Without their API, the genie would be just another ordinary commit summarizer.

Now, prepare to be amazed as RiddleSolver unravels the mysteries of your Git commits and brings clarity to your development journey! 🎉✨