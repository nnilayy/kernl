from .ssh_client_base import SSHClient
from .ssh_client_github import GitHubSSHClient
from .ssh_client_gitlab import GitLabSSHClient
from .ssh_client_bitbucket import BitbucketSSHClient

# ------------------------------------------------------------------------------------------------------------
# LOCAL CMD FUNCTIONS
# ------------------------------------------------------------------------------------------------------------
def generate_key_cmd(args):
    client = SSHClient()
    client.generate_ssh_key(
        key_type=args.type,
        bits=args.bits,
        email=args.email,
        key_name=args.key_name,
        passphrase=args.passphrase,
        overwrite_key=args.overwrite,
    )

def list_local_keys_cmd(args):
    client = SSHClient()
    keys = client.list_ssh_keys_from_local_env()
    if keys:
        print("🔑 Available SSH Public Keys:")
        for key in keys:
            print(f" - {key}")
    else:
        print("⚠️ No SSH public keys found in ~/.ssh")

def delete_local_key_cmd(args):
    client = SSHClient()
    client.delete_ssh_key_from_local_env(args.key_name)

def expose_public_key_cmd(args):
    client = SSHClient()
    client.expose_public_key(args.key_name)

def set_git_credentials_cmd(args):
    scope_map = {"global": True, "local": False}
    SSHClient.set_git_credentials(
        user_name=args.name,
        user_email=args.email,
        global_scope=scope_map[args.scope]
    )

def update_ssh_config_cmd(args):
    client = SSHClient()
    client.update_ssh_config(
        private_key_path=args.private_key_path,
        hostname=args.hostname,
        alias=args.alias,
        user=args.user,
        port=args.port
    )

def reset_ssh_config_cmd(args):
    client = SSHClient()
    client.reset_ssh_config(
        delete_config=args.reset_config,
        delete_known_hosts=args.reset_known_hosts
    )
# ------------------------------------------------------------------------------------------------------------
# GITHUB CMD FUNCTIONS
# ------------------------------------------------------------------------------------------------------------
def github_set_token_cmd(args):
    client = GitHubSSHClient()
    client.set_github_personal_access_token(args.token)

def github_remove_token_cmd(args):
    client = GitHubSSHClient()
    client.remove_github_token()

def github_add_key_cmd(args):
    client = GitHubSSHClient()
    client.add_ssh_key_to_github(args.title, args.path)

def github_list_keys_cmd(args):
    client = GitHubSSHClient()
    client.list_ssh_keys_from_github()

def github_delete_key_cmd(args):
    client = GitHubSSHClient()
    client.delete_ssh_key_from_github(args.id)

# ------------------------------------------------------------------------------------------------------------
# GITLAB CMD FUNCTIONS
# ------------------------------------------------------------------------------------------------------------

def gitlab_set_token_cmd(args):
    client = GitLabSSHClient()
    client.set_gitlab_personal_access_token(args.token)

def gitlab_remove_token_cmd(args):
    client = GitLabSSHClient()
    client.remove_gitlab_token()

def gitlab_add_key_cmd(args):
    client = GitLabSSHClient()
    client.add_ssh_key_to_gitlab(args.title, args.path)

def gitlab_list_keys_cmd(args):
    client = GitLabSSHClient()
    client.list_ssh_keys_from_gitlab()

def gitlab_delete_key_cmd(args):
    client = GitLabSSHClient()
    client.delete_ssh_key_from_gitlab(args.id)

# ------------------------------------------------------------------------------------------------------------
# BITBUCKET CMD FUNCTIONS
# ------------------------------------------------------------------------------------------------------------

def bitbucket_set_token_cmd(args):
    client = BitbucketSSHClient()
    client.set_bitbucket_api_token(args.email, args.token)

def bitbucket_remove_token_cmd(args):
    client = BitbucketSSHClient()
    client.remove_bitbucket_token()

def bitbucket_add_key_cmd(args):
    client = BitbucketSSHClient()
    client.add_ssh_key_to_bitbucket(args.title, args.path)

def bitbucket_list_keys_cmd(args):
    client = BitbucketSSHClient()
    client.list_ssh_keys_from_bitbucket()

def bitbucket_delete_key_cmd(args):
    client = BitbucketSSHClient()
    client.delete_ssh_key_from_bitbucket(args.id)

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
def add_ssh_subcommands(subparsers):
    ssh_parser = subparsers.add_parser("ssh", help="SSH key and Git provider management")
    ssh_subparsers = ssh_parser.add_subparsers(dest="ssh_scope", required=True)

# ------------------------------------------------------------------------------------------------------------
# LOCAL PARSER
# ------------------------------------------------------------------------------------------------------------
    local_parser = ssh_subparsers.add_parser("local", help="Local SSH key + config operations")
    local_subparsers = local_parser.add_subparsers(dest="local_cmd", required=True)

    # -----------------------------------------------
    # local generate-key
    # -----------------------------------------------
    gen_parser = local_subparsers.add_parser(
        "generate-key", 
        help="Generate a new SSH key pair"
    )

    gen_parser.add_argument(
        "--type",
        default="ed25519",
        choices=["rsa", "ecdsa", "ed25519"],
        help=(
            "Specifies the type of SSH key to generate.\n"
            "Options: [rsa, ecdsa, ed25519].\n"
            "Default: ed25519"
        )
    )

    gen_parser.add_argument(
        "--bits",
        type=int,
        help=(
            "Sets the key size in bits.\n"
            "Options:\n"
            "  - RSA: 2048, 4096\n"
            "  - ECDSA: 256, 384, 521\n"
            "  - ED25519: ignored.\n"
            "Default: None"
        )
    )

    gen_parser.add_argument(
        "--email",
        type=str,
        default="",
        help="Associates an email comment with the public key."
    )

    gen_parser.add_argument(
        "--key-name",
        type=str,
        help="Sets the base name for the key pair files."
    )

    gen_parser.add_argument(
        "--passphrase",
        type=str,
        default="",
        help="Encrypts the private key using the given passphrase."
    )

    gen_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrites existing key files if they already exist."
    )

    gen_parser.set_defaults(func=generate_key_cmd)

    # -----------------------------------------------
    # local list-keys
    # -----------------------------------------------
    list_parser = local_subparsers.add_parser(
        "list-keys",
        help="List all local SSH public keys"
    )
    list_parser.set_defaults(func=list_local_keys_cmd)

    # -----------------------------------------------
    # local delete-key
    # -----------------------------------------------
    delete_parser = local_subparsers.add_parser(
        "delete-key",
        help="Delete a local SSH key pair"
    )

    delete_parser.add_argument(
        "key_name",
        help=(
            "Name of the SSH key pair to delete (do not include the .pub extension).\n"
            "Deletes both private and public key files from the local environment."
        )
    )

    delete_parser.set_defaults(func=delete_local_key_cmd)

    # -----------------------------------------------
    # local expose-public-key
    # -----------------------------------------------
    expose_parser = local_subparsers.add_parser(
        "expose-public-key",
        help="Expose and/or copy a public SSH key to clipboard"
    )

    expose_parser.add_argument(
        "key_name",
        help=(
            "Name of the public key file to expose (e.g., id_ed25519.pub).\n"
            "Prints the key to terminal and attempts to copy it to clipboard."
        )
    )

    expose_parser.set_defaults(func=expose_public_key_cmd)

    # -----------------------------------------------
    # local set-git-credentials
    # -----------------------------------------------
    git_config_parser = local_subparsers.add_parser(
        "set-git-credentials",
        help="Configure Git user name and email"
    )

    git_config_parser.add_argument(
        "--name",
        required=True,
        type=str,
        help="Set Git user name."
    )

    git_config_parser.add_argument(
        "--email",
        required=True,
        type=str,
        help="Set Git user email."
    )

    git_config_parser.add_argument(
        "--scope",
        choices=["global", "local"],
        default="global",
        help="Scope to apply Git credentials."
    )

    git_config_parser.set_defaults(func=set_git_credentials_cmd)

    # -----------------------------------------------
    # local reset-ssh-config
    # -----------------------------------------------
    reset_config_parser = local_subparsers.add_parser(
        "reset-ssh-config",
        help="Reset SSH config and/or known_hosts files"
    )

    reset_config_parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Remove all entries from the SSH config file."
    )

    reset_config_parser.add_argument(
        "--reset-known-hosts",
        action="store_true",
        help="Remove all entries from the known_hosts file."
    )

    reset_config_parser.set_defaults(func=reset_ssh_config_cmd)

    # -----------------------------------------------
    # local update-ssh-config
    # -----------------------------------------------
    update_config_parser = local_subparsers.add_parser(
        "update-ssh-config",
        help="Add a new SSH config entry and scan host key"
    )

    update_config_parser.add_argument(
        "--private-key-path",
        required=True,
        help="Path to the private SSH key to use."
    )

    update_config_parser.add_argument(
        "--hostname",
        required=True,
        help="Hostname of the SSH server (e.g., github.com)."
    )

    update_config_parser.add_argument(
        "--alias",
        required=True,
        help="Alias to use in SSH config."
    )

    update_config_parser.add_argument(
        "--user",
        required=True,
        help="SSH username."
    )

    update_config_parser.add_argument(
        "--port",
        type=int,
        default=22,
        help="SSH port (default: 22)."
    )

    update_config_parser.set_defaults(func=update_ssh_config_cmd)

# ------------------------------------------------------------------------------------------------------------
# GITHUB PARSER
# ------------------------------------------------------------------------------------------------------------
    github_parser = ssh_subparsers.add_parser("github", help="GitHub SSH key + token operations")
    github_subparsers = github_parser.add_subparsers(dest="github_cmd", required=True)

    # -----------------------------------------------
    # github set-token
    # -----------------------------------------------
    github_set_token_parser = github_subparsers.add_parser(
        "set-token",
        help="Set and persist GitHub personal access token"
    )
    github_set_token_parser.add_argument(
        "--token",
        required=True,
        type=str,
        help="GitHub personal access token"
    )
    github_set_token_parser.set_defaults(func=github_set_token_cmd)

    # -----------------------------------------------
    # github remove-token
    # -----------------------------------------------
    github_remove_token_parser = github_subparsers.add_parser(
        "remove-token",
        help="Remove stored GitHub token"
    )
    github_remove_token_parser.set_defaults(func=github_remove_token_cmd)

    # -----------------------------------------------
    # github add-key
    # -----------------------------------------------
    github_add_key_parser = github_subparsers.add_parser(
        "add-key",
        help="Upload a local SSH public key to GitHub"
    )
    github_add_key_parser.add_argument(
        "--title",
        required=True,
        help="Title/label for the SSH key in GitHub"
    )
    github_add_key_parser.add_argument(
        "--path",
        required=True,
        help="Path to the public key file (.pub)"
    )
    github_add_key_parser.set_defaults(func=github_add_key_cmd)

    # -----------------------------------------------
    # github delete-key
    # -----------------------------------------------
    github_delete_key_parser = github_subparsers.add_parser(
        "delete-key",
        help="Delete an SSH key from GitHub using its ID"
    )
    github_delete_key_parser.add_argument(
        "--id",
        required=True,
        type=int,
        help="GitHub SSH key ID to delete"
    )
    github_delete_key_parser.set_defaults(func=github_delete_key_cmd)

    # -----------------------------------------------
    # github list-keys
    # -----------------------------------------------
    github_list_keys_parser = github_subparsers.add_parser(
        "list-keys",
        help="List all SSH keys stored in your GitHub account"
    )
    github_list_keys_parser.set_defaults(func=github_list_keys_cmd)

# ------------------------------------------------------------------------------------------------------------
# GITLAB PARSER
# ------------------------------------------------------------------------------------------------------------
    gitlab_parser = ssh_subparsers.add_parser("gitlab", help="GitLab SSH key + token operations")
    gitlab_subparsers = gitlab_parser.add_subparsers(dest="gitlab_cmd", required=True)

    # -----------------------------------------------
    # gitlab set-token
    # -----------------------------------------------
    gitlab_set_token_parser = gitlab_subparsers.add_parser(
        "set-token",
        help="Set and persist GitLab personal access token"
    )
    gitlab_set_token_parser.add_argument(
        "--token",
        required=True,
        type=str,
        help="GitLab personal access token"
    )
    gitlab_set_token_parser.set_defaults(func=gitlab_set_token_cmd)

    # -----------------------------------------------
    # gitlab remove-token
    # -----------------------------------------------
    gitlab_remove_token_parser = gitlab_subparsers.add_parser(
        "remove-token",
        help="Remove stored GitLab token"
    )
    gitlab_remove_token_parser.set_defaults(func=gitlab_remove_token_cmd)

    # -----------------------------------------------
    # gitlab add-key
    # -----------------------------------------------
    gitlab_add_key_parser = gitlab_subparsers.add_parser(
        "add-key",
        help="Upload a local SSH public key to GitLab"
    )
    gitlab_add_key_parser.add_argument(
        "--title",
        required=True,
        help="Title/label for the SSH key in GitLab"
    )
    gitlab_add_key_parser.add_argument(
        "--path",
        required=True,
        help="Path to the public key file (.pub)"
    )
    gitlab_add_key_parser.set_defaults(func=gitlab_add_key_cmd)

    # -----------------------------------------------
    # gitlab delete-key
    # -----------------------------------------------
    gitlab_delete_key_parser = gitlab_subparsers.add_parser(
        "delete-key",
        help="Delete an SSH key from GitLab using its ID"
    )
    gitlab_delete_key_parser.add_argument(
        "--id",
        required=True,
        type=int,
        help="GitLab SSH key ID to delete"
    )
    gitlab_delete_key_parser.set_defaults(func=gitlab_delete_key_cmd)

    # -----------------------------------------------
    # gitlab list-keys
    # -----------------------------------------------
    gitlab_list_keys_parser = gitlab_subparsers.add_parser(
        "list-keys",
        help="List all SSH keys stored in your GitLab account"
    )
    gitlab_list_keys_parser.set_defaults(func=gitlab_list_keys_cmd)

# ------------------------------------------------------------------------------------------------------------
# BITBUCKET PARSER
# ------------------------------------------------------------------------------------------------------------
    bitbucket_parser = ssh_subparsers.add_parser("bitbucket", help="Bitbucket SSH key + token operations")
    bitbucket_subparsers = bitbucket_parser.add_subparsers(dest="bitbucket_cmd", required=True)

    # -----------------------------------------------
    # bitbucket set-token
    # -----------------------------------------------
    bitbucket_set_token_parser = bitbucket_subparsers.add_parser(
        "set-token",
        help="Set Bitbucket API credentials (email + app password)"
    )
    bitbucket_set_token_parser.add_argument(
        "--email",
        required=True,
        type=str,
        help="Bitbucket account email"
    )
    bitbucket_set_token_parser.add_argument(
        "--token",
        required=True,
        type=str,
        help="Bitbucket App Password"
    )
    bitbucket_set_token_parser.set_defaults(func=bitbucket_set_token_cmd)

    # -----------------------------------------------
    # bitbucket remove-token
    # -----------------------------------------------
    bitbucket_remove_token_parser = bitbucket_subparsers.add_parser(
        "remove-token",
        help="Remove stored Bitbucket token"
    )
    bitbucket_remove_token_parser.set_defaults(func=bitbucket_remove_token_cmd)

    # -----------------------------------------------
    # bitbucket add-key
    # -----------------------------------------------
    bitbucket_add_key_parser = bitbucket_subparsers.add_parser(
        "add-key",
        help="Upload a local SSH public key to Bitbucket"
    )
    bitbucket_add_key_parser.add_argument(
        "--title",
        required=True,
        help="Title/label for the SSH key in Bitbucket"
    )
    bitbucket_add_key_parser.add_argument(
        "--path",
        required=True,
        help="Path to the public key file (.pub)"
    )
    bitbucket_add_key_parser.set_defaults(func=bitbucket_add_key_cmd)

    # -----------------------------------------------
    # bitbucket delete-key
    # -----------------------------------------------
    bitbucket_delete_key_parser = bitbucket_subparsers.add_parser(
        "delete-key",
        help="Delete an SSH key from Bitbucket using its ID"
    )
    bitbucket_delete_key_parser.add_argument(
        "--id",
        required=True,
        help="Bitbucket SSH key ID to delete"
    )
    bitbucket_delete_key_parser.set_defaults(func=bitbucket_delete_key_cmd)

    # -----------------------------------------------
    # bitbucket list-keys
    # -----------------------------------------------
    bitbucket_list_keys_parser = bitbucket_subparsers.add_parser(
        "list-keys",
        help="List all SSH keys stored in your Bitbucket account"
    )
    bitbucket_list_keys_parser.set_defaults(func=bitbucket_list_keys_cmd)

