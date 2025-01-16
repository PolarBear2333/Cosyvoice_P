# 针对每个yeild之间的停顿问题

​`yeild` ​的返回只在 `stream = True` ​时才会返回

## 方案一

#### **在生成语音时添加静音段**

在每次 `yield`​ 返回语音片段之前，可以在语音数据中插入一段静音（silence），以模拟自然的停顿效果。

#### **实现方法**

* 静音段的长度 0.5 秒。
* 静音段的值通常为 `0`​（表示无声）。

以及针对语境进行停顿的调整

```python
import torch

def add_silence(sample_rate, silence_duration=0.5):
    """
    生成静音段。
  
    :param sample_rate: 采样率。
    :param silence_duration: 静音时长（秒），默认为 0.5 秒。
    :return: 静音段，类型为 torch.Tensor。
    """
    # 计算静音段的帧数
    silence_samples = int(silence_duration * sample_rate)
  
    # 创建静音段（torch.Tensor 格式）
    silence = torch.zeros((1, silence_samples), dtype=torch.float32)  # 假设数据类型为 torch.float32
    return silence

def inference_sft(self, tts_text, spk_id, stream=False, speed=1.0, text_frontend=True):
    # 对文本进行归一化和分割
    texts = list(self.frontend.text_normalize(tts_text, split=True, text_frontend=text_frontend))  # 显式转换为列表
  
    for idx, i in enumerate(tqdm(texts)):  # 使用 enumerate 获取索引
        model_input = self.frontend.frontend_sft(i, spk_id)
        start_time = time.time()
        logging.info('synthesis text {}'.format(i))
      
        # 生成语音
        for model_output in self.model.tts(**model_input, stream=stream, speed=speed):
            # 根据上下文添加静音段（如果需要）
            # model_output['tts_speech'] = add_contextual_silence(model_output['tts_speech'], self.sample_rate, i)
          
            # 计算语音时长和实时因子（RTF）
            speech_len = model_output['tts_speech'].shape[1] / self.sample_rate
            logging.info('yield speech len {}, rtf {}'.format(speech_len, (time.time() - start_time) / speech_len))
          
            # 返回语音片段
            yield model_output
            start_time = time.time()
      
        # 在每个部分生成语音后添加停顿
        if idx != len(texts) - 1:  # 如果不是最后一个部分，添加停顿
            silence = add_silence(self.sample_rate, silence_duration=0.5)  # 0.5 秒静音
            yield {'tts_speech': silence, 'sample_rate': self.sample_rate}
```

有关`add_silence`​函数中静音片段的形成说明

1. **输入和输出格式**：

    * 输入 `audio`​ 是一个 `torch.Tensor`​，形状为 `(1, T)`​，数据类型为 `torch.float32`​。
    * 输出也是一个 `torch.Tensor`​，形状为 `(1, T + silence_samples)`​，数据类型为 `torch.float32`​。
2. **静音段的创建**：

    * 使用 `torch.zeros`​ 创建静音段，确保其数据类型和设备与输入 `audio`​ 一致。
    * ​`dtype=audio.dtype`​：保持数据类型为 `torch.float32`​。
    * ​`device=audio.device`​：确保静音段与输入音频在同一个设备上（如 CPU 或 GPU）

## 方案二

如果你不希望修改生成器内部的逻辑，可以在调用生成器时，在每次 `yield`​ 之间手动添加停顿。

#### **实现方法**

* 使用 `time.sleep()`​ 在每次获取语音片段后暂停一段时间。
* 停顿的时长可以根据需要调整。

#### **代码示例**

```python
import time

for model_output in cosyvoice.inference_sft("你好，这是一个测试。", "speaker_1", stream=True):
    tts_speech = model_output['tts_speech']
    sample_rate = model_output['sample_rate']
  
    # 处理语音数据（例如播放或保存）
    play_audio(tts_speech, sample_rate)
  
    # 添加停顿
    time.sleep(0.2)  # 停顿 0.2 秒
```

## 方案三

在文本中标记停顿后，再提交给模型推理

目前 cosyvoice 好像不支持这种方法

‍
