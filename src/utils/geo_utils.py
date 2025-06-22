"""
GeoIP utilities for IP address to country mapping
"""
import geoip2.database
from typing import Optional
import os


class GeoIPManager:
    """Manages GeoIP database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self) -> None:
        """Initialize GeoIP database reader"""
        if not os.path.exists(self.db_path):
            print(f"Warning: GeoIP database not found at {self.db_path}")
            return
            
        try:
            self.reader = geoip2.database.Reader(self.db_path)
        except Exception as e:
            print(f"Warning: Could not load GeoIP database: {e}")
    
    def get_country(self, ip: str) -> str:
        """Get country code from IP address"""
        if not self.reader:
            return "Unknown"
            
        try:
            response = self.reader.country(ip)
            return response.country.iso_code or "Unknown"
        except Exception:
            return "Unknown"
    
    def close(self) -> None:
        """Close GeoIP database reader"""
        if self.reader:
            self.reader.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 