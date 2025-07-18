import time
import getpass
import argparse
import traceback
from server.kernl_server import KernlServer
from dataset_managers.dataset_manager_kaggle import KaggleManager
from dataset_managers.dataset_manager_huggingface import HuggingFaceManager


def prompt_secure_input(prompt_text: str) -> str:
    while True:
        value = getpass.getpass(prompt_text)
        if value.strip():
            return value
        print("Input cannot be empty. Please try again.")


def start_server(args):
    try:
        if args.dataset_manager not in {"kaggle", "huggingface"}:
            raise ValueError(
                "Invalid dataset_manager. Choose 'kaggle' or 'huggingface'."
            )

        if args.ngrok_token:
            ngrok_token = args.ngrok_token
        else:
            ngrok_token = prompt_secure_input(
                "Enter your Ngrok Auth Token (output is hidden — paste and press Enter): "
            )

        if args.dataset_manager_token:
            dataset_token = args.dataset_manager_token
        else:
            if args.dataset_manager == "kaggle":
                dataset_token = prompt_secure_input(
                    "Enter your Kaggle key file path (output is hidden — paste and press Enter): "
                )
            elif args.dataset_manager == "huggingface":
                dataset_token = prompt_secure_input(
                    "Enter your Hugging Face token (output is hidden — paste and press Enter): "
                )

        if args.dataset_manager == "kaggle":
            manager = KaggleManager()
            manager.set_token(kaggle_json_path=dataset_token)
        else:
            manager = HuggingFaceManager()
            manager.set_token(token=dataset_token)

        print("🚀 Starting VSCode Server...")
        server = KernlServer(
            dataset_manager=manager,
            ngrok_auth_token=ngrok_token,
            password=args.password,
            extensions=args.extensions,
            load_existing_vsc_config_by_id=args.load_config,
            working_directory=args.working_directory,
        )
        server.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n[🔴] VSCode server stopped.")

    except Exception as e:
        print("❌ Error starting VSCode server:")
        print(str(e))
        traceback.print_exc()


def add_server_subcommands(subparsers):
    server_parser = subparsers.add_parser("server", help="Manage the Kernl VSCode Server")
    server_subparsers = server_parser.add_subparsers(dest="server_cmd", required=True)

    start_parser = server_subparsers.add_parser("start", help="Start the VSCode server")

    start_parser.add_argument(
        "--dataset_manager",
        required=True,
        choices=["kaggle", "huggingface"],
        help="Dataset manager to use: 'kaggle' or 'huggingface'",
    )
    start_parser.add_argument(
        "--dataset_manager_token",
        type=str,
        default=None,
        help="Dataset manager token or key file path (optional — if not provided, you will be prompted)",
    )
    start_parser.add_argument(
        "--ngrok_token",
        type=str,
        default=None,
        help="Ngrok authentication token (optional — if not provided, you will be prompted)",
    )
    start_parser.add_argument(
        "--working_directory",
        type=str,
        default=None,
        help="Directory to open in VSCode. Defaults to current working directory.",
    )
    start_parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Password for the VSCode server. If not provided, a strong password will be generated and copied to clipboard.",
    )
    start_parser.add_argument(
        "--extensions",
        nargs="*",
        default=[],
        help="List of VSCode extension IDs to install (space-separated)",
    )
    start_parser.add_argument(
        "--load_config",
        type=str,
        default=None,
        help="Slug ID of previously saved VSCode config to restore (optional)",
    )

    start_parser.set_defaults(func=start_server)