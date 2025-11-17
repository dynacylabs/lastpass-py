"""
Tests for lastpass.xml_parser module
"""

import pytest
from lastpass.xml_parser import parse_login_response, parse_account_xml
from lastpass.session import Session
from lastpass.exceptions import LoginFailedException
from tests.test_fixtures import (
    MOCK_LOGIN_SUCCESS_XML,
    MOCK_LOGIN_FAILURE_XML,
    MOCK_LOGIN_MFA_REQUIRED_XML,
    MOCK_LOGIN_MFA_FAILED_XML,
)


class TestParseLoginResponse:
    """Test parsing login XML responses"""
    
    def test_parse_successful_login(self):
        """Test parsing successful login response"""
        session = parse_login_response(MOCK_LOGIN_SUCCESS_XML)
        
        assert isinstance(session, Session)
        assert session.uid == "123456789"
        assert session.sessionid == "test_session_id_12345"
        assert session.token == "test_token_67890"
        assert session.private_key == "mock_private_key_hex"
        assert session.is_valid()
    
    def test_parse_login_failure(self):
        """Test parsing failed login response"""
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(MOCK_LOGIN_FAILURE_XML)
        
        assert "Invalid username or password" in str(exc_info.value)
    
    def test_parse_mfa_required(self):
        """Test parsing MFA required error"""
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(MOCK_LOGIN_MFA_REQUIRED_XML)
        
        assert "Multifactor authentication required" in str(exc_info.value)
    
    def test_parse_mfa_failed(self):
        """Test parsing MFA failure"""
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(MOCK_LOGIN_MFA_FAILED_XML)
        
        assert "Invalid multifactor" in str(exc_info.value)
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML"""
        invalid_xml = b"not valid xml <>"
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(invalid_xml)
        
        assert "Invalid XML" in str(exc_info.value)
    
    def test_parse_missing_ok_element(self):
        """Test response missing 'ok' element"""
        xml = b"""<?xml version="1.0"?>
        <response>
            <something>data</something>
        </response>"""
        
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(xml)
        
        assert "missing 'ok' element" in str(exc_info.value)
    
    def test_parse_missing_required_attributes(self):
        """Test response missing required session attributes"""
        # Missing token
        xml = b"""<?xml version="1.0"?>
        <response>
            <ok uid="123" sessionid="sess"/>
        </response>"""
        
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(xml)
        
        assert "missing required session data" in str(exc_info.value)
    
    def test_parse_with_optional_private_key(self):
        """Test parsing response without private key"""
        xml = b"""<?xml version="1.0"?>
        <response>
            <ok uid="123" sessionid="sess" token="tok"/>
        </response>"""
        
        session = parse_login_response(xml)
        assert session.uid == "123"
        assert session.private_key == ""
    
    def test_parse_error_with_cause(self):
        """Test parsing error with specific cause"""
        xml = b"""<?xml version="1.0"?>
        <response>
            <error cause="outofbandrequired" message="Out of band auth required"/>
        </response>"""
        
        with pytest.raises(LoginFailedException) as exc_info:
            parse_login_response(xml)
        
        assert "cause: outofbandrequired" in str(exc_info.value)


class TestParseAccountXML:
    """Test parsing account XML elements"""
    
    def test_parse_account_basic(self):
        """Test parsing basic account XML"""
        import xml.etree.ElementTree as ET
        
        xml_str = """<account id="1001" name="GitHub" username="user" password="pass"/>"""
        element = ET.fromstring(xml_str)
        
        data = parse_account_xml(element)
        assert data["id"] == "1001"
        assert data["name"] == "GitHub"
        assert data["username"] == "user"
        assert data["password"] == "pass"
    
    def test_parse_account_with_group(self):
        """Test parsing account with group"""
        import xml.etree.ElementTree as ET
        
        xml_str = """<account id="1002" name="Gmail" group="Email" 
                     username="test@gmail.com" password="secret"/>"""
        element = ET.fromstring(xml_str)
        
        data = parse_account_xml(element)
        assert data["group"] == "Email"
    
    def test_parse_account_with_all_fields(self):
        """Test parsing account with all fields"""
        import xml.etree.ElementTree as ET
        
        xml_str = """<account id="1003" name="AWS" group="Cloud" 
                     url="https://aws.amazon.com" username="admin" 
                     password="pass" extra="notes here" 
                     fav="1" pwprotect="1" 
                     last_touch="1234567890" last_modified_gmt="1234567891"/>"""
        element = ET.fromstring(xml_str)
        
        data = parse_account_xml(element)
        assert data["id"] == "1003"
        assert data["name"] == "AWS"
        assert data["group"] == "Cloud"
        assert data["url"] == "https://aws.amazon.com"
        assert data["username"] == "admin"
        assert data["password"] == "pass"
        assert data["notes"] == "notes here"
        assert data["fav"] is True
        assert data["pwprotect"] is True
        assert data["last_touch"] == "1234567890"
        assert data["last_modified_gmt"] == "1234567891"
    
    def test_parse_account_missing_optional_fields(self):
        """Test parsing account with missing optional fields"""
        import xml.etree.ElementTree as ET
        
        xml_str = """<account id="1004" name="Test"/>"""
        element = ET.fromstring(xml_str)
        
        data = parse_account_xml(element)
        assert data["id"] == "1004"
        assert data["name"] == "Test"
        assert data["username"] == ""
        assert data["password"] == ""
        assert data["url"] == ""
        assert data["group"] == ""
        assert data["notes"] == ""
        assert data["fav"] is False
        assert data["pwprotect"] is False
    
    def test_parse_account_fav_flag(self):
        """Test parsing favorite flag"""
        import xml.etree.ElementTree as ET
        
        # fav="1" should be True
        xml_str1 = """<account id="1" name="Test" fav="1"/>"""
        element1 = ET.fromstring(xml_str1)
        data1 = parse_account_xml(element1)
        assert data1["fav"] is True
        
        # fav="0" should be False
        xml_str2 = """<account id="2" name="Test" fav="0"/>"""
        element2 = ET.fromstring(xml_str2)
        data2 = parse_account_xml(element2)
        assert data2["fav"] is False
        
        # Missing fav should be False
        xml_str3 = """<account id="3" name="Test"/>"""
        element3 = ET.fromstring(xml_str3)
        data3 = parse_account_xml(element3)
        assert data3["fav"] is False
    
    def test_parse_account_pwprotect_flag(self):
        """Test parsing password protect flag"""
        import xml.etree.ElementTree as ET
        
        xml_str = """<account id="1" name="Test" pwprotect="1"/>"""
        element = ET.fromstring(xml_str)
        data = parse_account_xml(element)
        assert data["pwprotect"] is True


class TestXMLParserEdgeCases:
    """Test edge cases for XML parsing"""
    
    def test_parse_empty_xml(self):
        """Test parsing empty XML"""
        with pytest.raises(LoginFailedException):
            parse_login_response(b"")
    
    def test_parse_xml_with_special_characters(self):
        """Test parsing XML with special characters"""
        xml = b"""<?xml version="1.0"?>
        <response>
            <ok uid="123&amp;456" sessionid="sess&lt;test&gt;" token="tok"/>
        </response>"""
        
        session = parse_login_response(xml)
        assert session.uid == "123&456"
        assert session.sessionid == "sess<test>"
    
    def test_parse_xml_with_unicode(self):
        """Test parsing XML with unicode characters"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <ok uid="用户123" sessionid="sess" token="tok"/>
        </response>""".encode('utf-8')
        
        session = parse_login_response(xml)
        assert session.uid == "用户123"
    
    def test_parse_malformed_xml(self):
        """Test parsing malformed XML"""
        xml = b"""<?xml version="1.0"?>
        <response>
            <ok uid="123"
        </response>"""
        
        with pytest.raises(LoginFailedException):
            parse_login_response(xml)
