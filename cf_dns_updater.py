import csv
import time
import requests
import json
import subprocess
import zipfile
import os
from datetime import datetime
import re
import socket

# Remove proxy environment variables
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(key, None)

# ... (rest of the code remains the same until the fetch_ips function)

def fetch_ips():
    print("下载并生成第三方中转IP列表...")
    current_date = datetime.now().strftime('%Y%m%d')
    download_folder = os.path.join('3ip_file', current_date)

    response = requests.get("https://zip.baipiao.eu.org/")
    with open("3ip_file.zip", "wb") as file:
        file.write(response.content)

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    with zipfile.ZipFile('3ip_file.zip', 'r') as archive:
        archive.extractall(download_folder)

    valid_ips = []

    for file_name in os.listdir(download_folder):
        if file_name.endswith('.txt'):
            with open(os.path.join(download_folder, file_name), 'r') as infile:
                for line in infile:
                    if line.strip():
                        ip = line.strip()
                        if is_valid_ipv4(ip):
                            valid_ips.append(ip)

    valid_ips = get_previously_selected_ips() + get_fixed_ips() + valid_ips
    valid_ips = list(set(valid_ips))
    print(f"共获取{len(valid_ips)}个IP")

    with open(os.path.join(download_folder, 'combined.txt'), 'w') as outfile:
        outfile.write('\n'.join(valid_ips))

    if os.path.exists('3ip.txt'):
        os.remove('3ip.txt')

    os.rename(os.path.join(download_folder, 'combined.txt'), '3ip.txt')

    print("此次优选IP已保存到3ip.txt")

# ... (rest of the code remains the same)

def run_cloudflare_speedtest():
    print("测速并生成result.csv...")
    with open('./config/cmd.txt', 'r') as file:
        cmd = file.readline().strip().split()
    cmd.extend(['-p', '0'])
    subprocess.run(cmd)

    print("测速完成，生成result.csv文件")

# ... (rest of the code remains the same)

def load_config():
    with open("config/config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
        email = config.get("email")
        global_api_key = config.get("global_api_key")
        zone_id = config.get("zone_id")
        domains = config.get("domains")
        if not email or not global_api_key or not zone_id or not domains:
            print("错误: config.json文件中缺少必要的key！")
            exit()
    return email, global_api_key, zone_id, domains

# ... (rest of the code remains the same)

if __name__=="__main__":
    main()
    print("10秒后自动退出程序")
    time.sleep(10)
