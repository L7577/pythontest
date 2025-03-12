# import os
# import requests
# from urllib.parse import urljoin

# 函数：下载 m3u8 文件中的 .ts 视频片段和 key 文件
# def bk_download_m3u8_video(m3u8_url, key_url, output_dir):
#     # 创建输出目录
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # 下载 key 文件
#     key_response = requests.get(key_url)
#     key_path = os.path.join(output_dir, 'key.key')
#     with open(key_path, 'wb') as key_file:
#         key_file.write(key_response.content)

#     # 下载 m3u8 文件并解析
#     m3u8_response = requests.get(m3u8_url)
#     m3u8_content = m3u8_response.text

#     # 提取 .ts 文件的 URL
#     ts_urls = []
#     for line in m3u8_content.splitlines():
#         if line.endswith('.ts'):
#             ts_urls.append(urljoin(m3u8_url, line))

#     # 下载 .ts 文件
#     ts_files = []
#     for ts_url in ts_urls:
#         ts_response = requests.get(ts_url)
#         ts_filename = os.path.join(output_dir, os.path.basename(ts_url))
#         with open(ts_filename, 'wb') as ts_file:
#             ts_file.write(ts_response.content)
#         ts_files.append(ts_filename)
    
#     return ts_files, key_path

# # ts_files, key_path = download_m3u8_video(m3u8_url, key_url, output_dir)
# # print(f"下载完成，.ts 文件保存在: {ts_files}")
# # print(f"密钥文件保存在: {key_path}")

# from concurrent.futures import ThreadPoolExecutor


# # 下载 .ts 文件的函数
# def download_ts_file(ts_url, output_dir):
#     ts_response = requests.get(ts_url, stream=True)
#     ts_filename = os.path.join(output_dir, os.path.basename(ts_url))
#     with open(ts_filename, 'wb') as ts_file:
#         for chunk in ts_response.iter_content(chunk_size=8192):
#             ts_file.write(chunk)
#     return ts_filename

# # 主函数：使用线程池下载所有 .ts 文件
# def download_m3u8_video(m3u8_url, key_url, output_dir):
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # 下载 key 文件
#     key_response = requests.get(key_url)
#     key_path = os.path.join(output_dir, 'key.key')
#     with open(key_path, 'wb') as key_file:
#         key_file.write(key_response.content)

#     # 下载 m3u8 文件并解析
#     m3u8_response = requests.get(m3u8_url)
#     m3u8_content = m3u8_response.text

#     # 提取 .ts 文件的 URL
#     ts_urls = []
#     for line in m3u8_content.splitlines():
#         if line.endswith('.ts'):
#             ts_urls.append(urljoin(m3u8_url, line))

#     # 使用 ThreadPoolExecutor 下载 .ts 文件
#     ts_files = []
#     with ThreadPoolExecutor(max_workers=6) as executor:  # max_workers 可以调整线程数
#         ts_files = list(executor.map(lambda url: download_ts_file(url, output_dir), ts_urls))

#     return ts_files, key_path

# ts_files, key_path = download_m3u8_video(m3u8_url, key_url, output_dir)
# print(f"下载完成，.ts 文件保存在: {ts_files}")
# print(f"密钥文件保存在: {key_path}")


#############################################################################

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

# 下载 .ts 文件的函数
def download_ts_file(ts_url, output_dir):
    ts_response = requests.get(ts_url, stream=True)
    ts_filename = os.path.join(output_dir, os.path.basename(ts_url))
    with open(ts_filename, 'wb') as ts_file:
        for chunk in ts_response.iter_content(chunk_size=8192):
            ts_file.write(chunk)
    return ts_filename

# 主函数：使用线程池下载所有 .ts 文件
def download_m3u8_video(m3u8_url, key_url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 下载 key 文件
    key_response = requests.get(key_url)
    key_path = os.path.join(output_dir, 'key.key')
    with open(key_path, 'wb') as key_file:
        key_file.write(key_response.content)

    # 下载 m3u8 文件并解析
    m3u8_response = requests.get(m3u8_url)
    m3u8_content = m3u8_response.text

    # 提取 .ts 文件的 URL
    ts_urls = []
    for line in m3u8_content.splitlines():
        if line.endswith('.ts'):
            ts_urls.append(urljoin(m3u8_url, line))

    # 使用 ThreadPoolExecutor 下载 .ts 文件
    ts_files = []
    with ThreadPoolExecutor(max_workers=6) as executor:  # max_workers 可以调整线程数
        futures = [executor.submit(download_ts_file, url, output_dir) for url in ts_urls]

        # 使用 as_completed 处理每个已完成的任务
        for future in as_completed(futures):
            ts_file = future.result()  # 获取下载的文件路径
            ts_files.append(ts_file)

    return ts_files, key_path


# 示例调用
m3u8_url = 'https://v.gsuus.com/play/Qe18OjdJ/index.m3u8'
key_url = 'https://v.gsuus.com/play/Qe18OjdJ/enc.key'
output_dir = './video_downloads'


ts_files, key_path = download_m3u8_video(m3u8_url, key_url, output_dir)
print(f"下载完成，.ts 文件保存在: {ts_files}")
print(f"密钥文件保存在: {key_path}")