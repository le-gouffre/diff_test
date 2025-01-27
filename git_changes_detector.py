import requests
import os
import sys

def get_commit_data():
    """Gets commit data including changed files and diff content using GitHub API."""
    repo = os.getenv("GITHUB_REPOSITORY")
    commit_sha = os.getenv("GITHUB_SHA")
    token = os.getenv("GITHUB_TOKEN")
    workspace = os.getenv("GITHUB_WORKSPACE")  # Get the absolute workspace path
    
    if not repo or not commit_sha or not token or not workspace:
        print("Missing required environment variables.", file=sys.stderr)
        sys.exit(1)
    
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commit_data = response.json()
        
        changed_files = [os.path.join(workspace, file["filename"]) for file in commit_data.get("files", [])]
        diff_content = requests.get(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3.diff"}).text.strip()
        
        return changed_files, diff_content
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving commit data: {e}", file=sys.stderr)
        return [], ""

def main():
    changed_files, diff_content = get_commit_data()
    
    if changed_files:
        package_path = " ".join(changed_files)  # Store the full absolute paths in PACKAGE_PATH
        print(f"PACKAGE_PATH={package_path}")

        # Export PACKAGE_PATH for use in subsequent GitHub Actions steps
        github_env = os.getenv("GITHUB_ENV")
        if github_env:
            with open(github_env, "a") as env_file:
                env_file.write(f"PACKAGE_PATH={package_path}\n")
        
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
