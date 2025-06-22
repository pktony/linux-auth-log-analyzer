"""
Visualization utilities for creating charts and graphs
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import Optional, List, Dict, Any
from collections import Counter
from models.access_log_models import AccessLogStats
from models.error_log_models import ErrorLogStats


class ChartRenderer:
    """Handles chart rendering operations"""
    
    @staticmethod
    def save_chart(save_path: Optional[str], filename: str, dpi: int = 150) -> None:
        """Save chart to file if save_path is provided"""
        if save_path:
            plt.savefig(f"{save_path}_{filename}.png", dpi=dpi, bbox_inches='tight')
    
    @staticmethod
    def show_chart() -> None:
        """Display the current chart"""
        plt.show()


class BarChartRenderer(ChartRenderer):
    """Renders bar charts"""
    
    @staticmethod
    def render_vertical_bar(data: Dict[str, int], title: str, xlabel: str, ylabel: str, 
                           save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render vertical bar chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(10, 6))
        labels = list(data.keys())
        values = list(data.values())
        
        plt.bar(labels, values, color='blue', alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for i, value in enumerate(values):
            plt.text(i, value + max(values) * 0.01, str(value), ha='center', va='bottom')
        
        plt.tight_layout()
        BarChartRenderer.save_chart(save_path, filename)
        BarChartRenderer.show_chart()
    
    @staticmethod
    def render_horizontal_bar(data: Dict[str, int], title: str, xlabel: str, ylabel: str,
                             save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render horizontal bar chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(12, 8))
        labels = list(data.keys())
        values = list(data.values())
        
        plt.barh(labels, values, color='orange', alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        # Add value labels on bars
        for i, value in enumerate(values):
            plt.text(value + max(values) * 0.01, i, str(value), va='center')
        
        plt.tight_layout()
        BarChartRenderer.save_chart(save_path, filename)
        BarChartRenderer.show_chart()


class LineChartRenderer(ChartRenderer):
    """Renders line charts"""
    
    @staticmethod
    def render_line_chart(data: Dict[str, int], title: str, xlabel: str, ylabel: str,
                         save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render line chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(14, 6))
        labels = sorted(data.keys())
        values = [data[label] for label in labels]
        
        plt.plot(labels, values, marker='o', linewidth=2, markersize=4, color='red')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Show every nth label to avoid overcrowding
        n = max(1, len(labels) // 10)
        plt.xticks(labels[::n])
        
        plt.tight_layout()
        LineChartRenderer.save_chart(save_path, filename)
        LineChartRenderer.show_chart()


class PieChartRenderer(ChartRenderer):
    """Renders pie charts"""
    
    @staticmethod
    def render_pie_chart(data: Dict[str, int], title: str,
                        save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render pie chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(12, 8))
        labels = list(data.keys())
        values = list(data.values())
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(title)
        plt.axis('equal')
        
        plt.tight_layout()
        PieChartRenderer.save_chart(save_path, filename)
        PieChartRenderer.show_chart()


class TimeSeriesRenderer(ChartRenderer):
    """Renders time series charts"""
    
    @staticmethod
    def render_hourly_chart(data: Dict[int, int], title: str,
                           save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render hourly distribution chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(12, 6))
        hours = sorted(data.keys())
        values = [data[hour] for hour in hours]
        
        plt.plot(hours, values, marker='o', linewidth=2, markersize=6, color='red')
        plt.fill_between(hours, values, alpha=0.3, color='red')
        plt.title(title)
        plt.xlabel('Hour')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24))
        
        plt.tight_layout()
        TimeSeriesRenderer.save_chart(save_path, filename)
        TimeSeriesRenderer.show_chart()


class LogVisualizer:
    """Unified visualizer for both access and error logs"""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = save_path
        self._setup_matplotlib()
    
    def _setup_matplotlib(self) -> None:
        """Setup matplotlib configuration for Korean text support"""
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic']
        plt.rcParams['axes.unicode_minus'] = False
    
    def visualize_access_logs(self, stats: AccessLogStats) -> None:
        """Create all access log visualization charts"""
        self._create_access_country_distribution_chart(stats)
        self._create_access_daily_distribution_chart(stats)
        self._create_access_status_code_chart(stats)
        self._create_access_method_chart(stats)
        self._create_access_weekly_trend_chart(stats)
        self._create_access_summary_chart(stats)
    
    def visualize_error_logs(self, stats: ErrorLogStats) -> None:
        """Create all error log visualization charts"""
        self._create_error_level_chart(stats)
        self._create_error_hourly_distribution_chart(stats)
        self._create_error_daily_distribution_chart(stats)
        self._create_error_country_chart(stats)
        self._create_error_type_chart(stats)
        self._create_error_method_chart(stats)
        self._create_error_summary_chart(stats)
    
    # Access Log Visualization Methods
    def _create_access_country_distribution_chart(self, stats: AccessLogStats) -> None:
        """Create country distribution chart for access logs"""
        if not stats.requests_by_country:
            print("No country data available for access log visualization")
            return
        
        # Get top 10 countries
        top_countries = dict(Counter(stats.requests_by_country).most_common(10))
        
        BarChartRenderer.render_horizontal_bar(
            data=top_countries,
            title="Top 10 Countries by Request Count (Access Logs)",
            xlabel="Request Count",
            ylabel="Country",
            save_path=self.save_path,
            filename="access_country_distribution"
        )
    
    def _create_access_daily_distribution_chart(self, stats: AccessLogStats) -> None:
        """Create daily distribution chart for access logs"""
        if not stats.requests_by_date:
            print("No daily data available for access log visualization")
            return
        
        # Sort by date
        sorted_daily_data = dict(sorted(stats.requests_by_date.items()))
        
        LineChartRenderer.render_line_chart(
            data=sorted_daily_data,
            title="Request Distribution by Date (Access Logs)",
            xlabel="Date",
            ylabel="Request Count",
            save_path=self.save_path,
            filename="access_daily_distribution"
        )
    
    def _create_access_status_code_chart(self, stats: AccessLogStats) -> None:
        """Create status code distribution chart for access logs"""
        if not stats.requests_by_status:
            print("No status code data available for access log visualization")
            return
        
        PieChartRenderer.render_pie_chart(
            data=stats.requests_by_status,
            title="Request Distribution by Status Code (Access Logs)",
            save_path=self.save_path,
            filename="access_status_codes"
        )
    
    def _create_access_method_chart(self, stats: AccessLogStats) -> None:
        """Create HTTP method distribution chart for access logs"""
        if not stats.requests_by_method:
            print("No method data available for access log visualization")
            return
        
        BarChartRenderer.render_vertical_bar(
            data=stats.requests_by_method,
            title="Request Distribution by HTTP Method (Access Logs)",
            xlabel="HTTP Method",
            ylabel="Request Count",
            save_path=self.save_path,
            filename="access_http_methods"
        )
    
    def _create_access_weekly_trend_chart(self, stats: AccessLogStats) -> None:
        """Create weekly trend chart for access logs"""
        if not stats.weekly_stats:
            print("No weekly data available for access log visualization")
            return
        
        # Get top 5 countries for trend analysis
        total_by_country = {}
        for week, country_counts in stats.weekly_stats.items():
            for country, count in country_counts.items():
                if country not in total_by_country:
                    total_by_country[country] = 0
                total_by_country[country] += count
        
        top_countries = dict(Counter(total_by_country).most_common(5))
        
        # Create trend chart
        plt.figure(figsize=(14, 8))
        weeks = sorted(stats.weekly_stats.keys())
        
        for country in top_countries.keys():
            country_weekly_data = []
            for week in weeks:
                country_weekly_data.append(stats.weekly_stats[week].get(country, 0))
            
            plt.plot(weeks, country_weekly_data, marker='o', linewidth=2, label=country)
        
        plt.title("Weekly Request Trends by Top Countries (Access Logs)")
        plt.xlabel("Week")
        plt.ylabel("Request Count")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if self.save_path:
            plt.savefig(f"{self.save_path}_access_weekly_trends.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    def _create_access_summary_chart(self, stats: AccessLogStats) -> None:
        """Create a summary chart for access logs with key metrics"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Top countries (top 5)
        top_countries = dict(Counter(stats.requests_by_country).most_common(5))
        countries = list(top_countries.keys())
        counts = list(top_countries.values())
        
        ax1.barh(countries, counts, color='skyblue')
        ax1.set_title('Top 5 Countries (Access Logs)')
        ax1.set_xlabel('Request Count')
        
        # Top status codes (top 5)
        top_status_codes = dict(Counter(stats.requests_by_status).most_common(5))
        status_codes = list(top_status_codes.keys())
        status_counts = list(top_status_codes.values())
        
        ax2.bar(status_codes, status_counts, color='lightcoral')
        ax2.set_title('Top 5 Status Codes (Access Logs)')
        ax2.set_xlabel('Status Code')
        ax2.set_ylabel('Request Count')
        
        # HTTP methods
        methods = list(stats.requests_by_method.keys())
        method_counts = list(stats.requests_by_method.values())
        
        ax3.bar(methods, method_counts, color='lightgreen')
        ax3.set_title('HTTP Method Distribution (Access Logs)')
        ax3.set_ylabel('Request Count')
        
        # Daily distribution (top 10 days)
        top_daily = dict(Counter(stats.requests_by_date).most_common(10))
        dates = list(top_daily.keys())
        daily_counts = list(top_daily.values())
        
        ax4.bar(range(len(dates)), daily_counts, color='gold')
        ax4.set_title('Top 10 Days by Request Count (Access Logs)')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Request Count')
        ax4.set_xticks(range(len(dates)))
        ax4.set_xticklabels(dates, rotation=45)
        
        plt.tight_layout()
        
        if self.save_path:
            plt.savefig(f"{self.save_path}_access_summary.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    # Error Log Visualization Methods
    def _create_error_level_chart(self, stats: ErrorLogStats) -> None:
        """Create error level distribution chart for error logs"""
        if not stats.errors_by_level:
            print("No error level data available for error log visualization")
            return
        
        PieChartRenderer.render_pie_chart(
            data=stats.errors_by_level,
            title="Error Distribution by Level (Error Logs)",
            save_path=self.save_path,
            filename="error_levels"
        )
    
    def _create_error_hourly_distribution_chart(self, stats: ErrorLogStats) -> None:
        """Create hourly distribution chart for error logs"""
        if not stats.errors_by_hour:
            print("No hourly data available for error log visualization")
            return
        
        TimeSeriesRenderer.render_hourly_chart(
            data=stats.errors_by_hour,
            title="Error Distribution by Hour (Error Logs)",
            save_path=self.save_path,
            filename="error_hourly_distribution"
        )
    
    def _create_error_daily_distribution_chart(self, stats: ErrorLogStats) -> None:
        """Create daily distribution chart for error logs"""
        if not stats.errors_by_date:
            print("No daily data available for error log visualization")
            return
        
        # Sort by date
        sorted_daily_data = dict(sorted(stats.errors_by_date.items()))
        
        LineChartRenderer.render_line_chart(
            data=sorted_daily_data,
            title="Error Distribution by Date (Error Logs)",
            xlabel="Date",
            ylabel="Error Count",
            save_path=self.save_path,
            filename="error_daily_distribution"
        )
    
    def _create_error_country_chart(self, stats: ErrorLogStats) -> None:
        """Create country distribution chart for error logs"""
        if not stats.errors_by_country:
            print("No country data available for error log visualization")
            return
        
        # Get top 10 countries
        top_countries = dict(Counter(stats.errors_by_country).most_common(10))
        
        BarChartRenderer.render_horizontal_bar(
            data=top_countries,
            title="Top 10 Countries by Error Count (Error Logs)",
            xlabel="Error Count",
            ylabel="Country",
            save_path=self.save_path,
            filename="error_country_distribution"
        )
    
    def _create_error_type_chart(self, stats: ErrorLogStats) -> None:
        """Create error type distribution chart for error logs"""
        if not stats.errors_by_error_type:
            print("No error type data available for error log visualization")
            return
        
        BarChartRenderer.render_vertical_bar(
            data=stats.errors_by_error_type,
            title="Error Distribution by Type (Error Logs)",
            xlabel="Error Type",
            ylabel="Error Count",
            save_path=self.save_path,
            filename="error_types"
        )
    
    def _create_error_method_chart(self, stats: ErrorLogStats) -> None:
        """Create HTTP method distribution chart for error logs"""
        if not stats.errors_by_method:
            print("No method data available for error log visualization")
            return
        
        BarChartRenderer.render_vertical_bar(
            data=stats.errors_by_method,
            title="Error Distribution by HTTP Method (Error Logs)",
            xlabel="HTTP Method",
            ylabel="Error Count",
            save_path=self.save_path,
            filename="error_http_methods"
        )
    
    def _create_error_summary_chart(self, stats: ErrorLogStats) -> None:
        """Create a summary chart for error logs with key metrics"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Error levels
        levels = list(stats.errors_by_level.keys())
        level_counts = list(stats.errors_by_level.values())
        
        ax1.pie(level_counts, labels=levels, autopct='%1.1f%%')
        ax1.set_title('Error Level Distribution (Error Logs)')
        
        # Hourly distribution
        hours = sorted(stats.errors_by_hour.keys())
        hourly_counts = [stats.errors_by_hour[hour] for hour in hours]
        
        ax2.plot(hours, hourly_counts, marker='o', color='red')
        ax2.set_title('Hourly Error Distribution (Error Logs)')
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Error Count')
        ax2.grid(True, alpha=0.3)
        
        # Top countries (top 5)
        top_countries = dict(Counter(stats.errors_by_country).most_common(5))
        countries = list(top_countries.keys())
        counts = list(top_countries.values())
        
        ax3.barh(countries, counts, color='orange')
        ax3.set_title('Top 5 Countries by Errors (Error Logs)')
        ax3.set_xlabel('Error Count')
        
        # Error types
        error_types = list(stats.errors_by_error_type.keys())
        error_type_counts = list(stats.errors_by_error_type.values())
        
        ax4.bar(error_types, error_type_counts, color='lightcoral')
        ax4.set_title('Error Type Distribution (Error Logs)')
        ax4.set_ylabel('Error Count')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if self.save_path:
            plt.savefig(f"{self.save_path}_error_summary.png", dpi=150, bbox_inches='tight')
        plt.show() 