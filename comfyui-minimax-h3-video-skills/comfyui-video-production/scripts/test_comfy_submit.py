"""Offline tests: no connection to ComfyUI and no GPU jobs submitted."""
import argparse
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

import comfy_submit as runner


INFO = {
    "MiniMaxH3ReferenceToVideo": {"input": {"required": {}}, "output": ["CONDITIONING", "LATENT"]},
    "LoadImage": {"input": {"required": {"image": ["STRING"]}}, "output": ["IMAGE"]},
    "SaveImage": {"input": {"required": {}}, "output": []},
}


class FakeClient:
    base = "http://test:8188"

    def __init__(self, lost_response=False, fail_execution=False):
        self.events = []
        self.accepted = {}
        self.lost_response = lost_response
        self.fail_execution = fail_execution

    def upload(self, path, video_id):
        self.events.append("upload")
        return "uploaded/" + path.name

    def json(self, path, payload=None):
        if path == "/prompt":
            prompt_id = payload["prompt_id"]
            self.events.append("submit:" + prompt_id)
            self.accepted[prompt_id] = {
                "status": {"completed": not self.fail_execution,
                           "status_str": "error" if self.fail_execution else "success",
                           "messages": [["execution_error", {}]] if self.fail_execution else []},
                "outputs": {"save": {"gifs": [{"filename": "server.mp4", "type": "output", "subfolder": "test"}]}},
            }
            if self.lost_response:
                self.lost_response = False
                raise runner.RunnerError("simulated lost response AFTER acceptance")
            return {"prompt_id": prompt_id, "node_errors": {}}
        if path.startswith("/history/"):
            self.events.append("history:" + path.rsplit("/", 1)[-1])
            key = path.rsplit("/", 1)[-1]
            return {key: self.accepted[key]} if key in self.accepted else {}
        if path == "/queue":
            return {"queue_running": [], "queue_pending": []}
        raise AssertionError(path)

    def download(self, output, path):
        self.events.append("download")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake-video")


class RunnerTests(unittest.TestCase):
    @staticmethod
    def make_png(path, w=8, h=8):
        """Minimal valid RGB PNG so the executor can read its IHDR size."""
        raw = b"".join(b"\x00" + b"\x00\x00\x00" * w for _ in range(h))
        def chunk(tag, data):
            body = tag + data
            return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                         + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / "image.png").write_bytes(b"test-image")
        (self.root / "prompt.txt").write_text("Use <Picture 1>. English text; 中文对白.")
        runner.write_json(self.root / "template.json", {
            "265": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
                "prompt": "{{PROMPT}}", "width": "{{WIDTH}}", "height": "{{HEIGHT}}", "length": "{{LENGTH}}"}},
            "save": {"class_type": "SaveImage", "inputs": {"images": ["265", 0], "prefix": "{{PREFIX}}"}},
        })
        self.config = {"server": FakeClient.base, "video_id": "test", "workflows": {"preview": "template.json"},
                       "defaults": {"profile": "preview", "width": 544, "height": 960, "seconds": 15, "seed": 42}}
        self.jobs = [{"id": name, "status": "ready", "prompt_file": "prompt.txt", "images": ["image.png"]}
                     for name in ("S01_v01", "S02_v01")]
        self.args = argparse.Namespace(wait_timeout=2, poll=0.1, retry_failed=False)

    def run_jobs(self, client, jobs=None):
        runner.run_jobs(self.root, self.config, jobs or self.jobs, client, INFO, self.args)

    def four_view_job(self):
        self.config["require_scene_references"] = True
        views = {}
        for role in runner.SCENE_VIEW_ROLES:
            name = role + ".png"
            (self.root / name).write_bytes(role.encode())
            views[role] = name
        self.config["scene_reference_sets"] = {"room_v01": views}
        job = dict(self.jobs[0], scene_ids=["room_v01"],
                   images=["image.png", *views.values()], anchor_image_index=1)
        (self.root / "prompt.txt").write_text(" ".join(f"<Picture {n}>" for n in range(1, 6)))
        return job

    def test_four_views_and_continuation_are_all_bound(self):
        job = self.four_view_job()
        template = runner.read_json(self.root / "template.json")
        template["223"] = {"class_type": "BasicGuider", "inputs": {"conditioning": ["265", 0]}}
        runner.write_json(self.root / "template.json", template)
        prepared = runner.materialize(self.root, self.config, job)
        graph = runner.build_prompt(self.config, job, prepared, job["images"], "r1")
        for i, name in enumerate(job["images"]):
            self.assertEqual(graph[str(10001+i)]["inputs"]["image"], name)
            self.assertEqual(graph["265"]["inputs"][f"ref_images.ref_image_{i}"], [str(10001+i), 0])
        self.assertEqual(graph["1265"]["inputs"]["image"], ["10001", 0])

    def test_four_view_missing_binding_fails_even_with_matching_prompt(self):
        job = self.four_view_job()
        job["images"].pop()
        (self.root / "prompt.txt").write_text(" ".join(f"<Picture {n}>" for n in range(1, 5)))
        with self.assertRaisesRegex(runner.RunnerError, "top_90.*实际绑定"):
            runner.materialize(self.root, self.config, job)

    def test_four_view_requires_scene_declaration(self):
        job = self.four_view_job()
        del job["scene_ids"]
        with self.assertRaisesRegex(runner.RunnerError, "scene_ids"):
            runner.materialize(self.root, self.config, job)

    def test_four_view_group_and_files_are_complete(self):
        job = self.four_view_job()
        views = self.config["scene_reference_sets"]["room_v01"]
        del views["back"]
        with self.assertRaisesRegex(runner.RunnerError, "必须包含"):
            runner.materialize(self.root, self.config, job)
        views["back"] = "missing.png"
        with self.assertRaisesRegex(runner.RunnerError, "实际绑定"):
            runner.materialize(self.root, self.config, job)

    def test_four_view_duplicate_content_fails(self):
        job = self.four_view_job()
        (self.root / "back.png").write_bytes((self.root / "front.png").read_bytes())
        with self.assertRaisesRegex(runner.RunnerError, "重复单图"):
            runner.materialize(self.root, self.config, job)

    def test_four_view_over_budget_and_missing_prompt_reference_fail(self):
        job = self.four_view_job()
        (self.root / "prompt.txt").write_text("<Picture 1>")
        with self.assertRaisesRegex(runner.RunnerError, "图片引用"):
            runner.materialize(self.root, self.config, job)
        job["images"] += ["image.png"] * 5
        with self.assertRaisesRegex(runner.RunnerError, "1–9"):
            runner.materialize(self.root, self.config, job)

    def test_four_view_rejects_i2v(self):
        job = self.four_view_job()
        template = runner.read_json(self.root / "template.json")
        template["265"]["class_type"] = "MiniMaxH3ImageToVideo"
        runner.write_json(self.root / "template.json", template)
        with self.assertRaisesRegex(runner.RunnerError, "Ref2VA"):
            runner.materialize(self.root, self.config, job)

    def test_scene_contract_fingerprint_and_legacy_compatibility(self):
        legacy = runner.materialize(self.root, self.config, self.jobs[0])[-1]
        self.config["scene_reference_sets"] = {}
        self.assertEqual(legacy, runner.materialize(self.root, self.config, self.jobs[0])[-1])
        job = self.four_view_job()
        first = runner.materialize(self.root, self.config, job)[-1]
        views = self.config["scene_reference_sets"]["room_v01"]
        views["front"], views["back"] = views["back"], views["front"]
        self.assertNotEqual(first, runner.materialize(self.root, self.config, job)[-1])
        self.config["require_scene_references"] = False
        job["scene_ids"] = ["unknown"]
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, job)

    def test_scene_exception_requires_authorization_record(self):
        self.config["require_scene_references"] = True
        job = dict(self.jobs[0], scene_reference_exception={"reason": "no scene"})
        with self.assertRaisesRegex(runner.RunnerError, "authorization"):
            runner.materialize(self.root, self.config, job)
        job["scene_reference_exception"]["authorization"] = "test user request"
        runner.materialize(self.root, self.config, job)
        job["scene_ids"] = ["room"]
        with self.assertRaisesRegex(runner.RunnerError, "不得同时"):
            runner.materialize(self.root, self.config, job)

    def test_four_view_receipt_records_roles_hashes_and_indices(self):
        job = self.four_view_job()
        del job["anchor_image_index"]  # Minimal fake server has no Guide node.
        self.run_jobs(FakeClient(), [job])
        receipt = next((self.root / "07_任务/runs").rglob("receipt.json"))
        recorded = runner.read_json(receipt)["scene_references"]["scenes"]["room_v01"]
        self.assertEqual(recorded["front"]["picture_index"], 2)
        self.assertEqual(recorded["top_90"]["sha256"], runner.file_hash(self.root / "top_90.png"))

    def test_alignment_and_picture_binding(self):
        prepared = runner.materialize(self.root, self.config, self.jobs[0])
        graph = runner.build_prompt(self.config, self.jobs[0], prepared, ["a.png"], "r1")
        self.assertEqual(graph["265"]["inputs"]["length"], 362)
        self.assertEqual(graph["265"]["inputs"]["ref_images.ref_image_0"], ["10001", 0])
        self.assertIn("中文", graph["265"]["inputs"]["prompt"])
        self.assertNotIn("ref_audios", str(graph))

    def test_reject_draft_bad_refs_and_path_escape(self):
        self.jobs[0]["status"] = "draft"
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, self.jobs[0])
        self.jobs[0]["status"] = "ready"
        (self.root / "prompt.txt").write_text("Wrong <Picture 2>.")
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, self.jobs[0])
        with self.assertRaises(runner.RunnerError):
            runner.project_path(self.root, "../outside.txt")

    def test_image_to_video_binds_actual_first_and_last_frames(self):
        template = runner.read_json(self.root / "template.json")
        template["265"]["class_type"] = "MiniMaxH3ImageToVideo"
        runner.write_json(self.root / "template.json", template)
        job = dict(self.jobs[0], images=["image.png", "image.png"])
        (self.root / "prompt.txt").write_text("First <Picture 1>, last <Picture 2>.")
        prepared = runner.materialize(self.root, self.config, job)
        graph = runner.build_prompt(self.config, job, prepared, ["first.png", "last.png"], "r1")
        inputs = graph["265"]["inputs"]
        self.assertEqual(inputs["first_frame"], ["10001", 0])
        self.assertEqual(inputs["last_frame"], ["10002", 0])
        self.assertFalse(any(k.startswith("ref_images") for k in inputs))
        self.assertNotIn("1265", graph)

    def test_image_to_video_single_first_frame(self):
        template = runner.read_json(self.root / "template.json")
        template["265"]["class_type"] = "MiniMaxH3ImageToVideo"
        runner.write_json(self.root / "template.json", template)
        prepared = runner.materialize(self.root, self.config, self.jobs[0])
        graph = runner.build_prompt(self.config, self.jobs[0], prepared, ["first.png"], "r1")
        self.assertEqual(graph["265"]["inputs"]["first_frame"], ["10001", 0])
        self.assertNotIn("last_frame", graph["265"]["inputs"])

    def test_image_to_video_rejects_incompatible_reference_inputs(self):
        template = runner.read_json(self.root / "template.json")
        template["265"]["class_type"] = "MiniMaxH3ImageToVideo"
        runner.write_json(self.root / "template.json", template)
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, dict(self.jobs[0], anchor_image_index=1))
        (self.root / "prompt.txt").write_text("<Picture 1> <Picture 2> <Picture 3>")
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config,
                               dict(self.jobs[0], images=["image.png"] * 3))
        (self.root / "sound.wav").write_bytes(b"audio")
        (self.root / "prompt.txt").write_text("<Picture 1> <Audio 1>")
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, dict(self.jobs[0], audios=["sound.wav"]))

    def test_server_model_validation(self):
        graph = {"1": {"class_type": "Loader", "inputs": {"model": "missing"}}}
        info = {"Loader": {"input": {"required": {"model": [["installed"]]}}, "output": ["MODEL"]}}
        with self.assertRaises(runner.RunnerError):
            runner.validate_graph(graph, info)

    def test_preflight_allows_images_not_uploaded_yet(self):
        graph = {"10001": {"class_type": "LoadImage", "inputs": {"image": "future-upload.png"}}}
        info = {"LoadImage": {"input": {"required": {"image": [["old-file.png"]]}}, "output": ["IMAGE"]}}
        runner.validate_graph(graph, info)

    def test_serial_order_and_resume_without_duplicates(self):
        client = FakeClient()
        self.run_jobs(client)
        submits = [i for i, x in enumerate(client.events) if x.startswith("submit:")]
        self.assertEqual(len(submits), 2)
        self.assertIn("download", client.events[submits[0]:submits[1]])
        count = len(client.events)
        self.run_jobs(client)
        self.assertEqual(len(client.events), count)

    def test_lost_response_reconciles_without_second_post(self):
        client = FakeClient(lost_response=True)
        with self.assertRaises(runner.RunnerError):
            self.run_jobs(client, self.jobs[:1])
        self.run_jobs(client, self.jobs[:1])
        self.assertEqual(sum(x.startswith("submit:") for x in client.events), 1)
        self.assertIn("download", client.events)

    def test_unknown_submission_not_blindly_retried(self):
        client = FakeClient(lost_response=True)
        with self.assertRaises(runner.RunnerError):
            self.run_jobs(client, self.jobs[:1])
        client.accepted.clear()
        with self.assertRaises(runner.RunnerError):
            self.run_jobs(client, self.jobs[:1])
        self.assertEqual(sum(x.startswith("submit:") for x in client.events), 1)

    def test_execution_error_stops_following_jobs(self):
        client = FakeClient(fail_execution=True)
        with self.assertRaises(runner.RunnerError):
            self.run_jobs(client)
        self.assertEqual(sum(x.startswith("submit:") for x in client.events), 1)
        with self.assertRaises(runner.RunnerError):
            self.run_jobs(client)
        self.assertEqual(sum(x.startswith("submit:") for x in client.events), 1)

    def test_modified_prompt_requires_new_job_version(self):
        client = FakeClient()
        self.run_jobs(client, self.jobs[:1])
        (self.root / "prompt.txt").write_text("Updated <Picture 1>.")
        with self.assertRaises(runner.RunnerError):
            self.run_jobs(client, self.jobs[:1])
        self.assertEqual(sum(x.startswith("submit:") for x in client.events), 1)

    def test_missing_local_output_redownloads_without_resubmit(self):
        client = FakeClient()
        self.run_jobs(client, self.jobs[:1])
        next((self.root / "08_输出").rglob("*.mp4")).unlink()
        self.run_jobs(client, self.jobs[:1])
        self.assertEqual(sum(x.startswith("submit:") for x in client.events), 1)
        self.assertEqual(client.events.count("download"), 2)

    def test_selection_preserves_manifest_order(self):
        self.assertEqual(runner.select_jobs(self.jobs, "S02_v01,S01_v01"), self.jobs)

    def test_audio_reference_binding_and_hash(self):
        (self.root / "voice.wav").write_bytes(b"voice-a")
        (self.root / "prompt.txt").write_text("Use <Picture 1>; <Audio 1> guides timbre only.")
        job = self.jobs[0]
        job["audios"] = ["voice.wav"]
        prepared = runner.materialize(self.root, self.config, job)
        graph = runner.build_prompt(self.config, job, prepared, ["a.png"], "r", ["voice.wav"])
        self.assertEqual(graph["11001"]["class_type"], "LoadAudio")
        self.assertEqual(graph["265"]["inputs"]["ref_audios.ref_audio_0"], ["11001", 0])
        (self.root / "voice.wav").write_bytes(b"voice-b")
        self.assertNotEqual(prepared[-1], runner.materialize(self.root, self.config, job)[-1])

    def test_audio_reference_must_match_input(self):
        (self.root / "prompt.txt").write_text("Use <Picture 1> and <Audio 1>.")
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, self.jobs[0])

    def test_first_frame_guide_rewires_conditioning(self):
        template = runner.read_json(self.root / "template.json")
        template["223"] = {"class_type": "BasicGuider", "inputs": {"conditioning": ["265", 0]}}
        runner.write_json(self.root / "template.json", template)
        job = self.jobs[0]
        job["anchor_image_index"] = 1
        prepared = runner.materialize(self.root, self.config, job)
        graph = runner.build_prompt(self.config, job, prepared, ["a.png"], "r")
        self.assertEqual(graph["1265"]["inputs"]["image"], ["10001", 0])
        self.assertEqual(graph["223"]["inputs"]["conditioning"], ["1265", 0])

    def _guider_template(self):
        template = runner.read_json(self.root / "template.json")
        template["223"] = {"class_type": "BasicGuider", "inputs": {"conditioning": ["265", 0]}}
        runner.write_json(self.root / "template.json", template)

    def test_tail_guide_chains_after_first_guide(self):
        self._guider_template()
        (self.root / "tail.png").write_bytes(b"tail")
        job = dict(self.jobs[0], anchor_image_index=1, tail_image="tail.png")
        prepared = runner.materialize(self.root, self.config, job)
        self.assertEqual(len(prepared[3]), 2)  # 参考图 + 尾帧图都上传
        graph = runner.build_prompt(self.config, job, prepared, ["a.png", "t.png"], "r")
        tail = graph["1266"]["inputs"]
        self.assertEqual(tail["class_type"] if "class_type" in tail else graph["1266"]["class_type"],
                         "MiniMaxH3AddGuide")
        self.assertEqual(tail["positive"], ["1265", 0])
        self.assertEqual(tail["image"], ["10002", 0])
        self.assertEqual(tail["frame_idx"], -1)
        self.assertEqual(graph["223"]["inputs"]["conditioning"], ["1266", 0])
        # 尾帧图不进入 <Picture N> 参考
        self.assertNotIn("ref_images.ref_image_1", graph["265"]["inputs"])

    def test_tail_guide_without_head_uses_model_conditioning(self):
        self._guider_template()
        (self.root / "tail.png").write_bytes(b"tail")
        job = dict(self.jobs[0], tail_image="tail.png", tail_frame_index=100)
        prepared = runner.materialize(self.root, self.config, job)
        graph = runner.build_prompt(self.config, job, prepared, ["a.png", "t.png"], "r")
        self.assertNotIn("1265", graph)
        self.assertEqual(graph["1266"]["inputs"]["positive"], ["265", 0])
        self.assertEqual(graph["1266"]["inputs"]["frame_idx"], 100)
        self.assertEqual(graph["223"]["inputs"]["conditioning"], ["1266", 0])

    def test_tail_guide_changes_fingerprint_and_is_rejected_on_image_to_video(self):
        (self.root / "tail.png").write_bytes(b"tail")
        job = dict(self.jobs[0], tail_image="tail.png")
        base = runner.materialize(self.root, self.config, self.jobs[0])[-1]
        self.assertNotEqual(base, runner.materialize(self.root, self.config, job)[-1])
        template = runner.read_json(self.root / "template.json")
        template["265"]["class_type"] = "MiniMaxH3ImageToVideo"
        runner.write_json(self.root / "template.json", template)
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, job)
    def _clip(self, count=5, size=(8, 8)):
        names = []
        for i in range(count):
            name = f"clip_{i}.png"
            self.make_png(self.root / name, *size)
            names.append(name)
        return names

    def test_clip_frames_build_image_batch_and_anchor(self):
        self._guider_template()
        frames = self._clip(5)
        job = dict(self.jobs[0], clip_frames=frames, clip_frame_index=0)
        prepared = runner.materialize(self.root, self.config, job)
        self.assertEqual(len(prepared[3]), 6)  # 1 参考 + 5 片段帧
        names = ["ref.png"] + [f"f{i}.png" for i in range(5)]
        graph = runner.build_prompt(self.config, job, prepared, names, "r")
        for k in range(4):
            self.assertEqual(graph[f"{12001 + k}"]["class_type"], "ImageBatch")
        self.assertEqual(graph["12001"]["inputs"]["image1"], ["10002", 0])
        self.assertEqual(graph["12004"]["inputs"]["image2"], ["10006", 0])
        guide = graph["1265"]["inputs"]
        self.assertEqual(guide["image"], ["12004", 0])
        self.assertEqual(guide["frame_idx"], 0)
        self.assertEqual(graph["223"]["inputs"]["conditioning"], ["1265", 0])
        self.assertNotIn("ref_images.ref_image_1", graph["265"]["inputs"])

    def test_clip_frames_chain_tail_after_last_frame(self):
        self._guider_template()
        frames = self._clip(5)
        self.make_png(self.root / "tail.png")
        job = dict(self.jobs[0], clip_frames=frames, tail_image="tail.png")
        prepared = runner.materialize(self.root, self.config, job)
        names = ["ref.png"] + [f"f{i}.png" for i in range(5)] + ["t.png"]
        graph = runner.build_prompt(self.config, job, prepared, names, "r")
        self.assertEqual(graph["1266"]["inputs"]["image"], ["10007", 0])
        self.assertEqual(graph["1266"]["inputs"]["positive"], ["1265", 0])
        self.assertEqual(graph["223"]["inputs"]["conditioning"], ["1266", 0])

    def test_clip_frames_validation(self):
        self._guider_template()
        with self.assertRaises(runner.RunnerError):   # 少于 5 帧
            runner.materialize(self.root, self.config, dict(self.jobs[0], clip_frames=self._clip(4)))
        mixed = self._clip(5)
        self.make_png(self.root / "big.png", 16, 16)
        with self.assertRaises(runner.RunnerError):   # 尺寸不一致
            runner.materialize(self.root, self.config, dict(self.jobs[0], clip_frames=mixed[:4] + ["big.png"]))
        self.make_png(self.root / "notpng.png")
        (self.root / "bogus.png").write_bytes(b"not a png")
        with self.assertRaises(runner.RunnerError):
            runner.materialize(self.root, self.config, dict(self.jobs[0], clip_frames=mixed[:4] + ["bogus.png"]))
        with self.assertRaises(runner.RunnerError):   # 不能与单张首帧同时用
            runner.materialize(self.root, self.config,
                               dict(self.jobs[0], clip_frames=mixed, anchor_image_index=1))

    def test_clip_frames_change_fingerprint(self):
        frames = self._clip(5)
        base = runner.materialize(self.root, self.config, self.jobs[0])[-1]
        job = dict(self.jobs[0], clip_frames=frames)
        self.assertNotEqual(base, runner.materialize(self.root, self.config, job)[-1])


if __name__ == "__main__":
    unittest.main()
