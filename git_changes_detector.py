import requests
import os
import sys

def get_commit_data():
    """Gets commit data including changed files and diff content using GitHub API."""
    repo = os.getenv("GITHUB_REPOSITORY")
    commit_sha = os.getenv("GITHUB_SHA")
    token = os.getenv("GITHUB_TOKEN")
    
    if not repo or not commit_sha or not token:
        print("Missing required environment variables.", file=sys.stderr)
        sys.exit(1)
    
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commit_data = response.json()
        
        changed_files = [file["filename"] for file in commit_data.get("files", [])]
        diff_content = requests.get(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3.diff"}).text.strip()
        
        return changed_files, diff_content
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving commit data: {e}", file=sys.stderr)
        return [], ""

def main():
    changed_files, diff_content = get_commit_data()
    
    if changed_files:
        package_path = " ".join(changed_files)  # Store the changed file paths in PACKAGE_PATH
        print(f"PACKAGE_PATH={package_path}")
        print("Changed files:")
        for file in changed_files:
            print(file)
    else:
        print("No files changed in the current commit.")
    
    if diff_content:
        print("\nDiff content:")
        print(diff_content)
    else:
        print("No diff content available.")

if __name__ == "__main__":
    main()
