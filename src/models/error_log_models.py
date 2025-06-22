"""
Data models for error log analysis
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ErrorLogEntry:
    """Error log entry data structure"""
    timestamp: datetime
    level: str
    pid: int
    tid: int
    client_id: int
    message: str
    client_ip: str
    server: str
    request: str
    host: str
    referrer: Optional[str]
    date: str
    hour: int
    country: str
    error_type: str
    url_path: str
    http_method: str


@dataclass
class ErrorLogStats:
    """Error log statistics data structure"""
    total_errors: int
    errors_by_level: dict
    errors_by_hour: dict
    errors_by_date: dict
    top_error_messages: dict
    errors_by_pid: dict
    errors_by_country: dict
    errors_by_ip: dict
    errors_by_url: dict
    errors_by_method: dict
    errors_by_error_type: dict 