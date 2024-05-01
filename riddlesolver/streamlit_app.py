import configparser
from datetime import datetime, timedelta

import streamlit as st

from repository import fetch_commits
from summary import generate_commit_summary
from utils import get_repository_type

# Load the configuration
config = configparser.ConfigParser()
config.add_section("github")
config.add_section("openai")

# Set the page title
st.set_page_config(page_title="RiddleSolver", page_icon=":mag_right:")

# Add a title and description
st.title("RiddleSolver 🎩🔍")
st.write(
    "RiddleSolver is like a magical genie 🧞‍ that grants your wish to understand the cryptic riddles known as Git "
    "commits. With a wave of its virtual wand 🪄, RiddleSolver conjures up clear, concise, and standardized summaries "
    "of your Git commit messages, leaving you in awe and amazement! 🎆")

# Sidebar inputs
st.sidebar.title("Configuration")
access_token = st.sidebar.text_input("Access Token", type="password", placeholder="Enter your GitHub access token")
api_key = st.sidebar.text_input("API Key", type="password", placeholder="Enter your OpenAI API key")
model = st.sidebar.text_input("Model", placeholder="Enter the OpenAI model", value="gpt-3.5-turbo")
base_url = st.sidebar.text_input("Base URL", placeholder="Enter the OpenAI API base URL",
                                 value="https://api.openai.com/v1")

# Input fields
repo_url = st.text_input("Repository URL", placeholder="Enter GitHub repository URL")
col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", value=datetime.now() - timedelta(days=7))
end_date = col2.date_input("End Date", value=datetime.now())
branch = col1.text_input("Branch (optional)", placeholder="Enter branch name")
author = col2.text_input("Author (optional)", placeholder="Enter author name or email")

# Generate summary button
if st.button("Generate Summary"):
    with st.spinner("Generating summary..."):
        if repo_url and access_token and api_key:
            try:
                repo_type = get_repository_type(repo_url)
                if repo_type == "github":
                    repo_name = repo_url.split("/")[-1]
                    # Update the configuration temporarily
                    config.set("github", "access_token", access_token)
                    config.set("openai", "api_key", api_key)
                    if model:
                        config.set("openai", "model", model)
                    if base_url:
                        config.set("openai", "base_url", base_url)

                    batched_commits = fetch_commits(repo_url, start_date, end_date, branch, author, access_token,
                                                    repo_type)
                    summary = generate_commit_summary(batched_commits, config)

                    if not summary:
                        st.error("No commits found in the specified date range.")
                    else:
                        with st.expander("Summary Results", expanded=True):
                            st.text(summary)
                    st.success("Summary generated successfully!")

                    branch_msg = f"_{branch}" if branch else ""
                    author_msg = f"_{author}" if author else ""
                    if st.download_button("Download Summary", data=summary, file_name=f"{repo_name}{branch_msg}{author_msg}_summary.txt"):
                        st.write("Downloaded summary successfully!")
                else:
                    st.error("Only GitHub repositories are supported.")
            except Exception as e:
                st.error(str(e))
        else:
            if not repo_url:
                st.warning("Please enter a repository URL.")
            if not access_token:
                st.warning("Please enter your GitHub access token.")
            if not api_key:
                st.warning("Please enter your OpenAI API key.")
