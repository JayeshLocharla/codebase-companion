import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def download_py_files(repo_full_name, save_dir="data/repos"):
    """
    Recursively downloads all .py files from a GitHub repo.
    """
    def crawl(path=""):
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {url}")
            return

        items = response.json()
        for item in items:
            if item["type"] == "file" and item["name"].endswith(".py"):
                save_path = os.path.join(save_dir, repo_full_name.replace("/", "_"), item["path"])
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file_res = requests.get(item["download_url"])
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(file_res.text)
                print(f"✅ Downloaded: {item['path']}")
            elif item["type"] == "dir":
                crawl(item["path"])

    crawl()

if __name__ == "__main__":
    repo = input("Enter GitHub repo (e.g., psf/requests): ")
    download_py_files(repo)
