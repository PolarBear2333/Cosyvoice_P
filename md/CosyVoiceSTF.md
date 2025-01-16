# STF生成函数

```python
def inference_sft(self, tts_text, spk_id, stream=False, speed=1.0, text_frontend=True):
        for i in tqdm(self.frontend.text_normalize(tts_text, split=True, text_frontend=text_frontend)):
            model_input = self.frontend.frontend_sft(i, spk_id)
            start_time = time.time()
            logging.info('synthesis text {}'.format(i))
            for model_output in self.model.tts(**model_input, stream=stream, speed=speed):
                speech_len = model_output['tts_speech'].shape[1] / self.sample_rate
                logging.info('yield speech len {}, rtf {}'.format(speech_len, (time.time() - start_time) / speech_len))
                yield model_output
                start_time = time.time()
```

**函数参数**

1. ​**​`tts_text`​**​：

   * 输入的文本内容，需要被转换为语音。
   * 例如：`"你好，这是一个测试。"`​
2. ​**​`spk_id`​**​：

   * 说话人 ID，用于指定生成语音的说话人（声音风格）。
   * 例如：`"speaker_1"`​
3. ​**​`stream`​**​：

   * 是否启用流式输出模式。
   * 如果为 `True`​，则逐步生成语音片段；如果为 `False`​，则一次性生成完整语音。
   * 默认值：`False`​
4. ​**​`speed`​**​：

   * 语音生成的速度控制。
   * 例如：`1.0`​ 表示正常速度，`2.0`​ 表示两倍速，`0.5`​ 表示半速。
   * 默认值：`1.0`​
5. ​**​`text_frontend`​**​：

   * 是否使用前端文本处理。
   * 如果为 `True`​，则对输入文本进行归一化和分割；如果为 `False`​，则直接使用原始文本。
   * 默认值：`True`​

## 执行逻辑

### **1. 文本归一化与分割**

```python
for i in tqdm(self.frontend.text_normalize(tts_text, split=True, text_frontend=text_frontend)):
```

* **功能**：对输入的文本进行归一化和分割。
* **解释**：

  * ​`self.frontend.text_normalize(tts_text, split=True, text_frontend=text_frontend)`​：

    * 对 `tts_text`​ 进行归一化处理（如数字转中文、标点符号规范化等）。
    * 如果 `split=True`​，则将文本分割为多个句子或段落。
    * 返回一个文本列表，每个元素是一个句子或段落。
  * ​`tqdm`​：用于显示进度条，方便观察处理进度。
  * ​`for i in ...`​：遍历归一化和分割后的文本列表，逐句或逐段处理。

---

### **2. 模型输入准备**

```python
model_input = self.frontend.frontend_sft(i, spk_id)
```

* **功能**：将文本和说话人 ID 转换为模型所需的输入格式。
* **解释**：

  * ​`self.frontend.frontend_sft(i, spk_id)`​：

    * 将当前句子或段落 `i`​ 和说话人 ID `spk_id`​ 转换为模型输入。
    * 返回一个字典，包含文本的 token、说话人嵌入等信息。
  * ​`model_input`​：模型输入数据，传递给 TTS 模型。

---

### **3. 语音生成**

```python
for model_output in self.model.tts(**model_input, stream=stream, speed=speed):
```

* **功能**：调用 TTS 模型生成语音。
* **解释**：

  * ​`self.model.tts(**model_input, stream=stream, speed=speed)`​：

    * 使用模型输入 `model_input`​ 调用 TTS 模型。
    * ​`stream=stream`​：控制是否启用流式输出。
    * ​`speed=speed`​：控制语音生成的速度。
    * 返回一个生成器，逐步生成语音片段。
  * ​`for model_output in ...`​：遍历生成器，获取每个语音片段。

---

### **4. 语音片段处理**

```python
speech_len = model_output['tts_speech'].shape[1] / self.sample_rate
logging.info('yield speech len {}, rtf {}'.format(speech_len, (time.time() - start_time) / speech_len))
yield model_output
start_time = time.time()
```

* **功能**：处理生成的语音片段，并计算实时因子（RTF）。
* **解释**：

  * ​`model_output['tts_speech']`​：生成的语音片段，是一个 NumPy 数组或张量。
  * ​`speech_len = model_output['tts_speech'].shape[1] / self.sample_rate`​：

    * 计算语音片段的时长（秒）。
    * ​`shape[1]`​ 是语音片段的帧数，`self.sample_rate`​ 是采样率（如 16000 Hz）。
  * ​`logging.info(...)`​：记录语音片段的时长和实时因子（RTF）。

    * RTF（Real-Time Factor）表示生成语音所需的时间与实际语音时长的比值。
    * RTF \< 1 表示生成速度快于实时，RTF \> 1 表示生成速度慢于实时。
  * ​`yield model_output`​：将语音片段返回给调用者，支持流式输出。
  * ​`start_time = time.time()`​：重置计时器，用于计算下一个语音片段的 RTF。

‍

‍

## 关于函数的 `inference_sft` ​返回

​`inference_sft`​ 函数的返回格式是一个**生成器**（generator），它会逐步生成语音片段。每个语音片段是一个字典，包含生成的语音数据和其他相关信息。以下是返回格式的详细说明：

### **返回格式**

#### **生成器返回值**

* 每次调用 `yield model_output`​ 时，返回一个字典 `model_output`​，包含以下字段：

|字段名|数据类型|说明|
| --------| ------------| ----------------------------------------------------------------------|
|​`tts_speech`​|​`numpy.ndarray`​ 或 `torch.Tensor`​|生成的语音数据，形状为 `(1, T)`​，其中 `T`​ 是语音帧数。|
|​`sample_rate`​|​`int`​|语音的采样率（如 16000 Hz）。|
|其他字段|根据模型定义|可能包含其他模型输出的信息，如音素对齐、音高等（具体取决于模型实现）。|

**字段详细说明**

#### **1.**  **​`tts_speech`​**​

* **数据类型**：`numpy.ndarray`​ 或 `torch.Tensor`​
* **形状**：`(1, T)`​，其中 `T`​ 是语音帧数。
* **说明**：

  * 这是生成的语音数据，表示为一个单通道的音频信号。
  * 如果是 `numpy.ndarray`​，数据类型通常是 `float32`​，取值范围为 `[-1, 1]`​。
  * 如果是 `torch.Tensor`​，数据类型通常是 `torch.float32`​，取值范围为 `[-1, 1]`​。
* **示例**：

  ```
  tts_speech = model_output['tts_speech']  # 形状为 (1, T)
  ```

**2.**  **​`sample_rate`​**​

* **数据类型**：`int`​
* **说明**：

  * 语音的采样率，表示每秒的采样点数。
  * 常见的采样率有 16000 Hz、22050 Hz、44100 Hz 等。
* **示例**：

  ```
  sample_rate = model_output['sample_rate']  # 例如 16000
  ```

#### **3. 其他字段**

* **说明**：

  * 根据 TTS 模型的具体实现，`model_output`​ 可能包含其他字段，例如：

    * **音素对齐信息**：表示每个音素的起止时间。
    * **音高信息**：表示语音的音高变化。
    * **能量信息**：表示语音的能量变化。
  * 这些字段的具体内容和格式取决于模型的输出设计。

### **示例**

**生成器返回值示例**

假设 `model_output`​ 包含以下内容：

```python
{
    'tts_speech': np.array([[0.1, 0.2, 0.3, ...]], dtype=np.float32),  # 语音数据
    'sample_rate': 16000,  # 采样率
    'phoneme_alignment': [...],  # 音素对齐信息（可选）
    'pitch': [...]  # 音高信息（可选）
}
```

**使用示例**

```python
for model_output in cosyvoice.inference_sft("你好，这是一个测试。", "speaker_1", stream=True):
    tts_speech = model_output['tts_speech']  # 获取语音数据
    sample_rate = model_output['sample_rate']  # 获取采样率
    # 处理语音数据（例如保存为文件或播放）
    save_audio(tts_speech, sample_rate, "output.wav")
```

### **流式输出与非流式输出**

#### **1. 流式输出（**​**​`stream=True`​**​ **）**

* **行为**：

  * 逐步生成语音片段，每次 `yield`​ 返回一个语音片段。
  * 适用于实时语音合成场景，可以边生成边播放或传输。
* **示例**：

  ```python
  for model_output in cosyvoice.inference_sft("你好，这是一个测试。", "speaker_1", stream=True):
      tts_speech = model_output['tts_speech']
      play_audio(tts_speech, sample_rate)
  ```

#### **2. 非流式输出（**​**​`stream=False`​**​ **）**

* **行为**：

  * 一次性生成完整语音，`yield`​ 只返回一次。
  * 适用于非实时场景，需要等待完整语音生成后再处理。
* **示例**：

  ```python
  for model_output in cosyvoice.inference_sft("你好，这是一个测试。", "speaker_1", stream=False):
      tts_speech = model_output['tts_speech']
      save_audio(tts_speech, sample_rate, "output.wav")
  ```
