"""Build a self-contained public plugin; never copy runtime/private data."""
import json
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def build(dest):
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError('Use a fresh output directory')
    dest.mkdir(parents=True)
    for name in ('README.md', 'LICENSE'):
        shutil.copy2(ROOT/name, dest/name)
    for directory, pattern in [('templates', '**/*.md'), ('docs', 'CORE.md'), ('config', 'settings.example.json'), ('tests', 'example.json'), ('scripts', 'healing_journal.py')]:
        for src in (ROOT/directory).glob(pattern):
            target = dest/src.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    for src in (ROOT/'.agents/skills').glob('*/SKILL.md'):
        target = dest/'skills'/src.parent.name/'SKILL.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(src.read_text().replace('.agents/skills/', 'skills/').replace('同级', '同级'))
    core = dest/'docs/CORE.md'
    core.write_text(core.read_text().replace('.agents/skills/', 'skills/'))
    setup = dest/'skills/healing-setup/SKILL.md'
    setup.parent.mkdir(parents=True)
    setup.write_text('''---
name: healing-setup
description: 初始化 Healing Journal 的独立数据目录和 Obsidian 连接，不发布笔记。
---

确认用户的数据目录与 Vault 路径，不猜测路径。插件包只读，私人数据不得写入安装目录。使用插件内 scripts/healing_journal.py --root <用户数据目录> init --vault <用户确认的Vault>，再运行 doctor。没有 Vault 时省略 --vault。已有配置不覆盖。后续 import/status/publish 始终显式传 --root。先阅读插件 docs/CORE.md；其中路径 config、imports、private、drafts、creative-drafts 相对于用户数据目录，Skill、模板和脚本相对于插件安装目录。只用合成样例测试，未经批准不处理历史或发布。安装不自动创建定时任务。
''')
    for skill in (dest/'skills').glob('*/SKILL.md'):
        if skill != setup:
            skill.write_text(skill.read_text()+'\n插件安装模式：先读取 skills/healing-setup/SKILL.md，确认独立数据目录。脚本始终传 --root <数据目录>；模板与 Skill 来自插件包，私有文件来自数据目录，不能写入插件安装目录。\n')
    manifest = {'$schema':'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json','name':'healing-journal','version':'0.2.0','description':'Review-first personal journals and creative drafts from authorized conversations','author':{'name':'Healing Journal contributors'},'license':'MIT','repository':'https://github.com/golden-river-rep/healing-journal','extensions':{'com.openai':{'onboardingSkill':'./skills/healing-setup/SKILL.md'}}}
    (dest/'plugin.json').write_text(json.dumps(manifest, indent=2)+'\n')

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('destination', type=Path)
    build(p.parse_args().destination)
