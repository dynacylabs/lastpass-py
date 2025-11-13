"""
Blob parsing and serialization for LastPass vault data
"""

import struct
import base64
from typing import List, Optional, Tuple
from io import BytesIO

from .models import Account, Field, Share, Attachment
from .cipher import aes_decrypt, aes_decrypt_base64, hex_to_bytes
from .exceptions import DecryptionException


class BlobParser:
    """Parse encrypted LastPass blob"""
    
    def __init__(self, blob_data: bytes, key: bytes):
        self.data = BytesIO(blob_data)
        self.key = key
        self.accounts: List[Account] = []
        self.shares: List[Share] = []
    
    def read_chunk(self) -> Tuple[str, bytes]:
        """Read a chunk: 4-byte ID + 4-byte size + data"""
        chunk_id = self.data.read(4)
        if len(chunk_id) < 4:
            return "", b""
        
        size_bytes = self.data.read(4)
        if len(size_bytes) < 4:
            return "", b""
        
        size = struct.unpack(">I", size_bytes)[0]
        data = self.data.read(size)
        
        try:
            chunk_id_str = chunk_id.decode('ascii')
        except:
            chunk_id_str = chunk_id.hex()
        
        return chunk_id_str, data
    
    def read_item(self, data: BytesIO) -> bytes:
        """Read size-prefixed item from data stream"""
        size_bytes = data.read(4)
        if len(size_bytes) < 4:
            return b""
        
        size = struct.unpack(">I", size_bytes)[0]
        return data.read(size)
    
    def decrypt_item(self, data: bytes, key: Optional[bytes] = None) -> str:
        """Decrypt an item with AES"""
        if not data:
            return ""
        
        if key is None:
            key = self.key
        
        try:
            decrypted = aes_decrypt(data, key)
            return decrypted.decode('utf-8', errors='replace')
        except Exception:
            return ""
    
    def parse_account(self, data: bytes, share: Optional[Share] = None) -> Optional[Account]:
        """Parse ACCT chunk into Account object"""
        stream = BytesIO(data)
        
        try:
            account_id = self.read_item(stream).decode('utf-8', errors='replace')
            name_enc = self.read_item(stream)
            group_enc = self.read_item(stream)
            url_enc = self.read_item(stream)
            notes_enc = self.read_item(stream)
            
            # Skip some fields
            self.read_item(stream)  # fav
            
            # Read share ID if present
            share_id = self.read_item(stream).decode('utf-8', errors='replace')
            
            username_enc = self.read_item(stream)
            password_enc = self.read_item(stream)
            
            pwprotect = self.read_item(stream) == b'1'
            
            # Skip generated password flag
            self.read_item(stream)
            
            # Skip sn (secure note flag)
            self.read_item(stream)
            
            last_touch = self.read_item(stream).decode('utf-8', errors='replace')
            
            # Skip auto login
            self.read_item(stream)
            
            # Skip never autofill
            self.read_item(stream)
            
            # Read realm data
            self.read_item(stream)
            
            # Read fiid
            self.read_item(stream)
            
            # Read custom js
            self.read_item(stream)
            
            # Read submit id
            self.read_item(stream)
            
            # Read captcha id
            self.read_item(stream)
            
            # Read urid
            self.read_item(stream)
            
            # Read basic auth
            self.read_item(stream)
            
            # Read method
            self.read_item(stream)
            
            # Read action
            self.read_item(stream)
            
            # Read group id
            self.read_item(stream)
            
            # Read deleted
            self.read_item(stream)
            
            # Read attach key
            attachkey_enc = self.read_item(stream)
            
            # Read attach present
            attach_present = self.read_item(stream) == b'1'
            
            # Skip individual share name
            self.read_item(stream)
            
            # Read last modified gmt
            last_modified_gmt = self.read_item(stream).decode('utf-8', errors='replace')
            
            # Decrypt fields
            decryption_key = share.key if share else self.key
            
            name = self.decrypt_item(name_enc, decryption_key)
            group = self.decrypt_item(group_enc, decryption_key)
            url = self.decrypt_item(url_enc, decryption_key)
            notes = self.decrypt_item(notes_enc, decryption_key)
            username = self.decrypt_item(username_enc, decryption_key)
            password = self.decrypt_item(password_enc, decryption_key)
            attachkey = self.decrypt_item(attachkey_enc, decryption_key)
            
            # Build fullname (group + name)
            if group:
                fullname = f"{group}/{name}"
            else:
                fullname = name
            
            account = Account(
                id=account_id,
                name=name,
                username=username,
                password=password,
                url=url,
                group=group,
                notes=notes,
                fullname=fullname,
                last_touch=last_touch,
                last_modified_gmt=last_modified_gmt,
                pwprotect=pwprotect,
                attach_present=attach_present,
                share=share,
            )
            
            return account
        except Exception as e:
            # Skip malformed accounts
            return None
    
    def parse_field(self, data: bytes, account_key: bytes) -> Optional[Field]:
        """Parse ACFL (account field) chunk"""
        stream = BytesIO(data)
        
        try:
            # Skip account ID
            self.read_item(stream)
            
            name_enc = self.read_item(stream)
            type_str = self.read_item(stream).decode('utf-8', errors='replace')
            value_enc = self.read_item(stream)
            checked = self.read_item(stream) == b'1'
            
            name = self.decrypt_item(name_enc, account_key)
            value = self.decrypt_item(value_enc, account_key)
            
            return Field(
                name=name,
                value=value,
                type=type_str,
                checked=checked,
            )
        except Exception:
            return None
    
    def parse_share(self, data: bytes) -> Optional[Share]:
        """Parse SHAR chunk"""
        stream = BytesIO(data)
        
        try:
            share_id = self.read_item(stream).decode('utf-8', errors='replace')
            share_name_enc = self.read_item(stream)
            share_key_enc = self.read_item(stream)
            
            # Decrypt share key with main key
            share_key_hex = self.decrypt_item(share_key_enc, self.key)
            
            if not share_key_hex or len(share_key_hex) != 64:  # 32 bytes = 64 hex chars
                return None
            
            share_key = hex_to_bytes(share_key_hex)
            
            # Decrypt share name with share key
            share_name = self.decrypt_item(share_name_enc, share_key)
            
            # Read readonly flag
            readonly = self.read_item(stream) == b'1'
            
            return Share(
                id=share_id,
                name=share_name,
                key=share_key,
                readonly=readonly,
            )
        except Exception:
            return None
    
    def parse(self) -> Tuple[List[Account], List[Share]]:
        """Parse the entire blob"""
        shares_by_id = {}
        accounts_by_id = {}
        fields_by_account_id = {}
        
        while True:
            chunk_id, chunk_data = self.read_chunk()
            
            if not chunk_id:
                break
            
            if chunk_id == "SHAR":
                share = self.parse_share(chunk_data)
                if share:
                    shares_by_id[share.id] = share
                    self.shares.append(share)
            
            elif chunk_id == "ACCT":
                # Determine which share this account belongs to
                # We'll need to re-parse to get share_id
                stream = BytesIO(chunk_data)
                account_id = self.read_item(stream).decode('utf-8', errors='replace')
                self.read_item(stream)  # name
                self.read_item(stream)  # group
                self.read_item(stream)  # url
                self.read_item(stream)  # notes
                self.read_item(stream)  # fav
                share_id = self.read_item(stream).decode('utf-8', errors='replace')
                
                share = shares_by_id.get(share_id)
                account = self.parse_account(chunk_data, share)
                
                if account:
                    accounts_by_id[account.id] = account
                    self.accounts.append(account)
            
            elif chunk_id == "ACFL":
                # Custom field - we need to associate it with an account
                stream = BytesIO(chunk_data)
                account_id = self.read_item(stream).decode('utf-8', errors='replace')
                
                if account_id in accounts_by_id:
                    account = accounts_by_id[account_id]
                    share = account.share
                    field_key = share.key if share else self.key
                    
                    field = self.parse_field(chunk_data, field_key)
                    if field:
                        account.fields.append(field)
        
        return self.accounts, self.shares


def parse_blob(blob_data: bytes, key: bytes) -> Tuple[List[Account], List[Share]]:
    """Parse encrypted blob and return accounts and shares"""
    # Blob is base64 encoded
    try:
        decoded = base64.b64decode(blob_data)
    except Exception:
        decoded = blob_data
    
    parser = BlobParser(decoded, key)
    return parser.parse()
