# 个人知识库网站

`docs/` 是发布到 GitHub Pages 的完整静态网站，包含本地知识库的原始文件、可直接阅读的 HTML 页面和健康记录查阅台。此仓库公开时，`docs/` 中所有内容都可被任何人下载。

## 同步本地更新

在这台 Mac 上运行：

```sh
cd /Users/a/Documents/ChatGPT/agent/knowledge-base-pages
python3 sync.py
git add docs
git commit -m "Update knowledge base"
git push
```

`sync.py` 默认读取 `/Users/a/Documents/Codex/2026-10-23/new-chat/knowledge-base`；来源位置变化时传入 `--source /新路径`。网页中的 ChatGPT Space 链接会尽量替换为对应的本地页面。健康查阅台中手动填写的补充保存在当前浏览器，不会随着 Git 同步。

GitHub Pages 发布源使用 `main` 分支的 `/docs` 目录。每次推送后等待 GitHub Pages 更新。
