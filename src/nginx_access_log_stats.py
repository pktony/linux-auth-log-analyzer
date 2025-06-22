import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from analyzers.access_log_analyzer import AccessLogAnalyzer
from utils.visualization_utils import LogVisualizer


def main():
    """Main function to analyze access logs using the new analyzer"""
    analyzer = AccessLogAnalyzer()
    stats = analyzer.analyze_logs()
    
    # Print results
    print("Access Log Analysis Results:")
    print("=" * 50)
    
    # Print weekly stats
    for week in sorted(stats.weekly_stats):
        print(f"\n{week}")
        for country, count in stats.weekly_stats[week].most_common():
            print(f"  {country}: {count}")
    
    # Print summary
    print(f"\nTotal unique IPs: {stats.total_unique_ips}")
    print(f"Total requests: {stats.total_requests}")
    print(f"Top countries: {stats.top_countries}")
    
    # Get detailed IP records
    ip_records = analyzer.get_ip_records()
    if ip_records:
        import pandas as pd
        df = pd.DataFrame(ip_records)
        df.to_csv('ip_stats.csv', index=False)
        print('\nIP별 상세 통계가 ip_stats.csv로 저장되었습니다.')
    
    # Create visualizations using unified LogVisualizer
    print("\n차트 생성을 시작합니다...")
    visualizer = LogVisualizer(save_path="access_analysis")
    
    # Create all access log charts
    print("Access log 차트들을 생성합니다...")
    visualizer.visualize_access_logs(stats)
    
    print("\n모든 차트가 생성되었습니다!")
    print("생성된 파일들:")
    print("- access_analysis_access_summary.png")
    print("- access_analysis_access_country_distribution.png")
    print("- access_analysis_access_daily_distribution.png")
    print("- access_analysis_access_status_codes.png")
    print("- access_analysis_access_http_methods.png")
    print("- access_analysis_access_weekly_trends.png")


if __name__ == "__main__":
    main()