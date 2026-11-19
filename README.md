# Healing Journal

Python 3.11+，仅标准库，无网络调用。读取主动导出的 ChatGPT conversations JSON，创建可审核的 Obsidian Markdown。最小版本保守提取原话与历史助手回复；不自动推断生活事实或心理变化。语义分类与主题认知变化由 Codex 在审核草稿阶段完成。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/healing_journal.py import tests/example.json
python3 scripts/healing_journal.py import /path/to/conversations.json --from-date 2026-11-01 --to-date 2026-11-19
python3 scripts/healing_journal.py status BATCH_ID
# 仅在用户审核并明确批准当前内容后执行：
python3 scripts/healing_journal.py publish BATCH_ID --approve-sha256 REVIEWED_HASH
```

导入返回 BATCH_ID；审核 drafts/BATCH_ID/Daily 下所有文件。按 templates 整理内容，主题文件放 drafts/BATCH_ID/Insights，并使用 [[文件名]] 双向链接。发布摘要包含文件路径和完整内容，修改后需重新审核。CLI 的批准参数是操作确认机制，不会自动判定用户是否同意。

config/settings.json 的 timezone 决定消息所属日期；vault_path 默认为 null，发布到当前项目。可设置自己的绝对 Vault 路径，外部路径下只新建 Healing Journal 子目录，已有文件拒绝覆盖。Obsidian 可直接打开本项目为 Vault。

原始文件按 SHA256 归档到 imports，不覆盖；草稿 manifest 保存消息内容、来源节点及时间形成的去重键。增量导入保留旧草稿，每批采用唯一文件名，避免覆盖已审核内容。修改过的消息产生新记录。不要删除 manifest，否则可能再次导入。所有分支均保留并标记；缺失或无时区时间进入 undated，日期筛选排除 undated。日期过滤作用于消息日期，不能当作事件发生日期。非文本附件不解析。

原话、AI 解释、心理学假设严格分栏；缺失信息待确认，不作诊断。原始引用可能包含 Obsidian 链接语法，审核时请核对。默认忽略 imports、drafts、Daily、Insights；合成测试数据可入 Git。请勿把真实导出放入 tests 或其他受版本管理目录。无远程存储或遥测，备份由用户自行管理。


## 首次使用与复刻

需要 Python 3.11+，无需第三方 Python 包。下载或 clone 本仓库，进入项目目录：

```sh
cp config/settings.example.json config/settings.json
python3 -m unittest discover -s tests -v
python3 scripts/healing_journal.py import tests/example.json
```

按返回的批次号打开 drafts 目录审核。修改 config/settings.json 的 vault_path 为你自己的 Obsidian Vault 绝对路径；null 表示发布到项目目录。不要复制他人的真实数据或路径。Windows 可手动复制示例配置文件。

Codex 在此项目中可使用 `.agents/skills/healing-journal/SKILL.md`。说“写到日志中”表示把已授权的当前材料整理成草稿；“确认发布”才允许写入 Vault。重点保留用户感受、思考、历史 AI 建议以及有证据的认知变化，原话和回顾分开。Markdown 聊天整理目前由 Codex 完成，CLI import 仅支持 JSON。没有自动访问普通 ChatGPT 历史或后台同步功能。

## 维护与贡献

欢迎提交 Issue 或 Pull Request。仅使用合成或彻底匿名的数据复现问题，禁止附上私人聊天、真实日记或个人 Vault 配置。修改后运行自动化测试。现阶段是最小版本：不保证所有导出变体均可解析；并发导入、发布事务回滚及撤销发布尚未实现。发布前核对内容，避免多人同时操作同一 Vault。

工具不进行心理诊断，AI 整理仍需本人审核。工具代码不主动联网；使用 Codex 整理时，选中的材料会进入当前 AI 会话，不能视为完全离线推理。

MIT 许可证允许复制、修改和分发工具；许可证不要求分享任何个人记录。


## 创作 Skills（通用初版）

- healing-xiaohongshu：具体处境、真实发现、标题与封面文案、短篇正文。
- healing-wechat-essay：由经历展开思考，保留理解如何变化，形成完整文章。
- healing-fiction-seeds：小说素材卡与明确标注的虚构场景。

这些是写作默认值，不是平台算法保证或官方字数限制。小红书标题与正文需一致，可参考官方说明：https://school.xiaohongshu.com/rule/detail/2569 。

在 Codex 中说“整理今天的，生成全套”，先依据已授权材料创建日记草稿，再依次读取上述三个 Skill，输出三份创作草稿到 creative-drafts/<批次>/。材料日期不明时列待确认，不自行把事件记成今天。该操作由 Codex 编排，当前没有无人值守的一键 CLI，也不会自动发布。

个人范文、模板和改稿偏好放在 private/style/ 的 xiaohongshu、wechat、fiction 子目录；未提供时使用通用初版。改稿后先提议风格更新，由用户确认后形成偏好。private/ 和 creative-drafts/ 均忽略提交，公开仓库只包含通用规则与空白模板。
