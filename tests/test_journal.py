import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('journal', Path(__file__).parents[1]/'scripts/healing_journal.py')
j = importlib.util.module_from_spec(spec)
spec.loader.exec_module(j)
class JournalTests(unittest.TestCase):
    def test_branches_missing_and_time(self):
        data = json.loads((Path(__file__).parent/'example.json').read_text())
        records = list(j.parse(data))
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]['branch'], 'active')
        self.assertEqual(records[2]['date'], 'undated')
        self.assertEqual(records[2]['branch'], 'alternate_or_unknown')
    def test_workflow(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'config').mkdir()
            (root/'config/settings.json').write_text('{"timezone":"Asia/Shanghai","vault_path":null}')
            args = ['--root', d]
            source = str(Path(__file__).parent/'example.json')
            j.main(args+['import',source])
            j.main(args+['import',source])
            batches = list((root/'drafts').iterdir())
            self.assertEqual(len(batches),1)
            self.assertFalse((root/'Daily').exists())
            with self.assertRaises(SystemExit):
                j.main(args+['publish',batches[0].name,'--approve-sha256','wrong'])
            files = sorted(batches[0].glob('Daily/*.md'))
            sha = j.digest(b''.join(str(f.relative_to(batches[0])).encode()+b'\0'+f.read_bytes() for f in files))
            j.main(args+['publish',batches[0].name,'--approve-sha256',sha])
            self.assertEqual(len(list((root/'Daily').glob('*.md'))),2)
            with self.assertRaises(SystemExit):
                j.main(args+['publish',batches[0].name,'--approve-sha256',sha])
if __name__ == '__main__': unittest.main()
