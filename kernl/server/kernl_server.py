import os
import time
import socket
import string
import shutil
import secrets
import logging
import pyperclip
import subprocess
from tqdm import tqdm
from pyngrok import ngrok

logging.getLogger("pyngrok").setLevel(logging.WARNING)


class KernlServer:
    def __init__(
        self,
        dataset_manager,
        ngrok_auth_token,
        working_directory=None,
        password=None,
        load_existing_vsc_config_by_id=None,
        extensions=None,
    ):
        if dataset_manager is None:
            raise ValueError(
                "Dataset manager is required for uploading/downloading datasets."
            )
        if ngrok_auth_token is None:
            raise ValueError(
                "Ngrok auth token is required to expose VSCode server publicly."
            )

        self.dataset_manager = dataset_manager
        self.ngrok_auth_token = ngrok_auth_token
        self.password = password
        self.working_directory = working_directory or os.getcwd()
        self.load_existing_vsc_config_by_id = load_existing_vsc_config_by_id
        self.extensions = extensions or []
        self.config_path = os.path.expanduser("~/.local/share/code-server")
        self._handle_password()

    def save_venv(self, slug_id="venv-backup", venv_path="venv", visibility="private"):
        venv_full_path = os.path.join(self.working_directory, venv_path)
        if not os.path.exists(venv_full_path):
            raise FileNotFoundError(
                f"Virtual environment not found at {venv_full_path}"
            )

        print(
            f"Saving virtual environment from {venv_full_path} to Kaggle as {slug_id}..."
        )
        self.dataset_manager.upload_dataset(
            slug_id=slug_id, folder_path=venv_full_path, visibility=visibility
        )
        print(
            f"Virtual environment saved to Kaggle dataset {self.dataset_manager.username}/{slug_id}"
        )

    def load_venv(self, slug_id="venv-backup", venv_path="venv"):
        venv_full_path = os.path.abspath(venv_path)
        os.makedirs(venv_full_path, exist_ok=True)

        print(
            f"Loading venv from {self.dataset_manager.username}/{slug_id} to {venv_full_path}..."
        )
        self.dataset_manager.download_dataset(
            slug_id=slug_id, output_dir=venv_full_path, extract=True
        )
        print(f"Venv loaded at lightning speed to {venv_full_path}!")

    def save_vs_code_config(self, slug_id="my-vscode-config", visibility="private"):
        parent_dir = os.path.dirname(self.config_path)
        vsc_config_dir = os.path.join(parent_dir, "vsc-config")
        print(vsc_config_dir)

        if os.path.exists(vsc_config_dir):
            shutil.rmtree(vsc_config_dir)

        os.makedirs(vsc_config_dir, exist_ok=True)

        user_src = os.path.join(self.config_path, "User")
        extensions_src = os.path.join(self.config_path, "extensions")

        if os.path.exists(user_src):
            shutil.copytree(user_src, os.path.join(vsc_config_dir, "User"))
        if os.path.exists(extensions_src):
            shutil.copytree(extensions_src, os.path.join(vsc_config_dir, "extensions"))

        self.dataset_manager.upload_dataset(
            slug_id=slug_id, folder_path=vsc_config_dir, visibility=visibility
        )

        shutil.rmtree(vsc_config_dir)

    def _load_vsc_config(self, slug_id="my-vscode-config"):
        parent_dir = os.path.dirname(self.config_path)
        vsc_config_dir = os.path.join(parent_dir, "vsc-config")

        if os.path.exists(vsc_config_dir):
            shutil.rmtree(vsc_config_dir)

        print(f"[⬇️] Downloading config into: {parent_dir}")
        self.dataset_manager.download_dataset(slug_id=slug_id, output_dir=parent_dir)

        user_src = os.path.join(vsc_config_dir, "User")
        extensions_src = os.path.join(vsc_config_dir, "extensions")
        user_dest = os.path.join(self.config_path, "User")
        extensions_dest = os.path.join(self.config_path, "extensions")

        if os.path.isdir(user_src):
            if os.path.exists(user_dest):
                shutil.rmtree(user_dest)
            shutil.copytree(user_src, user_dest)

        if os.path.isdir(extensions_src):
            if os.path.exists(extensions_dest):
                shutil.rmtree(extensions_dest)
            shutil.copytree(extensions_src, extensions_dest)

        shutil.rmtree(vsc_config_dir)

    def _handle_password(self):
        if not self.password:
            self.password = "".join(
                secrets.choice(
                    string.ascii_letters + string.digits + string.punctuation
                )
                for _ in range(16)
            )
        try:
            pyperclip.copy(self.password)
            print("[🔐] Password copied to clipboard.")
        except pyperclip.PyperclipException:
            print(f"[❌] Cannot copy password to clipboard. Your password for this session is: {self.password}")


        return self.password

    def install_code_server(self):
        try:
            subprocess.run(
                ["code-server", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("code-server is already installed.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Installing code-server...")
            try:
                subprocess.run(
                    "curl -fsSL https://code-server.dev/install.sh | sh",
                    shell=True,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print("code-server installation complete.")
            except subprocess.CalledProcessError as e:
                print("Failed to install code-server.")
                print("Details:\n", e)

    def install_extensions(self):
        extensions_dir = os.path.join(self.config_path, "extensions")
        existing = (
            set(ext.lower() for ext in os.listdir(extensions_dir))
            if os.path.isdir(extensions_dir)
            else set()
        )

        if self.extensions:
            for ext in tqdm(self.extensions, desc="Installing Extensions", unit="ext"):
                if any(ext.lower() in name for name in existing):
                    continue  # Already installed via config
                try:
                    subprocess.run(
                        ["code-server", "--install-extension", ext],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except subprocess.CalledProcessError:
                    tqdm.write(f"❌ Failed to install extension: {ext}")

    def find_available_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def start_code_server(self, port):
        os.environ["PASSWORD"] = self.password
        os.environ.pop("VSCODE_IPC_HOOK_CLI", None)
        cmd = f"nohup code-server --bind-addr 0.0.0.0:{port} --auth password {self.working_directory} > code.log 2>&1 &"
        os.system(cmd)
        time.sleep(3)

    def setup_ngrok(self, port):
        ngrok.set_auth_token(self.ngrok_auth_token)
        tunnel = ngrok.connect(port)
        return tunnel.public_url

    def wait_until_port_open(self, port, timeout=60):
        """Wait until a local TCP port is open."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("0.0.0.0", port))
                if result == 0:
                    return True
            time.sleep(0.5)
        raise TimeoutError(
            f"[⏱] Timed out waiting for code-server to start on port {port}."
        )

    def start(self):
        try:
            self.install_code_server()

            if self.load_existing_vsc_config_by_id:
                self._load_vsc_config(self.load_existing_vsc_config_by_id)

            port = self.find_available_port()
            self.start_code_server(port)
            self.wait_until_port_open(port)

            self.install_extensions()

            public_url = self.setup_ngrok(port)
            print("Public URL:", public_url + "/?folder=" + self.working_directory)
            print("[🟢] VSCode server is running.")

        except Exception:
            print("[🔴] VSCode server stopped.")
            raise
