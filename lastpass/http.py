"""
HTTP communication with LastPass servers
"""

import requests
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlencode
from .exceptions import NetworkException, LoginFailedException
from .session import Session


class HTTPClient:
    """HTTP client for LastPass API"""
    
    def __init__(self, server: str = "lastpass.com"):
        self.server = server
        self.base_url = f"https://{server}"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "lastpass-python-cli/1.0.0",
        })
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             session: Optional[Session] = None) -> Tuple[bytes, int]:
        """
        POST request to LastPass
        Returns: (response_body, status_code)
        """
        url = f"{self.base_url}/{endpoint}"
        
        if data is None:
            data = {}
        
        # Add session credentials if provided
        if session and session.is_valid():
            data["token"] = session.token
            data["sessionid"] = session.sessionid
        
        try:
            response = self.session.post(url, data=data, timeout=30)
            return response.content, response.status_code
        except requests.RequestException as e:
            raise NetworkException(f"HTTP request failed: {e}")
    
    def get_iterations(self, username: str) -> int:
        """Get PBKDF2 iteration count for a username"""
        try:
            content, status = self.post("iterations.php", {"email": username})
            
            if status != 200:
                raise NetworkException(f"Failed to get iterations: HTTP {status}")
            
            iterations = int(content.decode('utf-8').strip())
            
            if iterations < 2:
                raise NetworkException(f"Invalid iteration count: {iterations}")
            
            return iterations
        except ValueError as e:
            raise NetworkException(f"Invalid iterations response: {e}")
    
    def login(self, username: str, login_key: str, iterations: int,
              trust: bool = False, otp: Optional[str] = None) -> Tuple[bytes, int]:
        """
        Authenticate with LastPass
        Returns: (response_xml, status_code)
        """
        data = {
            "method": "cli",
            "xml": "2",
            "username": username,
            "hash": login_key,
            "iterations": str(iterations),
        }
        
        if trust:
            data["trust"] = "1"
        
        if otp:
            data["otp"] = otp
        
        return self.post("login.php", data)
    
    def logout(self, session: Session) -> None:
        """Logout and invalidate session"""
        try:
            self.post("logout.php", session=session)
        except NetworkException:
            # Logout failures are non-critical
            pass
    
    def download_blob(self, session: Session) -> bytes:
        """Download encrypted vault blob"""
        content, status = self.post("getaccts.php", {"mobile": "1", "b64": "1", "hash": "0.0"}, session=session)
        
        if status != 200:
            raise NetworkException(f"Failed to download blob: HTTP {status}")
        
        return content
    
    def upload_blob(self, session: Session, blob_data: str) -> None:
        """Upload encrypted vault blob"""
        content, status = self.post("update.php", {"blob": blob_data}, session=session)
        
        if status != 200:
            raise NetworkException(f"Failed to upload blob: HTTP {status}")
    
    def get_attachment(self, session: Session, attachment_id: str, 
                      share_id: Optional[str] = None) -> bytes:
        """Download attachment data"""
        data = {"getattach": attachment_id}
        
        if share_id:
            data["shareid"] = share_id
        
        content, status = self.post("getattach.php", data, session=session)
        
        if status != 200:
            raise NetworkException(f"Failed to get attachment: HTTP {status}")
        
        return content
    
    def delete_account(self, session: Session, account_id: str, 
                      share_id: Optional[str] = None) -> None:
        """Delete an account from the vault"""
        data = {"extjs": "1", "delete": "1", "aid": account_id}
        
        if share_id:
            data["sharedfolderid"] = share_id
        
        content, status = self.post("show_website.php", data, session=session)
        
        if status != 200:
            raise NetworkException(f"Failed to delete account: HTTP {status}")
