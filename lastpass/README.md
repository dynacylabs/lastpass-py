# LastPass Python Implementation

This directory contains a complete Python implementation of the LastPass CLI.

## Structure

```
lastpass/
  __init__.py       # Package initialization and exports
  client.py         # Main LastPass client with Python API
  cli.py            # Command-line interface
  models.py         # Data models (Account, Field, Share, etc.)
  session.py        # Session management
  http.py           # HTTP communication
  blob.py           # Vault blob parsing
  cipher.py         # Cryptographic operations
  kdf.py            # Key derivation functions
  xml_parser.py     # XML response parsing
  exceptions.py     # Custom exceptions

examples/           # Example scripts
tests/              # Unit tests
```

## Quick Start

See [README_PYTHON.md](../README_PYTHON.md) for complete documentation.

### CLI Usage

```bash
# Login
python lpass.py login user@example.com

# Show account
python lpass.py show github --password

# List accounts
python lpass.py ls
```

### API Usage

```python
from lastpass import LastPassClient

client = LastPassClient()
client.login("user@example.com", "password")

# Get accounts
accounts = client.get_accounts()
for account in accounts:
    print(account.name)

# Find account
account = client.find_account("github")
print(account.password)
```

## Installation

```bash
pip install -r requirements.txt
```

Or install as package:

```bash
pip install -e .
```

## Testing

```bash
pytest tests/
```
