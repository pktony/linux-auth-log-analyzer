"""
Visualization utilities for successful request analysis
"""
from typing import Dict, Optional
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
from models.access_log_models import SuccessfulRequestStats
from utils.visualization_utils import (
    BarChartRenderer, 
    LineChartRenderer, 
    PieChartRenderer
)


class SuccessfulRequestVisualizer:
    """Visualizes successful request analysis results"""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = save_path
        self._setup_matplotlib()
    
    def _setup_matplotlib(self) -> None:
        """Setup matplotlib configuration for Korean text support"""
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_all_charts(self, stats: SuccessfulRequestStats) -> None:
        """Create all successful request visualization charts"""
        self._create_country_distribution_chart(stats)
        self._create_daily_distribution_chart(stats)
        self._create_method_distribution_chart(stats)
        self._create_url_distribution_chart(stats)
        self._create_summary_chart(stats)
    
    def _create_country_distribution_chart(self, stats: SuccessfulRequestStats) -> None:
        """Create country distribution chart for successful requests"""
        if not stats.successful_requests_by_country:
            print("No country data available for successful request visualization")
            return
        
        # Get top 10 countries
        top_countries = dict(Counter(stats.successful_requests_by_country).most_common(10))
        
        BarChartRenderer.render_horizontal_bar(
            data=top_countries,
            title="Top 10 Countries by Successful Requests",
            xlabel="Successful Request Count",
            ylabel="Country",
            save_path=self.save_path,
            filename="successful_requests_country_distribution"
        )
    
    def _create_daily_distribution_chart(self, stats: SuccessfulRequestStats) -> None:
        """Create daily distribution chart for successful requests"""
        if not stats.successful_requests_by_date:
            print("No daily data available for successful request visualization")
            return
        
        # Sort by date
        sorted_daily_data = dict(sorted(stats.successful_requests_by_date.items()))
        
        LineChartRenderer.render_line_chart(
            data=sorted_daily_data,
            title="Successful Request Distribution by Date",
            xlabel="Date",
            ylabel="Successful Request Count",
            save_path=self.save_path,
            filename="successful_requests_daily_distribution"
        )
    
    def _create_method_distribution_chart(self, stats: SuccessfulRequestStats) -> None:
        """Create HTTP method distribution chart for successful requests"""
        if not stats.successful_requests_by_method:
            print("No method data available for successful request visualization")
            return
        
        BarChartRenderer.render_vertical_bar(
            data=stats.successful_requests_by_method,
            title="Successful Request Distribution by HTTP Method",
            xlabel="HTTP Method",
            ylabel="Successful Request Count",
            save_path=self.save_path,
            filename="successful_requests_method_distribution"
        )
    
    def _create_url_distribution_chart(self, stats: SuccessfulRequestStats) -> None:
        """Create URL distribution chart for successful requests"""
        if not stats.successful_requests_by_url:
            print("No URL data available for successful request visualization")
            return
        
        # Get top 15 URLs
        top_urls = dict(Counter(stats.successful_requests_by_url).most_common(15))
        
        # Truncate long URLs for display
        display_urls = {}
        for url, count in top_urls.items():
            if len(url) > 50:
                display_url = url[:47] + "..."
            else:
                display_url = url
            display_urls[display_url] = count
        
        BarChartRenderer.render_horizontal_bar(
            data=display_urls,
            title="Top 15 URLs by Successful Requests",
            xlabel="Successful Request Count",
            ylabel="URL",
            save_path=self.save_path,
            filename="successful_requests_url_distribution"
        )
    
    def _create_summary_chart(self, stats: SuccessfulRequestStats) -> None:
        """Create a summary chart for successful requests with key metrics"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Top countries (top 5)
        top_countries = dict(Counter(stats.successful_requests_by_country).most_common(5))
        countries = list(top_countries.keys())
        counts = list(top_countries.values())
        
        ax1.barh(countries, counts, color='lightgreen')
        ax1.set_title('Top 5 Countries by Successful Requests')
        ax1.set_xlabel('Successful Request Count')
        
        # HTTP methods
        methods = list(stats.successful_requests_by_method.keys())
        method_counts = list(stats.successful_requests_by_method.values())
        
        ax2.pie(method_counts, labels=methods, autopct='%1.1f%%')
        ax2.set_title('Successful Requests by HTTP Method')
        
        # Top URLs (top 5)
        top_urls = dict(Counter(stats.successful_requests_by_url).most_common(5))
        urls = list(top_urls.keys())
        url_counts = list(top_urls.values())
        
        # Truncate URLs for display
        display_urls = []
        for url in urls:
            if len(url) > 30:
                display_urls.append(url[:27] + "...")
            else:
                display_urls.append(url)
        
        ax3.bar(range(len(display_urls)), url_counts, color='skyblue')
        ax3.set_title('Top 5 URLs by Successful Requests')
        ax3.set_xlabel('URL')
        ax3.set_ylabel('Successful Request Count')
        ax3.set_xticks(range(len(display_urls)))
        ax3.set_xticklabels(display_urls, rotation=45, ha='right')
        
        # Daily trend (top 10 days)
        top_daily = dict(Counter(stats.successful_requests_by_date).most_common(10))
        dates = list(top_daily.keys())
        daily_counts = list(top_daily.values())
        
        ax4.bar(range(len(dates)), daily_counts, color='gold')
        ax4.set_title('Top 10 Days by Successful Requests')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Successful Request Count')
        ax4.set_xticks(range(len(dates)))
        ax4.set_xticklabels(dates, rotation=45)
        
        plt.tight_layout()
        
        if self.save_path:
            plt.savefig(f"{self.save_path}_successful_requests_summary.png", dpi=150, bbox_inches='tight')
        plt.show()
    
    def create_detailed_report(self, stats: SuccessfulRequestStats, filename: str = "successful_requests_report.csv") -> None:
        """Create a detailed CSV report of successful requests"""
        if not stats.successful_requests_details:
            print("No successful request details available for report")
            return
        
        records = []
        for req in stats.successful_requests_details:
            records.append({
                'IP': req.ip,
                'Timestamp': req.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Method': req.method,
                'URL': req.url,
                'Status_Code': req.status_code,
                'Country': req.country,
                'Date': req.date,
                'Hour': req.hour,
                'User_Agent': req.user_agent or '',
                'Referer': req.referer or '',
                'Response_Size': req.response_size or 0
            })
        
        df = pd.DataFrame(records)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"상세 성공 요청 보고서가 {filename}로 저장되었습니다.") 