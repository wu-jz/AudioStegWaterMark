import audio_steg_util

hidden_text = b"ip-name-addr"
lsb_num = 1
wav_file_path = "G:/test/audio.wav"
mp3_file_path = "G:/test/audio.mp3"
analysis_wav_file_path = "G:/test/audio_steg.wav"
# 截断测试地址
# analysis_wav_file_path = "G:/test/steg_new.wav"

def wav_steg_by_path():
    # 对wav格式音频添加隐写内容
    audio_steg_util.add_steg_in_wav(wav_file_path, hidden_text, analysis_wav_file_path, lsb_num)
    # 对mp3格式音频添加隐写内容
    # audio_steg_util.add_steg_in_audio(mp3_file_path, hidden_text, analysis_wav_file_path, lsb_num)
    
def wav_analysis_by_path():
    # 恢复信息
    analysis_text = audio_steg_util.recover_data_wav(analysis_wav_file_path, lsb_num, len(hidden_text))
    if hidden_text in analysis_text:
        print("get hidden_text :" + str(analysis_text))
    else:
        print("the file is truncated...")
        # 判断为文件进行了截断，再根据实际情况添加更大位进行隐写内容判断(测试鲁棒性)
        analysis_text = audio_steg_util.recover_data_wav(analysis_wav_file_path, lsb_num, 5000)
        if hidden_text in analysis_text:
            print(analysis_text)
        else:
            print("none")


if __name__ == '__main__':
    wav_steg_by_path()
    wav_analysis_by_path()
