"""Refresh portable prompt snapshots from the canonical core rules."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
core = (root / 'docs/CORE.md').read_text()
for name in ('qianwen', 'workbuddy'):
    path = root / f'adapters/{name}.md'
    prefix = path.read_text().split('# Healing Journal 通用核心规则')[0]
    path.write_text(prefix + core)
