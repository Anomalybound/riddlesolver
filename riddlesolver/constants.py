DEFAULT_SETTINGS = {
    "default_date_range": 7,  # Number of days to consider if start and end dates are not provided
    "batch_size": 50,  # Number of commits to process in each batch
    "api_endpoints": {
        "github": "https://api.github.com",
        "gitlab": "https://gitlab.com/api/v4"
    }
}

DATE_FORMAT = "%Y-%m-%d"  # Format for parsing and displaying dates

SUMMARY_PROMPT_TEMPLATE = """
You are a helpful assistant that summarizes Git commit messages for the branch "{branch_name}" in a clear, concise, and standardized manner.

Please provide a summary of the following Git commit messages:

{commit_messages}

Strictly obey the output format the summary as follows:
- 📝 Summary:
    - In a single sentence, capture the overall purpose and changes made in these commits.
    - Follow the Git commit message pattern: Use the imperative mood, capitalize the first letter, and omit the period at the end.
    - Example: "✨ Add new feature for user authentication"

- 🔍 Key Changes:
    - 🌟 Feature: Describe any new features or enhancements added
    - 🛠️ Refactor: Mention any significant refactoring or code improvements
    - 🐛 Fix: Note any bug fixes or issue resolutions
    - 📚 Docs: Highlight any updates to documentation
    - 🚀 Perf: Indicate any performance optimizations
    - 🧪 Test: Mention any additions or modifications to tests
    - 🎨 Style: Note any changes related to styling or UI improvements
    - 🔧 Chore: Describe any build process, dependency, or configuration updates
    Add more bullet points as needed, using gitmoji to categorize the changes. You can omit non-mentioned categories.

- 💡 Insights:
    - Provide any additional insights or observations about the commits
    - Mention any potential impact or benefits of the changes
    - Add any relevant notes or suggestions for future improvements

Please ensure the summary adheres to the gitmoji conventions and the Git commit message pattern. Use markdown formatting for clarity and structure.
""".strip()
