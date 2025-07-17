import os
import re
import json
import shutil
import logging
import tempfile
import subprocess
from .dataset_manager_base import BaseDatasetManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KaggleManager(BaseDatasetManager):
    def __init__(self):
        self.kaggle_json_path = None
        self.username = None
        self.license_name = "CC0-1.0"

    def set_token(self, kaggle_json_path: str) -> None:
        self.kaggle_json_path = kaggle_json_path

        if not os.path.exists(kaggle_json_path):
            raise FileNotFoundError(f"Kaggle config file not found: {kaggle_json_path}")

        with open(kaggle_json_path, "r") as f:
            try:
                kaggle_config = json.load(f)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in kaggle config: {kaggle_json_path}")

        self.username = kaggle_config.get("username")
        if not self.username:
            raise ValueError("Username not found in kaggle.json")

        kaggle_config_dir = os.path.expanduser("~/.config/kaggle")
        dest_path = os.path.join(kaggle_config_dir, "kaggle.json")

        os.makedirs(kaggle_config_dir, exist_ok=True)
        shutil.copy(kaggle_json_path, dest_path)
        os.chmod(dest_path, 0o600)
        logger.info(f"Kaggle API key setup complete at {dest_path}")

    def _generate_title(self, slug: str) -> str:
        words = re.split(r"[-_.\s]+", slug)
        return " ".join(word.capitalize() for word in words if word)

    def set_license(self, license_name: str) -> None:
        self.license_name = license_name

    def _require_token(self):
        if not self.kaggle_json_path or not self.username:
            raise RuntimeError("Kaggle token not set. Call set_token(path) first.")

    def _create_metadata(self, title: str, slug: str) -> dict:
        return {
            "title": title,
            "id": f"{self.username}/{slug}",
            "licenses": [{"name": self.license_name}],
        }

    def _validate_kaggle_slug_id(self, slug_id: str) -> None:
        if not (6 <= len(slug_id) <= 50):
            raise ValueError(
                f"Invalid slug ID '{slug_id}': must be between 6 and 50 characters long."
            )
        if not re.fullmatch(r"[A-Za-z0-9-]+", slug_id):
            raise ValueError(
                f"Invalid slug ID '{slug_id}': only letters (A–Z, a–z), numbers (0–9), and hyphens (-) are allowed."
            )

    def upload_dataset(
        self, slug_id: str, folder_path: str, visibility: str = "private"
    ) -> None:
        self._require_token()
        self._validate_kaggle_slug_id(slug_id)

        if visibility not in ("public", "private"):
            raise ValueError("Visibility must be either 'public' or 'private'.")

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        if not os.path.isdir(folder_path):
            raise ValueError(
                "Only folders can be uploaded as datasets.\n"
                "Tip: Move your files into a folder and upload that folder instead."
            )

        repo_id = f"{self.username}/{slug_id}"
        folder_name = os.path.basename(folder_path)
        temp_dir = tempfile.mkdtemp(prefix="kaggle_upload_")

        print(f"Compressing {folder_path} to {repo_id} with LZ4...")

        lz4_file = os.path.join(temp_dir, f"{folder_name}.lz4")
        self.tar_lz4_compression(folder_path, lz4_file)

        metadata = self._create_metadata(self._generate_title(slug_id), slug_id)
        metadata_file = os.path.join(temp_dir, "dataset-metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        kaggle_command = ["kaggle", "datasets", "create", "-p", temp_dir]
        if visibility == "public":
            kaggle_command.append("--public")

        logger.info("Starting dataset upload...")

        try:
            result = subprocess.run(
                kaggle_command, capture_output=True, text=True, timeout=600, check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Upload failed (return code {e.returncode}): {e.stderr}")
            raise RuntimeError(f"Dataset upload failed: {e.stderr.strip()}") from e
        except subprocess.TimeoutExpired:
            logger.error("Upload timed out after 10 minutes")
            raise RuntimeError(
                "Upload timeout - the dataset may be too large or network is slow"
            )
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        logger.info("Dataset upload completed successfully")
        print(
            f"Dataset uploaded successfully: https://www.kaggle.com/datasets/{repo_id}"
        )

    def download_dataset(self, slug_id: str, output_dir: str = ".") -> None:
        self._require_token()

        repo_id = f"{self.username}/{slug_id}"
        os.makedirs(output_dir, exist_ok=True)

        print(f"Downloading {repo_id} to {output_dir}...")

        kaggle_command = [
            "kaggle",
            "datasets",
            "download",
            "-d",
            repo_id,
            "-p",
            output_dir,
            "--unzip",
        ]

        try:
            result = subprocess.run(
                kaggle_command, capture_output=True, text=True, timeout=600
            )
            if result.returncode != 0:
                logger.error(f"Download failed: {result.stderr}")
                raise RuntimeError(
                    f"Download failed with code {result.returncode}: {result.stderr}"
                )

            print("Download completed successfully.")
            self.tar_lz4_decompression(output_dir)

        except subprocess.TimeoutExpired:
            logger.error("Download timed out after 10 minutes")
            raise RuntimeError("Download timeout")
        except Exception as e:
            logger.error(f"Download error: {e}")
            raise
