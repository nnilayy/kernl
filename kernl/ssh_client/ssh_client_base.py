import os
import pyperclip
import subprocess
from utils.messages import success, fail, caution

class SSHClient:
    def __init__(self, ssh_dir=None):
        self.ssh_dir = ssh_dir or os.path.expanduser("~/.ssh")
        os.makedirs(self.ssh_dir, exist_ok=True)



    def generate_ssh_key(
        self,
        key_type: str = "ed25519",
        bits: int = None,
        email: str = "",
        key_name: str = None,
        passphrase: str = "",
        overwrite_key: bool = False,
    ):
        supported_types = {"rsa", "ecdsa", "ed25519"}
        if key_type not in supported_types:
            raise ValueError(caution(f"Unsupported key_type '{key_type}'. Supported types: {supported_types}"))

        if key_type == "rsa":
            bits = bits or 4096
            if bits not in [2048, 3072, 4096]:
                raise ValueError(caution("RSA key must have bits = 2048, 3072, or 4096"))
        elif key_type == "ecdsa":
            bits = bits or 256
            if bits not in [256, 384, 521]:
                raise ValueError(caution("ECDSA key must have bits = 256, 384, or 521"))
        elif key_type == "ed25519":
            if bits is not None:
                print(caution("Note: ed25519 keys do not use the -b (bit length) parameter. Ignoring it."))
            bits = None

        key_name = key_name or f"id_{key_type}"
        key_path = os.path.join(self.ssh_dir, key_name)

        if os.path.exists(key_path) or os.path.exists(key_path + ".pub"):
            if not overwrite_key:
                raise FileExistsError(caution(f"SSH key '{key_name}' already exists. Set overwrite_key=True to overwrite it or choose a different key_name."))
            else:
                os.remove(key_path) if os.path.exists(key_path) else None
                os.remove(key_path + ".pub") if os.path.exists(key_path + ".pub") else None

        cmd = ["ssh-keygen", "-t", key_type, "-f", key_path, "-N", passphrase]
        if email:
            cmd.extend(["-C", email])
        if bits and key_type != "ed25519":
            cmd.extend(["-b", str(bits)])

        try:
            subprocess.run(cmd, check=True)
            print(success(f"SSH key generated at {key_path} and {key_path}.pub"))
        except subprocess.CalledProcessError as e:
            print(fail(f"Failed to generate SSH key:", e))

        return key_path, key_path + ".pub"



    def list_ssh_keys_from_local_env(self):
        keys = []
        for file in os.listdir(self.ssh_dir):
            path = os.path.join(self.ssh_dir, file)
            if os.path.isfile(path) and file.endswith(".pub"):
                keys.append(file)
        return keys



    def delete_ssh_key_from_local_env(self, key_name: str):
        if not isinstance(key_name, str):
            raise TypeError(caution("Key name must be a string."))
        if not key_name.strip():
            raise ValueError(caution("Key name cannot be an empty string."))

        if key_name.endswith(".pub"):
            key_name = key_name[:-4]

        private_key = os.path.join(self.ssh_dir, key_name)
        public_key = private_key + ".pub"

        deleted = []
        for path in [private_key, public_key]:
            if os.path.exists(path):
                os.remove(path)
                deleted.append(os.path.basename(path))

        if not deleted:
            print(caution(f"No key pair named '{key_name}' found."))
        else:
            print(success(f"Deleted: {', '.join(deleted)}"))



    def expose_public_key(self, key_name: str):
        if not isinstance(key_name, str):
            raise TypeError(caution("Key name must be a string."))
        if not key_name.strip():
            raise ValueError(caution("Key name cannot be an empty string."))
        if not key_name.endswith(".pub"):
            raise ValueError(caution("Only public keys ending with '.pub' can be exposed."))

        pub_key_path = os.path.join(self.ssh_dir, key_name)
        if not os.path.isfile(pub_key_path):
            raise FileNotFoundError(fail(f"Public key '{key_name}' not found in {self.ssh_dir}."))

        with open(pub_key_path, "r") as f:
            public_key = f.read().strip()

        try:
            pyperclip.copy(public_key)
            print(success(f"Public key '{key_name}' copied to clipboard successfully."))
        except pyperclip.PyperclipException:
            print(caution("Copy-to-clipboard not available in this environment."))
            print(caution("Here is the public key:"))
            print(caution(public_key))



    def update_ssh_config(
        self,
        private_key_path: str,
        hostname: str,
        alias: str,
        user: str,
        port: int = 22,
    ):
        if not isinstance(private_key_path, str) or not private_key_path.strip():
            raise ValueError("The private_key_path must be a non-empty string.")
        if not isinstance(hostname, str) or not hostname.strip():
            raise ValueError("The hostname must be a non-empty string.")
        if not isinstance(alias, str) or not alias.strip():
            raise ValueError("The alias must be a non-empty string.")
        if not isinstance(user, str) or not user.strip():
            raise ValueError("The user must be a non-empty string.")
        if not isinstance(port, int) or port <= 0:
            raise ValueError("The port must be a positive integer.")

        private_key_path = os.path.expanduser(private_key_path)
        if not os.path.isfile(private_key_path):
            raise FileNotFoundError(f"Private key file not found: {private_key_path}")

        config_path = os.path.join(self.ssh_dir, "config")
        known_hosts_path = os.path.join(self.ssh_dir, "known_hosts")

        for path in [config_path, known_hosts_path]:
            if not os.path.exists(path):
                with open(path, "w"):
                    pass

        with open(config_path, "r") as f:
            if f"# === BEGIN ALIAS {alias} ===" in f.read():
                print(
                    f"⚠️ Alias '{alias}' already exists in SSH config. Please choose a different alias."
                )
                return

        config_block = f"""
    # === BEGIN ALIAS {alias} ===
    Host {alias}
    HostName {hostname}
    User {user}
    Port {port}
    IdentityFile {private_key_path}
    # === END ALIAS {alias} ===
    """

        with open(config_path, "a") as f:
            f.write(config_block.strip() + "\n")

        os.chmod(config_path, 0o600)
        print(f"✅ SSH config updated with alias '{alias}'.")

        try:
            subprocess.run(
                ["ssh-add", private_key_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("🔑 Private key added to ssh-agent.")
        except subprocess.CalledProcessError:
            print("❌ Failed to add private key to ssh-agent. Is the agent running?")

        try:
            with open(known_hosts_path, "a") as kh:
                subprocess.run(
                    ["ssh-keyscan", "-p", str(port), hostname],
                    stdout=kh,
                    check=True,
                    stderr=subprocess.DEVNULL,
                )
            os.chmod(known_hosts_path, 0o644)
            print(f"🔐 Host '{hostname}' added to known_hosts.")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to scan and add {hostname} to known_hosts.")



    def reset_ssh_config(
        self, delete_config: bool = True, delete_known_hosts: bool = True
    ):
        if not delete_config and not delete_known_hosts:
            print("⚠️ Nothing to reset. Both flags are set to False.")
            return

        if delete_config:
            config_path = os.path.join(self.ssh_dir, "config")
            if os.path.exists(config_path):
                os.remove(config_path)
                print(f"🧹 Removed {config_path}")
            with open(config_path, "w"):
                pass
            os.chmod(config_path, 0o600)
            print("✅ SSH config reset.")

        if delete_known_hosts:
            for name in ["known_hosts", "known_hosts.old"]:
                path = os.path.join(self.ssh_dir, name)
                if os.path.exists(path):
                    os.remove(path)
                    print(f"🧹 Removed {path}")
                with open(path, "w"):
                    pass
                os.chmod(path, 0o644)
            print("✅ known_hosts files reset.")



    def verify_remote_ssh_connection(self, host: str):
        """
        Verifies SSH connection to a given host (e.g., github.com).
        """
        print(f"Verifying SSH connection to {host}...")
        try:
            result = subprocess.run(
                ["ssh", "-T", f"git@{host}"], capture_output=True, text=True
            )
            print(result.stderr.strip() or result.stdout.strip())
            if "successfully authenticated" in result.stderr:
                print("✅ SSH connection successful.")
            else:
                print("❌ SSH connection failed.")
        except subprocess.CalledProcessError as e:
            print("❌ SSH verification command failed:", e)



    @staticmethod
    def set_git_credentials(user_name: str, user_email: str, global_scope: bool = True):
        print("Setting up Git credentials...")

        if not isinstance(user_name, str) or not user_name.strip():
            raise ValueError("The 'user_name' must be a non-empty string.")
        if not isinstance(user_email, str) or not user_email.strip():
            raise ValueError("The 'user_email' must be a non-empty string.")

        scope = "--global" if global_scope else "--local"

        try:
            subprocess.run(
                ["git", "config", scope, "user.name", user_name],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", scope, "user.email", user_email],
                check=True,
                capture_output=True,
                text=True,
            )

            print(
                f"✅ Git credentials set {'globally' if global_scope else 'locally'}:"
            )
            print(f"  Name : {user_name}")
            print(f"  Email: {user_email}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to set Git credentials: {e.stderr or str(e)}")
            raise
