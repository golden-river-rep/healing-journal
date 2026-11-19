import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder', ROOT/'scripts/build_plugin.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class PluginTests(unittest.TestCase):
    def test_clean_install(self):
        with tempfile.TemporaryDirectory() as d:
            package=Path(d)/'plugin';data=Path(d)/'data';vault=Path(d)/'vault'
            (vault/'.obsidian').mkdir(parents=True)
            b.build(package)
            self.assertEqual(json.loads((package/'plugin.json').read_text())['name'],'healing-journal')
            self.assertFalse((package/'config/settings.json').exists())
            self.assertFalse((package/'imports').exists())
            cli=[sys.executable,str(package/'scripts/healing_journal.py'),'--root',str(data)]
            subprocess.run(cli+['init','--vault',str(vault)],check=True,capture_output=True)
            self.assertNotEqual(subprocess.run(cli+['init'],capture_output=True).returncode,0)
            subprocess.run(cli+['doctor'],check=True,capture_output=True)
            first=subprocess.run(cli+['import',str(package/'tests/example.json')],check=True,capture_output=True,text=True).stdout.strip()
            self.assertIn('No new records',subprocess.run(cli+['import',str(package/'tests/example.json')],check=True,capture_output=True,text=True).stdout)
            self.assertFalse((vault/'Healing Journal').exists())
            sha=subprocess.run(cli+['status',first],check=True,capture_output=True,text=True).stdout.strip()
            subprocess.run(cli+['publish',first,'--approve-sha256',sha],check=True,capture_output=True)
            self.assertEqual(len(list((vault/'Healing Journal/Daily').glob('*.md'))),2)
