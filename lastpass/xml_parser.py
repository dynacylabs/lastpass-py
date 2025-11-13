"""
XML parsing for LastPass responses
"""

import xml.etree.ElementTree as ET
from typing import Optional
from .session import Session
from .exceptions import LoginFailedException


def parse_login_response(xml_data: bytes) -> Session:
    """Parse login response XML and extract session data"""
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise LoginFailedException(f"Invalid XML response: {e}")
    
    # Check for errors
    error = root.find(".//error")
    if error is not None:
        cause = error.get("cause", "unknown")
        message = error.get("message", "Login failed")
        
        # Handle specific error cases
        if cause == "googleauthrequired" or cause == "microsoftauthrequired":
            raise LoginFailedException("Multifactor authentication required. Use --otp option.")
        elif cause == "googleauthfailed" or cause == "microsoftauthfailed":
            raise LoginFailedException("Invalid multifactor authentication code.")
        else:
            raise LoginFailedException(f"{message} (cause: {cause})")
    
    # Check for "ok" response with session data
    ok = root.find(".//ok")
    if ok is None:
        raise LoginFailedException("Login response missing 'ok' element")
    
    # Extract session attributes
    uid = ok.get("uid")
    sessionid = ok.get("sessionid")
    token = ok.get("token")
    private_key_hex = ok.get("privatekeyenc")
    
    if not uid or not sessionid or not token:
        raise LoginFailedException("Login response missing required session data")
    
    session = Session(
        uid=uid,
        sessionid=sessionid,
        token=token,
        private_key=private_key_hex or "",
    )
    
    return session


def parse_account_xml(xml_element: ET.Element) -> dict:
    """Parse account XML element into dictionary"""
    return {
        "id": xml_element.get("id", ""),
        "name": xml_element.get("name", ""),
        "group": xml_element.get("group", ""),
        "url": xml_element.get("url", ""),
        "username": xml_element.get("username", ""),
        "password": xml_element.get("password", ""),
        "notes": xml_element.get("extra", ""),
        "fav": xml_element.get("fav", "0") == "1",
        "pwprotect": xml_element.get("pwprotect", "0") == "1",
        "last_touch": xml_element.get("last_touch", ""),
        "last_modified_gmt": xml_element.get("last_modified_gmt", ""),
    }
