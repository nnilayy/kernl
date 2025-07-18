import os
import requests
from .ssh_client_base import SSHClient


class GitLabSSHClient(SSHClient):
    def __init__(self):
        super().__init__()
        self.gitlab_token = None
        self.api_url = "https://gitlab.com/api/v4/user/keys"

    def set_gitlab_personal_access_token(self, token: str):
        if not isinstance(token, str) or not token.strip():
            raise ValueError("Token must be a non-empty string.")
        self.gitlab_token = token.strip()
        print("✅ GitLab token set successfully.")

    def _require_token(self):
        if not self.gitlab_token:
            raise RuntimeError(
                "GitLab token not set. Please use set_gitlab_personal_access_token(token) before calling this method."
            )

    def add_ssh_key_to_gitlab(self, title: str, ssh_key_path: str):
        self._require_token()

        if not isinstance(title, str) or not title.strip():
            raise ValueError("The 'title' must be a non-empty string.")
        if not isinstance(ssh_key_path, str) or not ssh_key_path.strip():
            raise ValueError("The 'ssh_key_path' must be a non-empty string.")
        if not ssh_key_path.endswith(".pub"):
            raise ValueError("The provided SSH key must be a public key file ending with '.pub'.")
        if not os.path.isfile(ssh_key_path):
            raise FileNotFoundError(f"Public key not found at: {ssh_key_path}")

        with open(ssh_key_path, "r") as f:
            public_key = f.read().strip()

        headers = {"PRIVATE-TOKEN": self.gitlab_token}
        payload = {"title": title.strip(), "key": public_key}

        response = requests.post(self.api_url, json=payload, headers=headers)

        if response.status_code == 201:
            key_data = response.json()
            print(f"✅ SSH key '{title}' added to GitLab successfully (ID: {key_data['id']}).")
            return key_data["id"]
        else:
            print(f"❌ Failed to add SSH key to GitLab: {response.status_code}")
            print(response.json())
            return None

    def list_ssh_keys_from_gitlab(self):
        self._require_token()

        headers = {"PRIVATE-TOKEN": self.gitlab_token}
        response = requests.get(self.api_url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Failed to fetch SSH keys: {response.status_code}")
            print(response.json())
            return []

        keys = response.json()
        if not keys:
            print("ℹ️ No SSH keys found in your GitLab account.")
            return []

        print("📌 SSH Keys on GitLab:")
        for key in keys:
            print(f"- ID: {key['id']} | Title: {key['title']} | Created: {key['created_at']}")

        return keys

    def delete_ssh_key_from_gitlab(self, key_id: int):
        self._require_token()

        if not isinstance(key_id, int):
            raise ValueError("The 'key_id' must be an integer.")

        delete_url = f"{self.api_url}/{key_id}"
        headers = {"PRIVATE-TOKEN": self.gitlab_token}

        response = requests.delete(delete_url, headers=headers)

        if response.status_code == 204:
            print(f"✅ SSH key with ID {key_id} deleted successfully from GitLab.")
        elif response.status_code == 404:
            print(f"❌ SSH key with ID {key_id} not found on GitLab.")
        else:
            print(f"❌ Failed to delete SSH key from GitLab (status code {response.status_code}):")
            print(response.json())

