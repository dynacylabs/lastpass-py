"""
Example: Working with custom fields
"""

from lastpass import LastPassClient
from getpass import getpass


def main():
    # Login
    client = LastPassClient()
    username = input("Email: ")
    password = getpass("Master Password: ")
    
    client.login(username, password)
    
    # Get all accounts with custom fields
    accounts = client.get_accounts()
    accounts_with_fields = [a for a in accounts if a.fields]
    
    print(f"Found {len(accounts_with_fields)} accounts with custom fields:\n")
    
    for account in accounts_with_fields[:5]:
        print(f"Account: {account.fullname}")
        print(f"Custom fields:")
        for field in account.fields:
            print(f"  - {field.name}: {field.value}")
        print()
    
    # Search for account and get specific field
    query = input("Search for an account to view fields: ").strip()
    if query:
        account = client.find_account(query)
        if account:
            print(f"\n{account.fullname}:")
            if account.fields:
                for field in account.fields:
                    print(f"  {field.name}: {field.value}")
            else:
                print("  (no custom fields)")
    
    client.logout()


if __name__ == "__main__":
    main()
