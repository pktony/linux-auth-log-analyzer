import os
import re
import gzip
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from dotenv import load_dotenv
import geoip2.database

# Configuration
LOG_DIR = "logs"
GEOIP_DB = "src/GeoLite2-Country.mmdb"

# Enhanced error log pattern to extract more information
ERROR_LOG_PATTERN = re.compile(
    r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (\d+)#(\d+): \*(\d+) (.+?), client: ([\d\.]+), server: ([^,]+), request: "([^"]+)", host: "([^"]+)"(?:, referrer: "([^"]+)")?$'
)

@dataclass
class ErrorLogEntry:
    """Enhanced error log entry data structure"""
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
class ErrorStats:
    """Enhanced error statistics data structure"""
    total_errors: int
    errors_by_level: Counter
    errors_by_hour: Counter
    errors_by_date: Counter
    top_error_messages: Counter
    errors_by_pid: Counter
    errors_by_country: Counter
    errors_by_ip: Counter
    errors_by_url: Counter
    errors_by_method: Counter
    errors_by_error_type: Counter

class ErrorLogParser:
    """Responsible for parsing error log files"""
    
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
    def get_country(ip: str, reader) -> str:
        """Get country from IP address"""
        try:
            response = reader.country(ip)
            return response.country.iso_code or "Unknown"
        except Exception:
            return "Unknown"
    
    @staticmethod
    def parse_error_line(line: str, reader=None) -> Optional[ErrorLogEntry]:
        """Parse a single error log line with enhanced information"""
        if not line.strip():
            return None
            
        match = ERROR_LOG_PATTERN.match(line)
        if not match:
            return None
            
        (timestamp_str, level, pid, tid, client_id, message, 
         client_ip, server, request, host, referrer) = match.groups()
        
        timestamp = ErrorLogParser.parse_timestamp(timestamp_str)
        if not timestamp:
            return None
        
        # Extract country information
        country = "Unknown"
        if reader:
            country = ErrorLogParser.get_country(client_ip, reader)
        
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

class ErrorLogProcessor:
    """Responsible for processing error log files"""
    
    def __init__(self, geoip_reader=None):
        self.stats = ErrorStats(
            total_errors=0,
            errors_by_level=Counter(),
            errors_by_hour=Counter(),
            errors_by_date=Counter(),
            top_error_messages=Counter(),
            errors_by_pid=Counter(),
            errors_by_country=Counter(),
            errors_by_ip=Counter(),
            errors_by_url=Counter(),
            errors_by_method=Counter(),
            errors_by_error_type=Counter()
        )
        self.geoip_reader = geoip_reader
    
    def process_file(self, filepath: str) -> None:
        """Process a single error log file"""
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return
            
        open_func = gzip.open if filepath.endswith('.gz') else open
        
        try:
            with open_func(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    self._process_line(line)
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
    
    def _process_line(self, line: str) -> None:
        """Process a single log line"""
        entry = ErrorLogParser.parse_error_line(line, self.geoip_reader)
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

class ErrorLogAnalyzer:
    """Main analyzer class that orchestrates the analysis"""
    
    def __init__(self):
        self.geoip_reader = None
        try:
            self.geoip_reader = geoip2.database.Reader(GEOIP_DB)
        except Exception as e:
            print(f"Warning: Could not load GeoIP database: {e}")
        
        self.processor = ErrorLogProcessor(self.geoip_reader)
    
    def __del__(self):
        """Cleanup GeoIP reader"""
        if self.geoip_reader:
            self.geoip_reader.close()
    
    def analyze_logs(self) -> ErrorStats:
        """Analyze all error log files"""
        error_files = self._get_error_log_files()
        
        for filepath in error_files:
            self.processor.process_file(filepath)
        
        return self.processor.stats
    
    def _get_error_log_files(self) -> List[str]:
        """Get list of error log files to process"""
        if not os.path.exists(LOG_DIR):
            return []
            
        files = []
        for fname in os.listdir(LOG_DIR):
            if fname.startswith("error.log"):
                files.append(os.path.join(LOG_DIR, fname))
        
        return sorted(files)

class ErrorLogVisualizer:
    """Responsible for creating visualizations of error statistics"""
    
    @staticmethod
    def plot_error_levels(stats: ErrorStats, save_path: Optional[str] = None) -> None:
        """Plot error distribution by level"""
        if not stats.errors_by_level:
            print("No error level data to plot")
            return
            
        plt.figure(figsize=(10, 6))
        levels = list(stats.errors_by_level.keys())
        counts = list(stats.errors_by_level.values())
        
        plt.bar(levels, counts, color='red', alpha=0.7)
        plt.title('Error Distribution by Level')
        plt.xlabel('Error Level')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        
        for i, count in enumerate(counts):
            plt.text(i, count + max(counts) * 0.01, str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(f"{save_path}_levels.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_country_distribution(stats: ErrorStats, save_path: Optional[str] = None) -> None:
        """Plot error distribution by country"""
        if not stats.errors_by_country:
            print("No country data to plot")
            return
            
        # Get top 10 countries
        top_countries = dict(stats.errors_by_country.most_common(10))
        
        plt.figure(figsize=(12, 8))
        countries = list(top_countries.keys())
        counts = list(top_countries.values())
        
        plt.barh(countries, counts, color='orange', alpha=0.7)
        plt.title('Error Distribution by Country (Top 10)')
        plt.xlabel('Error Count')
        plt.ylabel('Country')
        
        for i, count in enumerate(counts):
            plt.text(count + max(counts) * 0.01, i, str(count), va='center')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(f"{save_path}_countries.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_error_types(stats: ErrorStats, save_path: Optional[str] = None) -> None:
        """Plot error distribution by error type"""
        if not stats.errors_by_error_type:
            print("No error type data to plot")
            return
            
        plt.figure(figsize=(12, 8))
        error_types = list(stats.errors_by_error_type.keys())
        counts = list(stats.errors_by_error_type.values())
        
        plt.pie(counts, labels=error_types, autopct='%1.1f%%', startangle=90)
        plt.title('Error Distribution by Type')
        plt.axis('equal')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(f"{save_path}_error_types.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_hourly_distribution(stats: ErrorStats, save_path: Optional[str] = None) -> None:
        """Plot error distribution by hour"""
        if not stats.errors_by_hour:
            print("No hourly data to plot")
            return
            
        plt.figure(figsize=(12, 6))
        hours = sorted(stats.errors_by_hour.keys())
        counts = [stats.errors_by_hour[hour] for hour in hours]
        
        plt.plot(hours, counts, marker='o', linewidth=2, markersize=6, color='red')
        plt.fill_between(hours, counts, alpha=0.3, color='red')
        plt.title('Error Distribution by Hour of Day')
        plt.xlabel('Hour')
        plt.ylabel('Error Count')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24))
        
        plt.tight_layout()
        if save_path:
            plt.savefig(f"{save_path}_hourly.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_daily_trend(stats: ErrorStats, save_path: Optional[str] = None) -> None:
        """Plot error trend by date"""
        if not stats.errors_by_date:
            print("No daily data to plot")
            return
            
        plt.figure(figsize=(14, 6))
        dates = sorted(stats.errors_by_date.keys())
        counts = [stats.errors_by_date[date] for date in dates]
        
        plt.plot(dates, counts, marker='o', linewidth=2, markersize=4, color='red')
        plt.title('Error Trend by Date')
        plt.xlabel('Date')
        plt.ylabel('Error Count')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Show every nth date label to avoid overcrowding
        n = max(1, len(dates) // 10)
        plt.xticks(dates[::n])
        
        plt.tight_layout()
        if save_path:
            plt.savefig(f"{save_path}_daily.png", dpi=150, bbox_inches='tight')
        plt.show()

class ErrorLogReporter:
    """Responsible for generating reports from error statistics"""
    
    @staticmethod
    def print_summary(stats: ErrorStats) -> None:
        """Print comprehensive summary of error statistics"""
        print("=" * 80)
        print("NGINX ERROR LOG ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total Errors: {stats.total_errors:,}")
        print()
        
        print("Errors by Level:")
        for level, count in stats.errors_by_level.most_common():
            percentage = (count / stats.total_errors) * 100
            print(f"  {level}: {count:,} ({percentage:.1f}%)")
        print()
        
        print("Errors by Type:")
        for error_type, count in stats.errors_by_error_type.most_common():
            percentage = (count / stats.total_errors) * 100
            print(f"  {error_type}: {count:,} ({percentage:.1f}%)")
        print()
        
        print("Top 10 Countries by Error Count:")
        for country, count in stats.errors_by_country.most_common(10):
            percentage = (count / stats.total_errors) * 100
            print(f"  {country}: {count:,} ({percentage:.1f}%)")
        print()
        
        print("Top 10 IP Addresses by Error Count:")
        for ip, count in stats.errors_by_ip.most_common(10):
            percentage = (count / stats.total_errors) * 100
            print(f"  {ip}: {count:,} ({percentage:.1f}%)")
        print()
        
        print("Top 10 Error Messages:")
        for message, count in stats.top_error_messages.most_common(10):
            print(f"  {count:,}: {message[:80]}{'...' if len(message) > 80 else ''}")
        print()
        
        print("Top 10 URLs with Errors:")
        for url, count in stats.errors_by_url.most_common(10):
            percentage = (count / stats.total_errors) * 100
            print(f"  {url}: {count:,} ({percentage:.1f}%)")
        print()
        
        print("HTTP Methods with Errors:")
        for method, count in stats.errors_by_method.most_common():
            percentage = (count / stats.total_errors) * 100
            print(f"  {method}: {count:,} ({percentage:.1f}%)")
        print()
        
        print("Errors by Process ID:")
        for pid, count in stats.errors_by_pid.most_common(5):
            print(f"  PID {pid}: {count:,}")
        print()
        
        if stats.errors_by_date:
            print("Date Range:")
            dates = sorted(stats.errors_by_date.keys())
            print(f"  From: {dates[0]}")
            print(f"  To: {dates[-1]}")
            print(f"  Days with errors: {len(dates)}")
    
    @staticmethod
    def save_detailed_report(stats: ErrorStats, filename: str = "error_stats.csv") -> None:
        """Save detailed error statistics to CSV"""
        if not stats.errors_by_date:
            print("No data to save")
            return
            
        # Create detailed report data
        report_data = []
        for date in sorted(stats.errors_by_date.keys()):
            report_data.append({
                'date': date,
                'error_count': stats.errors_by_date[date]
            })
        
        df = pd.DataFrame(report_data)
        df.to_csv(filename, index=False)
        print(f"Detailed error statistics saved to {filename}")
    
    @staticmethod
    def save_country_report(stats: ErrorStats, filename: str = "error_country_stats.csv") -> None:
        """Save country-based error statistics to CSV"""
        if not stats.errors_by_country:
            print("No country data to save")
            return
            
        report_data = []
        for country, count in stats.errors_by_country.most_common():
            percentage = (count / stats.total_errors) * 100
            report_data.append({
                'country': country,
                'error_count': count,
                'percentage': percentage
            })
        
        df = pd.DataFrame(report_data)
        df.to_csv(filename, index=False)
        print(f"Country-based error statistics saved to {filename}")

def main():
    """Main function to run error log analysis"""
    analyzer = ErrorLogAnalyzer()
    visualizer = ErrorLogVisualizer()
    reporter = ErrorLogReporter()
    
    print("Starting NGINX Error Log Analysis...")
    
    # Analyze logs
    stats = analyzer.analyze_logs()
    
    if stats.total_errors == 0:
        print("No error logs found or no errors detected.")
        return
    
    # Print summary
    reporter.print_summary(stats)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    visualizer.plot_error_levels(stats, "error_analysis")
    visualizer.plot_country_distribution(stats, "error_analysis")
    visualizer.plot_error_types(stats, "error_analysis")
    visualizer.plot_hourly_distribution(stats, "error_analysis")
    visualizer.plot_daily_trend(stats, "error_analysis")
    
    # Save detailed reports
    reporter.save_detailed_report(stats, "error_stats.csv")
    reporter.save_country_report(stats, "error_country_stats.csv")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main() 