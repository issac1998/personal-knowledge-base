# 个人知识库网站

`content/` 是本地知识库原始文件的 Git 快照；`docs/` 是生成的静态网站，包含原始文件、可直接阅读的 HTML 页面和健康记录查阅台。`site.zip` 包含 `docs/` 的全部内容，由 GitHub Actions 解压并发布到 GitHub Pages。此仓库及网站公开，所有内容都可被任何人下载。

## 同步本地更新

在这台 Mac 上运行一条命令：

```sh
cd /Users/a/Documents/ChatGPT/agent/knowledge-base-pages
./publish.sh
```

`publish.sh` 会调用 `sync.py`，把原始目录复制到 `content/`，生成阅读页面和 `site.zip`，提交发生变化的文件并推送。推送后，GitHub Actions 自动重新发布网站；没有内容变化时不会产生新的提交。这台 Mac 已验证可以直接推送到该仓库。

`sync.py` 在这台 Mac 上默认读取 `/Users/a/Documents/Codex/2026-10-23/new-chat/knowledge-base`；来源位置变化时传入 `--source /新路径`。其他电脑克隆仓库后，可使用 `python3 sync.py --source content` 重新生成网站。网页中的 ChatGPT Space 链接会尽量替换为对应的本地页面。健康查阅台中手动填写的补充保存在当前浏览器，不会随着 Git 同步。

GitHub Pages 发布源使用 **GitHub Actions**。每次提交新压缩包后等待工作流完成，再打开网站检查。
