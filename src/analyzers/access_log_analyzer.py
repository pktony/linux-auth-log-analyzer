"""
Analyzer for nginx access logs
"""
from typing import List
from utils.config_utils import ConfigManager
from utils.geo_utils import GeoIPManager
from utils.file_utils import FileProcessor
from processors.access_log_processor import AccessLogProcessor
from models.access_log_models import AccessLogStats


class AccessLogAnalyzer:
    """Main analyzer class for access logs"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.geoip_manager = None
        self._initialize_geoip()
        self.processor = AccessLogProcessor(self.geoip_manager)
    
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
    
    def analyze_logs(self) -> AccessLogStats:
        """Analyze all access log files"""
        log_dir = self.config.get_log_dir()
        access_files = FileProcessor.get_log_files(log_dir, "access.log")
        
        my_ip_list = self.config.get_my_ip_list()
        exclude_countries = self.config.get_exclude_countries()
        
        for filepath in access_files:
            self.processor.process_file(filepath, my_ip_list, exclude_countries)
        
        return self.processor.get_stats()
    
    def get_ip_records(self) -> List[dict]:
        """Get detailed IP records"""
        return self.processor.get_ip_records() 