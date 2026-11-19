---
name: healing-setup
description: 初始化 Healing Journal 的独立数据目录和 Obsidian 连接，不发布笔记。
---

确认用户的数据目录与 Vault 路径，不猜测路径。插件包只读，私人数据不得写入安装目录。使用插件内 scripts/healing_journal.py --root <用户数据目录> init --vault <用户确认的Vault>，再运行 doctor。没有 Vault 时省略 --vault。已有配置不覆盖。后续 import/status/publish 始终显式传 --root。先阅读插件 docs/CORE.md；其中路径 config、imports、private、drafts、creative-drafts 相对于用户数据目录，Skill、模板和脚本相对于插件安装目录。只用合成样例测试，未经批准不处理历史或发布。安装不自动创建定时任务。
