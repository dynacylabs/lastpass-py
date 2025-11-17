"""
Mock data fixtures for testing
"""

import base64
import struct
from typing import List
from lastpass.models import Account, Field, Share, Attachment
from lastpass.session import Session


# Sample test credentials
TEST_USERNAME = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_ITERATIONS = 5000
TEST_UID = "123456789"
TEST_SESSION_ID = "test_session_id_12345"
TEST_TOKEN = "test_token_67890"


def get_mock_session() -> Session:
    """Get a mock session object"""
    return Session(
        uid=TEST_UID,
        sessionid=TEST_SESSION_ID,
        token=TEST_TOKEN,
        private_key="mock_private_key_hex",
    )


def get_mock_accounts() -> List[Account]:
    """Get sample accounts for testing"""
    return [
        Account(
            id="1001",
            name="GitHub",
            username="testuser",
            password="github_pass_123",
            url="https://github.com/login",
            group="Development",
            notes="My GitHub account",
            fullname="Development/GitHub",
            last_touch="1234567890",
            last_modified_gmt="1234567890",
            pwprotect=False,
            favorite=True,
        ),
        Account(
            id="1002",
            name="Gmail",
            username="test@gmail.com",
            password="gmail_secure_pass",
            url="https://mail.google.com",
            group="Email",
            notes="Personal email",
            fullname="Email/Gmail",
            last_touch="1234567891",
            last_modified_gmt="1234567891",
            pwprotect=False,
            favorite=False,
        ),
        Account(
            id="1003",
            name="AWS Console",
            username="admin",
            password="aws_p@ssw0rd",
            url="https://console.aws.amazon.com",
            group="Development/Cloud",
            notes="Production AWS account",
            fullname="Development/Cloud/AWS Console",
            last_touch="1234567892",
            last_modified_gmt="1234567892",
            pwprotect=True,
            favorite=False,
        ),
    ]


def get_mock_fields() -> List[Field]:
    """Get sample custom fields"""
    return [
        Field(name="API Key", value="sk_test_123456", type="text"),
        Field(name="Secret Token", value="secret_xyz", type="password"),
        Field(name="Remember Me", value="yes", type="checkbox", checked=True),
    ]


def get_mock_shares() -> List[Share]:
    """Get sample shared folders"""
    return [
        Share(
            id="share_001",
            name="Team Passwords",
            key=b"0123456789abcdef0123456789abcdef",
            readonly=False,
        ),
        Share(
            id="share_002",
            name="Read Only Share",
            key=b"fedcba9876543210fedcba9876543210",
            readonly=True,
        ),
    ]


def get_mock_attachments() -> List[Attachment]:
    """Get sample attachments"""
    return [
        Attachment(
            id="att_001",
            parent_id="1001",
            mimetype="text/plain",
            filename="notes.txt",
            size="1024",
            storage_key="storage_key_001",
        ),
        Attachment(
            id="att_002",
            parent_id="1002",
            mimetype="image/png",
            filename="screenshot.png",
            size="51200",
            storage_key="storage_key_002",
        ),
    ]


# Mock XML responses
MOCK_LOGIN_SUCCESS_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<response>
    <ok uid="123456789" sessionid="test_session_id_12345" token="test_token_67890" 
        privatekeyenc="mock_private_key_hex"/>
</response>"""

MOCK_LOGIN_FAILURE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<response>
    <error cause="unknownemail" message="Invalid username or password"/>
</response>"""

MOCK_LOGIN_MFA_REQUIRED_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<response>
    <error cause="googleauthrequired" message="Multifactor authentication required"/>
</response>"""

MOCK_LOGIN_MFA_FAILED_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<response>
    <error cause="googleauthfailed" message="Invalid multifactor code"/>
</response>"""


# Mock blob data helpers
def create_blob_chunk(chunk_id: str, data: bytes) -> bytes:
    """Create a blob chunk with 4-byte ID, 4-byte size, and data"""
    chunk_id_bytes = chunk_id.encode('ascii')
    size = struct.pack(">I", len(data))
    return chunk_id_bytes + size + data


def create_blob_item(data: bytes) -> bytes:
    """Create a size-prefixed blob item"""
    size = struct.pack(">I", len(data))
    return size + data


def get_mock_blob_data(encryption_key: bytes) -> bytes:
    """Create a simple mock blob with encrypted account data"""
    from lastpass.cipher import aes_encrypt
    
    # Create a simple ACCT chunk
    account_data = BytesIO()
    
    # Write account fields (simplified version)
    account_data.write(create_blob_item(b"1001"))  # id
    account_data.write(create_blob_item(aes_encrypt("GitHub", encryption_key)))  # name
    account_data.write(create_blob_item(aes_encrypt("Development", encryption_key)))  # group
    account_data.write(create_blob_item(aes_encrypt("https://github.com", encryption_key)))  # url
    account_data.write(create_blob_item(aes_encrypt("Notes here", encryption_key)))  # notes
    account_data.write(create_blob_item(b"0"))  # fav
    account_data.write(create_blob_item(b""))  # share_id
    account_data.write(create_blob_item(aes_encrypt("testuser", encryption_key)))  # username
    account_data.write(create_blob_item(aes_encrypt("testpass", encryption_key)))  # password
    
    # Add remaining required fields with empty/default values
    for _ in range(20):  # Add enough fields to match expected structure
        account_data.write(create_blob_item(b""))
    
    acct_chunk = create_blob_chunk("ACCT", account_data.getvalue())
    
    return acct_chunk


# Import for BytesIO in function
from io import BytesIO
