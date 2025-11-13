"""
Example: Export all passwords to JSON
"""

import json
from lastpass import LastPassClient
from getpass import getpass


def main():
    # Login
    client = LastPassClient()
    username = input("Email: ")
    password = getpass("Master Password: ")
    
    print("Logging in...")
    client.login(username, password)
    
    # Get all accounts
    print("Fetching accounts...")
    accounts = client.get_accounts()
    
    # Convert to dictionaries
    data = [account.to_dict() for account in accounts]
    
    # Save to file
    output_file = "lastpass_export.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Exported {len(accounts)} accounts to {output_file}")
    
    # Logout
    client.logout()


if __name__ == "__main__":
    main()
