import os
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import subprocess

# 解密 .ts 文件
def decrypt_ts(ts_file_path, key_file_path, output_dir, index):
    # 读取密钥
    with open(key_file_path, 'rb') as key_file:
        key = key_file.read()

    # 使用 AES 解密
    cipher = AES.new(key, AES.MODE_CBC, iv=b'\x00' * 16)  # 假设 IV 是全 0，根据实际情况调整
    with open(ts_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    # 创建新文件名，并保存解密后的 .ts 文件
    decrypted_ts_filename = os.path.join(output_dir, f"decrypted_{index}.ts")
    with open(decrypted_ts_filename, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

    return decrypted_ts_filename

# 解密所有 .ts 文件并保存到新的文件夹
def decrypt_ts_files(ts_files, key_file_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    decrypted_ts_files = []
    for index, ts_file in enumerate(ts_files, start=1):
        decrypted_ts_file = decrypt_ts(ts_file, key_file_path, output_dir, index)
        decrypted_ts_files.append(decrypted_ts_file)
        print(f"解密完成，保存为 {decrypted_ts_file}")

    return decrypted_ts_files

# 使用 FFmpeg 合并 .ts 文件并转换为 .mp4
def merge_ts_files(ts_files, output_file):
    # 生成 FFmpeg 需要的文本文件列表
    with open('ts_list.txt', 'w') as list_file:
        for ts_file in ts_files:
            list_file.write(f"file '{ts_file}'\n")

    # 使用 FFmpeg 合并 .ts 文件并转换为 .mp4 格式
    command = f"ffmpeg -f concat -safe 0 -i ts_list.txt -c copy {output_file}"
    subprocess.run(command, shell=True)

    # 删除临时的 ts_list.txt 文件
    os.remove('ts_list.txt')

# 自动扫描文件夹中的 .ts 文件，并按升序排序
def get_ts_files_from_directory(directory):
    # 获取指定目录中所有 .ts 文件
    ts_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.ts')]
    
    # 提取文件名中的数字部分进行排序，使用正则提取数字
    ts_files.sort(key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1)))
    
    return ts_files

# 主函数：解密并合并视频
def decrypt_and_merge_video(ts_dir, key_file_path, output_dir, output_file):
    # 获取目录中所有的 .ts 文件，并按顺序排序
    ts_files = get_ts_files_from_directory(ts_dir)

    if not ts_files:
        print("未找到 .ts 文件，请确认目录是否正确。")
        return

    print(f"找到 {len(ts_files)} 个 .ts 文件，开始解密...")

    # 解密所有 .ts 文件
    decrypted_ts_files = decrypt_ts_files(ts_files, key_file_path, output_dir)
    print(f"所有解密文件已保存到: {output_dir}")

    # 合并解密后的 .ts 文件
    merge_ts_files(decrypted_ts_files, output_file)
    print(f"合并完成，输出为 {output_file}")

# 示例调用
ts_dir = './video_downloads'   # 存放 .ts 文件的目录
key_file_path = './video_downloads/key.key'
output_dir = './decrypted_video_files'
output_file = './video_output.mp4'

# 调用主函数
decrypt_and_merge_video(ts_dir, key_file_path, output_dir, output_file)
