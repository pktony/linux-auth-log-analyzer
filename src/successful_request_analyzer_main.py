"""
Main script for analyzing successful requests in nginx access logs
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from analyzers.successful_request_analyzer import SuccessfulRequestAnalyzer
from utils.successful_request_visualizer import SuccessfulRequestVisualizer


def print_successful_request_summary(stats) -> None:
    """Print a comprehensive summary of successful request analysis"""
    print("\n" + "="*60)
    print("성공 요청 분석 결과")
    print("="*60)
    
    print(f"\n📊 전체 통계:")
    print(f"  • 총 성공 요청 수: {stats.total_successful_requests:,}")
    print(f"  • 고유 IP 수: {stats.unique_ips:,}")
    
    if stats.successful_requests_by_country:
        print(f"\n🌍 국가별 성공 요청 (상위 10개):")
        for i, (country, count) in enumerate(stats.successful_requests_by_country.items(), 1):
            if i > 10:
                break
            print(f"  {i:2d}. {country}: {count:,}")
    
    if stats.successful_requests_by_method:
        print(f"\n🔧 HTTP 메소드별 성공 요청:")
        for method, count in stats.successful_requests_by_method.items():
            print(f"  • {method}: {count:,}")
    
    if stats.successful_requests_by_url:
        print(f"\n🔗 인기 URL (상위 10개):")
        for i, (url, count) in enumerate(stats.successful_requests_by_url.items(), 1):
            if i > 10:
                break
            # Truncate long URLs for display
            display_url = url if len(url) <= 60 else url[:57] + "..."
            print(f"  {i:2d}. {display_url}")
            print(f"      요청 수: {count:,}")
    
    if stats.successful_requests_by_date:
        print(f"\n📅 일별 성공 요청 트렌드 (상위 10일):")
        sorted_dates = sorted(stats.successful_requests_by_date.items(), 
                            key=lambda x: x[1], reverse=True)
        for i, (date, count) in enumerate(sorted_dates, 1):
            if i > 10:
                break
            print(f"  {i:2d}. {date}: {count:,}")


def main():
    """Main function to analyze successful requests"""
    print("🚀 성공 요청 분석을 시작합니다...")
    
    # Initialize analyzer
    analyzer = SuccessfulRequestAnalyzer()
    
    # Analyze logs
    print("\n📋 로그 파일을 분석하고 있습니다...")
    stats = analyzer.analyze_logs()
    
    if stats.total_successful_requests == 0:
        print("\n❌ 성공한 요청이 발견되지 않았습니다.")
        print("   - 로그 파일이 비어있거나")
        print("   - 성공 요청(200-299 상태 코드)이 없거나")
        print("   - 필터링 조건에 맞는 요청이 없을 수 있습니다.")
        return
    
    # Print summary
    print_successful_request_summary(stats)
    
    # Create detailed CSV report
    print("\n📄 상세 보고서를 생성하고 있습니다...")
    detailed_records = analyzer.get_detailed_records()
    if detailed_records:
        import pandas as pd
        df = pd.DataFrame(detailed_records)
        df.to_csv('successful_requests_detailed.csv', index=False, encoding='utf-8')
        print("✅ 상세 성공 요청 데이터가 'successful_requests_detailed.csv'로 저장되었습니다.")
    
    # Create visualizations
    print("\n📊 차트를 생성하고 있습니다...")
    visualizer = SuccessfulRequestVisualizer(save_path="successful_requests_analysis")
    visualizer.create_all_charts(stats)
    
    # Create detailed report
    visualizer.create_detailed_report(stats, "successful_requests_report.csv")
    
    print("\n✅ 모든 분석이 완료되었습니다!")
    print("\n📁 생성된 파일들:")
    print("  • successful_requests_detailed.csv - 상세 데이터")
    print("  • successful_requests_report.csv - 요약 보고서")
    print("  • successful_requests_analysis_successful_requests_summary.png - 요약 차트")
    print("  • successful_requests_analysis_successful_requests_country_distribution.png - 국가별 분포")
    print("  • successful_requests_analysis_successful_requests_daily_distribution.png - 일별 분포")
    print("  • successful_requests_analysis_successful_requests_method_distribution.png - HTTP 메소드별 분포")
    print("  • successful_requests_analysis_successful_requests_url_distribution.png - URL별 분포")
    
    print("\n🔍 분석 결과 요약:")
    print(f"  • 총 {stats.total_successful_requests:,}개의 성공 요청이 {stats.unique_ips:,}개의 고유 IP에서 발생")
    print(f"  • 가장 많은 성공 요청을 보낸 국가: {stats.top_successful_countries[0] if stats.top_successful_countries else 'N/A'}")
    print(f"  • 가장 인기 있는 URL: {stats.top_successful_urls[0] if stats.top_successful_urls else 'N/A'}")


if __name__ == "__main__":
    main() 