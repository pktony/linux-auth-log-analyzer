"""
Data models for access log analysis
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AccessLogEntry:
    """Access log entry data structure"""
    ip: str
    timestamp: datetime
    method: str
    url: str
    status_code: str
    country: str
    date: str
    hour: int


@dataclass
class AccessLogStats:
    """Access log statistics data structure"""
    total_requests: int
    requests_by_country: dict
    requests_by_hour: dict
    requests_by_date: dict
    requests_by_status: dict
    requests_by_method: dict 