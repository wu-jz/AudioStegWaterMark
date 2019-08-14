# -*- coding: utf-8 -*-
import wave
from time import time
import math
from pydub import AudioSegment
import lsb_interleave_bytes, lsb_deinterleave_bytes


# 通过解析wav文件进行隐写内容添加并输出添加后的文件(python中默认解析wav格式)
# sound_path:音频路径  file_data:隐写内容  output_path:文件输出路径  num_lsb:替换最低有效位位数
def add_steg_in_wav(sound_path, file_data, output_path, num_lsb):
    start = time()  # 计算程序总运行时间
    sound = wave.open(sound_path, "r")  # 读取文件

    params = sound.getparams()  # 获取文件参数
    num_channels = sound.getnchannels()  # 单双声道
    sample_width = sound.getsampwidth()  # 字节宽度
    num_frames = sound.getnframes()  # 采样频率

    # 每个文件可以隐藏最多的num_lsb位
    num_samples = num_frames * num_channels
    max_bytes_to_hide = (num_samples * num_lsb) // 8
    file_data_size = len(file_data)
    print(f"Using {num_lsb} LSBs, we can hide {max_bytes_to_hide} bytes")

    # 返回最大n帧的音频
    sound_frames = sound.readframes(num_frames)
    print(f"Files read".ljust(30) + f" in {time() - start:.2f}s")

    # 隐写内容过大
    if file_data_size > max_bytes_to_hide:
        required_lsb = math.ceil(file_data_size * 8 / num_samples)
        raise ValueError(
            "Input file too large to hide, "
            "requires {} LSBs, using {}".format(required_lsb, num_lsb)
        )

    # 音频模式（wav）不支持更高的字节宽度
    if sample_width != 1 and sample_width != 2:
        raise ValueError("File has an unsupported bit-depth")

    steg_start = time()  # 计算添加隐写内容需要的时间
    sound_frames = lsb_interleave_bytes(
        sound_frames, file_data, num_lsb, max_bytes_to_hide, byte_depth=sample_width
    )
    print(f"steg done! {file_data_size} bytes hidden".ljust(30) + f" in {time() - steg_start:.2f}s")

    # 将添加过隐写内容的音频数据写入新的音频文件中
    sound_steg = wave.open(output_path, "w")
    sound_steg.setparams(params)
    sound_steg.writeframes(sound_frames)
    sound_steg.close()
    print(f"Output steg wav written ! ".ljust(30) + f" in {time() - start:.2f}s")


# 通过解析所有类型音频文件进行隐写内容添加，最后输出为wav格式文件(使用pydub)
# sound_path:音频路径  file_data:隐写内容  output_path:文件输出路径  num_lsb:替换最低有效位位数
def hide_data_audio_type_to_wav(sound_path, file_data, output_path, num_lsb):
    start = time()  # 计算程序总运行时间
    # 通过pydub解析音频
    sound = AudioSegment.from_file(sound_path)
    num_channels = sound.channels  # 单双声道
    sample_width = sound.sample_width  # 字节宽度
    frame_rate = sound.frame_rate
    num_frames = sound.frame_count()  # 采样频率

    # 每个文件可以隐藏最多的num_lsb位
    num_samples = num_frames * num_channels
    max_bytes_to_hide = (num_samples * num_lsb) // 8
    file_data_size = len(file_data)
    print(f"Using {num_lsb} LSBs, we can hide {max_bytes_to_hide} bytes")

    # 返回最大n帧的音频
    sound_frames = sound.raw_data

    # 隐写内容过大
    if file_data_size > max_bytes_to_hide:
        required_lsb = math.ceil(file_data_size * 8 / num_samples)
        raise ValueError(
            "Input file too large to hide, "
            "requires {} LSBs, using {}".format(required_lsb, num_lsb)
        )

    steg_start = time()  # 计算添加隐写内容需要的时间
    sound_frames = lsb_interleave_bytes(
        sound_frames, file_data, num_lsb, max_bytes_to_hide, byte_depth=sample_width
    )
    print(f"steg done! {file_data_size} bytes hidden".ljust(30) + f" in {time() - steg_start:.2f}s")

    # 将添加过隐写内容的音频数据写入新的音频文件中（全部转为wav格式）
    analysis_wav = AudioSegment(
        data=sound_frames,
        sample_width=sample_width,
        frame_rate=frame_rate,
        channels=num_channels
    )
    analysis_wav.export(output_path, format='wav')
    print(f"Output steg wav written".ljust(30) + f" in {time() - start:.2f}s")


# 解析wav文件返回隐写内容
# sound_path:音频路径  num_lsb:替换最低有效位位数  bytes_to_recover:隐写内容位数
def recover_data_wav(sound_path, num_lsb, bytes_to_recover):
    start = time()
    sound = wave.open(sound_path, "r")
    # 获取音频的相关信息
    sample_width = sound.getsampwidth()
    num_frames = sound.getnframes()
    sound_frames = sound.readframes(num_frames)
    # 解析音频文件
    data = lsb_deinterleave_bytes(
        sound_frames, 8 * bytes_to_recover, num_lsb, byte_depth=sample_width
    )
    print(f"Recovered {bytes_to_recover} bytes".ljust(30) + f" in {time() - start:.2f}s")
    return data
