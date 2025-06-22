"""
Configuration utilities for environment variables and settings
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration settings from environment variables"""
    
    def __init__(self, env_path: Optional[str] = None):
        self.env_path = env_path or self._find_env_file()
        self._load_env()
    
    def _find_env_file(self) -> Optional[str]:
        """Find .env file in project root"""
        current_dir = Path(__file__).parent.parent.parent
        env_path = current_dir / '.env'
        return str(env_path) if env_path.exists() else None
    
    def _load_env(self) -> None:
        """Load environment variables from .env file"""
        if self.env_path and os.path.exists(self.env_path):
            load_dotenv(dotenv_path=self.env_path)
    
    def get_my_ip_list(self) -> List[str]:
        """Get list of my IP addresses from environment"""
        ip_str = os.getenv('MY_IP')
        if not ip_str:
            return []
        return [ip.strip() for ip in ip_str.split(',') if ip.strip()]
    
    def get_exclude_countries(self) -> List[str]:
        """Get list of countries to exclude from environment"""
        country_str = os.getenv('EXCLUDE_COUNTRIES')
        if not country_str:
            return []
        return [c.strip().upper() for c in country_str.split(',') if c.strip()]
    
    def get_log_dir(self) -> str:
        """Get log directory path"""
        return os.getenv('LOG_DIR', 'logs')
    
    def get_geoip_db_path(self) -> str:
        """Get GeoIP database path"""
        return os.getenv('GEOIP_DB', 'src/GeoLite2-Country.mmdb') 