"""
Processor for nginx error logs
"""
from collections import defaultdict, Counter
from typing import Optional
from models.error_log_models import ErrorLogEntry, ErrorLogStats
from parsers.error_log_parser import ErrorLogParser
from utils.file_utils import FileProcessor
from utils.geo_utils import GeoIPManager


class ErrorLogProcessor:
    """Processes error log files and generates statistics"""
    
    def __init__(self, geoip_manager: Optional[GeoIPManager] = None):
        self.geoip_manager = geoip_manager
        self.stats = ErrorLogStats(
            total_errors=0,
            errors_by_level=defaultdict(int),
            errors_by_hour=defaultdict(int),
            errors_by_date=defaultdict(int),
            top_error_messages=defaultdict(int),
            errors_by_pid=defaultdict(int),
            errors_by_country=defaultdict(int),
            errors_by_ip=defaultdict(int),
            errors_by_url=defaultdict(int),
            errors_by_method=defaultdict(int),
            errors_by_error_type=defaultdict(int)
        )
    
    def process_file(self, filepath: str) -> None:
        """Process a single error log file"""
        def line_processor(line: str) -> None:
            self._process_line(line)
        
        FileProcessor.process_log_file(filepath, line_processor)
    
    def _process_line(self, line: str) -> None:
        """Process a single log line"""
        entry = ErrorLogParser.parse_error_line(line, self.geoip_manager)
        if not entry:
            return
            
        self._update_stats(entry)
    
    def _update_stats(self, entry: ErrorLogEntry) -> None:
        """Update statistics with error log entry"""
        self.stats.total_errors += 1
        self.stats.errors_by_level[entry.level] += 1
        self.stats.errors_by_hour[entry.hour] += 1
        self.stats.errors_by_date[entry.date] += 1
        self.stats.top_error_messages[entry.message] += 1
        self.stats.errors_by_pid[entry.pid] += 1
        self.stats.errors_by_country[entry.country] += 1
        self.stats.errors_by_ip[entry.client_ip] += 1
        self.stats.errors_by_url[entry.url_path] += 1
        self.stats.errors_by_method[entry.http_method] += 1
        self.stats.errors_by_error_type[entry.error_type] += 1
    
    def get_stats(self) -> ErrorLogStats:
        """Get processed statistics"""
        return self.stats 