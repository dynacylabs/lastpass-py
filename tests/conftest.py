"""
Pytest configuration and fixtures
"""

import os
import pytest
from pathlib import Path
from typing import Dict, Any


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live API tests (requires valid LastPass credentials)"
    )
    parser.addoption(
        "--username",
        action="store",
        default=os.environ.get("LASTPASS_USERNAME", ""),
        help="LastPass username for live tests"
    )
    parser.addoption(
        "--password",
        action="store",
        default=os.environ.get("LASTPASS_PASSWORD", ""),
        help="LastPass password for live tests"
    )
    parser.addoption(
        "--otp",
        action="store",
        default=os.environ.get("LASTPASS_OTP", ""),
        help="LastPass OTP/verification code for email verification"
    )


def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "live: mark test as requiring live API connection"
    )
    config.addinivalue_line(
        "markers", "mock: mark test as using mocked responses (default)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip live tests unless --live flag is provided"""
    if config.getoption("--live"):
        # Running with --live, skip nothing
        return
    
    skip_live = pytest.mark.skip(reason="need --live option to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory"""
    config_dir = tmp_path / ".lpass"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def live_mode(request):
    """Check if we're in live mode"""
    return request.config.getoption("--live")


@pytest.fixture
def live_credentials(request) -> Dict[str, str]:
    """Get credentials for live testing"""
    return {
        "username": request.config.getoption("--username"),
        "password": request.config.getoption("--password"),
        "otp": request.config.getoption("--otp"),
    }


@pytest.fixture
def mock_encryption_key():
    """Standard encryption key for testing"""
    return b"0123456789abcdef0123456789abcdef"  # 32 bytes


@pytest.fixture
def mock_iterations():
    """Standard iteration count for testing"""
    return 5000


def get_otp_message():
    """Get message to display when email verification is required"""
    return (
        "\n" + "="*70 + "\n"
        "EMAIL VERIFICATION REQUIRED\n"
        "="*70 + "\n"
        "LastPass has sent a verification email to your address.\n"
        "Please check your email and re-run tests with --otp option:\n"
        "\n"
        "  ./run_tests.sh --live --username=<email> --password=<pwd> --otp=<code>\n"
        "\n"
        "Or set environment variable:\n"
        "  export LASTPASS_OTP=<code>\n"
        "="*70
    )
