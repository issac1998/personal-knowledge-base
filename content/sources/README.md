# 来源与覆盖范围

2026-10-30 按用户对可读性和记忆作用的反馈重写了阅读页面。首页突出已做选择、接续事项和可复用的方法；原始编号集中在资料页，旧话题留在资料池。

改写前的内容快照保存在 `history/2026-10-30-before-readable-rewrite.json`；改写内容保存在 `history/2026-10-30-readable-rewrite.json`。这两份是笔记版本记录，不是完整聊天备份。

- `app_threads.json`：2026-10-29 从当前应用列出的 **60 个** ChatGPT/Codex 对话目录项（近期、置顶、归档及选定的较早对话，已去重）。它是**目录快照**，不代表账号全部历史。
- `codex_root_sessions.tsv`：从本机 **859 个** Codex 会话档案中索引 **81 个不同、元数据未标记父会话的会话**。旧档案可能仍包含委派记录；索引不复制会话正文。可用 ID、日期和首条可读用户消息寻找遗漏主题。此索引也不是聊天内容备份。
- `scripts/index_chatgpt_export.py`：取得 ChatGPT 导出 ZIP 或 `conversations.json` 后，可生成元数据目录，例如 `python3 scripts/index_chatgpt_export.py /path/to/export.zip`。脚本不会复制完整对话正文。
- 各笔记中的来源 ID 对应原对话。已阅读部分消息的来源只支持笔记中具体那条记录，不能推出整段会话已经完整处理。

本次没有在本机 Downloads 找到 ChatGPT 数据导出文件。若以后提供导出 ZIP，先检查内容与访问权限，再批量盘点、去重、提炼。不要把完整导出文件直接上传到公开仓库。
