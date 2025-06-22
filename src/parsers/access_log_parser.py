"""
Parser for nginx access logs
"""
import re
from datetime import datetime
from typing import Optional
from models.access_log_models import AccessLogEntry


class AccessLogParser:
    """Parses nginx access log entries"""
    
    # Regular expressions for parsing access logs
    LOG_PATTERN = re.compile(r'^(\d+\.\d+\.\d+\.\d+) - - \[(\d{2}/\w{3}/\d{4})')
    LOG_PATTERN_FULL = re.compile(
        r'^(\d+\.\d+\.\d+\.\d+) - - \[(\d{2}/\w{3}/\d{4}):[^\]]+\] "(\w+) ([^ ]+) [^\"]+" (\d{3})'
    )
    
    @staticmethod
    def parse_timestamp(date_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        try:
            return datetime.strptime(date_str, "%d/%b/%Y")
        except ValueError:
            return None
    
    @staticmethod
    def parse_access_line(line: str) -> Optional[AccessLogEntry]:
        """Parse a single access log line"""
        if not line.strip():
            return None
            
        # Try full pattern first
        match = AccessLogParser.LOG_PATTERN_FULL.match(line)
        if match:
            ip, date_str, method, url, status_code = match.groups()
            timestamp = AccessLogParser.parse_timestamp(date_str)
            if not timestamp:
                return None
                
            return AccessLogEntry(
                ip=ip,
                timestamp=timestamp,
                method=method,
                url=url,
                status_code=status_code,
                country="Unknown",  # Will be set later
                date=date_str,  # Keep original format
                hour=timestamp.hour
            )
        
        # Try basic pattern
        match = AccessLogParser.LOG_PATTERN.match(line)
        if match:
            ip, date_str = match.groups()
            timestamp = AccessLogParser.parse_timestamp(date_str)
            if not timestamp:
                return None
                
            return AccessLogEntry(
                ip=ip,
                timestamp=timestamp,
                method="UNKNOWN",
                url="/",
                status_code="000",
                country="Unknown",  # Will be set later
                date=date_str,  # Keep original format
                hour=timestamp.hour
            )
        
        return None 