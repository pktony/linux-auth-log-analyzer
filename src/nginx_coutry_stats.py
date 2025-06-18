import os
import re
import gzip
from collections import defaultdict, Counter
import geoip2.database
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from dotenv import load_dotenv
import pandas as pd

# https://github.com/maxmind/GeoIP2-python
# https://www.maxmind.com/en/accounts/1185643/geoip/downloads
# conda install conda-forge::geoip2
LOG_DIR = "logs"
GEOIP_DB = "src/GeoLite2-Country.mmdb"

# 정규식: IP, 날짜 추출
log_pattern = re.compile(r'^(\d+\.\d+\.\d+\.\d+) - - \[(\d{2}/\w{3}/\d{4})')
# 정규식: IP, 날짜, 메서드, 쿼리, 코드 추출
log_pattern_full = re.compile(r'^(\d+\.\d+\.\d+\.\d+) - - \[(\d{2}/\w{3}/\d{4}):[^\]]+\] "(\w+) ([^ ]+) [^\"]+" (\d{3})')

def get_country(ip, reader):
    try:
        response = reader.country(ip)
        return response.country.iso_code or "Unknown"
    except Exception:
        return "Unknown"

def get_my_ip_list():
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        ip_str = os.getenv('MY_IP')
        if ip_str:
            return [ip.strip() for ip in ip_str.split(',') if ip.strip()]
    return []

def get_exclude_countries():
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        country_str = os.getenv('EXCLUDE_COUNTRIES')
        if country_str:
            return [c.strip().upper() for c in country_str.split(',') if c.strip()]
    return []

def process_log_file(filepath, reader, stats, my_ip_list=None, ip_records=None, exclude_countries=None):
    open_func = gzip.open if filepath.endswith('.gz') else open
    with open_func(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = log_pattern.match(line)
            if m:
                ip, date_str = m.groups()
                if my_ip_list and ip in my_ip_list:
                    continue
                country = get_country(ip, reader)
                if exclude_countries and country in exclude_countries:
                    continue
                try:
                    dt = datetime.datetime.strptime(date_str, "%d/%b/%Y")
                    week_key = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                except Exception:
                    week_key = "Unknown"
                stats[week_key][country] += 1
            # IP별 상세 통계
            m2 = log_pattern_full.match(line)
            if m2 and ip_records is not None:
                ip, date_str, method, query, code = m2.groups()
                if my_ip_list and ip in my_ip_list:
                    continue
                country = get_country(ip, reader)
                if exclude_countries and country in exclude_countries:
                    continue
                try:
                    date = datetime.datetime.strptime(date_str, "%d/%b/%Y").date()
                except Exception:
                    date = date_str
                ip_records.append({
                    'ip': ip,
                    'country': country,
                    'date': date,
                    'http_code': code,
                    'method': method,
                    'query': query
                })

def plot_stats(stats, top_n=5, save_path=None):
    weeks = sorted(stats)
    total_by_country = Counter()
    for week in weeks:
        total_by_country.update(stats[week])
    top_countries = [c for c, _ in total_by_country.most_common(top_n)]
    data = {country: [] for country in top_countries}
    data['Other'] = []
    for week in weeks:
        week_total = sum(stats[week].values())
        for country in top_countries:
            data[country].append(stats[week][country])
        other = week_total - sum(stats[week][c] for c in top_countries)
        data['Other'].append(other)
    # 색상 팔레트 고정
    colors = plt.get_cmap('tab20').colors
    plt.figure(figsize=(14, 7))
    bottom = [0] * len(weeks)
    for idx, country in enumerate(top_countries + ['Other']):
        plt.bar(weeks, data[country], bottom=bottom, label=country, color=colors[idx % len(colors)])
        bottom = [b + v for b, v in zip(bottom, data[country])]
    plt.xlabel('Week')
    plt.ylabel('Access Count')
    plt.title(f'Weekly Access Count by Country (Top {top_n})')
    plt.xticks(rotation=45)
    plt.legend(title='Country', bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.tight_layout()
    # x축 라벨 간격 조정
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()

def main():
    stats = defaultdict(Counter)
    my_ip_list = get_my_ip_list()
    exclude_countries = get_exclude_countries()
    ip_records = []
    with geoip2.database.Reader(GEOIP_DB) as reader:
        for fname in os.listdir(LOG_DIR):
            if fname.startswith("access.log"):
                process_log_file(
                    os.path.join(LOG_DIR, fname), reader, stats,
                    my_ip_list=my_ip_list, ip_records=ip_records, exclude_countries=exclude_countries)
    # 결과 출력
    for week in sorted(stats):
        print(f"{week}")
        for country, count in stats[week].most_common():
            print(f"  {country}: {count}")
        print()
    # 그래프 출력
    plot_stats(stats)
    # IP별 상세 통계 저장
    if ip_records:
        df = pd.DataFrame(ip_records)
        df.to_csv('ip_stats.csv', index=False)
        print('IP별 상세 통계가 ip_stats.csv로 저장되었습니다.')

if __name__ == "__main__":
    main()