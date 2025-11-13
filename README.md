<p align="center">
  <img src="https://raw.githubusercontent.com/nnilayy/kernl/main/assets/kernl-banner.png" alt="Kernl Banner" width="80%">
</p>

<p align="center">
  <a href="https://pypi.org/project/kernl/">
    <img src="https://img.shields.io/pypi/v/kernl.svg?color=brightgreen" alt="PyPI Version">
  </a>
  <a href="https://pepy.tech/project/kernl">
    <img src="https://static.pepy.tech/badge/kernl" alt="Downloads">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/kernl.svg" alt="Python Versions">
  <a href="https://github.com/nnilayy/kernl/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/nnilayy/kernl.svg" alt="License">
  </a>
</p>

## Overview

Kernl is a secure persistent development environment system for cloud based Linux/Unix instances, providing a VSCode Web workspace backed by cloud based dataset managers such as HuggingFace 🤗 and Kaggle to keep full codebases, configurations, virtual environments, and dependencies persistent in the cloud, while supporting connections to distributed version-control platforms including GitHub, GitLab, and Bitbucket for SSH access and seamless continuation of development work from the start.

## Features

**(1) Secure VSCode Web Workspace 🔐**: Kernl provides a secure, password-protected VSCode Web workspace that offers a full development environment for cloud-based Linux/Unix instances. The workspace is exposed through ngrok tunneling and provides complete access to the VSCode interface.

**(2) Cloud-backed Persistent Environment ☁️**: Workspaces are managed by cloud dataset managers such as HuggingFace 🤗 and Kaggle, keeping full codebases, VSCode configurations, virtual environments, and dependencies consistently preserved and restorable across sessions. Environment storage uses fast tar-lz4 compression and decompression for quick upload and retrieval of workspace components.

**(3) Integrated Version-Control Connectivity 🔗**: Kernl supports connections to all major distributed version-control platforms including GitHub, GitLab, and Bitbucket. It enables authentication through platform tokens, allows adding and deleting SSH keys directly from Kernl, and provides seamless access to repositories for immediate development.

**(4) Unified Remote Development Interface 🌐**: Kernl allows you to push full environments to the cloud and pull them back whenever needed, enabling seamless continuation of work without occupying storage on the host machine, and allowing development to resume on any compatible cloud instance using the stored environments and connected distributed version-control platforms.

**(5) API and CLI Availability 🧩**: Kernl is accessible as both a Python API and a terminal-based CLI tool, allowing you to automate tasks programmatically or interact directly from the command line depending on your workflow.


## Installation

`kernl` can be installed in two ways, either directly from PyPI for regular use or by cloning the repository if you want to modify the project or contribute. Before installing `kernl`, it is recommended to create a new virtual environment.

### **Create a Virtual Environment (Recommended)**

```bash
uv venv venv --python 3.11
source venv/bin/activate
```

### **1. Install `kernl` from PyPI**

```bash
uv pip install kernl
```

This installs `kernl` and makes the `kernl` API and CLI available on your Linux or Unix based system.

### **2. Install `kernl` from Source**

```bash
git clone https://github.com/nnilayy/kernl.git
cd kernl
uv pip install -e .
```

Installing in editable mode means any changes you make to the source code will immediately apply when running `kernl`.

## Contributing
Contributions are welcome! If you have suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request.

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure `kernl` runs as expected.
4. Submit a pull request with a clear and detailed explanation of your updates.

## License

This project is licensed under the **GNU General Public License v3.0**, check out the [LICENSE](LICENSE) file for more details.

## Support & Contact

If you have any questions or need assistance, feel free to reach out:

- **GitHub Issues**: [Issues Page](https://github.com/nnilayy/kernl/issues/new)
- **Email**: nnilayy.work@gmail.com

---
