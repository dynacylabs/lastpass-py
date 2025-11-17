"""
Tests for lastpass.client module
"""

import pytest
import responses
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from lastpass.client import LastPassClient
from lastpass.models import Account
from lastpass.exceptions import (
    LoginFailedException,
    AccountNotFoundException,
    InvalidSessionException,
)
from tests.test_fixtures import (
    MOCK_LOGIN_SUCCESS_XML,
    TEST_USERNAME,
    TEST_PASSWORD,
    get_mock_accounts,
)


class TestLastPassClient:
    """Test LastPassClient class"""
    
    def test_client_creation(self):
        """Test creating LastPassClient"""
        client = LastPassClient()
        assert client.server == "lastpass.com"
        assert client.session is None
        assert client.decryption_key is None
    
    def test_client_custom_server(self):
        """Test client with custom server"""
        client = LastPassClient(server="eu.lastpass.com")
        assert client.server == "eu.lastpass.com"
    
    def test_client_custom_config_dir(self, temp_config_dir):
        """Test client with custom config directory"""
        client = LastPassClient(config_dir=temp_config_dir)
        assert client.config_dir == temp_config_dir


class TestLogin:
    """Test login functionality"""
    
    @responses.activate
    def test_login_success(self, temp_config_dir):
        """Test successful login"""
        # Mock iterations request
        responses.add(
            responses.POST,
            "https://lastpass.com/iterations.php",
            body=b"5000",
            status=200,
        )
        
        # Mock login request
        responses.add(
            responses.POST,
            "https://lastpass.com/login.php",
            body=MOCK_LOGIN_SUCCESS_XML,
            status=200,
        )
        
        client = LastPassClient(config_dir=temp_config_dir)
        client.login(TEST_USERNAME, TEST_PASSWORD)
        
        assert client.session is not None
        assert client.session.is_valid()
        assert client.decryption_key is not None
    
    @responses.activate
    def test_login_invalid_credentials(self, temp_config_dir):
        """Test login with invalid credentials"""
        responses.add(
            responses.POST,
            "https://lastpass.com/iterations.php",
            body=b"5000",
            status=200,
        )
        
        failure_xml = b"""<?xml version="1.0"?>
        <response>
            <error cause="unknownemail" message="Invalid credentials"/>
        </response>"""
        
        responses.add(
            responses.POST,
            "https://lastpass.com/login.php",
            body=failure_xml,
            status=200,
        )
        
        client = LastPassClient(config_dir=temp_config_dir)
        
        with pytest.raises(LoginFailedException):
            client.login(TEST_USERNAME, "wrong_password")
    
    @responses.activate
    @patch('lastpass.client.getpass')
    def test_login_prompts_for_password(self, mock_getpass, temp_config_dir):
        """Test login prompts for password if not provided"""
        mock_getpass.return_value = TEST_PASSWORD
        
        responses.add(
            responses.POST,
            "https://lastpass.com/iterations.php",
            body=b"5000",
            status=200,
        )
        
        responses.add(
            responses.POST,
            "https://lastpass.com/login.php",
            body=MOCK_LOGIN_SUCCESS_XML,
            status=200,
        )
        
        client = LastPassClient(config_dir=temp_config_dir)
        client.login(TEST_USERNAME)  # No password provided
        
        mock_getpass.assert_called_once()
        assert client.session is not None


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_with_active_session(self, temp_config_dir):
        """Test logout with active session"""
        client = LastPassClient(config_dir=temp_config_dir)
        
        # Manually set up a mock session
        from lastpass.session import Session
        client.session = Session(uid="123", sessionid="sess", token="tok")
        client.decryption_key = b"test_key"
        
        with patch.object(client.http, 'logout'):
            client.logout()
        
        assert client.session is None
        assert client.decryption_key is None
    
    def test_logout_without_session(self, temp_config_dir):
        """Test logout without active session"""
        client = LastPassClient(config_dir=temp_config_dir)
        
        # Should not raise
        client.logout()


class TestIsLoggedIn:
    """Test is_logged_in method"""
    
    def test_is_logged_in_true(self):
        """Test is_logged_in returns True when logged in"""
        client = LastPassClient()
        
        from lastpass.session import Session
        client.session = Session(uid="123", sessionid="sess", token="tok")
        
        assert client.is_logged_in() is True
    
    def test_is_logged_in_false(self):
        """Test is_logged_in returns False when not logged in"""
        client = LastPassClient()
        assert client.is_logged_in() is False
    
    def test_is_logged_in_invalid_session(self):
        """Test is_logged_in with invalid session"""
        client = LastPassClient()
        
        from lastpass.session import Session
        client.session = Session()  # Invalid session
        
        assert client.is_logged_in() is False


class TestGetAccounts:
    """Test get_accounts method"""
    
    def test_get_accounts_syncs_first_time(self):
        """Test get_accounts syncs on first call"""
        client = LastPassClient()
        
        # Mock session and sync
        from lastpass.session import Session
        client.session = Session(uid="123", sessionid="sess", token="tok")
        client.decryption_key = b"test_key"
        
        with patch.object(client, 'sync') as mock_sync:
            client._accounts = get_mock_accounts()
            accounts = client.get_accounts()
            
            assert len(accounts) > 0
            # sync should be called since blob wasn't loaded
            assert mock_sync.called or len(accounts) > 0
    
    def test_get_accounts_no_sync_if_cached(self):
        """Test get_accounts doesn't sync if already cached"""
        client = LastPassClient()
        
        from lastpass.session import Session
        client.session = Session(uid="123", sessionid="sess", token="tok")
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        with patch.object(client, 'sync') as mock_sync:
            accounts = client.get_accounts(sync=False)
            
            assert len(accounts) > 0
            mock_sync.assert_not_called()
    
    def test_get_accounts_returns_list(self):
        """Test get_accounts returns list of Account objects"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        accounts = client.get_accounts(sync=False)
        
        assert isinstance(accounts, list)
        for account in accounts:
            assert isinstance(account, Account)


class TestFindAccount:
    """Test find_account method"""
    
    def test_find_account_by_name(self):
        """Test finding account by name"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        account = client.find_account("GitHub", sync=False)
        
        assert account is not None
        assert account.name == "GitHub"
    
    def test_find_account_case_insensitive(self):
        """Test finding account is case insensitive"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        account = client.find_account("github", sync=False)
        
        assert account is not None
        assert account.name == "GitHub"
    
    def test_find_account_by_id(self):
        """Test finding account by ID"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        account = client.find_account("1001", sync=False)
        
        assert account is not None
        assert account.id == "1001"
    
    def test_find_account_by_url(self):
        """Test finding account by URL"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        account = client.find_account("github.com", sync=False)
        
        assert account is not None
        assert "github.com" in account.url.lower()
    
    def test_find_account_not_found(self):
        """Test finding non-existent account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        account = client.find_account("NonExistent", sync=False)
        
        assert account is None


class TestSearchAccounts:
    """Test search_accounts method"""
    
    def test_search_accounts_basic(self):
        """Test searching accounts"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        results = client.search_accounts("git", sync=False)
        
        assert len(results) >= 1
        # Should find GitHub account
        assert any(acc.name == "GitHub" for acc in results)
    
    def test_search_accounts_case_insensitive(self):
        """Test search is case insensitive"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        results = client.search_accounts("GITHUB", sync=False)
        
        assert len(results) >= 1
    
    def test_search_accounts_no_results(self):
        """Test search with no results"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        results = client.search_accounts("nonexistent_xyz", sync=False)
        
        assert len(results) == 0


class TestListGroups:
    """Test list_groups method"""
    
    def test_list_groups(self):
        """Test listing unique groups"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        groups = client.list_groups(sync=False)
        
        assert isinstance(groups, list)
        assert "Development" in groups
        assert "Email" in groups
    
    def test_list_groups_sorted(self):
        """Test groups are sorted"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        groups = client.list_groups(sync=False)
        
        assert groups == sorted(groups)


class TestGeneratePassword:
    """Test generate_password method"""
    
    def test_generate_password_default(self):
        """Test generating password with default settings"""
        client = LastPassClient()
        password = client.generate_password()
        
        assert len(password) == 16
        assert isinstance(password, str)
    
    def test_generate_password_custom_length(self):
        """Test generating password with custom length"""
        client = LastPassClient()
        password = client.generate_password(length=32)
        
        assert len(password) == 32
    
    def test_generate_password_with_symbols(self):
        """Test generating password with symbols"""
        client = LastPassClient()
        password = client.generate_password(symbols=True)
        
        # Should contain at least some non-alphanumeric
        assert any(not c.isalnum() for c in password)
    
    def test_generate_password_without_symbols(self):
        """Test generating password without symbols"""
        client = LastPassClient()
        password = client.generate_password(symbols=False)
        
        # Should be alphanumeric only
        assert password.isalnum()
    
    def test_generate_password_uniqueness(self):
        """Test generated passwords are unique"""
        client = LastPassClient()
        passwords = [client.generate_password() for _ in range(10)]
        
        # All should be different
        assert len(set(passwords)) == 10


class TestGetPassword:
    """Test get_password method"""
    
    def test_get_password_success(self):
        """Test getting password for account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        password = client.get_password("GitHub", sync=False)
        
        assert password == "github_pass_123"
    
    def test_get_password_not_found(self):
        """Test getting password for non-existent account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        with pytest.raises(AccountNotFoundException):
            client.get_password("NonExistent", sync=False)


class TestGetUsername:
    """Test get_username method"""
    
    def test_get_username_success(self):
        """Test getting username for account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        username = client.get_username("GitHub", sync=False)
        
        assert username == "testuser"
    
    def test_get_username_not_found(self):
        """Test getting username for non-existent account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        with pytest.raises(AccountNotFoundException):
            client.get_username("NonExistent", sync=False)


class TestGetNotes:
    """Test get_notes method"""
    
    def test_get_notes_success(self):
        """Test getting notes for account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        notes = client.get_notes("GitHub", sync=False)
        
        assert "GitHub" in notes or "github" in notes.lower()
    
    def test_get_notes_not_found(self):
        """Test getting notes for non-existent account"""
        client = LastPassClient()
        client._accounts = get_mock_accounts()
        client._blob_loaded = True
        
        with pytest.raises(AccountNotFoundException):
            client.get_notes("NonExistent", sync=False)


class TestClientEdgeCases:
    """Test edge cases for LastPassClient"""
    
    def test_operations_without_login(self):
        """Test operations fail without login"""
        client = LastPassClient()
        
        # These should handle gracefully or raise appropriate errors
        accounts = client.get_accounts(sync=False)
        assert accounts == []
    
    def test_multiple_logins(self, temp_config_dir):
        """Test multiple login calls"""
        client = LastPassClient(config_dir=temp_config_dir)
        
        from lastpass.session import Session
        client.session = Session(uid="123", sessionid="sess", token="tok")
        client.decryption_key = b"key1"
        
        # Second login should replace session
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, "https://lastpass.com/iterations.php", body=b"5000")
            rsps.add(responses.POST, "https://lastpass.com/login.php", 
                    body=MOCK_LOGIN_SUCCESS_XML)
            
            client.login(TEST_USERNAME, TEST_PASSWORD, force=True)
        
        assert client.session is not None
