import os
import subprocess
from urllib.parse import urlparse

def download_github_repo(repo_url: str, target_dir="data/repos") -> str:
    """Clones a GitHub repo and returns the local path."""

    # Parse URL and extract user/repo name
    try:
        parsed_url = urlparse(repo_url)
        parts = parsed_url.path.strip("/").split("/")
        if len(parts) != 2:
            raise ValueError("❌ Invalid GitHub URL. Use format: https://github.com/owner/repo")
        user_name, repo_name = parts
    except Exception as e:
        raise ValueError(f"❌ Failed to parse repo URL: {e}")

    local_path = os.path.join(target_dir, f"{user_name}_{repo_name}")

    # If already cloned
    if os.path.exists(local_path):
        print(f"📦 Repo already exists locally at: {local_path}")
        return local_path

    # Run git clone
    print(f"⬇️ Cloning repo to: {local_path}")
    subprocess.run(["git", "clone", repo_url, local_path], check=True)
    return local_path
