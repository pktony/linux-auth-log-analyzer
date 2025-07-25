"""
Processor for nginx access logs
"""
from collections import defaultdict, Counter
from typing import List, Optional
from datetime import datetime
from models.access_log_models import AccessLogEntry, AccessLogStats
from parsers.access_log_parser import AccessLogParser
from utils.file_utils import FileProcessor
from utils.geo_utils import GeoIPManager


class AccessLogProcessor:
    """Processes access log files and generates statistics"""
    
    def __init__(self, geoip_manager: Optional[GeoIPManager] = None):
        self.geoip_manager = geoip_manager
        self.weekly_stats = defaultdict(Counter)
        self.unique_ips = set()
        self.stats = AccessLogStats(
            weekly_stats=self.weekly_stats,
            total_unique_ips=0,
            total_requests=0,
            top_countries=[],
            requests_by_country=defaultdict(int),
            requests_by_hour=defaultdict(int),
            requests_by_date=defaultdict(int),
            requests_by_status=defaultdict(int),
            requests_by_method=defaultdict(int)
        )
        self.ip_records = []
    
    def process_file(self, filepath: str, my_ip_list: Optional[List[str]] = None, 
                    exclude_countries: Optional[List[str]] = None) -> None:
        """Process a single access log file"""
        def line_processor(line: str) -> None:
            self._process_line(line, my_ip_list, exclude_countries)
        
        FileProcessor.process_log_file(filepath, line_processor)
    
    def _process_line(self, line: str, my_ip_list: Optional[List[str]] = None,
                     exclude_countries: Optional[List[str]] = None) -> None:
        """Process a single log line"""
        entry = AccessLogParser.parse_access_line(line)
        if not entry:
            return
        
        # Skip my IP addresses
        if my_ip_list and entry.ip in my_ip_list:
            return
        
        # Get country information
        if self.geoip_manager:
            entry.country = self.geoip_manager.get_country(entry.ip)
        
        # Skip excluded countries
        if exclude_countries and entry.country in exclude_countries:
            return
        
        self._update_stats(entry)
        self._add_ip_record(entry)
    
    def _update_stats(self, entry: AccessLogEntry) -> None:
        """Update statistics with access log entry"""
        self.stats.total_requests += 1
        self.unique_ips.add(entry.ip)
        
        # Update weekly stats
        try:
            dt = datetime.strptime(entry.date, "%d/%b/%Y")
            week_key = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
            self.weekly_stats[week_key][entry.country] += 1
        except Exception:
            week_key = "Unknown"
            self.weekly_stats[week_key][entry.country] += 1
        
        self.stats.requests_by_country[entry.country] += 1
        self.stats.requests_by_hour[entry.hour] += 1
        self.stats.requests_by_date[entry.date] += 1
        self.stats.requests_by_status[entry.status_code] += 1
        self.stats.requests_by_method[entry.method] += 1
    
    def _add_ip_record(self, entry: AccessLogEntry) -> None:
        """Add IP record for detailed analysis"""
        self.ip_records.append({
            'ip': entry.ip,
            'country': entry.country,
            'date': entry.date,
            'http_code': entry.status_code,
            'method': entry.method,
            'query': entry.url
        })
    
    def get_stats(self) -> AccessLogStats:
        """Get processed statistics"""
        # Update final stats
        self.stats.total_unique_ips = len(self.unique_ips)
        self.stats.weekly_stats = dict(self.weekly_stats)
        
        # Calculate top countries
        country_counter = Counter(self.stats.requests_by_country)
        self.stats.top_countries = [country for country, _ in country_counter.most_common(10)]
        
        return self.stats
    
    def get_ip_records(self) -> List[dict]:
        """Get IP records for detailed analysis"""
        return self.ip_records 