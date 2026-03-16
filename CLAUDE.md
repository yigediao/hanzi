# 听写小助手 — CLAUDE.md
**当前版本：v1.2.0（2026-03-15）**

## 项目概述
为小孩练习汉字听写的 Web 应用，部署在群晖 NAS 的 Web Station（WSGI 模式）。
家长在手机上操作：念出汉字，孩子在纸上写，家长判断对错。

## 文件结构
```
ROY_Chinese/
├── server.py          # Flask 后端，WSGI 入口（callable: app / application）
├── static/
│   └── index.html     # 整个前端（单文件 SPA，全部 HTML/CSS/JS）
├── data/
│   └── dictation_data.json  # 持久化数据（服务端存储）
└── CLAUDE.md
```

## 关键约束：文件编辑方式
**直接用 Edit/Write 工具编辑 SMB 挂载路径会报错（ENOTSUP）**。
必须用以下流程：
```bash
# 1. 复制到本地
cp "/run/user/1000/gvfs/smb-share:server=192.168.1.130,share=us,user=Frank/ROY_Chinese/static/index.html" /tmp/index_dictation.html

# 2. 用 Edit 工具编辑 /tmp/index_dictation.html

# 3. 复制回 NAS
cp /tmp/index_dictation.html "/run/user/1000/gvfs/smb-share:server=192.168.1.130,share=us,user=Frank/ROY_Chinese/static/index.html"
```
CLAUDE.md 同理，临时路径用 `/tmp/claude_dictation.md`。
server.py 同理，临时路径用 `/tmp/server_dictation.py`。

## 后端（server.py）
- Flask WSGI，Web Station callable 填 `app`
- 端口 5000（本地运行）或由 Web Station 管理
- API 端点：
  - `GET  /api/data`   — 读取全量数据
  - `POST /api/data`   — 写入全量数据
  - `GET  /api/backup` — 下载 JSON 备份
- 数据文件：`data/dictation_data.json`（原子写入，.tmp 中转）

## 前端（static/index.html）
单文件 SPA，无框架，纯 HTML/CSS/JS。

### 数据结构（state）
```javascript
state = {
  wordLists: [{ id, name, words: [{text, pinyin, meaning}] }],
  mistakes:  { 'text': { pinyin, count, dates: ['2026/2/23', ...] } },
  wrongLog:  { 'text': { pinyin, count, lastDate } },  // 累计错误，永不递减
  history:   [{ date, dateKey, total, correct, wrong:[], listName, mode }],
  settings:  { rate: 0.8, repeat: 2 }
}
```
- `mistakes.count` 答对会递减至 0 后删除
- `wrongLog.count` 只增不减，用于高频错词统计
- mistakes 键为单字（多字词答错后拆分存储）

### 持久化
- `localStorage` key: `dictation_v2`
- 服务端：`/api/data` POST（防抖 2 秒，localStorage 写完立即触发）
- 加载时：localStorage 先读，服务端数据后覆盖

### Tab 结构
```
🏠 首页       #page-home
📚 词表       #page-wordlists
❌ 错题本     #page-mistakes
📊 历史       #page-history
⚙ 设置        #page-settings（顶栏按钮）
```
全屏覆盖层（非 .page）：`#dictation-screen` / `#summary-screen` / `#quick-add-screen` / `#char-select-overlay`

### 核心函数索引
| 函数 | 作用 |
|------|------|
| `startDictation()` | 开始听写，从 buildQueue() 取题目队列 |
| `buildQueue(listIds[], count, incl)` | 构建听写队列，接受数组，支持 `__mistakes__` 特殊 listId，按日期过滤 |
| `judgeAnswer(correct)` | 判断对错；多字词或单字有 sourceWord 时触发 showCharSelect |
| `showCharSelect(word, today)` | 弹出次级菜单，让用户选具体哪个字写错；`word._mistakeChars` 中的字预先选中 |
| `confirmCharSelect()` | 确认选字，调用 recordWrong() 逐字记录 |
| `recordWrong(text, pinyin, today)` | 更新 mistakes + wrongLog 的公共函数 |
| `showSummary()` | 显示本次结果，写入 history |
| `renderMistakes()` | 渲染错题本（按日期分组） |
| `renderHighFreq()` | 渲染高频错词排行（来自 wrongLog），Top 15 |
| `renderHistory()` | 渲染历史记录列表 |
| `renderAnalysis()` | 渲染学习分析卡片（历史 Tab 顶部） |
| `generateZitie(dateFilter?)` | 生成字帖 PDF（新窗口打印）；传入日期字符串可过滤指定日期错题 |
| `openQuickAdd()` | 中途加入：全词表选词加入错题本 |
| `addListToSelection()` | 多选词表：从下拉添加 chip |
| `updateWordListSelect()` | 刷新首页词表下拉（含词语预览） |
| `autoFillPinyin()` | 用 pinyin-pro 自动补全拼音 |
| `migrateWrongLog()` | 一次性从 history 反推 wrongLog（首次加载） |
| `migratePresetListNames()` | 一次性把旧格式词表名迁移为 #N |

### 词表命名规则
- 自动编号：`#1` `#2` … `#全部`（`nextListNumber()` 取当前最大值+1）
- 旧格式 `第N组：...` 在 `migratePresetListNames()` 里自动迁移

### 外部依赖
```html
<!-- 自动拼音 -->
<script src="https://cdn.jsdelivr.net/npm/pinyin-pro/dist/index.js" defer></script>
<!-- 使用：pinyinPro.pinyin('汉字', { toneType: 'symbol', type: 'array' }) -->
```

### 听写多选词表（selectedListIds）
- 首页下拉改为 chip 多选：`addListToSelection()` / `removeListFromSelection(id)`
- `buildQueue` 接受 `listIds[]`，合并去重后建队列
- 词表 chip 容器：`#sel-chips`

### 多字词答错拆字（char-select-overlay）
- `judgeAnswer(false)` 检测到以下两种情况时弹出 overlay：
  1. `word.text` 本身是多字词（含词组合并项 `_mistakeChars`）
  2. `word.text` 是单字但有 `word.sourceWord`（错题本练习时，单字携带来源词组上下文）
- overlay 展示完整词组的所有字；`word._mistakeChars` 中的字**自动预选**（红色）
- 用户可追加选中词组中其他字，确认后调 `confirmCharSelect()`
- `recordWrong()` 将单字分别写入 `mistakes` 和 `wrongLog`（数据始终按单字存储）

### 错题本队列构建规则（buildQueue `__mistakes__`）
- **底层数据**：`state.mistakes` 始终以单字为 key 存储计数
- **展示层合并**：`buildQueue` 构建时，把有相同 `sourceWord` 的错字合并为**一条**队列项
  - `word.text` = 完整词组文本（如 `"做作业"`）
  - `word._mistakeChars` = 其中已知错字数组（如 `["做","作","业"]`）
  - `renderQuestion()` 将 `_mistakeChars` 中的字高亮红色，词组其余字正常显示
- 无 sourceWord 的单字错题：保持单字队列项，正常展示

### 字帖生成（generateZitie）
- 来源：`state.mistakes` 中 **单字** 条目（过滤掉多字词）
- 支持按日期过滤：`generateZitie(dateFilter?)` — 错题本每个日期分组右侧有"📝 字帖"按钮，传入该日期
- **字序排列**：按 `charSourceMap[ch].sources[0]`（来源词组）分组排序，同词组的字相邻输出，打印时整齐对应
- 格式：笔顺展示条（HanziWriter SVG）+ 1 范字 + 2 描红（透明度 38%）+ 7 空白 = 10 格/行
- 描红颜色：`rgba(220,80,80,0.38)`；字体：宋体（SimSun/STSong）
- 每字上方显示来源词组（`.char-word-label`）
- `break-inside: avoid` 防止田字格被分页割裂
- 笔顺 SVG：HanziWriter data CDN `https://cdn.jsdelivr.net/npm/hanzi-writer-data@2.0/${ch}.json`
- SVG 坐标翻转：`<g transform="scale(1,-1) translate(0,-1024)">`
- 常量：`const TRACE = 2, EMPTY = 7;`（描红2格，空白7格）

### 高频错词（wrongLog）
- 在 `recordWrong()` 时同步写入
- `migrateWrongLog()` 在 init 时从 history 一次性回填（wrongLog 为空时才执行）
- 显示：错题本 Tab 顶部，Top 15，进度条颜色：金(1-2次) / 橙(3-5次) / 红(6+次)

### 学习分析（renderAnalysis）
- 位置：历史 Tab 顶部 `#analysis-container`（数据为空时隐藏）
- 内容：
  1. **概览**：总次数、总听写数、平均正确率、连续练习天数（streak）
  2. **近期准确率趋势**：最近 10 次 session 的 CSS 柱状图，颜色同 score-hi/mid/lo
  3. **掌握进度**：分段进度条（绿=已掌握 / 金=练习中 / 红=需加强）
  4. **需重点关注**：仍在 mistakes 中、按 wrongLog.count 降序，金(3-5次)/红(6+次) pill
  5. **已取得进步**：wrongLog.count≥2 且已不在 mistakes 的字，绿色 pill
- CSS 类前缀：`.an-*`（`.an-section`、`.an-pill`、`.trend-bar`、`.mastery-*` 等）

### 中途加入（openQuickAdd）
- 展示所有词表的全部词，可多选
- 选中后加入 `state.mistakes`（今日日期，count+1）
- 适合新加入的孩子快速标记不会的词

## 已知预设词表
- `#1` ~ `#40`：从照片识别的小学词表（共约 222 字）
- `#全部`：全部 222 字合并
- 存储在 `PHOTO_WORDLISTS` 常量中，通过 `importPreset()` 导入

## 开发备注
- 没有构建工具，直接编辑 index.html 即生效（刷新浏览器）
- 群晖 Web Station 会自动热重载，无需重启服务
- 调试：浏览器 F12 控制台，`state` 对象全局可访问
- 数据备份：访问 `/api/backup` 下载完整 JSON
