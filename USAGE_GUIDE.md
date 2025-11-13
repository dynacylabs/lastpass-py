# LastPass Python CLI - Installation and Usage Guide

## Installation Options

### Option 1: Install as Python Package (Recommended)

```bash
cd /workspaces/lastpass-cli
pip install -e .
```

After installation, you can use the `lpass` command from anywhere:
```bash
lpass login user@example.com
lpass show github --password
```

### Option 2: Run Directly from Source

```bash
cd /workspaces/lastpass-cli
pip install -r requirements.txt
python lpass.py login user@example.com
```

### Option 3: Install from PyPI (when published)

```bash
pip install lastpass-python
```

## Quick Start Guide

### 1. Login

```bash
lpass login your.email@example.com
# You'll be prompted for your master password
```

### 2. List Your Accounts

```bash
# Simple list
lpass ls

# Detailed list
lpass ls --long

# List accounts in a specific group
lpass ls "Work"

# JSON output
lpass ls --json
```

### 3. Show Account Details

```bash
# Show all details
lpass show github

# Show only password
lpass show github --password

# Show only username
lpass show github --username

# Copy password to clipboard
lpass show github --password --clip

# JSON output
lpass show github --json
```

### 4. Generate Password

```bash
# Generate 16-character password
lpass generate

# Generate 24-character password
lpass generate 24

# Generate without symbols
lpass generate 20 --no-symbols

# Copy to clipboard
lpass generate --clip
```

### 5. Check Status

```bash
lpass status
```

### 6. Sync Vault

```bash
lpass sync
```

### 7. Logout

```bash
lpass logout
```

## Python API Examples

### Example 1: Basic Usage

```python
#!/usr/bin/env python3
from lastpass import LastPassClient

# Create client and login
client = LastPassClient()
client.login("your.email@example.com", "your_master_password")

# List all accounts
accounts = client.get_accounts()
print(f"You have {len(accounts)} accounts")

# Find specific account
github_account = client.find_account("github")
if github_account:
    print(f"GitHub username: {github_account.username}")
    print(f"GitHub password: {github_account.password}")

# Logout
client.logout()
```

### Example 2: Search and Filter

```python
from lastpass import LastPassClient

client = LastPassClient()
client.login("your.email@example.com", "your_master_password")

# Search by keyword
google_accounts = client.search_accounts("google")
print(f"Found {len(google_accounts)} Google accounts:")
for account in google_accounts:
    print(f"  - {account.fullname}: {account.username}")

# Get accounts in specific group
work_accounts = client.search_accounts("", group="Work")
print(f"\nWork accounts: {len(work_accounts)}")

# Filter secure notes
all_accounts = client.get_accounts()
notes = [a for a in all_accounts if a.is_secure_note()]
print(f"\nSecure notes: {len(notes)}")

client.logout()
```

### Example 3: Password Management

```python
from lastpass import LastPassClient

client = LastPassClient()
client.login("your.email@example.com", "your_master_password")

# Get password for a service
try:
    password = client.get_password("aws")
    print(f"AWS password: {password}")
except Exception as e:
    print(f"Error: {e}")

# Generate a new password
new_password = client.generate_password(length=20, symbols=True)
print(f"Generated password: {new_password}")

client.logout()
```

### Example 4: Export to JSON

```python
import json
from lastpass import LastPassClient

client = LastPassClient()
client.login("your.email@example.com", "your_master_password")

# Get all accounts
accounts = client.get_accounts()

# Convert to JSON
data = [account.to_dict() for account in accounts]

# Save to file
with open("lastpass_export.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Exported {len(accounts)} accounts to lastpass_export.json")

client.logout()
```

### Example 5: Automated Script (with saved session)

```python
#!/usr/bin/env python3
"""
This script assumes you've already logged in with 'lpass login'
It will use the saved session to retrieve passwords.
"""
import sys
from lastpass import LastPassClient, AccountNotFoundException

def get_password(account_name):
    client = LastPassClient()
    
    # Try to load existing session
    if not client.is_logged_in():
        print("Error: Not logged in. Run 'lpass login' first.", file=sys.stderr)
        sys.exit(1)
    
    try:
        return client.get_password(account_name)
    except AccountNotFoundException:
        print(f"Error: Account '{account_name}' not found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_password.py <account_name>")
        sys.exit(1)
    
    password = get_password(sys.argv[1])
    print(password)
```

## Architecture Overview

### Core Components

1. **client.py**: Main API interface
   - `LastPassClient` class with high-level methods
   - Login, logout, account management
   - Password generation

2. **cli.py**: Command-line interface
   - Argparse-based command handling
   - Wraps the client API

3. **session.py**: Session management
   - Stores encrypted session data
   - Handles session persistence

4. **http.py**: HTTP communication
   - All API calls to LastPass servers
   - Request/response handling

5. **blob.py**: Vault data parsing
   - Parses encrypted vault blob
   - Extracts accounts, fields, shares

6. **cipher.py**: Cryptographic operations
   - AES-256 encryption/decryption
   - RSA encryption for sharing
   - Base64 encoding/decoding

7. **kdf.py**: Key derivation
   - PBKDF2-HMAC-SHA256
   - Login key and decryption key generation

8. **models.py**: Data structures
   - Account, Field, Share, Attachment classes
   - Type-safe representations

## Security Considerations

### Encryption
- **AES-256-CBC**: All vault data encrypted with unique IVs
- **PBKDF2**: Master password hashed with 5000+ iterations
- **No plaintext storage**: Master password never stored

### Session Storage
- Sessions encrypted with derived key
- File permissions set to 0600 (owner-only)
- Stored in user config directory

### Memory Safety
- Sensitive data cleared when possible
- No password logging
- Secure password generation using `secrets` module

## Troubleshooting

### Import Error: No module named 'lastpass'

Install the package:
```bash
pip install -e .
```

### Import Error: No module named 'Crypto'

Install pycryptodome:
```bash
pip install pycryptodome
```

### Login Failed: Invalid iteration count

Check your internet connection and verify your username is correct.

### Decryption Error

Your session may be invalid. Try logging in again:
```bash
lpass logout
lpass login your.email@example.com
```

### Clipboard not working

Install clipboard support:
```bash
pip install pyperclip
# Or on Linux: sudo apt-get install xclip
```

## Advanced Features

### Using with Environment Variables

```bash
# Store credentials in environment
export LPASS_USER="your.email@example.com"
export LPASS_PASSWORD="your_master_password"

# Use in script
python -c "
import os
from lastpass import LastPassClient
client = LastPassClient()
client.login(os.environ['LPASS_USER'], os.environ['LPASS_PASSWORD'])
print(client.get_password('github'))
"
```

### Custom Configuration Directory

```python
from pathlib import Path
from lastpass import LastPassClient

# Use custom config directory
custom_dir = Path.home() / ".my_lpass_config"
client = LastPassClient(config_dir=custom_dir)
```

### Session Reuse

```python
from lastpass import LastPassClient

# First script - login
client = LastPassClient()
client.login("user@example.com", "password")
# Session is saved

# Second script - reuse session
client2 = LastPassClient()
if client2.is_logged_in():
    accounts = client2.get_accounts()
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=lastpass --cov-report=html

# Run specific test
pytest tests/test_basic.py::TestKDF::test_kdf_login_key
```

## Contributing

The code is organized to be easily extensible:

1. Add new API methods to `client.py`
2. Add new CLI commands to `cli.py`
3. Add new models to `models.py`
4. Add new exceptions to `exceptions.py`

## Differences from C Implementation

### Implemented
- ✅ Login/logout
- ✅ Account listing and search
- ✅ Password retrieval
- ✅ Password generation
- ✅ JSON export
- ✅ Session management
- ✅ Clipboard support

### Not Implemented (yet)
- ⚠️ Account creation/editing
- ⚠️ Account deletion
- ⚠️ Share management
- ⚠️ Attachment download/upload
- ⚠️ Agent/daemon mode
- ⚠️ Import functionality

### Differences
- Python API for programmatic access
- No compilation required
- Uses PyCryptodome instead of OpenSSL
- Session-based instead of agent-based authentication

## Performance Notes

- Initial login: ~1-2 seconds (PBKDF2 computation)
- Vault sync: ~0.5-1 second (depending on vault size)
- Account search: <0.01 seconds (in-memory)
- Session load: <0.1 seconds

## License

GNU General Public License v2.0 or later (GPLv2+)

Same license as the original LastPass CLI.
