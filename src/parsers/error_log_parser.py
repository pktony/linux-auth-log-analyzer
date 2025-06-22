"""
Parser for nginx error logs
"""
import re
from datetime import datetime
from typing import Optional, Tuple
from models.error_log_models import ErrorLogEntry


class ErrorLogParser:
    """Parses nginx error log entries"""
    
    # Enhanced error log pattern to extract more information
    ERROR_LOG_PATTERN = re.compile(
        r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (\d+)#(\d+): \*(\d+) (.+?), client: ([\d\.]+), server: ([^,]+), request: "([^"]+)", host: "([^"]+)"(?:, referrer: "([^"]+)")?$'
    )
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        try:
            return datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None
    
    @staticmethod
    def extract_error_type(message: str) -> str:
        """Extract error type from error message"""
        if "directory index" in message:
            return "Directory Index Forbidden"
        elif "client intended to send too large body" in message:
            return "Request Body Too Large"
        elif "connection refused" in message:
            return "Connection Refused"
        elif "timeout" in message:
            return "Timeout"
        elif "not found" in message:
            return "Not Found"
        else:
            return "Other"
    
    @staticmethod
    def parse_request(request: str) -> Tuple[str, str]:
        """Parse HTTP request to extract method and URL path"""
        parts = request.split(' ')
        if len(parts) >= 2:
            return parts[0], parts[1]
        return "UNKNOWN", "/"
    
    @staticmethod
    def parse_error_line(line: str, geoip_manager=None) -> Optional[ErrorLogEntry]:
        """Parse a single error log line with enhanced information"""
        if not line.strip():
            return None
            
        match = ErrorLogParser.ERROR_LOG_PATTERN.match(line)
        if not match:
            return None
            
        (timestamp_str, level, pid, tid, client_id, message, 
         client_ip, server, request, host, referrer) = match.groups()
        
        timestamp = ErrorLogParser.parse_timestamp(timestamp_str)
        if not timestamp:
            return None
        
        # Extract country information
        country = "Unknown"
        if geoip_manager:
            country = geoip_manager.get_country(client_ip)
        
        # Parse request details
        http_method, url_path = ErrorLogParser.parse_request(request)
        
        # Extract error type
        error_type = ErrorLogParser.extract_error_type(message)
        
        return ErrorLogEntry(
            timestamp=timestamp,
            level=level,
            pid=int(pid),
            tid=int(tid),
            client_id=int(client_id),
            message=message,
            client_ip=client_ip,
            server=server,
            request=request,
            host=host,
            referrer=referrer,
            date=timestamp.strftime("%Y-%m-%d"),
            hour=timestamp.hour,
            country=country,
            error_type=error_type,
            url_path=url_path,
            http_method=http_method
        ) 