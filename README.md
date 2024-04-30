# RiddleSolver 🎩🔍

Ladies and gentlemen, boys and girls, gather around for the most extraordinary, mind-bending, and side-splitting Git commit summarizer you've ever witnessed! 🤯🎪 Introducing... RiddleSolver! 🎭

RiddleSolver is like a magical genie 🧞‍♂️ that grants your wish to understand the cryptic riddles known as Git commits. With a wave of its virtual wand 🪄, RiddleSolver conjures up clear, concise, and standardized summaries of your Git commit messages, leaving you in awe and amazement! 🎆

## ✨ Features

- 🔮 Unravels the mysteries of Git commits and reveals their true purpose
- 🌿 Works its magic on both local and remote repositories (it's a versatile genie!)
- 📅 Grants you the power to specify a custom date range or relative time periods (days, weeks, months)
- 🔍 Categorizes changes using the enchanting gitmoji conventions (because even genies love emojis!)
- 💡 Provides mind-blowing insights and observations about the commits (prepare to be enlightened!)
- 🎛️ Allows you to summon the genie with configurable OpenAI API settings
- 🤫 Offers a silent mode for those times when you need to keep the genie's secrets
- 🌳 Lets you specify a branch to focus the genie's powers on
- 🧙‍♂️ Enables you to summon commits by a specific author (because even genies play favorites!)
- 📝 Grants you the ability to capture the genie's wisdom in a markdown file (for posterity, of course!)
- 🧙‍♂️ Bestows upon you the power to set configuration values using the mystical `config` subcommand

## 🧪 Installation

To unleash the power of RiddleSolver, simply recite the following incantation in your terminal:

```bash
pip install riddlesolver
```

And voila! The genie is now at your command! 🧞‍♂️✨

## 🕮 Usage

### Summoning the Genie

To summon the RiddleSolver genie and unravel the riddles of your Git commits, use the following command:

```bash
riddlesolver <repo> [options]
```

Replace `<repo>` with the path to your local repository, the URL of a remote repository, or the owner/repo format for GitHub repositories.

### Options 🎛️

- `-s`, `--start-date`: Specify the start date of the commit range (YYYY-MM-DD)
- `-e`, `--end-date`: Specify the end date of the commit range (YYYY-MM-DD)
- `-c`, `--config`: Provide the path to a custom configuration file
- `--silent`: Run RiddleSolver in silent mode (shhh, the genie is working!)
- `-v`, `--verbose`: Enable verbose mode for extra insights and behind-the-scenes magic
- `-d`, `--days`: Specify the number of days to include in the summary (e.g., `-d 2` for the last 2 days)
- `-w`, `--weeks`: Specify the number of weeks to include in the summary (e.g., `-w 1` for the last week)
- `-m`, `--months`: Specify the number of months to include in the summary (e.g., `-m 3` for the last 3 months)
- `-b`, `--branch`: Specify the branch name to focus the genie's powers on
- `-a`, `--author`: Specify the author's email or name to filter commits by
- `-o`, `--output`: Specify the path to save the genie's wisdom as a markdown file

### Configuring the Genie

To customize the genie's behavior and grant it access to the OpenAI API, use the mystical `config` subcommand:

```bash
riddlesolver config set <section> <key> <value>
```

For example, to set the OpenAI API key:

```bash
riddlesolver config set openai api_key YOUR_API_KEY
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

Summon the genie to reveal the secrets of the last 2 weeks in silent mode:

```bash
riddlesolver owner/repo -w 2 --silent
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

## 🔧 Configuration

The genie's secrets are stored in the sacred scroll located at `~/.riddlesolver/config.ini`. Here's a glimpse of what it contains:

```ini
[openai]
api_key = YOUR_API_KEY
model = gpt-3.5-turbo
base_url = https://api.openai.com/v1

[general]
verbose = False
batch_size = 50
```

- `api_key`: Replace `YOUR_API_KEY` with your OpenAI API key (the genie needs it to work its magic!)
- `model`: Specify the OpenAI model for the genie to use (default: `gpt-3.5-turbo`)
- `base_url`: Specify the base URL for the OpenAI API (default: `https://api.openai.com/v1`)
- `verbose`: Set to `True` to enable verbose mode and witness the genie's behind-the-scenes magic
- `batch_size`: Specify the number of riddles the genie should process in each batch (default: `50`)

## 🤝 Contributing

If you wish to contribute to the genie's power and make it even more extraordinary, please open an issue or submit a pull request on the [GitHub repository](https://github.com/AnomalyBound/riddlesolver). The genie appreciates all the help it can get!

## 📜 License

RiddleSolver is released under the [MIT License](https://opensource.org/licenses/MIT), granting you the power to use, modify, and distribute the genie as you see fit.

## 🙏 Acknowledgements

The genie would like to express its gratitude to the mighty OpenAI for granting it the power of language understanding and generation. Without their API, the genie would be just another ordinary commit summarizer.

## 🚀 Version

RiddleSolver is currently at version 0.1.6, ready to unravel the mysteries of your Git commits like never before!

Now, prepare to be amazed as RiddleSolver unravels the mysteries of your Git commits and brings clarity to your development journey! 🎉✨