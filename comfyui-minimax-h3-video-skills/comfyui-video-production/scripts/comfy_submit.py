#!/usr/bin/env python3
"""Project-local ComfyUI API runner. Python 3.10+, standard library only.

plan/prepare are offline. check is read-only. run uploads and submits, sequentially.
Never infer an executable API graph from a frontend canvas JSON.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import json
import struct
import mimetypes
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


class RunnerError(Exception):
    pass


class RequestError(RunnerError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
    temp.replace(path)


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(message):
    print(f"[{stamp()}] {message}", flush=True)


def project_path(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise RunnerError(f"项目内路径越界: {name}")
    return path


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Client:
    def __init__(self, base, timeout=30):
        self.base = base.rstrip("/")
        parsed = urllib.parse.urlsplit(self.base)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment:
            raise RunnerError("服务地址必须是 HTTP(S) base URL")
        # Bypass desktop proxy settings for the explicitly selected LAN endpoint.
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.timeout = timeout

    def request(self, path, body=None, content_type="application/json"):
        headers = {"Content-Type": content_type} if body is not None else {}
        req = urllib.request.Request(self.base + path, data=body, headers=headers)
        try:
            return self.opener.open(req, timeout=self.timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RequestError(f"HTTP {exc.code} {path}: {detail}", exc.code) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RunnerError(f"网络错误 {path}: {exc}") from exc

    def json(self, path, payload=None):
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
        with self.request(path, data) as response:
            return json.load(response)

    def upload(self, path, video_id):
        digest = file_hash(path)
        name = digest + path.suffix.lower()
        boundary = "comfy_" + uuid.uuid4().hex
        fields = {"type": "input", "subfolder": f"minimax-h3/{video_id}", "overwrite": "false"}
        body = bytearray()
        for key, value in fields.items():
            body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
        mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: {mime}\r\n\r\n'.encode())
        body.extend(path.read_bytes())
        body.extend(f"\r\n--{boundary}--\r\n".encode())
        with self.request("/upload/image", bytes(body), f"multipart/form-data; boundary={boundary}") as response:
            result = json.load(response)
        if not result.get("name"):
            raise RunnerError(f"上传响应缺少文件名: {result}")
        folder = result.get("subfolder", "").strip("/")
        return f"{folder}/{result['name']}" if folder else result["name"]

    def download(self, output, dest):
        query = urllib.parse.urlencode({k: output.get(k, "") for k in ("filename", "subfolder", "type")})
        partial = dest.with_suffix(dest.suffix + ".part")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self.request("/view?" + query) as response, partial.open("wb") as out:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                out.write(block)
        if partial.stat().st_size == 0:
            raise RunnerError(f"下载为空: {output['filename']}")
        partial.replace(dest)


def load_project(path):
    config_path = Path(path).resolve()
    root = config_path.parent
    config = read_json(config_path)
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", config.get("video_id", "")):
        raise RunnerError("video_id 仅允许字母、数字、下划线和连字符")
    jobs = read_json(project_path(root, config["jobs_file"]))["jobs"]
    ids = [j["id"] for j in jobs]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r"[a-zA-Z0-9_-]+", x) for x in ids):
        raise RunnerError("任务ID须唯一且仅包含字母、数字、下划线、连字符")
    return root, config, jobs


def select_jobs(jobs, names):
    if names:
        wanted = set(names.split(","))
        missing = wanted - {j["id"] for j in jobs}
        if missing:
            raise RunnerError(f"未知任务: {sorted(missing)}")
        # Selection does not reorder the manifest.
        selected = [j for j in jobs if j["id"] in wanted]
    else:
        selected = [j for j in jobs if j.get("enabled", False)]
    if not selected:
        raise RunnerError("没有可执行任务；启用任务或使用 --jobs ID1,ID2")
    return selected


def png_size(path):
    """Read a PNG's pixel size from its IHDR chunk without any image library."""
    with open(path, "rb") as fh:
        head = fh.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise RunnerError(f"clip_frames 只支持 PNG: {path}")
    return struct.unpack(">II", head[16:24])


SCENE_VIEW_ROLES = ("front", "back", "overhead_45", "top_90")


def scene_reference_contract(root, config, job, images, template):
    """Validate opt-in four-view projects without changing legacy inputs/order."""
    required = config.get("require_scene_references", False)
    if type(required) is not bool:
        raise RunnerError("require_scene_references 须为布尔值")
    active = required or any(k in job for k in ("scene_ids", "scene_reference_exception"))
    if not active:
        return None
    exception = job.get("scene_reference_exception")
    if exception is not None:
        if (not isinstance(exception, dict) or set(exception) != {"reason", "authorization"}
                or any(not isinstance(v, str) or not v.strip() for v in exception.values())):
            raise RunnerError("场景四图例外须记录非空 reason 与 authorization（用户授权依据）")
        if job.get("scene_ids"):
            raise RunnerError("四图例外不得同时声明 scene_ids；采用完整四图时移除例外")
        return {"exception": exception}
    ids = job.get("scene_ids")
    if (not isinstance(ids, list) or not ids
            or any(not isinstance(x, str) or not x.strip() for x in ids)
            or len(set(ids)) != len(ids)):
        raise RunnerError("任务须声明非空、无重复 scene_ids，默认完整使用每个场景的四图")
    if template.get("265", {}).get("class_type") != "MiniMaxH3ReferenceToVideo":
        raise RunnerError("场景四图须使用 Ref2VA 模板，不能静默改为仅首尾帧输入")
    sets = config.get("scene_reference_sets", {})
    if not isinstance(sets, dict):
        raise RunnerError("scene_reference_sets 须为场景ID到四图的映射")
    result = {}
    for scene_id in ids:
        views = sets.get(scene_id)
        if not isinstance(views, dict) or set(views) != set(SCENE_VIEW_ROLES):
            raise RunnerError(f"场景 {scene_id} 必须包含 front/back/overhead_45/top_90 四图")
        paths = []
        for role in SCENE_VIEW_ROLES:
            name = views[role]
            if not isinstance(name, str) or not name.strip():
                raise RunnerError(f"场景 {scene_id} 的 {role} 路径无效")
            path = project_path(root, name)
            if not path.is_file() or images.count(path) != 1:
                raise RunnerError(f"场景 {scene_id} 的 {role} 须在 images 中实际绑定且仅出现一次")
            paths.append(path)
        hashes = [file_hash(path) for path in paths]
        if len(set(paths)) != 4 or len(set(hashes)) != 4:
            raise RunnerError(f"场景 {scene_id} 四方向须为不同图片，不能重复单图凑数")
        result[scene_id] = {
            role: {"path": views[role], "sha256": digest, "picture_index": images.index(path) + 1}
            for role, path, digest in zip(SCENE_VIEW_ROLES, paths, hashes)
        }
    return {"scenes": result}


def materialize(root, config, job):
    if job.get("status") != "ready":
        raise RunnerError(f"{job['id']} 尚为草稿，不能提交")
    params = dict(config.get("defaults", {}))
    params.update(job.get("params", {}))
    seconds = params["seconds"]
    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or not 4 <= seconds <= 15:
        raise RunnerError("单段时长须为4–15秒")
    for key in ("width", "height"):
        if type(params[key]) is not int or params[key] < 32 or params[key] % 32:
            raise RunnerError(f"{key}须为正整数且为32的倍数")
    seed = params["seed"]
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise RunnerError("seed须为0到2**64-1的整数")
    profile = params["profile"]
    if profile not in config["workflows"]:
        raise RunnerError(f"未知工作流profile: {profile}")
    template = read_json(project_path(root, config["workflows"][profile]))
    if "nodes" in template or not template or any("class_type" not in n for n in template.values()):
        raise RunnerError("需要API格式工作流，不能直接提交画布JSON")
    prompt = project_path(root, job["prompt_file"]).read_text(encoding="utf-8").strip()
    if not prompt:
        raise RunnerError("提示词为空")
    images = [project_path(root, name) for name in job.get("images", [])]
    if not 1 <= len(images) <= 9 or not all(p.is_file() for p in images):
        raise RunnerError("须提供1–9张存在的图片")
    refs = {int(i) for i in re.findall(r"<Picture (\d+)>", prompt)}
    if refs != set(range(1, len(images) + 1)):
        raise RunnerError(f"图片引用须连续并与输入一致：引用{sorted(refs)}，图片数{len(images)}")
    scene_contract = scene_reference_contract(root, config, job, images, template)
    videos = [project_path(root, name) for name in job.get("videos", [])]
    if len(videos) > 3 or not all(p.is_file() for p in videos):
        raise RunnerError("视频参考须为0–3个存在的文件")
    video_refs = {int(i) for i in re.findall(r"<Video (\d+)>", prompt)}
    if video_refs != set(range(1, len(videos) + 1)):
        raise RunnerError(f"视频引用须连续并与输入一致：引用{sorted(video_refs)}，视频数{len(videos)}")
    if videos and template.get("265", {}).get("class_type") == "MiniMaxH3ImageToVideo":
        raise RunnerError("图生视频模板不接受参考视频")
    audios = [project_path(root, name) for name in job.get("audios", [])]
    if len(audios) > 3 or not all(p.is_file() for p in audios):
        raise RunnerError("音频参考须为0–3个存在的文件")
    audio_refs = {int(i) for i in re.findall(r"<Audio (\d+)>", prompt)}
    if audio_refs != set(range(1, len(audios) + 1)):
        raise RunnerError("音频引用编号须连续并与输入文件一致")
    anchor = job.get("anchor_image_index")
    if anchor is not None and (type(anchor) is not int or not 1 <= anchor <= len(images)):
        raise RunnerError("anchor_image_index须指向实际输入图片的1起始序号")
    if template.get("265", {}).get("class_type") == "MiniMaxH3ImageToVideo":
        if len(images) > 2 or audios or anchor is not None:
            raise RunnerError("图生视频模板仅接受首帧及可选尾帧，不接受参考音频或额外anchor_image_index")
        if job.get("tail_image") is not None:
            raise RunnerError("首尾帧模板请把尾帧放进 images 的第二张，不要用 tail_image")
    # 可选的尾帧锚点：不参与 <Picture N> 编号，只在 AddGuide 里锚定到指定帧。
    tail_path = None
    if job.get("tail_image") is not None:
        tail_path = project_path(root, job["tail_image"])
        if not tail_path.is_file():
            raise RunnerError(f"tail_image 不存在: {job['tail_image']}")
        tail_frame = job.get("tail_frame_index", -1)
        if type(tail_frame) is not int or not -9999 <= tail_frame <= 9999:
            raise RunnerError("tail_frame_index 须为 -9999 到 9999 的整数")
    # 可选的多帧片段锚点：按顺序锚成一段，不参与 <Picture N> 编号。
    clip_paths = [project_path(root, name) for name in job.get("clip_frames", [])]
    clip_frame_index = 0
    if clip_paths:
        if anchor is not None:
            raise RunnerError("clip_frames 与 anchor_image_index 不能同时使用")
        if template.get("265", {}).get("class_type") == "MiniMaxH3ImageToVideo":
            raise RunnerError("图生视频模板不支持 clip_frames")
        if len(clip_paths) < 5:
            raise RunnerError("clip_frames 至少 5 张；少于 5 帧只会用到第一张")
        if not all(p.is_file() for p in clip_paths):
            raise RunnerError("clip_frames 中有不存在的文件")
        if len({png_size(p) for p in clip_paths}) != 1:
            raise RunnerError("clip_frames 的尺寸必须一致")
        clip_frame_index = job.get("clip_frame_index", 0)
        if type(clip_frame_index) is not int or not -9999 <= clip_frame_index <= 9999:
            raise RunnerError("clip_frame_index 须为 -9999 到 9999 的整数")
    fingerprint_data = {
        "server": config["server"], "params": params, "template": template,
        "prompt": prompt, "images": [file_hash(p) for p in images],
    }
    if scene_contract is not None:
        fingerprint_data["scene_references"] = scene_contract
    # Keep old pure-image fingerprints stable for previously submitted tasks.
    if audios:
        fingerprint_data["audios"] = [file_hash(p) for p in audios]
    if videos:
        fingerprint_data["videos"] = [file_hash(p) for p in videos]
    if anchor is not None:
        fingerprint_data["anchor_image_index"] = anchor
    if tail_path is not None:
        fingerprint_data["tail_image"] = file_hash(tail_path)
        fingerprint_data["tail_frame_index"] = job.get("tail_frame_index", -1)
    if clip_paths:
        fingerprint_data["clip_frames"] = [file_hash(p) for p in clip_paths]
        fingerprint_data["clip_frame_index"] = clip_frame_index
    fingerprint = hashlib.sha256(json.dumps(fingerprint_data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    upload_images = images + clip_paths + ([tail_path] if tail_path is not None else [])
    return params, template, prompt, upload_images, fingerprint


def build_prompt(config, job, prepared, image_names, run_id, audio_names=None, video_names=None):
    params, template, text, _, _ = prepared
    base = round(params["seconds"] * 24)
    frames = base + (5 - base % 17) % 17
    values = {"PROMPT": text, "WIDTH": params["width"], "HEIGHT": params["height"],
              "LENGTH": frames, "SEED": params["seed"],
              "PREFIX": f"minimax-h3/{config['video_id']}/{job['id']}/{run_id}"}

    def replace(value):
        if isinstance(value, dict):
            return {k: replace(v) for k, v in value.items()}
        if isinstance(value, list):
            return [replace(v) for v in value]
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            key = value[2:-2]
            if key not in values:
                raise RunnerError(f"未知模板变量: {key}")
            return values[key]
        return value

    graph = replace(copy.deepcopy(template))
    conditioning = graph["265"]["inputs"]
    # Audio references and first-frame guides are opt-in per task.
    ref_count = len(job.get("images", []))
    clip_count = len(job.get("clip_frames", []))
    for i, name in enumerate(image_names):
        node_id = str(10001 + i)
        if node_id in graph:
            raise RunnerError("图片节点ID与模板冲突")
        graph[node_id] = {"class_type": "LoadImage", "inputs": {"image": name}}
        if i >= ref_count:
            # 片段帧或尾帧：已上传，但不作为 <Picture N> 参考。
            continue
        if graph["265"]["class_type"] == "MiniMaxH3ImageToVideo":
            conditioning["first_frame" if i == 0 else "last_frame"] = [node_id, 0]
        else:
            conditioning[f"ref_images.ref_image_{i}"] = [node_id, 0]
    for i, name in enumerate(audio_names or []):
        node_id = str(11001 + i)
        if node_id in graph:
            raise RunnerError("音频节点ID与模板冲突")
        graph[node_id] = {"class_type": "LoadAudio", "inputs": {"audio": name}}
        conditioning[f"ref_audios.ref_audio_{i}"] = [node_id, 0]
    for i, name in enumerate(video_names or []):
        node_id = str(13001 + i)
        if node_id in graph:
            raise RunnerError("视频节点ID与模板冲突")
        # H3 ref_videos takes IMAGE frames at 24 fps (2-15 s). VHS_LoadVideo is
        # the binding used by the user's optimized multi-reference template.
        graph[node_id] = {"class_type": "VHS_LoadVideo", "inputs": {
            "video": name, "force_rate": 24, "force_size": "Disabled",
            "custom_width": 0, "custom_height": 0, "frame_load_cap": 0,
            "skip_first_frames": 0, "select_every_nth": 1, "format": "AnimateDiff"}}
        conditioning[f"ref_videos.ref_video_{i}"] = [node_id, 0]
    if clip_count:
        # 多帧片段：把 m 张图拼成一个 IMAGE 批次，由 AddGuide 当片段锚定。
        first_img = str(10001 + ref_count)
        current = first_img
        for k in range(1, clip_count):
            batch_id = str(12001 + k - 1)
            if batch_id in graph:
                raise RunnerError("批量图节点ID与模板冲突")
            graph[batch_id] = {"class_type": "ImageBatch", "inputs": {
                "image1": [current, 0], "image2": [str(10001 + ref_count + k), 0]}}
            current = batch_id
        if "1265" in graph:
            raise RunnerError("首帧锚点节点ID与模板冲突")
        graph["1265"] = {"class_type": "MiniMaxH3AddGuide", "inputs": {
            "positive": ["265", 0], "latent": ["265", 1], "vae": ["36", 0],
            "image": [current, 0], "frame_idx": job.get("clip_frame_index", 0)}}
        graph["223"]["inputs"]["conditioning"] = ["1265", 0]
    elif job.get("anchor_image_index") is not None:
        guide_id = "1265"
        if guide_id in graph:
            raise RunnerError("首帧锚点节点ID与模板冲突")
        graph[guide_id] = {"class_type": "MiniMaxH3AddGuide", "inputs": {
            "positive": ["265", 0], "latent": ["265", 1], "vae": ["36", 0],
            "image": [str(10000 + job["anchor_image_index"]), 0], "frame_idx": 0}}
        graph["223"]["inputs"]["conditioning"] = [guide_id, 0]
    if len(image_names) > ref_count + clip_count:
        # 第二个 AddGuide 串在第一个后面，把尾帧锚到指定帧（默认最后一帧）。
        tail_id = "1266"
        if tail_id in graph:
            raise RunnerError("尾帧锚点节点ID与模板冲突")
        upstream = ["1265", 0] if (clip_count or job.get("anchor_image_index") is not None) else ["265", 0]
        graph[tail_id] = {"class_type": "MiniMaxH3AddGuide", "inputs": {
            "positive": upstream, "latent": ["265", 1], "vae": ["36", 0],
            "image": [str(10001 + ref_count + clip_count), 0],
            "frame_idx": job.get("tail_frame_index", -1)}}
        graph["223"]["inputs"]["conditioning"] = [tail_id, 0]
    return graph


def validate_graph(graph, info):
    """Validate links, installed classes, required inputs and declared model enums."""
    errors = []
    for node_id, node in graph.items():
        schema = info.get(node["class_type"])
        if not schema:
            errors.append(f"{node_id}: 未安装 {node['class_type']}")
            continue
        required = schema.get("input", {}).get("required", {})
        inputs = node["inputs"]
        for name in required:
            if name not in inputs:
                errors.append(f"{node_id}: 缺少输入 {name}")
        declared = dict(required)
        declared.update(schema.get("input", {}).get("optional", {}))
        for name, value in inputs.items():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str) and type(value[1]) is int:
                source = graph.get(value[0])
                outputs = info.get(source["class_type"], {}).get("output", []) if source else []
                if not source or not 0 <= value[1] < len(outputs):
                    errors.append(f"{node_id}.{name}: 无效连线 {value}")
                continue
            spec = declared.get(name)
            if not spec:
                continue  # Dynamic/autogrow and VHS codec fields are extension inputs.
            if (node["class_type"], name) in (("LoadImage", "image"), ("LoadAudio", "audio"), ("VHS_LoadVideo", "video")):
                # This enum lists files ALREADY on the server. New task images
                # are uploaded only by run, after read-only preflight succeeds.
                continue
            options = spec[0] if isinstance(spec[0], list) else None
            if spec[0] == "COMBO" and len(spec) > 1:
                options = spec[1].get("options")
            if options and value not in options:
                errors.append(f"{node_id}.{name}: 服务器不支持 {value!r}")
    if errors:
        raise RunnerError("预检失败:\n" + "\n".join(errors))


def output_files(history):
    found = []
    seen = set()
    for node_id, output in history.get("outputs", {}).items():
        for kind in ("gifs", "videos", "images", "audio"):
            entries = output.get(kind, [])
            if isinstance(entries, dict):
                entries = [entries]
            for item in entries:
                if not isinstance(item, dict) or not item.get("filename"):
                    continue
                if item.get("type") not in ("output", "temp"):
                    continue
                key = (item["filename"], item.get("subfolder", ""), item["type"])
                if key not in seen:
                    seen.add(key)
                    found.append((node_id, item))
    return found


def wait_history(client, prompt_id, timeout, poll):
    deadline = time.monotonic() + timeout
    last_notice = 0
    last_error = None
    while time.monotonic() < deadline:
        try:
            result = client.json("/history/" + urllib.parse.quote(prompt_id, safe=""))
            item = result.get(prompt_id)
            if item:
                status = item.get("status", {})
                failed = status.get("status_str") == "error" or any(
                    x[0] in ("execution_error", "execution_interrupted") for x in status.get("messages", []))
                if failed or status.get("completed"):
                    return item, failed
            last_error = None
        except RunnerError as exc:
            last_error = str(exc)
        if time.monotonic() - last_notice >= 30:
            log(f"等待 {prompt_id}" + (f"；暂时连接失败：{last_error}" if last_error else ""))
            last_notice = time.monotonic()
        time.sleep(poll)
    raise RunnerError(f"等待超时，保留任务ID，恢复时不会重新提交: {prompt_id}; {last_error or ''}")


@contextlib.contextmanager
def runner_lock(root):
    import fcntl
    path = root / "07_任务/runner.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RunnerError("本视频已有执行器运行，不能重复启动") from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def run_jobs(root, config, jobs, client, info, args):
    index_path = root / "07_任务/state.json"
    with runner_lock(root):
        index = read_json(index_path) if index_path.exists() else {"version": 1, "jobs": {}}
        for job in jobs:
            prepared = materialize(root, config, job)
            fingerprint = prepared[-1]
            previous = index["jobs"].get(job["id"])
            receipt_path = project_path(root, previous["receipt"]) if previous else None
            receipt = read_json(receipt_path) if receipt_path else None
            if receipt and receipt["fingerprint"] != fingerprint:
                raise RunnerError(f"{job['id']} 的参数或素材已变更；请用新的版本任务ID保留旧记录")
            if receipt and receipt["status"] == "completed" and all(
                project_path(root, f["path"]).is_file() and file_hash(project_path(root, f["path"])) == f["sha256"]
                for f in receipt.get("files", [])) and receipt.get("files"):
                log(f"跳过已完成 {job['id']}")
                continue
            if receipt and receipt["status"] == "failed":
                if not args.retry_failed:
                    raise RunnerError(f"{job['id']} 上次执行失败；修复后用 --retry-failed 显式重试")
                receipt = None
            if receipt is None:
                run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
                run_dir = root / "07_任务/runs" / run_id / job["id"]
                run_dir.mkdir(parents=True)
                names = [client.upload(p, config["video_id"]) for p in prepared[3]]
                audio_names = [client.upload(project_path(root, p), config["video_id"]) for p in job.get("audios", [])]
                video_names = [client.upload(project_path(root, p), config["video_id"]) for p in job.get("videos", [])]
                graph = build_prompt(config, job, prepared, names, run_id, audio_names, video_names)
                validate_graph(graph, info)
                write_json(run_dir / "workflow.api.json", graph)
                receipt_path = run_dir / "receipt.json"
                receipt = {"job_id": job["id"], "run_id": run_id, "fingerprint": fingerprint,
                           "server": client.base, "status": "submitting", "created_at": stamp(),
                           "prompt_id": str(uuid.uuid4()), "images": names, "params": prepared[0]}
                scene_contract = scene_reference_contract(
                    root, config, job,
                    [project_path(root, p) for p in job.get("images", [])], prepared[1])
                if scene_contract is not None:
                    receipt["scene_references"] = scene_contract
                if audio_names:
                    receipt["audios"] = audio_names
                if video_names:
                    receipt["videos"] = video_names
                if job.get("anchor_image_index") is not None:
                    receipt["anchor_image_index"] = job["anchor_image_index"]
                write_json(receipt_path, receipt)
                index["jobs"][job["id"]] = {"receipt": str(receipt_path.relative_to(root))}
                write_json(index_path, index)
                log(f"提交 {job['id']}，prompt_id={receipt['prompt_id']}")
                # Save intent BEFORE POST; never retry a submission on network failure.
                try:
                    body = {"prompt": graph, "prompt_id": receipt["prompt_id"],
                        "client_id": "minimax-h3-" + config["video_id"],
                        "extra_data": {"comfy_batch_run_id": run_id, "job_id": job["id"]}}
                    if getattr(args, "front", False):
                        q = client.json("/queue")
                        pend = [float(i[0]) for i in q.get("queue_pending", []) if i and len(i) > 0]
                        run = [float(i[0]) for i in q.get("queue_running", []) if i and len(i) > 0]
                        if pend:
                            body["number"] = min(pend) - 1.0
                        elif run:
                            body["number"] = max(run) + 0.5
                        else:
                            body["number"] = 0.0
                        log(f"插队提交：number={body['number']}（pending {len(pend)}，running {len(run)}）")
                    response = client.json("/prompt", body)
                except RunnerError as exc:
                    # A 4xx response explicitly rejects the request; timeout/5xx may
                    # occur after acceptance and must not trigger a blind retry.
                    rejected = isinstance(exc, RequestError) and exc.status is not None and 400 <= exc.status < 500
                    receipt["status"] = "failed" if rejected else "submission_unknown"
                    receipt["error"] = str(exc)
                    write_json(receipt_path, receipt)
                    raise
                write_json(run_dir / "submission.json", response)
                if response.get("node_errors") or not response.get("prompt_id"):
                    receipt.update(status="failed", error=response)
                    write_json(receipt_path, receipt)
                    raise RunnerError(f"提交未通过验证: {response}")
                receipt.update(status="submitted", prompt_id=response["prompt_id"])
                write_json(receipt_path, receipt)
            if receipt["status"] in ("submitting", "submission_unknown"):
                # Reconcile server receipts instead of risking duplicate GPU work.
                history = client.json("/history/" + receipt["prompt_id"])
                queue = client.json("/queue")
                accepted = receipt["prompt_id"] in history
                for item in queue.get("queue_running", []) + queue.get("queue_pending", []):
                    if item[1] == receipt["prompt_id"] or (len(item) > 3 and isinstance(item[3], dict)
                            and item[3].get("comfy_batch_run_id") == receipt["run_id"]):
                        receipt["prompt_id"] = item[1]
                        accepted = True
                if not accepted:
                    raise RunnerError(f"{job['id']} 提交结果不明，未在队列/历史找到；保留记录并停止，人工核实后再处理，禁止自动重投")
                receipt["status"] = "submitted"
                write_json(receipt_path, receipt)
            history, failed = wait_history(client, receipt["prompt_id"], args.wait_timeout, args.poll)
            write_json(receipt_path.parent / "history.json", history)
            if failed:
                receipt.update(status="failed", finished_at=stamp(), error=history.get("status"))
                write_json(receipt_path, receipt)
                raise RunnerError(f"{job['id']} 执行失败，已停止后续任务；查看 {receipt_path.parent / 'history.json'}")
            receipt["status"] = "downloading"
            write_json(receipt_path, receipt)
            outputs = output_files(history)
            if not outputs:
                raise RunnerError("执行完成但历史中未发现可下载输出，保留任务记录，不重投")
            files = []
            for seq, (node_id, item) in enumerate(outputs):
                # Remote paths are query parameters only; local filenames are sanitized.
                suffix = Path(item["filename"]).suffix.lower()
                if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
                    suffix = ".bin"
                dest = root / "08_输出" / job["id"] / receipt["run_id"] / f"{seq:02}_{node_id}{suffix}"
                client.download(item, dest)
                files.append({"path": str(dest.relative_to(root)), "sha256": file_hash(dest), "remote": item})
            receipt.update(status="completed", finished_at=stamp(), files=files)
            write_json(receipt_path, receipt)
            log(f"完成 {job['id']}，已下载{len(files)}个文件")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "prepare", "check", "run"])
    parser.add_argument("--project", required=True, help="video project.json path")
    parser.add_argument("--jobs", help="逗号分隔任务ID，仍按清单顺序执行；可选择未默认启用但ready的任务")
    parser.add_argument("--poll", type=float, default=5)
    parser.add_argument("--wait-timeout", type=float, default=7200, help="单任务等待秒数，不取消远端任务")
    parser.add_argument("--retry-failed", action="store_true", help="重投已明确失败的任务，不重投结果不明的任务")
    parser.add_argument("--front", action="store_true", help="插队提交：把 number 设为当前所有排队项之前（不影响正在跑的）")
    args = parser.parse_args(argv)
    if args.poll < 0.1 or args.wait_timeout <= 0:
        parser.error("poll至少0.1秒，wait-timeout必须大于0")
    try:
        root, config, all_jobs = load_project(args.project)
        jobs = select_jobs(all_jobs, args.jobs)
        compiled = []
        # Prepare ALL selected jobs before any upload or submission.
        for job in jobs:
            prepared = materialize(root, config, job)
            images = [f"minimax-h3/{config['video_id']}/{file_hash(p)}{p.suffix.lower()}" for p in prepared[3]]
            audios = [project_path(root, p) for p in job.get("audios", [])]
            audio_names = [f"minimax-h3/{config['video_id']}/{file_hash(p)}{p.suffix.lower()}" for p in audios]
            videos = [project_path(root, p) for p in job.get("videos", [])]
            video_names = [f"minimax-h3/{config['video_id']}/{file_hash(p)}{p.suffix.lower()}" for p in videos]
            graph = build_prompt(config, job, prepared, images, "PLAN", audio_names, video_names)
            compiled.append((job, graph))
            log(f"计划 {job['id']}: {prepared[0]['profile']}, {prepared[0]['seconds']}s, "
                f"{prepared[0]['width']}x{prepared[0]['height']}, {len(images)}张图, {len(video_names)}段视频, fingerprint={prepared[-1][:12]}")
        if args.command == "plan":
            return 0
        if args.command == "prepare":
            for job, graph in compiled:
                dest = root / "07_任务/prepared" / (job["id"] + ".api.json")
                write_json(dest, graph)
                log(f"已生成离线预览 {dest}；图片路径尚未上传")
            return 0
        client = Client(config["server"])
        stats = client.json("/system_stats")
        info = client.json("/object_info")
        for _, graph in compiled:
            validate_graph(graph, info)
        queue = client.json("/queue")
        log(f"服务版本 {stats.get('system', {}).get('comfyui_version', '?')}; "
            f"运行{len(queue.get('queue_running', []))}，等待{len(queue.get('queue_pending', []))}；预检通过")
        if args.command == "check":
            return 0
        run_jobs(root, config, jobs, client, info, args)
        return 0
    except (RunnerError, ValueError, KeyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("本地等待已停止，远端任务不会被取消；再次run将按已有记录恢复。", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
