import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from PIL import Image
from review_h3_clip import review


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg required')
class ClipReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '07_任务').mkdir()
        self.video = self.root / 'source.mp4'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error',
                        '-f', 'lavfi', '-i', 'color=red:s=96x160:r=24:d=1',
                        '-f', 'lavfi', '-i', 'color=blue:s=96x160:r=24:d=1',
                        '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]',
                        '-map', '[v]', '-c:v', 'libx264', str(self.video)], check=True)
        self.receipt = {'status': 'completed', 'prompt_id': 'offline', 'files': [
            {'path': 'source.mp4', 'sha256': hashlib.sha256(self.video.read_bytes()).hexdigest()}]}
        (self.root / 'receipt.json').write_text(json.dumps(self.receipt))
        (self.root / '07_任务/state.json').write_text(json.dumps(
            {'jobs': {'T00': {'receipt': 'receipt.json'}}}))

    def test_exact_last_included_frame_and_resume(self):
        result = review(self.root, 'T00', 1, 1)
        self.assertEqual(result['actual_last_frame_index'], 24)
        with Image.open(self.root / result['anchor_file']) as image:
            red, _, blue = image.convert('RGB').getpixel((40, 80))
        self.assertGreater(blue, red + 100)
        self.assertEqual(review(self.root, 'T00', 1, 1)['anchor_sha256'], result['anchor_sha256'])
        with self.assertRaises(ValueError):
            review(self.root, 'T00', 1, 0)
        revised = review(self.root, 'T00', 1, 0, revision=2)
        self.assertEqual(revised['actual_last_frame_index'], 23)
        self.assertTrue((self.root / '07_任务/制作记录/T00/edit_and_probe_v02.json').exists())
        self.assertEqual(review(self.root, 'T00', 1, 1)['anchor_sha256'], result['anchor_sha256'])

    def test_reject_short_source_or_changed_hash(self):
        with self.assertRaises(ValueError):
            review(self.root, 'T00', 3)
        self.receipt['files'][0]['sha256'] = 'wrong'
        (self.root / 'receipt.json').write_text(json.dumps(self.receipt))
        with self.assertRaises(ValueError):
            review(self.root, 'T00', 1)


if __name__ == '__main__':
    unittest.main()
