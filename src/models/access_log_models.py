"""
Data models for access log analysis
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List
from collections import Counter


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
class SuccessfulRequestEntry:
    """Successful request entry data structure"""
    ip: str
    timestamp: datetime
    method: str
    url: str
    status_code: str
    country: str
    date: str
    hour: int
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    response_size: Optional[int] = None


@dataclass
class SuccessfulRequestStats:
    """Successful request statistics data structure"""
    total_successful_requests: int
    unique_ips: int
    successful_requests_by_country: Dict[str, int]
    successful_requests_by_date: Dict[str, int]
    successful_requests_by_hour: Dict[int, int]
    successful_requests_by_method: Dict[str, int]
    successful_requests_by_url: Dict[str, int]
    top_successful_countries: List[str]
    top_successful_urls: List[str]
    successful_requests_details: List[SuccessfulRequestEntry]


@dataclass
class AccessLogStats:
    """Access log statistics data structure"""
    weekly_stats: Dict[str, Counter]
    total_unique_ips: int
    total_requests: int
    top_countries: List[str]
    requests_by_country: Dict[str, int]
    requests_by_hour: Dict[int, int]
    requests_by_date: Dict[str, int]
    requests_by_status: Dict[str, int]
    requests_by_method: Dict[str, int] 