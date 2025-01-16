# 文本的预处理和裁剪

## 文本裁切精度调整

将文本更精细的分割以显存用量降低

**在**​**cosyvoice/utils/frontend_utils.py****中**		**split_paragraph函数****负责中文裁切**

​`def split_paragraph(text: str, tokenize, lang="zh", token_max_n=80, token_min_n=60, merge_len=20, comma_split=False):`​

1. **参数说明**：

* ​`text`​：输入的文本。
* ​`tokenize`​：一个函数，用于计算文本的长度（对于英文，可能是分词后的长度）。
* ​`lang`​：语言类型，默认为中文（`"zh"`​）。
* ​`token_max_n`​：每个段落的最大长度（以字符或 token 为单位）。
* ​`token_min_n`​：每个段落的最小长度（以字符或 token 为单位）。
* ​`merge_len`​：如果段落长度小于此值，则将其与前一个段落合并。
* ​`comma_split`​：是否将逗号（`,`​）作为分割点。

2. **主要逻辑**：

* **标点符号处理**：

  * 根据语言类型（中文或英文）定义不同的标点符号列表。
  * 如果文本末尾没有标点符号，自动添加句号（`.`​ 或 `。`​）。
* **文本分割**：

  * 遍历文本，按照标点符号进行分割，并将分割后的段落存储在 `utts`​ 列表中。
  * 处理引号（`"`​ 或 `”`​）等特殊情况。
* **段落合并**：

  * 根据 `token_max_n`​ 和 `token_min_n`​ 的规则，将分割后的段落进行合并。
  * 如果某个段落的长度小于 `merge_len`​，则将其与前一个段落合并。

3. **返回值**：

* 返回一个列表，包含最终的分割和合并后的段落。

**在句号（**​ **​`。`​**​ **）、感叹号（**​ **​`！`​**​ **）和问号（**​ **​`？`​**​ **）处忽略长度限制，进行强制分割，可以在** **​`split_paragraph`​** **函数中添加一个逻辑，判断当前标点符号是否为强制分割的标点符号（句号、感叹号、问号），如果是，则无论当前段落的长度如何，都进行强制分割。**

新增：

```undefined
 # 强制分割的标点符号
    force_split_pounc = ['。', '？', '！', '.', '?', '!']
```

对合并段落重新编写

```python
# 合并段落
    final_utts = []
    cur_utt = ""
    for utt in utts:
        # 判断当前段落的最后一个字符是否为强制分割的标点符号
        if utt[-1] in force_split_pounc:
            # 如果是强制分割的标点符号，则直接分割
            if len(cur_utt) > 0:
                final_utts.append(cur_utt)
            final_utts.append(utt)
            cur_utt = ""
        else:
            # 否则按原有逻辑合并
            if calc_utt_length(cur_utt + utt) > token_max_n and calc_utt_length(cur_utt) > token_min_n:
                final_utts.append(cur_utt)
                cur_utt = ""
            cur_utt = cur_utt + utt

    # 处理剩余的段落
    if len(cur_utt) > 0:
        if should_merge(cur_utt) and len(final_utts) != 0:
            final_utts[-1] = final_utts[-1] + cur_utt
        else:
            final_utts.append(cur_utt)
```

‍

## 文本**预处理**

**在cosyvoice/cli/frontend.py中	CosyVoiceFrontEnd中的text_normalize函数负责文本预处理和裁切**

​`contains_chinese`​为对中文的预处理

‍

**1.**  **​`text = self.zh_tn_model.normalize(text)`​** ​

* **功能**：对文本进行**归一化处理**。

  * ​`self.zh_tn_model.normalize(text)`​ 是一个文本归一化模型（可能是基于规则或机器学习的模型），用于将文本中的非标准字符、数字、符号等转换为标准的中文表达。

    * 将 `123`​ 转换为 `一百二十三`​。
    * 将 `1/2`​ 转换为 `二分之一`​。
    * 将 `2023年`​ 转换为 `二零二三年`​。

---

**2.**  **​`text = text.replace("\n", "")`​** ​

* **功能**：移除文本中的**换行符**。

  * ​`\n`​ 是换行符，表示文本中的换行。
  * 通过 `replace("\n", "")`​，将所有换行符替换为空字符串，即将换行符移除。

---

**3.**  **​`text = replace_blank(text)`​** ​

* **功能**：移除文本中的**多余空白字符**。

  * ​`replace_blank(text)`​ 是一个自定义函数，用于移除文本中的多余空格、制表符等空白字符。
  * 例如：

    * 将 `"你好 世界"`​ 替换为 `"你好世界"`​。

---

**4.**  **​`text = replace_corner_mark(text)`​** ​

* **功能**：替换文本中的**角标符号**。

  * ​`replace_corner_mark(text)`​ 是一个自定义函数，用于处理文本中的角标符号（如 `™`​、`®`​、`©`​ 等）。
  * 例如：

    * 将 `"Python™"`​ 替换为 `"Python"`​。

---

### **5.**  **​`text = text.replace(".", "。")`​** ​

* **功能**：将英文句号（`.`​）替换为中文句号（`。`​）。

  * 英文句号 `.`​ 和中文句号 `。`​ 在语义上是等价的，但在中文文本中通常使用中文句号。
  * 通过 `replace(".", "。")`​，将所有英文句号替换为中文句号。

---

**6.**  **​`text = text.replace(" - ", "，")`​** ​

* **功能**：将 `" - "`​ 替换为中文逗号（`，`​）。

  * ​`" - "`​ 是一种常见的连接符号，通常用于表示停顿或分隔。
  * 通过 `replace(" - ", "，")`​，将其替换为中文逗号。

---

**7.**  **​`text = remove_bracket(text)`​** ​

* **功能**：移除文本中的**括号及其内容**。

  * ​`remove_bracket(text)`​ 是一个自定义函数，用于移除文本中的括号（如 `()`​、`[]`​、`{}`​）及其内部的内容。

    * 将 `"这是一个测试（仅供参考）"`​ 替换为 `"这是一个测试"`​。

---

**8.**  **​`text = re.sub(r'[，,、]+$', '。', text)`​** ​

* **功能**：将文本末尾的**逗号或顿号**替换为句号。

  * 使用正则表达式 `re.sub(r'[，,、]+$', '。', text)`​ 匹配文本末尾的逗号（`,`​）、中文逗号（`，`​）或顿号（`、`​），并将其替换为句号（`。`​）。

    * 将 `"这是一个测试，"`​ 替换为 `"这是一个测试。"`​。

---

**9.**  **​`texts = list(split_paragraph(...))`​** ​

* **功能**：将文本分割为多个段落或句子。

  * ​`split_paragraph`​ 是一个函数，用于将文本按照一定的规则分割为多个段落或句子。
  * 参数说明：

    * ​`text`​：待分割的文本。
    * ​`partial(self.tokenizer.encode, allowed_special=self.allowed_special)`​：一个部分函数，用于对文本进行分词或编码。
    * ​`lang="zh"`​：指定语言为中文。
    * ​`token_max_n=80`​：每个段落的最大长度（以字符或 token 为单位）。
    * ​`token_min_n=60`​：每个段落的最小长度（以字符或 token 为单位）。
    * ​`merge_len=20`​：如果段落长度小于此值，则将其与前一个段落合并。
    * ​`comma_split=False`​：是否将逗号作为分割点。
  * 例如：

    * 输入：`"你好！这是一个测试。这个测试的目的是验证分割功能。"`​
    * 输出：`["你好！", "这是一个测试。", "这个测试的目的是验证分割功能。"]`​

‍
