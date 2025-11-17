"""
Tests for lastpass.models module
"""

import pytest
from lastpass.models import Account, Field, Share, Attachment


class TestField:
    """Test Field model"""
    
    def test_field_creation(self):
        """Test creating a Field"""
        field = Field(name="API Key", value="secret123", type="text")
        assert field.name == "API Key"
        assert field.value == "secret123"
        assert field.type == "text"
        assert field.checked is False
    
    def test_field_with_checkbox(self):
        """Test Field with checkbox type"""
        field = Field(name="Remember", value="yes", type="checkbox", checked=True)
        assert field.checked is True
    
    def test_field_to_dict(self):
        """Test Field.to_dict()"""
        field = Field(name="Token", value="abc123", type="password")
        data = field.to_dict()
        assert data["name"] == "Token"
        assert data["value"] == "abc123"
        assert data["type"] == "password"
        assert data["checked"] is False


class TestAttachment:
    """Test Attachment model"""
    
    def test_attachment_creation(self):
        """Test creating an Attachment"""
        att = Attachment(
            id="att_001",
            parent_id="1001",
            mimetype="text/plain",
            filename="notes.txt",
            size="1024",
        )
        assert att.id == "att_001"
        assert att.parent_id == "1001"
        assert att.mimetype == "text/plain"
        assert att.filename == "notes.txt"
        assert att.size == "1024"
    
    def test_attachment_to_dict(self):
        """Test Attachment.to_dict()"""
        att = Attachment(
            id="att_002",
            parent_id="1002",
            mimetype="image/png",
            filename="screenshot.png",
            size="51200",
        )
        data = att.to_dict()
        assert data["id"] == "att_002"
        assert data["parent_id"] == "1002"
        assert data["filename"] == "screenshot.png"


class TestShare:
    """Test Share model"""
    
    def test_share_creation(self):
        """Test creating a Share"""
        share = Share(
            id="share_001",
            name="Team Passwords",
            key=b"0123456789abcdef",
            readonly=False,
        )
        assert share.id == "share_001"
        assert share.name == "Team Passwords"
        assert share.key == b"0123456789abcdef"
        assert share.readonly is False
    
    def test_share_readonly(self):
        """Test Share with readonly flag"""
        share = Share(
            id="share_002",
            name="Read Only",
            key=b"test_key",
            readonly=True,
        )
        assert share.readonly is True
    
    def test_share_to_dict(self):
        """Test Share.to_dict()"""
        share = Share(
            id="share_003",
            name="Project X",
            key=b"secret_key",
        )
        data = share.to_dict()
        assert data["id"] == "share_003"
        assert data["name"] == "Project X"
        assert data["readonly"] is False
        assert "key" not in data  # Key should not be in dict


class TestAccount:
    """Test Account model"""
    
    def test_account_creation(self):
        """Test creating an Account"""
        account = Account(
            id="1001",
            name="GitHub",
            username="testuser",
            password="testpass",
        )
        assert account.id == "1001"
        assert account.name == "GitHub"
        assert account.username == "testuser"
        assert account.password == "testpass"
    
    def test_account_with_all_fields(self):
        """Test Account with all fields"""
        account = Account(
            id="1002",
            name="Gmail",
            username="user@gmail.com",
            password="secure_pass",
            url="https://mail.google.com",
            group="Email",
            notes="Personal email account",
            fullname="Email/Gmail",
            last_touch="1234567890",
            last_modified_gmt="1234567890",
            pwprotect=True,
            favorite=True,
            is_app=False,
            attach_present=True,
        )
        assert account.group == "Email"
        assert account.notes == "Personal email account"
        assert account.fullname == "Email/Gmail"
        assert account.pwprotect is True
        assert account.favorite is True
        assert account.attach_present is True
    
    def test_account_with_fields(self):
        """Test Account with custom fields"""
        field1 = Field(name="API Key", value="key123", type="text")
        field2 = Field(name="Secret", value="secret", type="password")
        
        account = Account(
            id="1003",
            name="AWS",
            username="admin",
            password="pass",
            fields=[field1, field2],
        )
        assert len(account.fields) == 2
        assert account.fields[0].name == "API Key"
        assert account.fields[1].name == "Secret"
    
    def test_account_with_attachments(self):
        """Test Account with attachments"""
        att = Attachment(
            id="att_001",
            parent_id="1004",
            mimetype="text/plain",
            filename="notes.txt",
            size="1024",
        )
        
        account = Account(
            id="1004",
            name="Test",
            attachments=[att],
            attach_present=True,
        )
        assert len(account.attachments) == 1
        assert account.attachments[0].filename == "notes.txt"
        assert account.attach_present is True
    
    def test_account_with_share(self):
        """Test Account in shared folder"""
        share = Share(
            id="share_001",
            name="Team",
            key=b"share_key",
        )
        
        account = Account(
            id="1005",
            name="Shared Account",
            username="user",
            password="pass",
            share=share,
        )
        assert account.share is not None
        assert account.share.name == "Team"
    
    def test_account_to_dict(self):
        """Test Account.to_dict()"""
        account = Account(
            id="1006",
            name="Test Account",
            username="testuser",
            password="testpass",
            url="https://example.com",
            group="Test Group",
        )
        data = account.to_dict()
        assert data["id"] == "1006"
        assert data["name"] == "Test Account"
        assert data["username"] == "testuser"
        assert data["password"] == "testpass"
        assert data["url"] == "https://example.com"
        assert data["group"] == "Test Group"
    
    def test_account_to_dict_with_fields(self):
        """Test Account.to_dict() includes fields"""
        field = Field(name="Note", value="value", type="text")
        account = Account(
            id="1007",
            name="Test",
            fields=[field],
        )
        data = account.to_dict()
        assert "fields" in data
        assert len(data["fields"]) == 1
        assert data["fields"][0]["name"] == "Note"
    
    def test_account_defaults(self):
        """Test Account default values"""
        account = Account(id="1008", name="Minimal")
        assert account.username == ""
        assert account.password == ""
        assert account.url == ""
        assert account.group == ""
        assert account.notes == ""
        assert account.pwprotect is False
        assert account.favorite is False
        assert account.is_app is False
        assert account.attach_present is False
        assert account.fields == []
        assert account.attachments == []
        assert account.share is None
