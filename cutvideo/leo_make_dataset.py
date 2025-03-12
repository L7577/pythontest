# Copyright (c) OpenMMLab. All rights reserved.
import os
import os.path as osp
import tempfile
from argparse import ArgumentParser
import csv
import mmcv
import numpy as np
from mmtrack.apis import inference_mot, init_model
import cv2
import sys
from collections import defaultdict
import json
import subprocess
from tqdm import tqdm

original_dir='G:/biyeshejishujuji/studentbehavior/'
class_name='handup'
original_folder_dir=original_dir+class_name+'/'
new_video_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/Capture_Video/'
new_new_video_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/New_Capture_Video/'

save_frame_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/Frames/'
if not os.path.exists(save_frame_dir):
    os.makedirs(save_frame_dir)
save_track_frame_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/Track_Frames/'
if not os.path.exists(save_track_frame_dir):
    os.makedirs(save_track_frame_dir)
new_save_track_frame_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/New_Track_Frames/'
if not os.path.exists(new_save_track_frame_dir):
    os.makedirs(new_save_track_frame_dir)
save_csv_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/MOT_CSV/'
if not os.path.exists(save_csv_dir):
    os.makedirs(save_csv_dir)
save_output_video_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/Tracker_Video/'
if not os.path.exists(save_output_video_dir):
    os.makedirs(save_output_video_dir)
new_save_output_video_dir = 'G:/biyeshejishujuji/studentbehavior/dataset/New_Tracker_Video/'
if not os.path.exists(new_save_output_video_dir):
    os.makedirs(new_save_output_video_dir)





min_num_of_chuxian=25
config = '../configs/mot/ocsort/ocsort_yolox_x_crowdhuman_mot17-private-half-leo.py'
backend = 'cv2'
score_thr = 0.0
show = False
checkpoint = None
fps = None
device = 'cuda:0'


def main():
    video_list = os.listdir(original_folder_dir)
    for video_name in video_list:
        original_video_dir = original_folder_dir + video_name
        orignal_dir = original_folder_dir + video_name
        # original_video_dir='G:/biyeshejishujuji/studentbehavior/handup/060.mp4'
        # orignal_dir = 'G:/biyeshejishujuji/studentbehavior/handup/060.mp4'
        # img_shape_1 = [458, 800]

        capture = cv2.VideoCapture(original_video_dir)
        frame_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        img_shape = [int(frame_height), int(frame_width)]
        # print(img_shape_1==img_shape)
        # 这里是新的保存视频帧和csv文件的地方

        video_name_item = original_video_dir.rsplit('/', 1)[-1]
        orignal_dir = original_video_dir  # 将每一个的名字拼接出来
        print('正在处理:' + video_name_item + '这个视频')
        video_name = orignal_dir.rsplit('/', 1)[-1]
        video_save_dir = save_output_video_dir + video_name
        new_video_save_dir = new_save_output_video_dir + video_name
        # 先做个实验试试可不可以解决问题
        # --output ../leo_work/output/test_video_2_oc.mp4
        assert video_save_dir or show
        # load images
        if osp.isdir(orignal_dir):
            imgs = sorted(
                filter(lambda x: x.endswith(('.jpg', '.png', '.jpeg')),
                       os.listdir(orignal_dir)),
                key=lambda x: int(x.split('.')[0]))
            IN_VIDEO = False
        else:
            imgs = mmcv.VideoReader(orignal_dir)
            IN_VIDEO = True
        # define output
        if video_save_dir is not None:
            if video_save_dir.endswith('.mp4'):
                OUT_VIDEO = True
                # 我打算不使用临时文件夹了因为这样得到的文件夹在C盘里面，很不容易找到
                out_path = save_track_frame_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '')
                new_out_path = new_save_track_frame_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '')
                _out = video_save_dir.rsplit(os.sep, 1)
                if len(_out) > 1:
                    os.makedirs(_out[0], exist_ok=True)
            else:
                OUT_VIDEO = False
                out_path = video_save_dir
                os.makedirs(out_path, exist_ok=True)

        fps = None
        if show or OUT_VIDEO:
            if fps is None and IN_VIDEO:
                fps = imgs.fps
            if not fps:
                raise ValueError('Please set the FPS for the output video.')
            fps = int(fps)

        # build the model from a config file and a checkpoint file
        model = init_model(config, checkpoint, device=device)
        prog_bar = mmcv.ProgressBar(len(imgs))
        # test and show/save the images
        if not os.path.exists(save_frame_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '')):
            os.makedirs(save_frame_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', ''))

        # 设计一个字典，用来保存重复出现的人的信息和最大的置信度
        people_score_dict = {}
        people_num_dict = {}
        result_dict = {}  # 为了更新后的结果造一个字典
        with open(save_csv_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '') + ".csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(['video_name', 'frams_id', 'L-U-X', 'L-U-Y', 'R-D-X', 'R-D-Y', 'tracking_id'])
            # 初始化一个json字典
            #        via3 = Via3Json(save_json_dir, mode='dump')
            #        vid_list = list(map(str, range(1, len(imgs) + 1)))
            #        via3.dumpPrejects(vid_list)
            #        via3.dumpConfigs()
            #        via3.dumpAttributes(attributes_dict)

            for i, img in enumerate(imgs):
                if isinstance(img, str):
                    img = osp.join(orignal_dir, img)
                result = inference_mot(model, img, frame_id=i)
                result['det_bboxes'] = [result['det_bboxes'][00]]
                result['track_bboxes'] = [result['track_bboxes'][00]]
                # 先将此时的result保存下来
                result_dict[i] = result
                if video_save_dir is not None:
                    if IN_VIDEO or OUT_VIDEO:
                        out_file = osp.join(out_path, f'{i:06d}.jpg')
                    else:
                        out_file = osp.join(out_path, img.rsplit(os.sep, 1)[-1])
                else:
                    out_file = None

                # leo认为detectbox用处没有trackerbox大

                # 保存原始图像
                cv2.imwrite(save_frame_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '') + '/' + f'{i:06d}.jpg',
                            img)
                aa = result['track_bboxes'][0]

                if len(result['track_bboxes'][0]):  # 检测到才写不检测到就不需要写
                    # 检测到了需要写入json文件
                    # fname是图片名字
                    #                files_dict[str(i)] = dict(fname=f'{i:06d}.jpg', type=2)
                    #                via3.dumpFiles(files_dict)
                    # 简单计数器
                    num = 1
                    for data in result['track_bboxes'][0]:
                        # 对这个人出现的次数进行统计
                        if not data[0] in people_num_dict.keys():
                            people_num_dict[data[0]] = 1  # 没出现过第一次出现次数记为1
                        else:
                            people_num_dict[data[0]] = people_num_dict[data[0]] + 1  # 之后每次出现次数+1

                        if not data[0] in people_score_dict.keys():
                            people_score_dict[data[0]] = data[5]  # 键是号，值是概率值
                        else:
                            people_score_dict[data[0]] = data[5] if data[5] > people_score_dict[data[0]] else \
                                people_score_dict[data[0]]
                        bboxes = [data[1], data[2], data[3], data[4]]
                        bboxes[0::2] = np.clip(bboxes[0::2], 0, img.shape[1]) / img.shape[1]
                        bboxes[1::2] = np.clip(bboxes[1::2], 0, img.shape[0]) / img.shape[0]
                        data_new = [orignal_dir.rsplit('/', 1)[-1].replace('.mp4', ''), str(i), bboxes[0], bboxes[1],
                                    bboxes[2], bboxes[3], data[0]]
                        writer.writerow(data_new)
                else:
                    data_new = [orignal_dir.rsplit('/', 1)[-1].replace('.mp4', ''), str(i), '', '',
                                '', '', '']
                    writer.writerow(data_new)
                #                    temp_w = data[3] - data[1]
                #                    temp_h = data[4] - data[2]
                #                    metadata_dict = dict(vid=str(i),
                #                                         xy=[2, float(data[1]), float(data[2]), float(temp_w), float(temp_h)],
                #                                         av={'1': '0'})

                #                    metadatas_dict['image{}_{}'.format(str(i), str(num))] = metadata_dict
                #                    num = num + 1
                #                via3.dumpMetedatas(metadatas_dict)

                #            else:#这种情况是没有检测到但是为了json文件还是需要写上
                #                files_dict[str(i)] = dict(fname=f'{i:06d}.jpg', type=2)
                #                via3.dumpFiles(files_dict)

                model.show_result(
                    img,
                    result,
                    score_thr=score_thr,
                    show=show,
                    wait_time=int(1000. / fps) if fps else 0,
                    out_file=out_file,
                    backend=backend)

                prog_bar.update()
        f.close()

        with open(save_csv_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '') + ".csv", "r", newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            f.close()
        with open(save_csv_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '') + '_new' + ".csv", "w",
                  newline="") as fw:
            writer = csv.writer(fw)
            writer.writerow(['video_name', 'frams_id', 'L-U-X', 'L-U-Y', 'R-D-X', 'R-D-Y', 'tracking_id'])
            for data_row in data:
                if (not data_row[6] == 'tracking_id'):
                    if data_row[6] == '':
                        writer.writerow(data_row)
                    else:
                        if (people_score_dict[float(data_row[6])] > 0.60) and (
                                people_num_dict[float(data_row[6])] > min_num_of_chuxian):
                            writer.writerow(data_row)
                        else:
                            data_row_new = [data_row[0], data_row[1], '', '',
                                            '', '', '']
                            writer.writerow(data_row_new)

                # if (not data_row[6] == 'tracking_id') and (people_score_dict[float(data_row[6])] > 0.60) and (
                #        people_num_dict[float(data_row[6])] > min_num_of_chuxian):
                #    writer.writerow(data_row)
                # else:
                #    if (not data_row[6] == 'tracking_id') and (data_row[6]==''):
                #        writer.writerow(data_row)
            fw.close()

        if video_save_dir and OUT_VIDEO:
            print(f'making the output video at {video_save_dir} with a FPS of {fps}')
            mmcv.frames2video(out_path, video_save_dir, fps=fps, fourcc='mp4v')
        # 使用修改完的trackbox再次展示在图片上
        # 如果该重识别编号最高置信度小于0.6就舍弃掉
        for i, img in enumerate(imgs):
            if isinstance(img, str):
                img = osp.join(orignal_dir, img)
            if new_video_save_dir is not None:
                if IN_VIDEO or OUT_VIDEO:
                    out_file = osp.join(new_out_path, f'{i:06d}.jpg')
                else:
                    out_file = osp.join(new_out_path, img.rsplit(os.sep, 1)[-1])
            else:
                out_file = None
            tmp_result = result_dict[i]
            tmp_track_bboxes = tmp_result['track_bboxes']
            new_track_bboxes = np.empty([0, 6], float)
            for data in tmp_track_bboxes[0]:
                # data[0]对应了重识别号，data[5]对应了概率值，但这个概率值没有用我们看的是最高概率值
                if people_score_dict[float(data[0])] > 0.60 and people_num_dict[float(data[0])] > min_num_of_chuxian:
                    # 应该是array而不是list,按行进行追加 #参考链接https://blog.csdn.net/shield911/article/details/124269761
                    new_track_bboxes = np.append(new_track_bboxes, values=data.reshape((1, 6)), axis=0)

            result_dict[i]['track_bboxes'] = [new_track_bboxes]
            new_result = result_dict[i]
            model.show_result(
                img,
                new_result,
                score_thr=score_thr,
                show=show,
                wait_time=int(1000. / fps) if fps else 0,
                out_file=out_file,
                backend=backend)
        if new_video_save_dir and OUT_VIDEO:
            print(f'making the new_output video at {new_video_save_dir} with a FPS of {fps}')
            mmcv.frames2video(new_out_path, new_video_save_dir, fps=fps, fourcc='mp4v')

        # 先将文件读进来然后依次将现存的人的信息显示出来

        if not os.path.exists(new_video_dir + class_name):
            os.makedirs(new_video_dir + class_name)
        if not os.path.exists(new_new_video_dir + class_name):
            os.makedirs(new_new_video_dir + class_name)
        with open(save_csv_dir + orignal_dir.rsplit('/', 1)[-1].replace('.mp4', '') + '_new' + ".csv", "r",
                  newline="") as fr:
            reader = csv.reader(fr)
            data = list(reader)
            fr.close()
        idlist = []
        for data_row in data:
            if data_row[0] == 'video_name':
                continue  # 第一行跳过
            if data_row[6] != '' and data_row[6] not in idlist:  # 人工观察是0.0号是老师
                idlist.append(data_row[6])  # 将不重复的编号全部剪辑出来再挑选
        for id_str in tqdm(idlist):
            # 现在的data中就是我之前准备好的数据了
            short_cut_dict = {}
            # 这就是我要追踪的位置坐上和右下坐标
            for data_row in data:
                if data_row[0] == 'video_name':
                    continue  # 第一行跳过
                if data_row[6] != '' and float(data_row[6]) == float(id_str):  # 人工观察是0.0号是老师
                    # 当前这种情况下data[2],data[3]是左上坐标，data[4],data[5]是右下坐标
                    if 'L-U-X' not in short_cut_dict.keys():
                        short_cut_dict['L-U-X'] = data_row[2]
                        # print('L-U-X已经第一次赋值值为：' + short_cut_dict['L-U-X'])
                    else:
                        if short_cut_dict['L-U-X'] > data_row[2]:
                            short_cut_dict['L-U-X'] = data_row[2]
                    if 'L-U-Y' not in short_cut_dict.keys():
                        short_cut_dict['L-U-Y'] = data_row[3]
                        # print('L-U-Y已经第一次赋值值为：' + short_cut_dict['L-U-Y'])
                    else:
                        if short_cut_dict['L-U-Y'] > data_row[3]:
                            short_cut_dict['L-U-Y'] = data_row[3]
                    if 'R-D-X' not in short_cut_dict.keys():
                        short_cut_dict['R-D-X'] = data_row[4]
                        # print('R-D-X已经第一次赋值值为：' + short_cut_dict['R-D-X'])
                    else:
                        if short_cut_dict['R-D-X'] < data_row[4]:
                            short_cut_dict['R-D-X'] = data_row[4]
                    if 'R-D-Y' not in short_cut_dict.keys():
                        short_cut_dict['R-D-Y'] = data_row[5]
                        # print('R-D-Y已经第一次赋值值为：' + short_cut_dict['R-D-Y'])
                    else:
                        if short_cut_dict['R-D-Y'] < data_row[5]:
                            short_cut_dict['R-D-Y'] = data_row[5]
            # 更新完成得到老师编号框的最大范围
            # print('左上坐标为：' + '(' + short_cut_dict['L-U-X'] + ',' + short_cut_dict['L-U-Y'] + ')')
            # print('右下坐标为：' + '(' + short_cut_dict['R-D-X'] + ',' + short_cut_dict['R-D-Y'] + ')')
            # 自动生成ffmpeg语句
            # 输入视频的默认宽高为640x360
            # 现在获得了可以

            new_short_cut_dict = {}
            new_short_cut_dict['L-U-X'] = float(short_cut_dict['L-U-X']) * img_shape[1]
            new_short_cut_dict['L-U-Y'] = float(short_cut_dict['L-U-Y']) * img_shape[0]
            new_short_cut_dict['R-D-X'] = float(short_cut_dict['R-D-X']) * img_shape[1]
            new_short_cut_dict['R-D-Y'] = float(short_cut_dict['R-D-Y']) * img_shape[0]
            # print('左上坐标为：' + '(' + str(new_short_cut_dict['L-U-X']) + ',' + str(new_short_cut_dict['L-U-Y']) + ')')
            # print('宽为：' + str(float(new_short_cut_dict['R-D-X']) - float(new_short_cut_dict['L-U-X'])) + '，高为' + str(
            #    float(new_short_cut_dict['R-D-Y']) - float(new_short_cut_dict['L-U-Y'])))
            w = float(new_short_cut_dict['R-D-X']) - float(new_short_cut_dict['L-U-X'])
            h = float(new_short_cut_dict['R-D-Y']) - float(new_short_cut_dict['L-U-Y'])

            # 构建FFmpeg命令
            ffmpeg_command = 'ffmpeg -loglevel quiet -i ' + orignal_dir + ' -vf crop=' + str(w) + ':' + str(
                h) + ':' + str(
                new_short_cut_dict['L-U-X']) + ':' + str(
                new_short_cut_dict['L-U-Y']) + ' ' + new_video_dir + class_name+'/' + \
                             orignal_dir.rsplit('/', 1)[-1][:-4] + '_' + id_str[:-2] + '.mp4' + ' -y'

            # 使用subprocess.Popen执行命令
            process = subprocess.Popen(ffmpeg_command, shell=True)
            # 等待进程完成
            process.wait()

        print('处理完成:' + video_name_item + '这个视频')
        # print('ffmpeg -i ' + orignal_dir + ' -vf crop=' + str(w) + ':' + str(h) + ':' + str(
        #    new_short_cut_dict['L-U-X']) + ':' + str(new_short_cut_dict['L-U-Y']) + ' ' + new_video_dir + 'handup/' +
        #      orignal_dir.rsplit('/', 1)[-1] + ' -y')
        # print('ffmpeg -i ' + new_video_dir + 'handup/' + orignal_dir.rsplit('/', 1)[
        #    -1] + ' -vf scale=iw:256' + ' ' + new_new_video_dir + 'handup/' + 'new_' + orignal_dir.rsplit('/', 1)[
        #          -1] + ' -y')




if __name__ == '__main__':
    main()
