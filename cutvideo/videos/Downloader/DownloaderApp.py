import os
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import ffmpeg
import re

# 创建输出目录
def create_output_directories(base_dir):
    paths = ['downloads', 'decrypted', 'converted']
    for path in paths:
        dir_path = os.path.join(base_dir, path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    return {path: os.path.join(base_dir, path) for path in paths}

# 下载 .ts 文件
def download_ts_file(ts_url, output_dir):
    ts_filename = os.path.join(output_dir, os.path.basename(ts_url))
    
    # 如果文件已存在，跳过下载
    if os.path.exists(ts_filename):
        # print(f"文件已存在: {ts_filename}, 跳过下载")
        return ts_filename

    ts_response = requests.get(ts_url, stream=True)
    print(f"正在下载: {ts_url} 到 {ts_filename}")
    
    try:
        with open(ts_filename, 'wb') as ts_file:
            for chunk in ts_response.iter_content(chunk_size=8192):
                ts_file.write(chunk)
        print(f"下载完成: {ts_filename}")
        return ts_filename
    except Exception as e:
        print(f"错误: 下载文件失败 {ts_url} - {e}")
        return None

# 下载 m3u8 视频文件并解析
def download_m3u8_video_from_url(m3u8_url, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # 下载 m3u8 文件并解析
    m3u8_response = requests.get(m3u8_url)
    m3u8_content = m3u8_response.text

    # 提取加密信息
    encryption_info = extract_encryption_info(m3u8_content)
    is_encrypted = encryption_info is not None
    print(f"视频是否加密: {'是' if is_encrypted else '否'}")

    # 提取 .ts 文件的 URL
    ts_urls = [urljoin(m3u8_url, line) for line in m3u8_content.splitlines() if line.endswith('.ts')]

    print(f"找到 {len(ts_urls)} 个 .ts 文件，开始下载...")

    # 使用线程池下载 .ts 文件
    with ThreadPoolExecutor(max_workers=6) as executor:
        ts_files = list(executor.map(lambda url: download_ts_file(url, download_dir), ts_urls))

    return ts_files, encryption_info

# 从本地 m3u8 文件解析 .ts 文件
def download_m3u8_video_from_file(m3u8_file_path, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # 读取本地 m3u8 文件
    with open(m3u8_file_path, 'r') as m3u8_file:
        m3u8_content = m3u8_file.read()

    # 提取加密信息
    encryption_info = extract_encryption_info(m3u8_content)
    is_encrypted = encryption_info is not None
    print(f"视频是否加密: {'是' if is_encrypted else '否'}")

    # 提取 .ts 文件的 URL
    ts_urls = [line.strip() for line in m3u8_content.splitlines() if line.endswith('.ts')]

    print(f"找到 {len(ts_urls)} 个 .ts 文件，开始下载...")

    # 使用线程池下载 .ts 文件
    with ThreadPoolExecutor(max_workers=6) as executor:
        ts_files = list(executor.map(lambda url: download_ts_file(url, download_dir), ts_urls))

    return ts_files, encryption_info

# 下载密钥文件
def download_key_file(key_uri, base_url):
    # 如果 URI 是相对路径，组合成完整 URL
    full_url = urljoin(base_url, key_uri)
    print(f"密钥文件的完整 URL: {full_url}")
    
    response = requests.get(full_url)
    
    if response.status_code == 200:
        if len(response.content) != 16:
            print(f"错误: 下载的密钥不是16字节，而是 {len(response.content)} 字节")
            return None
        with open("enc.key", 'wb') as f:
            f.write(response.content)
        print("密钥文件下载成功")
        return response.content
    else:
        print(f"下载密钥文件失败: {full_url}")
        return None

# 解密 .ts 文件
def decrypt_ts_file(encrypted_file, key, iv, output_file):
    with open(encrypted_file, 'rb') as enc_file:
        encrypted_data = enc_file.read()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    try:
        with open(output_file, 'wb') as dec_file:
            dec_file.write(decrypted_data)
        # print(f"解密完成: {output_file}")
        return output_file
    except Exception as e:
        print(f"错误: 解密文件失败 {encrypted_file} - {e}")
        return None


import subprocess


# def convert_video(input_list_file, output_file, output_format='mp4'):
#     try:
#         # 构建 FFmpeg 命令
#         command = f"ffmpeg -f concat -safe 0 -i {input_list_file} -c copy {output_file}"

#         # 打印 FFmpeg 命令以调试
#         print(f"正在执行 FFmpeg 命令: {command}")

#         # 调用系统中的 FFmpeg
#         process = subprocess.run(command, shell=True, text=True, capture_output=True)

#         # 检查执行结果
#         if process.returncode == 0:
#             print(f"转换完成: {output_file}")
#         else:
#             print(f"FFmpeg 转换失败，错误码: {process.returncode}")
#             print(f"FFmpeg 输出: {process.stdout}")
#             print(f"FFmpeg 错误: {process.stderr}")

#     except Exception as e:
#         print(f"错误: FFmpeg 转换过程中出现异常: {e}")


# # 合并所有 .ts 文件
# def merge_ts_files(ts_files, output_file):
#     with open('concat_list.txt', 'w') as f:
#         for ts_file in ts_files:
#             f.write(f"file '{ts_file}'\n")
    
#     ffmpeg.input('concat_list.txt', format='concat', safe=0).output(output_file, vcodec='libx264', acodec='aac').run()
#     os.remove('concat_list.txt')  # 删除临时的 concat 文件
#     print(f"合并完成: {output_file}")


# 合并所有 .ts 文件并转换为指定格式
def merge_and_convert_ts_files(ts_files, output_file, output_format='mp4'):
    try:
        # 创建临时合并文件列表
        concat_list_file = 'concat_list.txt'
        with open(concat_list_file, 'w') as f:
            for ts_file in ts_files:
                f.write(f"file '{ts_file}'\n")

        # 构建 FFmpeg 命令进行合并
        merge_command = f"ffmpeg -f concat -safe 0 -i {concat_list_file} -c copy merged.ts"
        print(f"正在执行合并命令: {merge_command}")

        # 执行合并命令
        # process = subprocess.run(merge_command, shell=True, text=True, capture_output=True)

        # 检查合并结果
        # if process.returncode != 0:
        #     print(f"FFmpeg 合并失败，错误码: {process.returncode}")
        #     print(f"FFmpeg 输出: {process.stdout}")
        #     print(f"FFmpeg 错误: {process.stderr}")
        #     return

        print("合并完成: merged.ts")

        # 构建转换为目标格式的命令
        convert_command = f"ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda  -i merged.ts -c:v h264_nvenc  -b:v 5M -c:a aac {output_file}"
        # convert_command = f"ffmpeg -y -vsync 0 -i merged.ts -c:v h264_nvenc -b:v 5M -c:a aac {output_file}"

        print(f"正在执行转换命令: {convert_command}")

        # 执行转换命令
        convert_process = subprocess.run(convert_command, shell=True, text=True, capture_output=True)

        if convert_process.returncode == 0:
            print(f"转换完成: {output_file}")
        else:
            print(f"FFmpeg 转换失败，错误码: {convert_process.returncode}")
            print(f"FFmpeg 输出: {convert_process.stdout}")
            print(f"FFmpeg 错误: {convert_process.stderr}")

        # 删除临时合并文件
        # os.remove('concat_list.txt')
        # os.remove('merged.ts')

    except Exception as e:
        print(f"错误: FFmpeg 合并与转换过程中出现异常: {e}")




# 提取加密信息
def extract_encryption_info(m3u8_content):
    key_pattern = r'#EXT-X-KEY:METHOD=AES-128,URI="([^"]+)",IV=(0x[0-9A-Fa-f]+)'
    match = re.search(key_pattern, m3u8_content)
    
    if match:
        key_uri = match.group(1)
        iv_hex = match.group(2)
        try:
            iv_bytes = bytes.fromhex(iv_hex[2:])
            return {'iv': iv_bytes}
        except ValueError as e:
            print(f"错误: 无法解析 IV - {e}")
            return None
    else:
        print("未找到加密信息")
        return None

# 主函数
def main(m3u8_input, key_input, output_dir='./output'):
    if not m3u8_input or not key_input:
        print("错误: 请提供 m3u8 URL 或文件路径 和 密钥信息。")
        return

    directories = create_output_directories(output_dir)
    
    try:
        if len(key_input) == 32:  
            key = bytes.fromhex(key_input)
        else:
            with open(key_input, 'r') as key_file:
                hex_key = key_file.read().strip()
                if len(hex_key) == 32:
                    key = bytes.fromhex(hex_key)
                else:
                    print(f"错误: 密钥文件中的十六进制字符串长度不是32个字符，而是 {len(hex_key)} 个字符")
                    return
    except Exception as e:
        print(f"错误: 密钥加载失败: {str(e)}")
        return

    try:
        if m3u8_input.startswith('http') or m3u8_input.startswith('www'):
            ts_files, encryption_info = download_m3u8_video_from_url(m3u8_input, directories['downloads'])
            iv = encryption_info.get('iv')
            if iv:
                decrypted_files = []
                for ts_file in ts_files:
                    decrypted_file = os.path.join(directories['decrypted'], os.path.basename(ts_file).replace('.ts', '_decrypted.ts'))
                    decrypt_ts_file(ts_file, key, iv, decrypted_file)
                    decrypted_files.append(decrypted_file)
                # merged_video = os.path.join(directories['decrypted'], 'merged.ts')
                # merge_ts_files(decrypted_files, merged_video)
                # converted_video = os.path.join(directories['converted'], 'output.mp4')
                # convert_video(merged_video, converted_video)

                # merged_video = os.path.join(directories['decrypted'], 'merged.ts')
                converted_video = os.path.join(directories['converted'], 'output.mp4')

                # 合并并转换
                merge_and_convert_ts_files(decrypted_files, converted_video)

        else:
            ts_files, encryption_info = download_m3u8_video_from_file(m3u8_input, directories['downloads'])
            iv = encryption_info.get('iv')
            if iv:
                decrypted_files = []
                for ts_file in ts_files:
                    decrypted_file = os.path.join(directories['decrypted'], os.path.basename(ts_file).replace('.ts', '_decrypted.ts'))
                    decrypt_ts_file(ts_file, key, iv, decrypted_file)
                    decrypted_files.append(decrypted_file)
                # merged_video = os.path.join(directories['decrypted'], 'merged.ts')
                # merge_ts_files(decrypted_files, merged_video)
                # converted_video = os.path.join(directories['converted'], 'output.mp4')
                # convert_video(merged_video, converted_video)

                converted_video = os.path.join(directories['converted'], 'output.mp4')

                # 合并并转换
                merge_and_convert_ts_files(decrypted_files, converted_video)

        print("下载并处理完成")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python video_downloader.py <m3u8_url或文件路径> <密钥或密钥文件路径>")
    else:
        m3u8_input = sys.argv[1]
        key_input = sys.argv[2]
        main(m3u8_input, key_input)

