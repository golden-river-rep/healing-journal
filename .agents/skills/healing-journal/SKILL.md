---
name: healing-journal
description: 整理授权的 ChatGPT 导出为本地疗愈日记草稿，审核后发布。
---

先阅读 README.md。使用 scripts/healing_journal.py import 并限定用户授权的文件和日期；未经确认不读取完整历史、不上传数据。

在 drafts 内整理生活、情绪、睡眠、运动、饮食、事件。逐字保留用户原话及消息来源、原始时间；AI 解释、AI 整理、心理学假设分开标注。不诊断、不虚构。分支不视为实际经历，消息日期与事件日期分别核实。

主题认知变化参考 templates/insight.md 放同批次 Insights，提供前后证据，通过 [[文件名]] 与 Daily 互相链接。缺失证据列为待确认。

展示草稿供用户审核，status 获取内容摘要。只有用户明确批准当前版本才调用 publish --approve-sha256；改动后重新审核。不得自动发布。Vault 路径只使用配置，不修改已有笔记，不提交私人数据到 Git。

## 全套创作入口
用户说“整理今天的，生成全套”时，先整理有授权的日记草稿，再分别读取同级 healing-xiaohongshu、healing-wechat-essay、healing-fiction-seeds 的 SKILL.md 执行，生成三份创作草稿。不要把“今天整理”直接当作历史事件发生日期。个人参考放 private/style/，创作输出放 creative-drafts/，均不提交 Git；没有个人参考就使用通用风格。全套生成不代表允许发布任何内容。
