import os
import re
import shutil
import logging
import tempfile
from .dataset_manager_base import BaseDatasetManager
from huggingface_hub import HfApi, snapshot_download

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HuggingFaceManager(BaseDatasetManager):
    def __init__(self):
        self.token = None
        self.api = None
        self.username = None

    def set_token(self, token: str) -> None:
        self.token = token
        self.api = HfApi()
        self.username = self.get_username()

    def get_username(self) -> str:
        if not self.api or not self.token:
            raise RuntimeError("API not initialized. Call set_token() first.")
        return self.api.whoami(token=self.token)["name"]

    def _require_token(self):
        if not self.token or not self.api or not self.username:
            raise RuntimeError("Token not set. Call set_token(token) first.")

    def _generate_repo_id(self, slug_id: str) -> str:
        self._require_token()
        return f"{self.username}/{slug_id}"

    def _validate_hf_slug_id(self, slug: str) -> None:
        if not (1 <= len(slug) <= 96):
            raise ValueError(f"Slug '{slug}' must be between 1 and 96 characters long.")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", slug):
            raise ValueError(
                "Slug can only contain letters, numbers, hyphens (-), underscores (_), and periods (.)"
            )
        if slug.startswith(("-", ".")) or slug.endswith(("-", ".")):
            raise ValueError("Slug cannot start or end with a hyphen (-) or period (.)")
        if "--" in slug or ".." in slug:
            raise ValueError(
                "Slug cannot contain consecutive hyphens (--) or periods (..)"
            )
        if slug.endswith(".git") or slug.endswith(".ipynb"):
            raise ValueError("Slug cannot end with '.git' or '.ipynb'")

    def _create_repo(self, slug_id: str, private: bool = False) -> None:
        repo_id = self._generate_repo_id(slug_id)
        try:
            self.api.create_repo(
                repo_id=repo_id,
                repo_type="dataset",
                private=private,
                exist_ok=True,
                token=self.token,
            )
            logger.info(
                f"Repo created or exists: https://huggingface.co/datasets/{repo_id}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create dataset repo: {e}")

    def upload_dataset(
        self, slug_id: str, folder_path: str, visibility: str = "private"
    ) -> None:
        self._require_token()
        self._validate_hf_slug_id(slug_id)

        if visibility not in ("public", "private"):
            raise ValueError("Visibility must be either 'public' or 'private'.")

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Path not found: {folder_path}")

        if not os.path.isdir(folder_path):
            raise ValueError(
                "Only folders can be uploaded as datasets.\n"
                "Tip: Move your files into a folder and upload that folder instead."
            )

        repo_id = self._generate_repo_id(slug_id)

        folder_name = os.path.basename(folder_path)
        temp_dir = tempfile.mkdtemp(prefix="hf_upload_")

        print(f"Compressing {folder_path} to {repo_id} with LZ4...")

        lz4_file = os.path.join(temp_dir, f"{folder_name}.lz4")
        self.tar_lz4_compression(folder_path, lz4_file)

        is_private = visibility == "private"
        self._create_repo(slug_id, private=is_private)

        try:
            self.api.upload_folder(
                folder_path=temp_dir,
                repo_id=repo_id,
                repo_type="dataset",
                token=self.token,
            )
            logger.info(f"Uploaded folder: https://huggingface.co/datasets/{repo_id}")
        except Exception as e:
            raise RuntimeError(f"Upload failed: {e}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def download_dataset(self, slug_id: str, output_dir: str = ".") -> None:
        self._require_token()
        repo_id = self._generate_repo_id(slug_id)
        os.makedirs(output_dir, exist_ok=True)

        try:
            snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=output_dir,
                token=self.token,
                ignore_patterns=[".gitattributes"],
            )
            logger.info(f"Downloaded dataset to: {output_dir}")
            self.tar_lz4_decompression(output_dir)

            cache_path = os.path.join(output_dir, ".cache")
            if os.path.isdir(cache_path):
                shutil.rmtree(cache_path)
                logger.info("Removed .cache directory after download.")

        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")
