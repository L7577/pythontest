# import concurrent.futures
# import time
# import requests
# import os
# import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup

# # 设置下载目录
# download_folder = "downloaded_videos"
# if not os.path.exists(download_folder):
#     os.makedirs(download_folder)

# # 设置记录文件
# record_file = "valid_video_urls.csv"  # 记录有效的视频ID和URL

# # 配置Selenium WebDriver（假设使用Chrome浏览器）
# def setup_selenium_driver():
#     chrome_driver_path = '/home/l/test/video-dd/chromedriver-linux64/chromedriver'  # 替换为你的ChromeDriver路径
#     service = Service(chrome_driver_path)
#     options = Options()
#     options.add_argument('--headless')  # 无头模式（可选）
#     options.add_argument('--disable-gpu')  # 禁用GPU硬件加速
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.implicitly_wait(10)  # 等待页面加载完成
#     return driver

# # 获取视频页面的URL
# def get_video_url_by_id(driver, video_id):
#     url = f"https://gzseduyun.cn:9003/web/ExcellentCourse/excellentshow.html?id={video_id}"
#     driver.get(url)
#     time.sleep(3)  # 控制加载时间

#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     video_tag = soup.find('video')
#     if video_tag:
#         video_url = video_tag.get('src') or video_tag.find('source').get('src') if video_tag.find('source') else None
#         return video_url
#     return None

# # 判断视频URL是否有效（通过HEAD请求）
# def is_video_url_valid(video_url):
#     try:
#         response = requests.head(video_url, allow_redirects=True, timeout=5)
#         if response.status_code == 200:
#             return True
#         return False
#     except requests.RequestException as e:
#         print(f"Error checking video URL {video_url}: {e}")
#         return False

# # 记录有效的视频ID和URL
# def record_valid_video(video_id, video_url):
#     with open(record_file, 'a', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerow([video_id, video_url])
#         print(f"Recorded video {video_id} with URL {video_url}")

# # 批量收集有效视频URL，使用多线程提高速度
# def collect_valid_video_urls(start_id, end_id):
#     valid_video_count = 0
#     driver = setup_selenium_driver()

#     with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:  # 设定并发线程数
#         futures = []
#         for video_id in range(start_id, end_id + 1):
#             futures.append(executor.submit(process_video, driver, video_id))
        
#         for future in concurrent.futures.as_completed(futures):
#             result = future.result()
#             if result:
#                 valid_video_count += 1

#     print(f"Total valid videos found: {valid_video_count}")
#     driver.quit()

# # 处理视频，获取URL并验证
# def process_video(driver, video_id):
#     print(f"Processing video {video_id}...")
#     video_url = get_video_url_by_id(driver, video_id)
#     if video_url and is_video_url_valid(video_url):
#         record_valid_video(video_id, video_url)  # 记录有效的视频地址
#         return True
#     else:
#         print(f"No valid video found for id {video_id}. Skipping...")
#         return False

# # 下载视频文件
# def download_video(video_url, video_id):
#     try:
#         response = requests.get(video_url, stream=True, timeout=10)
#         if response.status_code == 200:
#             file_name = f"video_{video_id}.mp4"
#             file_path = os.path.join(download_folder, file_name)
#             with open(file_path, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)
#             print(f"Video {video_id} downloaded successfully!")
#             return True
#         else:
#             print(f"Failed to download video {video_id}. Status code: {response.status_code}")
#             return False
#     except Exception as e:
#         print(f"Error downloading video {video_id}: {e}")
#         return False

# # 批量下载有效视频，使用多线程
# def batch_download_valid_videos():
#     with open(record_file, 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # 限制最大线程数
#             futures = []
#             for row in reader:
#                 video_id, video_url = row
#                 futures.append(executor.submit(download_video, video_url, video_id))

#             for future in concurrent.futures.as_completed(futures):
#                 future.result()

# # 假设从id=100到id=1000
# collect_valid_video_urls(900, 1000)  # 收集并记录有效的视频地址
# batch_download_valid_videos()  # 下载所有有效的视频

import concurrent.futures
import time
import requests
import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 设置下载目录
download_folder = "downloaded_videos"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 设置记录文件
record_file = "valid_video_urls.csv"  # 记录有效的视频ID和URL

# 配置Selenium WebDriver（假设使用Chrome浏览器）
def setup_selenium_driver():
    chrome_driver_path = '/home/l/test/video-dd/chromedriver-linux64/chromedriver'  # 替换为你的ChromeDriver路径
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument('--headless')  # 无头模式（可选）
    options.add_argument('--disable-gpu')  # 禁用GPU硬件加速
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)  # 等待页面加载完成
    return driver

# 获取视频页面的URL
def get_video_url_by_id(driver, video_id):
    url = f"https://gzseduyun.cn:9003/web/ExcellentCourse/excellentshow.html?id={video_id}"
    driver.get(url)
    time.sleep(3)  # 控制加载时间

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    video_tag = soup.find('video')
    if video_tag:
        video_url = video_tag.get('src') or video_tag.find('source').get('src') if video_tag.find('source') else None
        return video_url
    return None

# 判断视频URL是否有效（通过HEAD请求）
def is_video_url_valid(video_url):
    try:
        response = requests.head(video_url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException as e:
        print(f"Error checking video URL {video_url}: {e}")
        return False

# 记录有效的视频ID和URL
def record_valid_video(video_id, video_url):
    with open(record_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([video_id, video_url])
        print(f"Recorded video {video_id} with URL {video_url}")

# 处理视频，获取URL并验证
def process_video(video_id):
    driver = setup_selenium_driver()  # 每个线程都使用独立的 driver 实例
    print(f"Processing video {video_id}...")
    video_url = get_video_url_by_id(driver, video_id)
    driver.quit()  # 处理完后退出 driver

    if video_url and is_video_url_valid(video_url):
        record_valid_video(video_id, video_url)  # 记录有效的视频地址
        return True
    else:
        print(f"No valid video found for id {video_id}. Skipping...")
        return False

# 批量收集有效视频URL，使用并行化提高速度
def collect_valid_video_urls(start_id, end_id):
    valid_video_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:  # 设置最大并发数
        futures = [executor.submit(process_video, video_id) for video_id in range(start_id, end_id + 1)]
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                valid_video_count += 1

    print(f"Total valid videos found: {valid_video_count}")

# 下载视频文件
def download_video(video_url, video_id):
    try:
        response = requests.get(video_url, stream=True, timeout=10)
        if response.status_code == 200:
            file_name = f"video_{video_id}.mp4"
            file_path = os.path.join(download_folder, file_name)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Video {video_id} downloaded successfully!")
            return True
        else:
            print(f"Failed to download video {video_id}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading video {video_id}: {e}")
        return False

# 批量下载有效视频，使用并行化
def batch_download_valid_videos():
    with open(record_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:  # 限制最大线程数
            futures = []
            for row in reader:
                video_id, video_url = row
                futures.append(executor.submit(download_video, video_url, video_id))

            for future in concurrent.futures.as_completed(futures):
                future.result()

# 假设从id=900到id=1000
collect_valid_video_urls(602, 603)  # 收集并记录有效的视频地址
batch_download_valid_videos()  # 下载所有有效的视频
