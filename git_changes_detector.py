import requests
import os
import sys

def get_diff_content():
    """Gets the diff content for the changed files in the current commit using GitHub API."""
    repo = os.getenv("GITHUB_REPOSITORY")
    commit_sha = os.getenv("GITHUB_SHA")
    token = os.getenv("GITHUB_TOKEN")
    
    if not repo or not commit_sha or not token:
        print("Missing required environment variables.", file=sys.stderr)
        sys.exit(1)
    
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3.diff"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving diff content: {e}", file=sys.stderr)
        return ""

def main():
    diff_content = get_diff_content()
    
    if diff_content:
        print("Diff content:")
        print(diff_content)
    else:
        print("No diff content available.")

if __name__ == "__main__":
    main()