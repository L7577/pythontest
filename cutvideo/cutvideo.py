

import csv
import subprocess
import os

# 设置 ffmpeg 执行路径和文件夹路径
ffmpeg_path = "ffmpeg"  # 如果 ffmpeg 不在环境变量中，设置为 ffmpeg 的完整路径
video_folder = "videos"  # 存放原始视频文件的文件夹
csv_folder = "csv_files"  # 存放CSV文件的文件夹
output_folder = "output"  # 存放剪辑片段的文件夹

# 创建输出文件夹（如果不存在的话）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 读取时间戳 CSV 文件
def read_timestamps(csv_file):
    timestamps = []
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            start_time = float(row['开始时间'])
            end_time = float(row['结束时间'])
            timestamps.append({
                'start': start_time,
                'end': end_time,
                'clip_name': row['片段编号'],
                'category': row['类别']
            })
    return timestamps

# 使用 ffmpeg 剪辑视频
def clip_video(start_seconds, end_seconds, clip_name, video_file, category):
    # 创建类别文件夹，如果不存在
    category_folder = os.path.join(output_folder, category)
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    # 获取视频文件名（不含扩展名）
    base_video_name = os.path.splitext(os.path.basename(video_file))[0]

    # 生成唯一文件名（包含视频名、片段编号、开始和结束时间）
    output_filename = os.path.join(category_folder, f"{base_video_name}_{clip_name}.mp4")

    # ffmpeg 剪辑命令
    # command = [
    #     ffmpeg_path,
    #     '-i', video_file,  # 输入视频文件
    #     '-ss', str(start_seconds),  # 起始时间
    #     '-to', str(end_seconds),  # 结束时间
    #     '-c', 'copy',  # 直接复制视频流，避免重新编码
    #     '-copyts',  # 保持原始时间戳
    #     '-y',  # 自动覆盖输出文件
    #     output_filename  # 输出文件路径
    # ]
    command = [
    ffmpeg_path,
    '-i', video_file,  # 输入视频文件
    '-ss', str(start_seconds),  # 起始时间（从最接近的关键帧开始）
    '-to', str(end_seconds),  # 结束时间
    '-c', 'copy',  # 直接复制视频流，避免重新编码
    '-copyts',  # 保持原始时间戳
    '-y',  # 自动覆盖输出文件
    '-c:v', 'h264_nvenc',  # 使用 NVIDIA GPU 加速的 H.264 编码器（可选，具体根据硬件支持）
    '-c:a', 'aac',  # 音频编码（保持相同）
    output_filename  # 输出文件名
    ]

    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
        print(f"已创建片段: {output_filename}")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg 错误: {e.stderr.decode()}")

# 主函数
def main():
    # 获取 video_folder 中的所有视频文件
    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]

    # 遍历每个视频文件
    for video_file in video_files:
        # 构造对应的视频文件路径
        video_file_path = os.path.join(video_folder, video_file)

        # 根据视频文件名生成对应的 CSV 文件路径
        csv_file = os.path.join(csv_folder, f"{os.path.splitext(video_file)[0]}_timestamps.csv")
        print(csv_file)

        if os.path.exists(csv_file):
            # 读取时间戳信息
            timestamps = read_timestamps(csv_file)

            # 为每个时间段生成剪辑并根据类别存储
            for timestamp in timestamps:
                clip_video(timestamp['start'], timestamp['end'], timestamp['clip_name'], video_file_path, timestamp['category'])
        else:
            print(f"未找到与视频 {video_file} 对应的 CSV 文件，跳过处理。")

if __name__ == "__main__":
    main()
