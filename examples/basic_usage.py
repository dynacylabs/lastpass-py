"""
Example: Basic usage of LastPass Python API
"""

from lastpass import LastPassClient
from getpass import getpass


def main():
    # Create client
    client = LastPassClient()
    
    # Login
    username = input("Email: ")
    password = getpass("Master Password: ")
    
    print("Logging in...")
    client.login(username, password)
    print("✓ Logged in successfully\n")
    
    # List all accounts
    print("Fetching accounts...")
    accounts = client.get_accounts()
    print(f"✓ Found {len(accounts)} accounts\n")
    
    # Show first 5 accounts
    print("First 5 accounts:")
    for account in accounts[:5]:
        print(f"  - {account.fullname}")
        print(f"    Username: {account.username}")
        print(f"    URL: {account.url}")
        print()
    
    # Search for an account
    query = input("Search for an account (or press Enter to skip): ").strip()
    if query:
        matches = client.search_accounts(query)
        print(f"\nFound {len(matches)} match(es):")
        for match in matches:
            print(f"  - {match.fullname}")
            print(f"    Username: {match.username}")
            print(f"    Password: {'*' * len(match.password)}")
            print()
    
    # Generate a password
    print("Generating a random password...")
    password = client.generate_password(length=20, symbols=True)
    print(f"Generated: {password}\n")
    
    # List groups
    groups = client.list_groups()
    print(f"Found {len(groups)} groups:")
    for group in groups[:10]:
        print(f"  - {group}")
    
    # Logout
    print("\nLogging out...")
    client.logout()
    print("✓ Logged out successfully")


if __name__ == "__main__":
    main()
