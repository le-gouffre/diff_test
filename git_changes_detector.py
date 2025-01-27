import requests
import os
import sys
import re

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

def normalize_path(path):
    """Ensures PACKAGE_PATH uses Windows-style backslashes."""
    return path.replace("/", "\\")

def extract_package_name(package_path):
    """Extracts the package name from the PACKAGE_PATH."""
    path_parts = package_path.replace("\\", "/").split("/")
    if "tools" in path_parts and len(path_parts) >= 3:
        tools_index = path_parts.index("tools")
        return f"{path_parts[tools_index+1]}_{path_parts[tools_index+2]}"
    return ""

def extract_package_version(diff_content):
    """Extracts the package version from config.yaml diff."""
    version_pattern = re.compile(r'\+\s+"(\d+\.\d+\.\d+)":')
    match = version_pattern.search(diff_content)
    return match.group(1) if match else ""

def main():
    changed_files, diff_content = get_commit_data()
    
    # Filter PACKAGE_PATH to include only config.yml changes
    config_files = [file for file in changed_files if file.endswith("config.yml")]
    package_path = normalize_path(" ".join(config_files)) if config_files else ""
    
    package_name = extract_package_name(config_files[0]) if config_files else ""
    package_version = extract_package_version(diff_content) if config_files else ""
    
    print(f"PACKAGE_PATH={package_path}")
    print(f"PACKAGE_NAME={package_name}")
    print(f"PACKAGE_VERSION={package_version}")

    # Export variables for use in GitHub Actions
    github_env = os.getenv("GITHUB_ENV")
    if github_env:
        with open(github_env, "a") as env_file:
            env_file.write(f"PACKAGE_PATH={package_path}\n")
            env_file.write(f"PACKAGE_NAME={package_name}\n")
            env_file.write(f"PACKAGE_VERSION={package_version}\n")
    
    print("Changed files:")
    for file in changed_files:
        print(file)
    
    if diff_content:
        print("\nDiff content:")
        print(diff_content)
    else:
        print("No diff content available.")

if __name__ == "__main__":
    main()
