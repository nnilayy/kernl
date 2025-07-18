GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def success(msg: str) -> str:
    """Return a green colored success message."""
    return f"{GREEN}{msg}{RESET}"

def caution(msg: str) -> str:
    """Return a yellow colored caution/warning message."""
    return f"{YELLOW}{msg}{RESET}"

def fail(msg: str) -> str:
    """Return a red colored failure/error message."""
    return f"{RED}{msg}{RESET}"
