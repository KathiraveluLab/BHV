import os
import base64
import requests
from dotenv import load_dotenv
import re

load_dotenv()

class GithubStorage:
    TOKEN = os.getenv("GITHUB_TOKEN")
    ORG = os.getenv("ORG_NAME")
    HEADERS = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    @staticmethod
    def clean_repo_name(name, user_id=None):
        
        name = name.lower()
        name = re.sub(r'[^a-z0-9]+', '-', name)
        name = re.sub(r'-+', '-', name).strip('-')
        
        if user_id:
            name = f"{name}-{user_id}"
            
        return name

    @staticmethod
    def get_or_create_repo(repo_name, user_id=None):
        unique_repo_name = GithubStorage.clean_repo_name(repo_name, user_id)
        url = f"https://api.github.com/repos/{GithubStorage.ORG}/{unique_repo_name}"
        response = requests.get(url, headers=GithubStorage.HEADERS)

        if response.status_code == 200:
            return True
        
        create_url = f"https://api.github.com/orgs/{GithubStorage.ORG}/repos"
        payload = {
            "name": unique_repo_name,
            "private": False,
            "auto_init": True
        }
        res = requests.post(create_url, headers=GithubStorage.HEADERS, json=payload)
        return res.status_code == 201

    @staticmethod
    def upload_file(repo_name, file_content, filename, user_id=None, commit_message="Upload via Web App"):
        unique_repo_name = GithubStorage.clean_repo_name(repo_name, user_id)
        
        GithubStorage.get_or_create_repo(repo_name, user_id)    

        path = f"img/{filename}"
        url = f"https://api.github.com/repos/{GithubStorage.ORG}/{unique_repo_name}/contents/{path}"
        
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "message": commit_message,
            "content": encoded_content
        }
        
        response = requests.put(url, headers=GithubStorage.HEADERS, json=payload)
        
        if response.status_code in [200, 201]:
            return f"https://raw.githubusercontent.com/{GithubStorage.ORG}/{unique_repo_name}/main/{path}"
        return None

    @staticmethod
    def delete_file(repo_name, filename, user_id=None):
        unique_repo_name = GithubStorage.clean_repo_name(repo_name, user_id)
        path = f"img/{filename}"
        url = f"https://api.github.com/repos/{GithubStorage.ORG}/{unique_repo_name}/contents/{path}"

        res = requests.get(url, headers=GithubStorage.HEADERS)
        if res.status_code != 200:
            return False

        sha = res.json().get("sha")

        payload = {
            "message": f"Delete {filename} via Web App",
            "sha": sha
        }

        delete_res = requests.delete(url, headers=GithubStorage.HEADERS, json=payload)
        return delete_res.status_code == 200