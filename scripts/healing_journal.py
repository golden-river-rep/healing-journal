"""Local, conservative ChatGPT export to reviewable Obsidian drafts. Python 3.11+."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def parse(data, tz='Asia/Shanghai'):
    conversations = data if isinstance(data, list) else data.get('conversations', [data])
    for conv in conversations:
        mapping = conv.get('mapping') or {}
        active, cursor = set(), conv.get('current_node')
        while cursor and cursor not in active and cursor in mapping:
            active.add(cursor)
            cursor = mapping[cursor].get('parent')
        for node_id, node in mapping.items():
            msg = node.get('message') or {}
            role = (msg.get('author') or {}).get('role')
            parts = (msg.get('content') or {}).get('parts') or []
            text = '\n'.join(p for p in parts if isinstance(p, str))
            if not text or role not in ('user', 'assistant'):
                continue
            raw = msg.get('create_time')
            date = 'undated'
            try:
                dt = datetime.fromtimestamp(float(raw), timezone.utc) if isinstance(raw, (float, int)) else datetime.fromisoformat(raw.replace('Z', '+00:00'))
                if dt.tzinfo is not None:
                    date = dt.astimezone(ZoneInfo(tz)).date().isoformat()
            except (ValueError, TypeError, AttributeError, OverflowError, OSError):
                pass
            record = dict(conversation=conv.get('id') or conv.get('conversation_id'), node=node_id,
                          message=msg.get('id'), role=role, text=text, raw_time=raw, date=date,
                          branch='active' if node_id in active else 'alternate_or_unknown')
            record['key'] = digest(json.dumps(record, sort_keys=True, ensure_ascii=False).encode())
            yield record

def write_new(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        f.write(text)

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    sub = p.add_subparsers(dest='cmd', required=True)
    init = sub.add_parser('init')
    init.add_argument('--vault', type=Path)
    init.add_argument('--timezone', default='Asia/Shanghai')
    sub.add_parser('doctor')
    imp = sub.add_parser('import')
    imp.add_argument('file', type=Path)
    imp.add_argument('--from-date')
    imp.add_argument('--to-date')
    pub = sub.add_parser('publish')
    pub.add_argument('batch')
    pub.add_argument('--approve-sha256', required=True, help='Hash of reviewed Markdown content')
    sub.add_parser('status').add_argument('batch')
    args = p.parse_args(argv)
    root = args.root.resolve()
    if args.cmd == 'init':
        ZoneInfo(args.timezone)
        vault = args.vault.expanduser().resolve() if args.vault else None
        if vault and not (vault.is_dir() and (vault/'.obsidian').is_dir()):
            p.error('Select an existing Obsidian Vault with .obsidian directory')
        config = root/'config/settings.json'
        if config.exists():
            p.error('Configuration exists; refusing to overwrite')
        for directory in ('imports/inbox', 'drafts', 'Daily', 'Insights', 'private/style', 'creative-drafts'):
            (root/directory).mkdir(parents=True, exist_ok=True)
        write_new(config, json.dumps({'timezone': args.timezone, 'vault_path': str(vault) if vault else None}, indent=2))
        print(f'Initialized {root}; no Vault files changed')
        return
    if not (root/'config/settings.json').exists():
        p.error('Run init first')
    cfg = json.loads((root/'config/settings.json').read_text())
    if args.cmd == 'doctor':
        ZoneInfo(cfg['timezone'])
        vault = Path(cfg['vault_path']).expanduser() if cfg.get('vault_path') else None
        if vault and not (vault/'.obsidian').is_dir():
            p.error('Configured Vault is missing')
        print('Configuration OK; Vault verified' if vault else 'Configuration OK; project-local output')
        print('No automatic ChatGPT history access; publishing requires approval')
        return
    if args.cmd == 'import':
        raw = args.file.read_bytes()
        records = list(parse(json.loads(raw), cfg['timezone']))
        source = digest(raw)
        archive = root/'imports'/f'{source}.json'
        if not archive.exists():
            write_new(archive, raw.decode('utf-8'))
        seen = set()
        for manifest in (root/'drafts').glob('*/manifest.json'):
            seen.update(json.loads(manifest.read_text())['keys'])
        records = [r for r in records if r['key'] not in seen and
                   (not args.from_date or r['date'] != 'undated' and r['date'] >= args.from_date) and
                   (not args.to_date or r['date'] != 'undated' and r['date'] <= args.to_date)]
        if not records:
            print('No new records'); return
        batch = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        folder = root/'drafts'/batch
        for date in sorted({r['date'] for r in records}):
            items = [r for r in records if r['date'] == date]
            body = f'---\ndate: {date}\nstatus: draft\n---\n# {date}\n\n## 生活、情绪、睡眠、运动、饮食与事件\n待审核：以下原话尚未自动归类；消息日期不一定是事件日期。\n\n## 用户原话与来源\n'
            for r in items:
                body += '\n' + ('### 用户原话' if r['role']=='user' else '### AI 解释（历史回复，非事实）') + '\n'
                body += '\n'.join('> '+line for line in r['text'].splitlines())+'\n\n'
                body += f"来源：imports/{source}.json；conversation={r['conversation']}；node={r['node']}；message={r['message']}；原始时间={r['raw_time']}；branch={r['branch']}\n"
            body += '\n## 观察（AI 整理）\n暂无。\n\n## 心理学假设（非诊断）\n暂无。\n\n## 待确认问题\n- 事件实际发生日期及生活分类是否准确？\n\n## 主题链接\n审核后可添加 [[主题名]]；主题笔记请放入本批次 Insights/。\n'
            write_new(folder/'Daily'/f'{date}-{batch}.md', body)
        write_new(folder/'manifest.json', json.dumps({'keys':[r['key'] for r in records], 'source':source}, indent=2))
        print(batch)
    else:
        if Path(args.batch).name != args.batch:
            p.error('Invalid batch')
        folder = root/'drafts'/args.batch
        files = sorted(folder.glob('Daily/*.md')) + sorted(folder.glob('Insights/*.md'))
        if not files:
            p.error('No draft notes')
        sha = digest(b''.join(str(f.relative_to(folder)).encode()+b'\0'+f.read_bytes() for f in files))
        if args.cmd == 'status':
            print(sha); return
        if args.approve_sha256 != sha:
            p.error('Reviewed content hash does not match')
        vault = Path(cfg['vault_path']).expanduser().resolve() if cfg.get('vault_path') else root
        target = vault/'Healing Journal' if vault != root else root
        destinations = [(target/f.relative_to(folder), f.read_text()) for f in files]
        if any(f.exists() for f, _ in destinations):
            p.error('Refusing to overwrite existing notes')
        for dest, content in destinations:
            write_new(dest, content)
        print(f'Published {len(files)} notes to {target}')

if __name__ == '__main__':
    main()
