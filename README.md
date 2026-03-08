<div align="center">

**[English](#english)** · **[中文](#中文)**

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Copyright](https://img.shields.io/badge/Copyright-2026%20yigediao-blue.svg)]()

</div>

---

<a name="english"></a>

# 听写小助手 · Chinese Dictation Assistant

A web app for primary school students to practice Chinese character dictation. Parents operate it on their phone — read a word aloud, the child writes it on paper, the parent marks it right or wrong. The app automatically tracks mistakes and generates printable practice sheets.

## Features

| Feature | Description |
|---------|-------------|
| 📖 Word Lists | Import custom vocabulary with characters / pinyin / meaning; auto-complete pinyin |
| 🎙️ Text-to-Speech | Browser TTS with adjustable speed and repeat count |
| ✅ Dictation & Judging | Tap "correct" / "wrong"; for multi-character words, pick exactly which character was missed |
| ❌ Mistake Book | Mistakes auto-archived by date; cleared when answered correctly |
| 🖨️ Practice Sheet | One-tap A4 PDF with stroke order diagrams, trace characters, and blank grids |
| 📊 Learning Analytics | Accuracy trend chart, mastery progress bar, high-frequency mistake ranking |
| 🔀 Multi-list Selection | Combine multiple word lists + mistake book in a single session |
| ➕ Mid-session Add | Quickly add unknown words to the mistake book at any time |
| ☁️ Cloud Sync | Data stored on the server; syncs across devices; supports JSON export/import |

## Tech Stack

- **Backend**: Python 3 + Flask (WSGI)
- **Frontend**: Single-file SPA (plain HTML / CSS / JS, no framework)
- **Deployment**: Synology NAS Web Station (WSGI mode) or any WSGI-compatible host
- **External CDN**: [pinyin-pro](https://github.com/zh-lx/pinyin-pro) · [HanziWriter](https://hanziwriter.org/)

## Deployment

### Option A: Synology NAS Web Station (Recommended)

1. **Install packages**
   Install `Web Station` from Package Center, plus Python 3 and Flask:
   ```bash
   pip3 install flask
   ```

2. **Upload files**
   Upload the repository to a shared folder, e.g. `/volume1/web/hanzi/`:
   ```
   hanzi/
   ├── server.py
   ├── static/
   │   └── index.html
   └── data/          ← created automatically on first run
   ```

3. **Create a Web Service**
   Web Station → Web Service → Add:
   - **Type**: Python (WSGI)
   - **Document root**: point to the `hanzi/` folder
   - **WSGI script**: `server.py`
   - **Callable**: `app`
   - **Port**: your choice (e.g. 8080)

4. **Open in browser**
   Navigate to `http://<NAS-IP>:<port>`.

### Option B: Local / Any Server

```bash
git clone https://github.com/yigediao/hanzi.git
cd hanzi
pip install flask
python server.py
```

Open `http://localhost:5000`.

## Usage

### 1 · Import a Word List

Go to **📚 Word Lists** → tap **＋ New List**.

Enter words, one per line:
```
汉字
春天/chūn tiān/season name
学习/xué xí
```
Format: `word / pinyin (optional, auto-filled) / meaning (optional)`

Lists are numbered automatically: `#1`, `#2`, …

### 2 · Start Dictation

Go to **🏠 Home**:
1. Select one or more word lists from the dropdown (multi-select supported)
2. Optionally include the **Mistake Book**
3. Set the number of questions
4. Tap **Start**

The app reads each word aloud. The parent marks the result:
- **✓ Correct** — mistake count decreases; removed from the book when it reaches 0
- **✗ Wrong** — for multi-character words, a picker lets you mark the exact character(s) missed

### 3 · Mistake Book

Go to **❌ Mistakes**:
- Top section shows **High-frequency mistakes** ranked by total error count
- Below, mistakes are grouped by date

### 4 · Generate Practice Sheet

In the Mistakes tab, tap **🖨 Generate Sheet**:
- Each wrong character gets one row: stroke-order diagram → model character → 2 trace squares → 7 blank grids
- Opens in a new browser window — use the browser's print dialog to save as PDF (A4)

### 5 · Learning Analytics

Go to **📊 History**:
- **Accuracy trend**: bar chart of the last 10 sessions
- **Mastery progress**: segmented bar — green (mastered) / gold (in progress) / red (needs work)
- **Focus words**: characters still in the mistake book, sorted by error count
- **Progress made**: characters that have been cleared from the mistake book

### 6 · Backup & Restore

- **Export**: Settings → **📤 Export** (downloads JSON)
- **Import**: Settings → **📥 Import** (restores from JSON)
- **Server backup**: visit `http://<server>/api/backup`

## Data Format

All data is stored in `data/dictation_data.json`:

```json
{
  "wordLists": [{ "id": "...", "name": "#1", "words": [...] }],
  "mistakes":  { "字": { "pinyin": "...", "count": 2, "dates": [...] } },
  "wrongLog":  { "字": { "pinyin": "...", "count": 5, "lastDate": "..." } },
  "history":   [{ "date": "...", "total": 10, "correct": 8, "wrong": [...] }],
  "settings":  { "rate": 0.8, "repeat": 2 }
}
```

- `mistakes` — current practice queue; correct answers decrement count to 0, then entry is deleted
- `wrongLog` — cumulative error history; count only ever increases; used for analytics

## License

Copyright © 2026 yigediao. Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) —
free to use and share for non-commercial purposes with attribution.
Third-party libraries (Flask, pinyin-pro, HanziWriter) retain their own licenses.

---

<a name="中文"></a>

# 听写小助手

一款专为小学生设计的汉字听写练习 Web 应用。家长在手机上操作，念出汉字，孩子在纸上写，家长判断对错，应用自动记录错题并生成练习字帖。

## 功能亮点

| 功能 | 说明 |
|------|------|
| 📖 词表管理 | 导入自定义词表，支持汉字 / 拼音 / 释义，自动补全拼音 |
| 🎙️ 语音朗读 | 调用浏览器 TTS，可调语速与重复次数 |
| ✅ 听写判题 | 家长点「会」/「不会」，多字词可精确标记哪个字写错 |
| ❌ 错题本 | 自动归档错题，按日期分组，答对自动递减 |
| 🖨️ 字帖生成 | 一键生成 A4 练习字帖（笔顺图示 + 描红 + 空白格），浏览器打印为 PDF |
| 📊 学习分析 | 准确率趋势、掌握进度条、高频错词排行、已掌握词汇 |
| 🔀 多选词表 | 听写时同时选多个词表 + 错题本，复习与新练一起来 |
| ➕ 中途加入 | 随时把不会的词加入错题本，适合中途加入的孩子 |
| ☁️ 数据同步 | 数据存储在服务器端，多设备自动同步，支持 JSON 导出备份 |

## 技术栈

- **后端**：Python 3 + Flask（WSGI）
- **前端**：单文件 SPA（纯 HTML / CSS / JS，无框架）
- **部署**：群晖 NAS Web Station（WSGI 模式）或任意支持 WSGI 的环境
- **外部依赖**：[pinyin-pro](https://github.com/zh-lx/pinyin-pro)（CDN，自动拼音）、[HanziWriter](https://hanziwriter.org/)（CDN，字帖笔顺）

## 部署教程

### 方式一：群晖 NAS Web Station（推荐）

1. **安装套件**
   套件中心安装 `Web Station`，并确保已安装 Python 3 套件（建议 3.9+）及 Flask：
   ```bash
   pip3 install flask
   ```

2. **上传文件**
   将仓库文件上传到群晖任意共享文件夹，例如 `/volume1/web/hanzi/`：
   ```
   hanzi/
   ├── server.py
   ├── static/
   │   └── index.html
   └── data/          ← 首次运行自动创建
   ```

3. **新建 Web 服务**
   Web Station → Web 服务 → 新增：
   - **类型**：Python（WSGI）
   - **文档根目录**：指向 `hanzi/` 文件夹
   - **WSGI 脚本**：`server.py`
   - **Callable**：`app`
   - **端口**：自定（例如 8080）

4. **访问**
   浏览器打开 `http://群晖IP:端口`，即可使用。

### 方式二：本地运行 / 其他服务器

```bash
git clone https://github.com/yigediao/hanzi.git
cd hanzi
pip install flask
python server.py
```

浏览器打开 `http://localhost:5000`。

## 使用教程

### 1 · 导入词表

进入 **📚 词表** Tab → 点击「＋ 新建词表」。

在输入框中按格式输入词语（每行一词）：
```
汉字
春天/chūn tiān/季节名
学习/xué xí
```
格式：`词语 / 拼音（可留空自动补全） / 释义（可选）`

词表自动编号为 `#1`、`#2`……

### 2 · 开始听写

进入 **🏠 首页**：
1. 从下拉选择词表（可多选）
2. 选择是否包含「错题本」
3. 设置题数
4. 点击「开始听写」

应用自动朗读词语，家长判断孩子是否写对：
- 点 **✓ 会写** — 该字错题计数 -1，归零后从错题本移除
- 点 **✗ 不会** — 进入字选择界面（多字词），精确标记哪个字写错

### 3 · 查看错题本

进入 **❌ 错题本** Tab：
- 顶部「高频错词」按历史错误次数排行
- 下方按日期分组显示当前待练错题

### 4 · 生成练习字帖

错题本 Tab → 点击「🖨 生成字帖」：
- 自动为每个错字生成一行：笔顺演示 + 范字 + 2 格描红 + 7 格空白格
- 在浏览器新窗口预览，调用系统打印功能输出为 A4 PDF

### 5 · 学习分析

进入 **📊 历史** Tab：
- **近期准确率趋势**：柱状图展示最近 10 次听写成绩
- **掌握进度**：绿色（已掌握）/ 金色（练习中）/ 红色（需加强）分段进度条
- **需重点关注**：错误次数最多、仍在错题本中的字
- **已取得进步**：曾经出错但已从错题本毕业的字

### 6 · 数据备份与恢复

- **导出**：设置 Tab → 「📤 导出」，下载 JSON 文件
- **导入**：设置 Tab → 「📥 导入」，选择 JSON 文件恢复
- **服务器备份**：访问 `http://服务器地址/api/backup` 直接下载

## 数据说明

所有数据存储在 `data/dictation_data.json`：

```json
{
  "wordLists": [{ "id": "...", "name": "#1", "words": [...] }],
  "mistakes":  { "字": { "pinyin": "...", "count": 2, "dates": [...] } },
  "wrongLog":  { "字": { "pinyin": "...", "count": 5, "lastDate": "..." } },
  "history":   [{ "date": "...", "total": 10, "correct": 8, "wrong": [...] }],
  "settings":  { "rate": 0.8, "repeat": 2 }
}
```

- `mistakes`：当前待练错题，答对自动递减至 0 后删除
- `wrongLog`：历史累计错误次数，只增不减，用于分析高频错词

## License

Copyright © 2026 yigediao. Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) —
free to use and share for non-commercial purposes with attribution.
Third-party libraries (Flask, pinyin-pro, HanziWriter) retain their own licenses.
