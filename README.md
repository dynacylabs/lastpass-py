# LastPass Python CLI and API

A complete Python implementation of the LastPass command-line interface with a friendly Python API for programmatic access.

## Features

✅ **Complete CLI Implementation** - All major LastPass CLI commands
✅ **Python API** - Clean, Pythonic interface for programmatic access
✅ **Secure** - AES-256 encryption, PBKDF2 key derivation
✅ **Cross-platform** - Works on Linux, macOS, and Windows
✅ **No Binary Dependencies** - Pure Python with standard crypto libraries

## Installation

### From Source

```bash
git clone https://github.com/lastpass/lastpass-python.git
cd lastpass-python
pip install -e .
```

### From PyPI (when published)

```bash
pip install lastpass-python
```

### Optional Dependencies

For clipboard support:
```bash
pip install lastpass-python[clipboard]
```

## Quick Start

### Command Line Interface

```bash
# Login
lpass login user@example.com

# List all accounts
lpass ls

# Show account details
lpass show github

# Get password only
lpass show github --password

# Copy password to clipboard
lpass show github --password --clip

# Generate a password
lpass generate 20

# Logout
lpass logout
```

### Python API

```python
from lastpass import LastPassClient

# Create client and login
client = LastPassClient()
client.login("user@example.com", "masterpassword")

# Get all accounts
accounts = client.get_accounts()
for account in accounts:
    print(f"{account.name}: {account.username}")

# Find a specific account
account = client.find_account("github")
print(f"Username: {account.username}")
print(f"Password: {account.password}")

# Search for accounts
matches = client.search_accounts("google")
for match in matches:
    print(match.fullname)

# Generate a password
password = client.generate_password(length=20, symbols=True)

# Logout
client.logout()
```

## CLI Commands

### login
Login to LastPass:
```bash
lpass login [OPTIONS] USERNAME

Options:
  --trust          Trust this device
  --otp CODE       One-time password for 2FA
  --force, -f      Force new login
```

### logout
Logout from LastPass:
```bash
lpass logout [OPTIONS]

Options:
  --force, -f      Force logout even if errors
```

### status
Show login status:
```bash
lpass status [OPTIONS]

Options:
  --quiet, -q      Quiet mode (no output)
```

### show
Display account details:
```bash
lpass show [OPTIONS] QUERY

Arguments:
  QUERY            Account name, ID, or URL

Options:
  --password       Show only password
  --username       Show only username
  --url           Show only URL
  --notes         Show only notes
  --field FIELD   Show specific field
  --json, -j      Output as JSON
  --clip, -c      Copy to clipboard
```

### ls
List accounts:
```bash
lpass ls [OPTIONS] [GROUP]

Arguments:
  GROUP           Filter by group/folder

Options:
  --long, -l      Long listing format
  --json, -j      Output as JSON
```

### generate
Generate a random password:
```bash
lpass generate [OPTIONS] [LENGTH]

Arguments:
  LENGTH          Password length (default: 16)

Options:
  --no-symbols    Exclude symbols
  --clip, -c      Copy to clipboard
```

### sync
Sync vault from server:
```bash
lpass sync
```

## Python API Reference

### LastPassClient

Main client class for interacting with LastPass.

```python
from lastpass import LastPassClient

client = LastPassClient(server="lastpass.com", config_dir=None)
```

#### Methods

##### login(username, password=None, trust=False, otp=None, force=False)
Login to LastPass.

```python
client.login("user@example.com", "masterpassword")

# With 2FA
client.login("user@example.com", "masterpassword", otp="123456")
```

##### logout(force=False)
Logout and clear session.

```python
client.logout()
```

##### is_logged_in()
Check if logged in.

```python
if client.is_logged_in():
    print("Logged in")
```

##### sync(force=False)
Sync vault from server.

```python
client.sync(force=True)
```

##### get_accounts(sync=True)
Get all accounts.

```python
accounts = client.get_accounts()
for account in accounts:
    print(account.name)
```

##### find_account(query, sync=True)
Find a single account by name, ID, or URL.

```python
account = client.find_account("github")
if account:
    print(account.password)
```

##### search_accounts(query, sync=True, group=None)
Search for accounts.

```python
matches = client.search_accounts("google")
for match in matches:
    print(match.fullname)
```

##### list_groups(sync=True)
Get all groups/folders.

```python
groups = client.list_groups()
for group in groups:
    print(group)
```

##### generate_password(length=16, symbols=True)
Generate a random password.

```python
password = client.generate_password(length=20, symbols=True)
```

##### get_password(query, sync=True)
Get password for an account.

```python
password = client.get_password("github")
```

##### get_username(query, sync=True)
Get username for an account.

```python
username = client.get_username("github")
```

##### get_notes(query, sync=True)
Get notes for an account.

```python
notes = client.get_notes("github")
```

### Data Models

#### Account
Represents a LastPass account/entry.

**Attributes:**
- `id` (str): Unique account ID
- `name` (str): Account name
- `username` (str): Username
- `password` (str): Password
- `url` (str): URL
- `group` (str): Group/folder name
- `notes` (str): Notes
- `fullname` (str): Full path (group/name)
- `fields` (List[Field]): Custom fields
- `attachments` (List[Attachment]): File attachments
- `share` (Share): Shared folder info (if applicable)

**Methods:**
- `to_dict()`: Convert to dictionary
- `get_field(name)`: Get custom field by name
- `is_secure_note()`: Check if it's a secure note

#### Field
Custom field in an account.

**Attributes:**
- `name` (str): Field name
- `value` (str): Field value
- `type` (str): Field type
- `checked` (bool): Checkbox state

#### Share
Shared folder information.

**Attributes:**
- `id` (str): Share ID
- `name` (str): Share name
- `readonly` (bool): Read-only flag

#### Attachment
File attachment.

**Attributes:**
- `id` (str): Attachment ID
- `parent_id` (str): Parent account ID
- `filename` (str): File name
- `mimetype` (str): MIME type
- `size` (str): File size

### Exceptions

All exceptions inherit from `LastPassException`:

- `LoginFailedException`: Authentication failed
- `InvalidSessionException`: Session expired or invalid
- `NetworkException`: Network/HTTP error
- `DecryptionException`: Decryption failed
- `AccountNotFoundException`: Account not found
- `InvalidPasswordException`: Invalid password

```python
from lastpass import LastPassClient, LoginFailedException

try:
    client = LastPassClient()
    client.login("user@example.com", "wrong_password")
except LoginFailedException as e:
    print(f"Login failed: {e}")
```

## Advanced Usage

### Using Context Manager

```python
from lastpass import LastPassClient

with LastPassClient() as client:
    client.login("user@example.com", "password")
    accounts = client.get_accounts()
    # Client automatically logs out when exiting context
```

### Filtering Accounts

```python
# Get accounts in specific group
accounts = client.search_accounts("", group="Work")

# Get all secure notes
accounts = [a for a in client.get_accounts() if a.is_secure_note()]

# Get accounts with specific URL
accounts = [a for a in client.get_accounts() if "github.com" in a.url]
```

### Working with Custom Fields

```python
account = client.find_account("mysite")

# Get all custom fields
for field in account.fields:
    print(f"{field.name}: {field.value}")

# Get specific field
api_key_field = account.get_field("API Key")
if api_key_field:
    print(api_key_field.value)
```

### JSON Export

```python
import json

# Export all accounts to JSON
accounts = client.get_accounts()
data = [a.to_dict() for a in accounts]

with open("export.json", "w") as f:
    json.dump(data, f, indent=2)
```

## Security Notes

- **Master Password**: Never stored, only used for key derivation
- **Encryption**: AES-256-CBC with unique IVs
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Session Storage**: Encrypted with derived key, mode 0600
- **Memory**: Sensitive data cleared when possible

## Configuration

Configuration is stored in:
- Linux/macOS: `~/.config/lpass/`
- Windows: `%APPDATA%\lpass\`

Files:
- `session`: Encrypted session data

## Development

### Setup Development Environment

```bash
git clone https://github.com/lastpass/lastpass-python.git
cd lastpass-python
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black lastpass/
flake8 lastpass/
mypy lastpass/
```

## Comparison with C CLI

This Python implementation provides:

✅ **All core functionality** of the C-based CLI
✅ **Python API** for programmatic access
✅ **No compilation** required
✅ **Easier to modify** and extend
✅ **Better error messages** and debugging

Some differences:
- Clipboard support requires `pyperclip` or system tools
- Agent/daemon not implemented (use session-based auth)
- Some advanced features (shares management, etc.) are simplified

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v2.0 or later (GPLv2+), the same license as the original LastPass CLI.

## Disclaimer

This is an independent implementation. It is not officially supported by LastPass/LogMeIn. Use at your own risk.

## Credits

- Original LastPass CLI by LastPass
- Python implementation by the community

## Related Projects

- [lastpass-cli](https://github.com/lastpass/lastpass-cli) - Original C implementation
- [lastpass-python](https://github.com/konomae/lastpass-python) - Alternative Python library
