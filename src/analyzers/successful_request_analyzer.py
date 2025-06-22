"""
Analyzer for successful requests in nginx access logs
"""
from typing import List, Dict, Optional
from collections import Counter
from datetime import datetime
from utils.config_utils import ConfigManager
from utils.geo_utils import GeoIPManager
from utils.file_utils import FileProcessor
from processors.access_log_processor import AccessLogProcessor
from models.access_log_models import SuccessfulRequestStats, SuccessfulRequestEntry


class SuccessfulRequestAnalyzer:
    """Analyzer for successful requests (status codes 200-299)"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.geoip_manager = None
        self._initialize_geoip()
        self.processor = AccessLogProcessor(self.geoip_manager)
        self.successful_requests: List[SuccessfulRequestEntry] = []
    
    def _initialize_geoip(self) -> None:
        """Initialize GeoIP manager"""
        try:
            db_path = self.config.get_geoip_db_path()
            self.geoip_manager = GeoIPManager(db_path)
        except Exception as e:
            print(f"Warning: Could not initialize GeoIP manager: {e}")
    
    def __del__(self):
        """Cleanup GeoIP manager"""
        if self.geoip_manager:
            self.geoip_manager.close()
    
    def _is_successful_request(self, status_code: str) -> bool:
        """Check if the status code indicates a successful request"""
        try:
            code = int(status_code)
            return 200 <= code < 300
        except (ValueError, TypeError):
            return False
    
    def _parse_log_line(self, line: str) -> Optional[SuccessfulRequestEntry]:
        """Parse a single log line and extract successful request data"""
        if not line.strip():
            return None
        
        try:
            # Basic nginx log format parsing
            parts = line.split()
            if len(parts) < 12:
                return None
            
            # Extract basic fields
            ip = parts[0]
            timestamp_str = f"{parts[3]} {parts[4]}"
            method = parts[5].strip('"')
            url = parts[6]
            status_code = parts[8]
            
            # Check if it's a successful request
            if not self._is_successful_request(status_code):
                return None
            
            # Parse timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, '[%d/%b/%Y:%H:%M:%S %z]')
            except ValueError:
                return None
            
            # Extract country
            country = "Unknown"
            if self.geoip_manager:
                country = self.geoip_manager.get_country(ip)
            
            # Extract additional fields if available
            user_agent = None
            referer = None
            response_size = None
            
            # Try to extract user agent and referer
            for i, part in enumerate(parts):
                if part.startswith('"') and 'Mozilla' in part:
                    user_agent = part.strip('"')
                elif part.startswith('"') and ('http://' in part or 'https://' in part):
                    referer = part.strip('"')
            
            # Try to extract response size (usually the last field)
            try:
                response_size = int(parts[-1])
            except (ValueError, IndexError):
                pass
            
            return SuccessfulRequestEntry(
                ip=ip,
                timestamp=timestamp,
                method=method,
                url=url,
                status_code=status_code,
                country=country,
                date=timestamp.strftime('%Y-%m-%d'),
                hour=timestamp.hour,
                user_agent=user_agent,
                referer=referer,
                response_size=response_size
            )
            
        except Exception as e:
            print(f"Error parsing log line: {e}")
            return None
    
    def analyze_logs(self) -> SuccessfulRequestStats:
        """Analyze all access log files for successful requests"""
        log_dir = self.config.get_log_dir()
        access_files = FileProcessor.get_log_files(log_dir, "access.log")
        
        my_ip_list = self.config.get_my_ip_list()
        exclude_countries = self.config.get_exclude_countries()
        
        print("분석 중인 성공 요청들...")
        
        for filepath in access_files:
            print(f"처리 중: {filepath}")
            self._process_file(filepath, my_ip_list, exclude_countries)
        
        return self._generate_stats()
    
    def _process_file(self, filepath: str, my_ip_list: List[str], exclude_countries: List[str]) -> None:
        """Process a single log file for successful requests"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    entry = self._parse_log_line(line)
                    if entry:
                        # Skip my own IPs
                        if entry.ip in my_ip_list:
                            continue
                        
                        # Skip excluded countries
                        if entry.country in exclude_countries:
                            continue
                        
                        self.successful_requests.append(entry)
                        
                        if line_num % 10000 == 0:
                            print(f"  처리된 라인: {line_num}")
                            
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
    
    def _generate_stats(self) -> SuccessfulRequestStats:
        """Generate statistics from collected successful requests"""
        if not self.successful_requests:
            return SuccessfulRequestStats(
                total_successful_requests=0,
                unique_ips=0,
                successful_requests_by_country={},
                successful_requests_by_date={},
                successful_requests_by_hour={},
                successful_requests_by_method={},
                successful_requests_by_url={},
                top_successful_countries=[],
                top_successful_urls=[],
                successful_requests_details=[]
            )
        
        # Count unique IPs
        unique_ips = len(set(req.ip for req in self.successful_requests))
        
        # Count by country
        country_counts = Counter(req.country for req in self.successful_requests)
        top_countries = [country for country, _ in country_counts.most_common(10)]
        
        # Count by date
        date_counts = Counter(req.date for req in self.successful_requests)
        
        # Count by hour
        hour_counts = Counter(req.hour for req in self.successful_requests)
        
        # Count by method
        method_counts = Counter(req.method for req in self.successful_requests)
        
        # Count by URL
        url_counts = Counter(req.url for req in self.successful_requests)
        top_urls = [url for url, _ in url_counts.most_common(10)]
        
        return SuccessfulRequestStats(
            total_successful_requests=len(self.successful_requests),
            unique_ips=unique_ips,
            successful_requests_by_country=dict(country_counts),
            successful_requests_by_date=dict(date_counts),
            successful_requests_by_hour=dict(hour_counts),
            successful_requests_by_method=dict(method_counts),
            successful_requests_by_url=dict(url_counts),
            top_successful_countries=top_countries,
            top_successful_urls=top_urls,
            successful_requests_details=self.successful_requests
        )
    
    def get_detailed_records(self) -> List[Dict]:
        """Get detailed records of successful requests for CSV export"""
        records = []
        for req in self.successful_requests:
            records.append({
                'ip': req.ip,
                'timestamp': req.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'method': req.method,
                'url': req.url,
                'status_code': req.status_code,
                'country': req.country,
                'date': req.date,
                'hour': req.hour,
                'user_agent': req.user_agent or '',
                'referer': req.referer or '',
                'response_size': req.response_size or 0
            })
        return records 