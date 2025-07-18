import os
import requests
from base64 import b64encode
from .ssh_client_base import SSHClient


class BitbucketSSHClient(SSHClient):
    def __init__(self):
        super().__init__()
        self.email = None
        self.token = None
        self.username = None
        self.api_base_url = "https://api.bitbucket.org/2.0/users"

    def set_bitbucket_api_token(self, email: str, token: str):
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Bitbucket email must be a non-empty string.")
        if not isinstance(token, str) or not token.strip():
            raise ValueError("API token must be a non-empty string.")
        self.email = email.strip()
        self.token = token.strip()

        # Get username from token
        headers = self._build_auth_headers()
        response = requests.get("https://api.bitbucket.org/2.0/user", headers=headers)
        if response.status_code == 200:
            self.username = response.json().get("username")
            print(f"✅ Bitbucket API token set successfully for user: {self.username}")
        else:
            raise RuntimeError(f"❌ Failed to verify token: {response.status_code} - {response.text}")

    def _require_token(self):
        if not self.email or not self.token or not self.username:
            raise RuntimeError(
                "Bitbucket credentials not fully set. Use set_bitbucket_api_token(email, token) first."
            )

    def _build_auth_headers(self):
        auth_string = f"{self.email}:{self.token}"
        encoded = b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }

    def add_ssh_key_to_bitbucket(self, title: str, ssh_key_path: str):
        self._require_token()

        if not title or not ssh_key_path.endswith(".pub"):
            raise ValueError("A title and a valid public key file (.pub) are required.")
        if not os.path.isfile(ssh_key_path):
            raise FileNotFoundError(f"SSH public key not found at: {ssh_key_path}")

        with open(ssh_key_path, "r") as f:
            public_key = f.read().strip()

        payload = {"label": title.strip(), "key": public_key}
        headers = self._build_auth_headers()
        url = f"{self.api_base_url}/{self.username}/ssh-keys"

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            key_data = response.json()
            print(f"✅ SSH key '{title}' added to Bitbucket (ID: {key_data.get('pk')}).")
            return key_data.get("pk")
        else:
            print(f"❌ Failed to add SSH key to Bitbucket: {response.status_code}")
            try:
                print(response.json())
            except Exception:
                print(response.text)
            return None

    def list_ssh_keys_from_bitbucket(self):
        self._require_token()
        headers = self._build_auth_headers()
        url = f"{self.api_base_url}/{self.username}/ssh-keys"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Failed to list SSH keys: {response.status_code}")
            try:
                print(response.json())
            except Exception:
                print(response.text)
            return []

        keys = response.json().get("values", [])
        if not keys:
            print("ℹ️ No SSH keys found in your Bitbucket account.")
            return []

        print("📌 SSH Keys on Bitbucket:")
        for key in keys:
            print(f"- UUID: {key['uuid']} | Label: {key['label']} | Created: {key['created_on']}")
        return keys

    def delete_ssh_key_from_bitbucket(self, key_id: str):
        self._require_token()
        headers = self._build_auth_headers()

        delete_url = f"{self.api_base_url}/{self.username}/ssh-keys/{key_id}"
        response = requests.delete(delete_url, headers=headers)

        if response.status_code == 204:
            print(f"✅ SSH key with UUID {key_id} deleted from Bitbucket.")
        elif response.status_code == 404:
            print(f"❌ SSH key with UUID {key_id} not found on Bitbucket.")
        else:
            print(f"❌ Failed to delete SSH key from Bitbucket (status: {response.status_code})")
            try:
                print(response.json())
            except Exception:
                print(response.text)

    def validate_token(self):
        self._require_token()
        headers = self._build_auth_headers()
        response = requests.get("https://api.bitbucket.org/2.0/user", headers=headers)
        if response.status_code == 200:
            print("✅ Bitbucket API token is valid.")
            return True
        print(f"❌ Invalid Bitbucket token. Status: {response.status_code}")
        try:
            print(response.json())
        except Exception:
            print(response.text)
        return False
