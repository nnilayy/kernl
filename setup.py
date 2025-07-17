from setuptools import setup, find_packages
import pathlib

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="kernl",
    version="0.2.0",
    author="Nilay Kumar Bhatnagar",
    author_email="nnilayy.work@email.com",
    description="To be Updated",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nnilayy/kernl",
    license="MIT",
    packages=find_packages(where="kernl"),
    package_dir={"": "kernl"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kernl=server.kernl_server_cli:main",
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
