"""
Analyzer for nginx error logs
"""
from utils.config_utils import ConfigManager
from utils.geo_utils import GeoIPManager
from utils.file_utils import FileProcessor
from processors.error_log_processor import ErrorLogProcessor
from models.error_log_models import ErrorLogStats


class ErrorLogAnalyzer:
    """Main analyzer class for error logs"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.geoip_manager = None
        self._initialize_geoip()
        self.processor = ErrorLogProcessor(self.geoip_manager)
    
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
    
    def analyze_logs(self) -> ErrorLogStats:
        """Analyze all error log files"""
        log_dir = self.config.get_log_dir()
        error_files = FileProcessor.get_log_files(log_dir, "error.log")
        
        for filepath in error_files:
            self.processor.process_file(filepath)
        
        return self.processor.get_stats() 