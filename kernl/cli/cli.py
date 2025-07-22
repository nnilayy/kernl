import argparse
import sys
from kernl.version import __version__
from kernl.banner import display_banner
from kernl.ssh_client.ssh_client_cli import add_git_ssh_subcommands
from kernl.server.kernl_server_cli import add_server_subcommands

def main():
    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        display_banner()

    parser = argparse.ArgumentParser(prog="kernl", description="Kernl CLI")
    parser.add_argument("--version", "-V", action="version", version=f"Kernl {__version__}")
    
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    add_git_ssh_subcommands(subparsers)
    add_server_subcommands(subparsers)
    
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
