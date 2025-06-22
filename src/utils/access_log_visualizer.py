"""
Access log visualization utilities
"""
from typing import Dict, List, Optional
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from utils.visualization_utils import (
    BarChartRenderer, 
    LineChartRenderer, 
    PieChartRenderer, 
    TimeSeriesRenderer
)
from models.access_log_models import AccessLogStats


class AccessLogVisualizer:
    """Visualizes access log analysis results"""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = save_path
        self._setup_matplotlib()
    
    def _setup_matplotlib(self) -> None:
        """Setup matplotlib configuration for Korean text support"""
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_all_charts(self, stats: AccessLogStats) -> None:
        """Create all access log visualization charts"""
        self._create_country_distribution_chart(stats)
        self._create_daily_distribution_chart(stats)
        self._create_status_code_chart(stats)
        self._create_method_chart(stats)
        self._create_weekly_trend_chart(stats)
    
    def _create_country_distribution_chart(self, stats: AccessLogStats) -> None:
        """Create country distribution chart"""
        if not stats.requests_by_country:
            print("No country data available for visualization")
            return
        
        # Get top 10 countries
        top_countries = dict(Counter(stats.requests_by_country).most_common(10))
        
        BarChartRenderer.render_horizontal_bar(
            data=top_countries,
            title="Top 10 Countries by Request Count",
            xlabel="Request Count",
            ylabel="Country",
            save_path=self.save_path,
            filename="access_country_distribution"
        )
    
    def _create_daily_distribution_chart(self, stats: AccessLogStats) -> None:
        """Create daily distribution chart"""
        if not stats.requests_by_date:
            print("No daily data available for visualization")
            return
        
        # Sort by date
        sorted_daily_data = dict(sorted(stats.requests_by_date.items()))
        
        LineChartRenderer.render_line_chart(
            data=sorted_daily_data,
            title="Request Distribution by Date",
            xlabel="Date",
            ylabel="Request Count",
            save_path=self.save_path,
            filename="access_daily_distribution"
        )
    
    def _create_status_code_chart(self, stats: AccessLogStats) -> None:
        """Create status code distribution chart"""
        if not stats.requests_by_status:
            print("No status code data available for visualization")
            return
        
        PieChartRenderer.render_pie_chart(
            data=stats.requests_by_status,
            title="Request Distribution by Status Code",
            save_path=self.save_path,
            filename="access_status_codes"
        )
    
    def _create_method_chart(self, stats: AccessLogStats) -> None:
        """Create HTTP method distribution chart"""
        if not stats.requests_by_method:
            print("No method data available for visualization")
            return
        
        BarChartRenderer.render_vertical_bar(
            data=stats.requests_by_method,
            title="Request Distribution by HTTP Method",
            xlabel="HTTP Method",
            ylabel="Request Count",
            save_path=self.save_path,
            filename="access_http_methods"
        )
    
    def _create_weekly_trend_chart(self, stats: AccessLogStats) -> None:
        """Create weekly trend chart"""
        if not stats.weekly_stats:
            print("No weekly data available for visualization")
            return
        
        # Aggregate weekly data by country
        weekly_country_data = {}
        for week, country_counts in stats.weekly_stats.items():
            for country, count in country_counts.items():
                if country not in weekly_country_data:
                    weekly_country_data[country] = {}
                weekly_country_data[country][week] = count
        
        # Get top 5 countries for trend analysis
        total_by_country = {}
        for country, weekly_data in weekly_country_data.items():
            total_by_country[country] = sum(weekly_data.values())
        
        top_countries = dict(Counter(total_by_country).most_common(5))
        
        # Create trend chart
        plt.figure(figsize=(14, 8))
        weeks = sorted(stats.weekly_stats.keys())
        
        for country in top_countries.keys():
            country_weekly_data = []
            for week in weeks:
                country_weekly_data.append(stats.weekly_stats[week].get(country, 0))
            
            plt.plot(weeks, country_weekly_data, marker='o', linewidth=2, label=country)
        
        plt.title("Weekly Request Trends by Top Countries")
        plt.xlabel("Week")
        plt.ylabel("Request Count")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if self.save_path:
            plt.savefig(f"{self.save_path}_access_weekly_trends.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    def create_summary_chart(self, stats: AccessLogStats) -> None:
        """Create a summary chart with key metrics"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Top countries (top 5)
        top_countries = dict(Counter(stats.requests_by_country).most_common(5))
        countries = list(top_countries.keys())
        counts = list(top_countries.values())
        
        ax1.barh(countries, counts, color='skyblue')
        ax1.set_title('Top 5 Countries')
        ax1.set_xlabel('Request Count')
        
        # Top status codes (top 5)
        top_status_codes = dict(Counter(stats.requests_by_status).most_common(5))
        status_codes = list(top_status_codes.keys())
        status_counts = list(top_status_codes.values())
        
        ax2.bar(status_codes, status_counts, color='lightcoral')
        ax2.set_title('Top 5 Status Codes')
        ax2.set_xlabel('Status Code')
        ax2.set_ylabel('Request Count')
        
        # HTTP methods
        methods = list(stats.requests_by_method.keys())
        method_counts = list(stats.requests_by_method.values())
        
        ax3.bar(methods, method_counts, color='lightgreen')
        ax3.set_title('HTTP Method Distribution')
        ax3.set_ylabel('Request Count')
        
        # Daily distribution (top 10 days)
        top_daily = dict(Counter(stats.requests_by_date).most_common(10))
        dates = list(top_daily.keys())
        daily_counts = list(top_daily.values())
        
        ax4.bar(range(len(dates)), daily_counts, color='gold')
        ax4.set_title('Top 10 Days by Request Count')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Request Count')
        ax4.set_xticks(range(len(dates)))
        ax4.set_xticklabels(dates, rotation=45)
        
        plt.tight_layout()
        
        if self.save_path:
            plt.savefig(f"{self.save_path}_access_summary.png", dpi=150, bbox_inches='tight')
        plt.show() 