import argparse
from ssh_client.ssh_client_cli import add_git_ssh_subcommands
from server.kernl_server_cli import add_server_subcommands

def main():
    parser = argparse.ArgumentParser(prog="kernl", description="Kernl CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    add_git_ssh_subcommands(subparsers)
    add_server_subcommands(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
