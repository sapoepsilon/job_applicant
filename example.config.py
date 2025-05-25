"""
Example configuration file for the Job Application Automation Tool.

To use this configuration:
1. Copy this file to `config.py`
2. Update the values with your personal information
3. The application will use these settings when running

Note: This file is for reference only. The actual configuration should be in `config.py`.
"""
from pathlib import Path
from typing import List, Optional
import os

# Project directory paths
PROJECT_ROOT = Path(__file__).parent
CREDENTIALS_FILE = PROJECT_ROOT / "job_credentials.csv"
TAILORED_RESUMES_PDF = PROJECT_ROOT / "tailored_resumes_pdf"
TAILORED_RESUMES_LATEX = PROJECT_ROOT / "tailored_resumes_latex"
TAILORED_RESUMES = PROJECT_ROOT / "tailored_resumes"

# Personal Information
class PersonalInfo:
    # Contact Information
    NAME = "Your Full Name"
    EMAIL = "your.email@example.com"
    PHONE = "1234567890"
    
    # Professional Profiles
    LINKEDIN = "https://www.linkedin.com/in/your-profile/"
    GITHUB = "https://github.com/yourusername"
    
    # Location
    LOCATION = "City, State, Country"
    WILLING_TO_RELOCATE = True
    
    # Preferences
    PREFERRED_NAME = "Your Preferred Name"
    
    # Demographics
    RACE_ETHNICITY = "Your Race/Ethnicity"
    IS_DISABLED = False
    IS_VETERAN = False
    
    # Account Information
    ACCOUNT_EMAIL = EMAIL  # For account creation/login
    
    # Work Authorization
    WORK_AUTHORIZED = True
    WORK_AUTHORIZATION_DETAILS = "I am authorized to work in [Country]"
    NEEDS_SPONSORSHIP = False
    VISA_STATUS = "Your Visa Status"  # e.g., "OPT", "H1B", "Green Card", "US Citizen", etc.
    
    @classmethod
    def get_formatted_info(cls) -> str:
        """Return personal information in a formatted string for prompts."""
        return f"""
PERSONAL INFORMATION:
- Name: {cls.NAME}
- Email: {cls.EMAIL}
- Phone: {cls.PHONE}
- Race/Ethnicity: {cls.RACE_ETHNICITY}
- LinkedIn: {cls.LINKEDIN}
- GitHub: {cls.GITHUB}
- Disabled: {'Yes' if cls.IS_DISABLED else 'No'}
- Veteran: {'Yes' if cls.IS_VETERAN else 'No'}
- Location: {cls.LOCATION}
- Willing to relocate: {'Yes' if cls.WILLING_TO_RELOCATE else 'No'}
- Preferred name: {cls.PREFERRED_NAME}
- Work Authorization: {cls.WORK_AUTHORIZATION_DETAILS}
- Visa Status: {cls.VISA_STATUS if cls.WORK_AUTHORIZED else 'Not authorized to work'}
- Requires Sponsorship: {'Yes' if cls.NEEDS_SPONSORSHIP else 'No'}
""".strip()
    
    @classmethod
    def get_work_authorization_statement(cls) -> str:
        """Return a formatted string about work authorization status."""
        if cls.WORK_AUTHORIZED:
            auth_status = cls.WORK_AUTHORIZATION_DETAILS
            if cls.NEEDS_SPONSORSHIP:
                return f"{auth_status}, but will need sponsorship in the future"
            return auth_status
        return "Not authorized to work"

# Playwright MCP Configuration
class PlaywrightConfig:
    # Browser configuration
    BROWSER: str = "chromium"  # Options: "chromium", "firefox", "webkit", "msedge"
    HEADLESS: bool = False
    DEVICE: Optional[str] = None  # e.g., "iPhone 15"
    VIEWPORT_SIZE: Optional[str] = None  # e.g., "1280,720"
    USER_AGENT: Optional[str] = None
    
    # User data and profiles
    USER_DATA_DIR: Optional[str] = os.path.expanduser(
        "~/.config/ms-playwright/chromium"
    )
    STORAGE_STATE: Optional[str] = None  # Path to storage state file
    
    # Network settings
    PROXY_SERVER: Optional[str] = None
    PROXY_BYPASS: Optional[str] = None
    IGNORE_HTTPS_ERRORS: bool = False
    
    # Security settings
    NO_SANDBOX: bool = True
    ALLOWED_ORIGINS: List[str] = []
    BLOCKED_ORIGINS: List[str] = []
    BLOCK_SERVICE_WORKERS: bool = False
    
    # Performance settings
    NO_IMAGE_RESPONSES: bool = False
    
    # Output settings
    OUTPUT_DIR: Optional[str] = None  # Directory for output files
    SAVE_TRACE: bool = False  # Whether to save Playwright Trace
    
    # Capabilities
    CAPABILITIES: List[str] = [
        "tabs", "pdf", "history", "wait", "files", "install"
    ]
    
    @classmethod
    def get_mcp_args(cls) -> list:
        """Convert configuration to MCP command line arguments."""
        args = ["-y", "@playwright/mcp@latest"]
        
        if cls.NO_SANDBOX:
            args.append("--no-sandbox")
            
        if cls.USER_DATA_DIR:
            args.extend(["--user-data-dir", str(Path(cls.USER_DATA_DIR).expanduser())])
            
        if cls.HEADLESS:
            args.append("--headless")
            
        if cls.DEVICE:
            args.extend(["--device", cls.DEVICE])
            
        if cls.VIEWPORT_SIZE:
            args.extend(["--viewport-size", cls.VIEWPORT_SIZE])
            
        if cls.USER_AGENT:
            args.extend(["--user-agent", f'"{cls.USER_AGENT}"'])
            
        if cls.PROXY_SERVER:
            args.extend(["--proxy-server", cls.PROXY_SERVER])
            
        if cls.PROXY_BYPASS:
            args.extend(["--proxy-bypass", cls.PROXY_BYPASS])
            
        if cls.IGNORE_HTTPS_ERRORS:
            args.append("--ignore-https-errors")
            
        if cls.ALLOWED_ORIGINS:
            args.extend(["--allowed-origins", ";".join(cls.ALLOWED_ORIGINS)])
            
        if cls.BLOCKED_ORIGINS:
            args.extend(["--blocked-origins", ";".join(cls.BLOCKED_ORIGINS)])
            
        if cls.BLOCK_SERVICE_WORKERS:
            args.append("--block-service-workers")
            
        if cls.NO_IMAGE_RESPONSES:
            args.append("--no-image-responses")
            
        if cls.OUTPUT_DIR:
            args.extend(["--output-dir", str(Path(cls.OUTPUT_DIR).expanduser())])
            
        if cls.SAVE_TRACE:
            args.append("--save-trace")
            
        if cls.CAPABILITIES:
            args.extend(["--caps", ",".join(cls.CAPABILITIES)])
            
        return args

# Terminal controller configuration
class TerminalConfig:
    COMMAND = "npx"
    ARGS = ["-y", "@wonderwhy-er/desktop-commander@latest"]
    ENV = None
