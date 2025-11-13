"""
Command-line interface for LastPass
"""

import sys
import argparse
import json
import getpass
from typing import Optional, List
from pathlib import Path

from . import __version__
from .client import LastPassClient
from .exceptions import LastPassException, AccountNotFoundException
from .models import Account


class CLI:
    """Command-line interface handler"""
    
    def __init__(self):
        self.client = LastPassClient()
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI with arguments"""
        parser = self._create_parser()
        
        if args is None:
            args = sys.argv[1:]
        
        # If no args, show help
        if not args:
            parser.print_help()
            return 1
        
        parsed_args = parser.parse_args(args)
        
        try:
            return parsed_args.func(parsed_args)
        except LastPassException as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nAborted", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='lpass',
            description='LastPass command-line interface',
        )
        
        parser.add_argument('--version', action='version', 
                          version=f'LastPass CLI v{__version__}')
        
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Login
        login_parser = subparsers.add_parser('login', help='Login to LastPass')
        login_parser.add_argument('username', help='LastPass username/email')
        login_parser.add_argument('--trust', action='store_true',
                                help='Trust this device')
        login_parser.add_argument('--otp', help='One-time password for 2FA')
        login_parser.add_argument('--force', '-f', action='store_true',
                                help='Force new login')
        login_parser.set_defaults(func=self.cmd_login)
        
        # Logout
        logout_parser = subparsers.add_parser('logout', help='Logout from LastPass')
        logout_parser.add_argument('--force', '-f', action='store_true',
                                 help='Force logout')
        logout_parser.set_defaults(func=self.cmd_logout)
        
        # Status
        status_parser = subparsers.add_parser('status', help='Show login status')
        status_parser.add_argument('--quiet', '-q', action='store_true',
                                 help='Quiet mode')
        status_parser.set_defaults(func=self.cmd_status)
        
        # Show
        show_parser = subparsers.add_parser('show', help='Show account details')
        show_parser.add_argument('query', help='Account name, ID, or URL')
        show_parser.add_argument('--password', action='store_true',
                               help='Show only password')
        show_parser.add_argument('--username', action='store_true',
                               help='Show only username')
        show_parser.add_argument('--url', action='store_true',
                               help='Show only URL')
        show_parser.add_argument('--notes', action='store_true',
                               help='Show only notes')
        show_parser.add_argument('--field', metavar='FIELD',
                               help='Show only specified field')
        show_parser.add_argument('--json', '-j', action='store_true',
                               help='Output as JSON')
        show_parser.add_argument('--clip', '-c', action='store_true',
                               help='Copy to clipboard')
        show_parser.set_defaults(func=self.cmd_show)
        
        # List
        ls_parser = subparsers.add_parser('ls', help='List accounts')
        ls_parser.add_argument('group', nargs='?', help='Filter by group')
        ls_parser.add_argument('--long', '-l', action='store_true',
                             help='Long listing format')
        ls_parser.add_argument('--json', '-j', action='store_true',
                             help='Output as JSON')
        ls_parser.set_defaults(func=self.cmd_ls)
        
        # Generate
        generate_parser = subparsers.add_parser('generate', 
                                               help='Generate password')
        generate_parser.add_argument('length', type=int, nargs='?', default=16,
                                   help='Password length (default: 16)')
        generate_parser.add_argument('--no-symbols', action='store_true',
                                   help='Exclude symbols')
        generate_parser.add_argument('--clip', '-c', action='store_true',
                                   help='Copy to clipboard')
        generate_parser.set_defaults(func=self.cmd_generate)
        
        # Sync
        sync_parser = subparsers.add_parser('sync', help='Sync vault from server')
        sync_parser.set_defaults(func=self.cmd_sync)
        
        return parser
    
    def cmd_login(self, args) -> int:
        """Handle login command"""
        password = getpass.getpass("Master Password: ")
        
        try:
            self.client.login(
                args.username,
                password,
                trust=args.trust,
                otp=args.otp,
                force=args.force
            )
            print(f"Success: Logged in as {args.username}")
            return 0
        except Exception as e:
            print(f"Login failed: {e}", file=sys.stderr)
            return 1
    
    def cmd_logout(self, args) -> int:
        """Handle logout command"""
        try:
            self.client.logout(force=args.force)
            print("Logged out successfully")
            return 0
        except Exception as e:
            print(f"Logout failed: {e}", file=sys.stderr)
            return 1
    
    def cmd_status(self, args) -> int:
        """Handle status command"""
        if self.client.is_logged_in():
            if not args.quiet:
                print(f"Logged in as {self.client.session.uid}")
            return 0
        else:
            if not args.quiet:
                print("Not logged in")
            return 1
    
    def cmd_show(self, args) -> int:
        """Handle show command"""
        try:
            account = self.client.find_account(args.query)
            
            if not account:
                print(f"Account not found: {args.query}", file=sys.stderr)
                return 1
            
            # Output specific field
            if args.password:
                output = account.password
            elif args.username:
                output = account.username
            elif args.url:
                output = account.url
            elif args.notes:
                output = account.notes
            elif args.field:
                field = account.get_field(args.field)
                if field:
                    output = field.value
                else:
                    print(f"Field not found: {args.field}", file=sys.stderr)
                    return 1
            elif args.json:
                output = json.dumps(account.to_dict(), indent=2)
            else:
                # Default: show all info
                output = self._format_account(account)
            
            if args.clip:
                self._copy_to_clipboard(output)
                print("Copied to clipboard")
            else:
                print(output)
            
            return 0
        except AccountNotFoundException as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def cmd_ls(self, args) -> int:
        """Handle ls command"""
        try:
            accounts = self.client.get_accounts()
            
            # Filter by group if specified
            if args.group:
                accounts = [a for a in accounts if a.group == args.group]
            
            if args.json:
                data = [a.to_dict() for a in accounts]
                print(json.dumps(data, indent=2))
            elif args.long:
                for account in accounts:
                    print(f"{account.id:10} {account.fullname:40} {account.username:30}")
            else:
                for account in accounts:
                    print(account.fullname)
            
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def cmd_generate(self, args) -> int:
        """Handle generate command"""
        password = self.client.generate_password(
            length=args.length,
            symbols=not args.no_symbols
        )
        
        if args.clip:
            self._copy_to_clipboard(password)
            print("Password copied to clipboard")
        else:
            print(password)
        
        return 0
    
    def cmd_sync(self, args) -> int:
        """Handle sync command"""
        try:
            self.client.sync(force=True)
            print("Vault synced successfully")
            return 0
        except Exception as e:
            print(f"Sync failed: {e}", file=sys.stderr)
            return 1
    
    def _format_account(self, account: Account) -> str:
        """Format account for display"""
        lines = [
            f"Name: {account.name}",
            f"Fullname: {account.fullname}",
            f"Username: {account.username}",
            f"Password: {account.password}",
            f"URL: {account.url}",
        ]
        
        if account.notes:
            lines.append(f"Notes: {account.notes}")
        
        if account.fields:
            lines.append("Fields:")
            for field in account.fields:
                lines.append(f"  {field.name}: {field.value}")
        
        return "\n".join(lines)
    
    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(text)
        except ImportError:
            # Try using system commands
            import subprocess
            import platform
            
            system = platform.system()
            
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(['pbcopy'], input=text.encode(), check=True)
                elif system == "Linux":
                    # Try xclip first, then xsel
                    try:
                        subprocess.run(['xclip', '-selection', 'clipboard'],
                                     input=text.encode(), check=True)
                    except FileNotFoundError:
                        subprocess.run(['xsel', '--clipboard', '--input'],
                                     input=text.encode(), check=True)
                else:
                    print("Clipboard not supported on this platform", 
                          file=sys.stderr)
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("Could not copy to clipboard. Install xclip, xsel, or pyperclip",
                      file=sys.stderr)


def main():
    """Main entry point"""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
