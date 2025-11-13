"""
Example: Automated password retrieval for scripts
"""

import sys
from lastpass import LastPassClient, AccountNotFoundException


def get_password(account_name: str) -> str:
    """
    Get password for an account.
    Assumes user is already logged in.
    """
    client = LastPassClient()
    
    # Try to load existing session
    # (user must have logged in previously with --trust)
    if not client.is_logged_in():
        print("Error: Not logged in. Run 'lpass login' first.", file=sys.stderr)
        sys.exit(1)
    
    try:
        password = client.get_password(account_name)
        return password
    except AccountNotFoundException:
        print(f"Error: Account '{account_name}' not found.", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python automated_script.py <account_name>")
        sys.exit(1)
    
    account_name = sys.argv[1]
    password = get_password(account_name)
    
    # Print password to stdout (can be captured by scripts)
    print(password)


if __name__ == "__main__":
    main()
