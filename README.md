# CosyVoice_P

对CosyVoice的探索

‍

## 特点

* **对api支持**
* **STF生成函数**

  相关参数以及执行逻辑
* **文本预处理和裁剪精确度**

  可自行调节文本的预处理和裁剪精确度来调整显存的占用
* **每个yeild直接停顿**

  适当添加停顿优化语音效果

‍

## 相关文档

[针对每个yelid之间的停顿问题](https://github.com/PolarBear2333/Cosyvoice_P/tree/main/md/YeildPause.md)

[STF生成函数](https://github.com/PolarBear2333/Cosyvoice_P/tree/main/md/CosyVoiceSTF.md)

[文本预处理和裁剪](https://github.com/PolarBear2333/Cosyvoice_P/tree/main/md/Normalizer.md)

‍

‍

## **api相关**

#### api启动

​`python cosyvoice-api.py --port 50000 --model_dir pretrained_models/CosyVoice-300M-SFT`​

‍

#### 请求发送

1. 非流式

    ​`curl -X POST http://localhost:50000/ -H "Content-Type: application/json" -d '{"text": "你好", "speaker": "角色A"}'`​

2. 流式

    ​`curl -X POST http://localhost:50000/ -H "Content-Type: application/json" -d '{"text": "你好", "speaker": "角色A", "streaming": 1}'`​

3. 获取角色列表

    ​`curl -X GET http://localhost:50000/speakers`​

* **请求参数**：

  * ​`text`​：需要合成的文本（必填）。
  * ​`speaker`​：角色名（必填）。
  * ​`streaming`​：是否启用流式传输（可选，默认为 0）。
  * ​`speed`​：音频播放速度（可选，默认为 1.0）。

‍

#### 返回内容

1. **音频文件**：

    * WAV 格式（非流式模式）。
    * PCM 格式（流式模式）。
2. **错误信息**：

    * 如果缺少必填参数（如 `text`​ 或 `speaker`​），返回 JSON 格式的错误信息，HTTP 状态码为 400。
3. **角色列表**：

    * 返回一个 JSON 数组，包含所有可用的角色名。
