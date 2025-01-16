import time
import io, os, sys
from flask_cors import CORS
import pyaudio
import numpy as np
from flask import Flask, request, Response
import torch
import torchaudio

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('{}'.format(ROOT_DIR))
sys.path.append('{}/third_party/Matcha-TTS'.format(ROOT_DIR))

from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav

# 初始化 CosyVoice 模型
cosyvoice = CosyVoice('pretrained_models/CosyVoice-300M-SFT')

app = Flask(__name__)
CORS(app)

# 初始化 PyAudio
p = pyaudio.PyAudio()
audio_stream = p.open(format=pyaudio.paFloat32,
                      channels=1,
                      rate=22050,  # 假设采样率为 22050
                      output=True)

@app.route("/inference/stream", methods=['POST'])
def stream():
    question_data = request.get_json()
    tts_text = question_data.get('query')
    
    if not tts_text:
        return {"error": "Query parameter 'query' is required"}, 400

    def generate_stream():
        # 使用内置音色进行流式语音合成
        for chunk in cosyvoice.inference_sft(tts_text, stream=True):
            float_data = chunk['tts_speech'].numpy().flatten()
            byte_data = float_data.tobytes()
            
            # 实时播放音频
            audio_stream.write(byte_data)
            yield byte_data

    return Response(generate_stream(), mimetype="audio/pcm")

def console_input():
    while True:
        text = input("请输入要合成的文本（输入 'exit' 退出）：")
        if text.lower() == 'exit':
            break
        
        # 使用内置音色进行流式语音合成
        for chunk in cosyvoice.inference_sft(text,'中文女',stream=True):
            float_data = chunk['tts_speech'].numpy().flatten()
            byte_data = float_data.tobytes()
            
            # 实时播放音频
            audio_stream.write(byte_data)
        
        print("语音合成完成")

if __name__ == "__main__":
    try:
        # 启动控制台输入模式
        console_input()
    finally:
        # 关闭 PyAudio 流
        audio_stream.stop_stream()
        audio_stream.close()
        p.terminate()