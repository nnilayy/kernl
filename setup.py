from setuptools import setup, find_packages
import pathlib
import re
import os

def get_version():
    version_file = os.path.join("kernl/", "version.py")
    with open(version_file, encoding="utf-8") as f:
        match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", f.read())
        if match:
            return match.group(1)
        raise RuntimeError("Version not found.")

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="kernl",
    version=get_version(),
    author="Nilay Kumar Bhatnagar",
    author_email="nnilayy.work@email.com",
    description="To be Updated",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nnilayy/kernl",
    license="MIT",
    packages=find_packages(),
    # package_dir={"": "kernl"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kernl=kernl.cli.cli:main",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.11",
)
