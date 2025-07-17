import os
import shutil
import logging
import subprocess

logger = logging.getLogger(__name__)


class BaseDatasetManager:
    def _install_lz4(self) -> None:
        if shutil.which("lz4") is not None:
            return
        logger.info("lz4 not found. Attempting to install with sudo...")
        try:
            subprocess.run(
                ["sudo", "apt-get", "update"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "lz4"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("lz4 installation successful")
        except subprocess.CalledProcessError as e:
            logger.error(f"lz4 installation failed: {e.stderr}")
            raise RuntimeError("lz4 installation failed. Please install it manually.")

    def tar_lz4_compression(self, folder_path: str, output_file: str) -> None:
        self._install_lz4()
        folder_name = os.path.basename(folder_path)
        folder_parent = os.path.dirname(folder_path)
        logger.info(f"Creating compressed archive: {output_file}")

        tar_cmd = ["tar", "-cf", "-", "-C", folder_parent, folder_name]
        lz4_cmd = ["lz4", "-", output_file]

        try:
            tar_proc = subprocess.Popen(
                tar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            lz4_proc = subprocess.Popen(
                lz4_cmd,
                stdin=tar_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            tar_proc.stdout.close()
            tar_proc.wait()
            lz4_proc.wait()

            if tar_proc.returncode != 0:
                raise RuntimeError(f"Tar failed: {tar_proc.stderr.read().decode()}")
            if lz4_proc.returncode != 0:
                raise RuntimeError(f"LZ4 failed: {lz4_proc.stderr.read().decode()}")
            logger.info("Compression completed successfully")

        except Exception as e:
            logger.error(f"Compression failed: {e}")
            raise

    def tar_lz4_decompression(self, output_dir: str) -> None:
        self._install_lz4()
        lz4_files = [f for f in os.listdir(output_dir) if f.endswith(".lz4")]
        if not lz4_files:
            return
        if len(lz4_files) > 1:
            logger.warning(
                f"Multiple .lz4 files found: {lz4_files}. Using the first one."
            )

        lz4_file = os.path.join(output_dir, lz4_files[0])
        logger.info(f"Extracting {lz4_file}...")

        try:
            lz4_proc = subprocess.Popen(
                ["lz4", "-d", "-c", lz4_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            tar_proc = subprocess.Popen(
                ["tar", "-xf", "-", "-C", output_dir],
                stdin=lz4_proc.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            lz4_proc.stdout.close()
            tar_proc.wait()
            lz4_proc.wait()

            if lz4_proc.returncode != 0:
                raise RuntimeError(
                    f"LZ4 decompression failed: {lz4_proc.stderr.read().decode()}"
                )
            if tar_proc.returncode != 0:
                raise RuntimeError(
                    f"Tar extraction failed: {tar_proc.stderr.read().decode()}"
                )

            os.remove(lz4_file)
            logger.info("Extraction completed successfully")
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
