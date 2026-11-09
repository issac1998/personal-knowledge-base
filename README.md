# 个人知识库网站

`docs/` 是完整静态网站，包含本地知识库的原始文件、可直接阅读的 HTML 页面和健康记录查阅台。`site.zip` 包含 `docs/` 的全部内容，由 GitHub Actions 解压并发布到 GitHub Pages。此仓库及网站公开时，所有内容都可被任何人下载。

## 同步本地更新

在这台 Mac 上运行：

```sh
cd /Users/a/Documents/ChatGPT/agent/knowledge-base-pages
python3 sync.py
```

然后打开 GitHub 仓库，选择 **Add file → Upload files**，上传新生成的 `site.zip` 并提交。GitHub Actions 会自动重新发布网站。如果已配置好 GitHub 命令行认证，也可在本地提交并推送更新后的 `site.zip`。

`sync.py` 默认读取 `/Users/a/Documents/Codex/2026-10-23/new-chat/knowledge-base`；来源位置变化时传入 `--source /新路径`。网页中的 ChatGPT Space 链接会尽量替换为对应的本地页面。健康查阅台中手动填写的补充保存在当前浏览器，不会随着 Git 同步。

GitHub Pages 发布源使用 **GitHub Actions**。每次提交新压缩包后等待工作流完成，再打开网站检查。
