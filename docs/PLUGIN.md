# 插件预览版 0.2.0

本版是可分发的本地 Skills 插件，不含 MCP 服务；不是官方目录上架版。真实客户端安装与 UI 尚待验证，不能声称已一键连接手机 ChatGPT。

## 安装

支持仓库市场的 Codex 客户端可添加：

```sh
codex plugin marketplace add golden-river-rep/healing-journal
```

随后在桌面应用插件目录中选择 Healing Journal Community，安装 Healing Journal，并在新聊天中运行 healing-setup。客户端没有该入口时，继续使用仓库的 AGENTS.md 工作流。

安装后让助手读取 healing-setup，指定独立数据目录和现有 Vault。脚本支持：

```sh
python3 /插件路径/scripts/healing_journal.py --root /数据目录 init --vault /现有Vault
python3 /插件路径/scripts/healing_journal.py --root /数据目录 doctor
```

init 不改动 Vault；已有配置拒绝覆盖。私人数据永远放数据目录，不放插件缓存。日记生成后必须审核批准具体内容摘要再发布。插件安装不会自动安装每晚任务，各用户独立配置。

## 维护

源规则位于 .agents/skills 和 docs/CORE.md。scripts/build_plugin.py 只复制公开白名单文件生成 plugins/healing-journal；输出目录必须不存在，更新时先将旧包移动到临时目录，再重新构建并审查 diff。不复制私人数据。运行 unittest 验证干净目录的初始化、去重、审核和发布流程。

打包格式依据 https://developers.openai.com/plugins/build/plugins 。千问与 WorkBuddy 使用 adapters 的通用指令，尚未验证它们能安装此插件包。
