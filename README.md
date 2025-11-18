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

## Usage

Kernl can be used either through its terminal-based CLI or its Python API, both offering full functional access to all Kernl capabilities, with details provided in the subsections below.



### Kernl CLI Usage

The Kernl CLI provides all functionality available through the Kernl API, including starting the secure VSCode Web workspace, managing SSH keys for GitHub, GitLab, and Bitbucket, and uploading or downloading persistent environments using HuggingFace 🤗 or Kaggle dataset managers. All core actions can be executed directly from the terminal for fast and portable cloud-based development.

#### **1. Starting the VSCode Web Server**

To start the secure VSCode Web workspace server using Kernl, run the following command with the available configuration options:

```bash
kernl server start \
  --ngrok_token <NGROK_TOKEN> \
  --password <PASSWORD> \
  --working_directory <WORKING_DIRECTORY> \
  --extensions <EXTENSION_IDS> \
  --dataset_manager <DATASET_MANAGER> \
  --dataset_manager_token <DATASET_MANAGER_TOKEN> \
  --load_config <SLUG_ID>
```

Replace the following:

* **`<NGROK_TOKEN>`**:
  Your ngrok authentication token used to expose the VSCode Web interface over an HTTPS tunnel
  *(If not provided, Kernl will securely prompt you.)*

* **`<PASSWORD>`**:
  Password that secures the VSCode Web workspace from unauthorized access
  *(If omitted, Kernl generates a strong password automatically.)*

* **`<WORKING_DIRECTORY>`**:
  The directory that will serve as the workspace root inside VSCode
  *(Defaults to the current working directory if not specified.)*

* **`<EXTENSION_IDS>`** *(optional)*:
  Space-separated VSCode extension identifiers to install at startup
  Example: `ms-python.python ms-toolsai.jupyter`

* **`<DATASET_MANAGER>`**:
  Cloud backend for storing or restoring persistent environments
  Options: `huggingface`, `kaggle`

* **`<DATASET_MANAGER_TOKEN>`**:
  Authentication for the selected dataset manager

  * For HuggingFace → your HF token
  * For Kaggle → path to your `kaggle.json` file
    *(If not provided, Kernl will securely prompt you.)*

* **`<SLUG_ID>`** *(optional)*:
  Identifier of a previously uploaded VSCode configuration to restore at startup
---

#### **2. Connecting to Distributed Version-Control Platforms & SSH Integrations**

Kernl lets you connect your remote VSCode Web workspace to major distributed version-control platforms like GitHub, GitLab, and Bitbucket and set up SSH integrations with ease in just a few steps. Instead of manually generating keys, configuring SSH files and known hosts, and uploading public keys to these platforms individually, Kernl provides simple CLI commands that set up SSH integration with your VCPs and get you connected to your codebases quickly so you can start building from the get-go.

All SSH integration and helper operations in Kernl are organized under the `kernl ssh` command interface as follows:

```
kernl ssh <scope> <command> [flags]
```

* **`<scope>`** defines the target surface, it can be `local` for managing keys on your workspace, or a provider scope like `github`, `gitlab`, or `bitbucket` for platform-specific operations.
* **`<command>`** specifies what operation to perform, such as `generate-key`, `set-token`, or `add-key`.
* **`[flags]`** provide the required inputs like key names, token values, titles, or file paths.


##### **A. Local Scope — Managing SSH Keys on Your Workspace**

The `local` scope includes all operations for generating, inspecting, and managing SSH keys inside your Kernl workspace. These commands help prepare your environment before connecting to GitHub, GitLab, or Bitbucket.

###### **(I) Generate a New SSH Keypair**

```bash
kernl ssh local generate-key \
  --type <KEY_TYPE> \
  --bits <BIT_SIZE> \
  --email <EMAIL> \
  --key-name <KEY_NAME> \
  --passphrase <PASSPHRASE> \
  --overwrite
```

Generates a new SSH keypair inside `~/.ssh/`.

* **`<KEY_TYPE>`**: Algorithm to use (ed25519, rsa, ecdsa)
* **`<BIT_SIZE>`**: Key size for RSA/ECDSA (2048, 3072, 4096, 256, 384, 521)
* **`<EMAIL>`**: Comment stored inside the public key
* **`<KEY_NAME>`**: Output filename under `~/.ssh/`
* **`<PASSPHRASE>`**: Optional passphrase for securing the private key
* `--overwrite`: Boolean flag — if provided, overwrites an existing key; if omitted = False

###### **(II) List All Local SSH Keys**

```bash
kernl ssh local list-keys
```

Displays all SSH public keys available in your workspace.


###### **(III) Delete a Local SSH Keypair**

```bash
kernl ssh local delete-key <KEY_NAME>
```

Deletes both the private and public key for the specified keypair.

* **`<KEY_NAME>`**: Name of the SSH keypair to remove

###### **(IV) Expose (Print) a Public Key**

```bash
kernl ssh local expose-public-key <PUBLIC_KEY_FILE>
```

Prints the contents of a public key.

* **`<PUBLIC_KEY_FILE>`**: The `.pub` key file to display

###### **(V) Set Git Credentials**

```bash
kernl ssh local set-git-credentials \
  --name <GIT_USER_NAME> \
  --email <GIT_USER_EMAIL> \
  --scope <CONFIG_SCOPE>
```

Configures Git’s username and email.

* **`<GIT_USER_NAME>`**: Author name for Git commits
* **`<GIT_USER_EMAIL>`**: Author email for Git commits
* **`<CONFIG_SCOPE>`**: Git configuration scope (`global` or `local`)


###### **(VI) Update SSH Config Entries**

```bash
kernl ssh local update-ssh-config \
  --private-key-path <PRIVATE_KEY_PATH> \
  --hostname <HOSTNAME> \
  --alias <HOST_ALIAS> \
  --user <SSH_USER> \
  --port <SSH_PORT>
```

Adds or updates an SSH config entry.

* **`<PRIVATE_KEY_PATH>`**: Path to the private key
* **`<HOSTNAME>`**: SSH host (e.g., github.com)
* **`<HOST_ALIAS>`**: Alias for the SSH config
* **`<SSH_USER>`**: SSH username (usually `"git"`)
* **`<SSH_PORT>`**: SSH port (default `22`)

###### **(VII) Reset SSH Config & Known Hosts**

```bash
kernl ssh local reset-ssh-config \
  --reset-config \
  --reset-known-hosts
```

Resets your SSH configuration files.

* `--reset-config`: Boolean flag, if provided, resets `~/.ssh/config`; if omitted = False
* `--reset-known-hosts`: Boolean flag, if provided, resets `~/.ssh/known_hosts`; if omitted = False

---
##### **B. Provider Scope — Connecting Kernl to GitHub, GitLab & Bitbucket**

The `provider` scope allows Kernl to authenticate with GitHub, GitLab, and Bitbucket and register SSH keys so your remote VSCode workspace can clone, pull, and push securely using provider-managed SSH access.


###### **(I) Set Provider Token**

```bash
kernl ssh <provider> set-token <TOKEN>
```

Authenticates Kernl with your version-control provider.

* **`<provider>`**: Choose one of `github`, `gitlab`, or `bitbucket`
* **`<TOKEN>`**: Your personal access token for the selected provider

###### **(Special Case) Bitbucket Token Format**

Bitbucket uses a **username:app-password** structure instead of a standard token.

```bash
kernl ssh bitbucket set-token <USERNAME:APP_PASSWORD>
```

* **`<provider>`**: Must be `bitbucket` for this variant
* **`<USERNAME>`**: Your Bitbucket account username
* **`<APP_PASSWORD>`**: App password generated from Bitbucket settings

###### **(II) Upload a Public SSH Key to Provider**

```bash
kernl ssh <provider> add-key \
  --title <TITLE> \
  --path <PUBLIC_KEY_PATH>
```

Registers an SSH public key to the selected provider.

* **`<provider>`**: Choose `github`, `gitlab`, or `bitbucket`
* **`<TITLE>`**: Display name for the key in the provider dashboard
* **`<PUBLIC_KEY_PATH>`**: Path to the `.pub` key to upload

###### **(III) Delete an SSH Key From Provider**

```bash
kernl ssh <provider> delete-key <KEY_ID>
```

Removes a previously registered SSH key from the selected provider.

* **`<provider>`**: Choose `github`, `gitlab`, or `bitbucket`
* **`<KEY_ID>`**: Identifier of the key as returned by the provider

###### **(IV) List SSH Keys on Provider**

```bash
kernl ssh <provider> list-keys
```

Retrieves all SSH keys registered on the selected provider.

* **`<provider>`**: Choose `github`, `gitlab`, or `bitbucket`


###### **(V) Test SSH Connectivity With Provider**

```bash
kernl ssh <provider> test-connection
```

Checks whether Kernl can authenticate with the selected provider using SSH.

* **`<provider>`**: Choose `github`, `gitlab`, or `bitbucket`
---

##### **C. General Workflow for Complete SSH Integration**

This section outlines the recommended end-to-end workflow for preparing your Kernl remote VSCode workspace with fully functional SSH authentication across GitHub, GitLab, or Bitbucket.
Follow these steps sequentially to ensure a smooth and reliable setup.

###### **(I) Generate or Prepare Your Local SSH Keypair**

If you don’t already have an SSH keypair for Kernl, generate one:

```bash
kernl ssh local generate-key \
  --type <KEY_TYPE> \
  --bits <BIT_SIZE> \
  --email <EMAIL> \
  --key-name <KEY_NAME>
```

This creates your private and public keys under `~/.ssh/` inside the workspace.

###### **(II) Set Git Identity for Commits**

```bash
kernl ssh local set-git-credentials \
  --name <GIT_USER_NAME> \
  --email <GIT_USER_EMAIL> \
  --scope <CONFIG_SCOPE>
```

Ensures all commits pushed from Kernl have the correct author identity.

###### **(III) Connect Kernl to Your Provider Account**

```bash
kernl ssh <provider> set-token <TOKEN>
```

This authorizes Kernl to upload and manage SSH keys on your provider account.
If using Bitbucket, use the `<USERNAME:APP_PASSWORD>` format.

###### **(IV) Upload Your SSH Public Key to the Provider**

```bash
kernl ssh <provider> add-key \
  --title <TITLE> \
  --path <PUBLIC_KEY_PATH>
```

This registers your workspace’s SSH public key with your chosen provider.

###### **(V) Verify the Key Was Successfully Added**

To confirm the key exists on your account:

```bash
kernl ssh <provider> list-keys
```

Make sure your uploaded key appears in the returned list.

###### **(VI) Test SSH Connectivity End-to-End**

```bash
kernl ssh <provider> test-connection
```

Validates that Kernl can authenticate with your provider via SSH.
If this succeeds, your setup is complete.

###### **(VII) Clone Your Repository and Start Working**

Once everything is connected, simply run:

```bash
git clone git@<provider>.com:<user_or_org>/<repo>.git
```

Or via provider-specific alias (after your SSH config is updated):

```bash
git clone <HOST_ALIAS>:<user_or_org>/<repo>.git
```

Your workspace is now fully authenticated and ready for development.

###### **(VIII) Push, Pull, and Work Seamlessly**

After initial setup, all Git operations will work smoothly:

```bash
git pull
git add .
git commit -m "Your message"
git push
```
No passwords or tokens required, everything uses secure SSH.

#### **3. Managing Data & Environments Using Dataset Managers (To be done)** 

Kernl supports cloud-backed environment storage through HuggingFace 🤗 and Kaggle, allowing you to upload or download full development environments, codebases, configurations, virtual environments, or any folder-based workspace components. All operations are handled through the dataset manager you selected when starting the server.

To perform dataset operations through the CLI, use:

```bash
kernl dataset \
  --dataset_manager <huggingface|kaggle> \
  --action <upload|download> \
  --slug_id <SLUG_ID> \
  --path <LOCAL_FOLDER_PATH> \
  --token <TOKEN>
```

Replace the following:

* **`<dataset_manager>`**:
  The cloud backend to use for storage, options are `huggingface`, `kaggle`

* **`<action>`**:
  The dataset operation to perform, options are `upload`, `download`

* **`<SLUG_ID>`**:
  Unique dataset identifier for the selected platform
  • HuggingFace: must follow HF slug rules
  • Kaggle: must be 6–50 chars, alphanumeric and hyphens only

* **`<LOCAL_FOLDER_PATH>`**:
  Path to the folder you want to upload or where a downloaded environment should be stored

* **`<TOKEN>`**:
  Authentication credential for the chosen dataset manager
  • HuggingFace uses a Personal Access Token
  • Kaggle uses a `kaggle.json` file path

Environment upload automatically performs fast **tar-lz4** compression, and downloads automatically decompress the archived folder, allowing development environments to be transferred, restored, or reused across cloud instances efficiently.


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
