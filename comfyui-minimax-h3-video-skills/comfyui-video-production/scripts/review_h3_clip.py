#!/usr/bin/env python3
"""Prepare local clip evidence and an exact edited-end anchor; never submit jobs."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    subprocess.run(args, check=True)


def review(root, job_id, duration, start_frame=0, revision=1):
    root = Path(root).resolve()
    state = read(root / '07_任务/state.json')
    receipt_path = root / state['jobs'][job_id]['receipt']
    receipt = read(receipt_path)
    if receipt['status'] != 'completed':
        raise ValueError('The submitted job has not completed')
    output = next(f for f in receipt['files'] if f['path'].endswith('.mp4'))
    video = root / output['path']
    if sha(video) != output['sha256']:
        raise ValueError('Source video hash differs from the submission receipt')
    probe = json.loads(subprocess.run([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)
    ], capture_output=True, text=True, check=True).stdout)
    stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    if stream['r_frame_rate'] != '24/1' or stream['avg_frame_rate'] != '24/1':
        raise ValueError('This anchor workflow requires constant 24fps source footage')
    frames = round(duration * 24)
    if start_frame < 0 or frames <= 0:
        raise ValueError('Invalid edit range')
    stop = start_frame + frames
    if int(stream['nb_frames']) < stop:
        raise ValueError('Not enough source frames for the intended edit range')
    folder = root / '07_任务/制作记录' / job_id
    folder.mkdir(parents=True, exist_ok=True)
    if revision < 1:
        raise ValueError('Edit revision must be positive')
    record_file = folder / ('edit_and_probe.json' if revision == 1 else f'edit_and_probe_v{revision:02d}.json')
    if record_file.exists():
        old = read(record_file)
        if (old['source_sha256'], old['in_frame'], old['out_frame_exclusive']) != (
                output['sha256'], start_frame, stop):
            raise ValueError('Existing evidence uses a different source or edit; create a new version')
    anchor = root / '07_任务/derived_anchors' / f'{job_id}_cut_f{stop - 1:04d}.png'
    anchor.parent.mkdir(parents=True, exist_ok=True)
    if not anchor.exists():
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
             '-vf', f'select=eq(n\\,{stop - 1})', '-frames:v', '1', str(anchor)])
    sheet = folder / 'review_0.5s.jpg'
    if not sheet.exists():
        rows = math.ceil(math.ceil(float(probe['format']['duration']) * 2) / 6)
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
             '-vf', f'fps=2,scale=272:-1,tile=6x{rows}', '-frames:v', '1', str(sheet)])
    record = dict(job_id=job_id, prompt_id=receipt['prompt_id'],
                  receipt=str(receipt_path.relative_to(root)), source_video=output['path'],
                  source_sha256=output['sha256'], source_frame_count=int(stream['nb_frames']),
                  width=stream['width'], height=stream['height'], fps=24,
                  in_frame=start_frame, out_frame_exclusive=stop,
                  duration_seconds=frames / 24, actual_last_frame_index=stop - 1,
                  anchor_file=str(anchor.relative_to(root)), anchor_sha256=sha(anchor),
                  transform='none; native source frame',
                  review_sheet=str(sheet.relative_to(root)), qa_status='evidence_only_not_content_approval')
    record_file.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--job', required=True)
    p.add_argument('--duration', type=float, required=True)
    p.add_argument('--in-frame', type=int, default=0)
    p.add_argument('--revision', type=int, default=1)
    a = p.parse_args()
    print(json.dumps(review(a.project.resolve().parent, a.job, a.duration, a.in_frame, a.revision),
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
