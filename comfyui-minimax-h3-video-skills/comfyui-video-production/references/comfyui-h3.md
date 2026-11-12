# ComfyUI / H3 执行适配

本文件描述随附执行器实现，不是所有 ComfyUI 节点的通用能力声明。移植或升级时重新读执行器与模板，并以目标服务的实时 `/object_info` 为准。下面的节点 ID 是当前执行器绑定接口；换模板时需同步验证，不能随意重编号。

## 依赖与工作流选择

工作流和通用执行工具都随技能分发；以下 `scripts/` 路径相对于本技能目录：

- `scripts/comfy_submit.py`：Python 3.10+ 标准库，任务绑定、预检、顺序提交、下载和恢复。
- [随附完整二采 API 模板](../assets/workflows/h3_direct_second_pass_v01.api.json)：新项目复制到自己的 `06_工作流/`，之后由本项目锁定版本。
- [源画布参考](../assets/workflows/source/h3_multireference_source_sanitized_v01.canvas.json)：可导入 ComfyUI 查看和编辑，含前端结构与额外分支，不直接提交也不代表生产配置；文件用途、差异与配置步骤见[工作流说明](workflow-guide.md)。
- `scripts/review_h3_clip.py`：依赖 ffmpeg/ffprobe，可按实际采用区间提取末帧和证据；不做内容批准。
- [batter-h3-prompt-writing](../../batter-h3-prompt-writing/SKILL.md)：写正式提示词前必须加载，负责分段规划、模式、结构、参考标签和局部说话人 ID；多段请求同时读其长视频指南。缺失时查找已安装副本，未找到则说明依赖缺失，不以旧版或记忆格式替代。模式须与真实执行能力匹配；通用提示词指南不表示此适配已支持所有模式。

现有项目优先沿用已验证的本地 API 模板，不用共享模板覆盖已提交输入。服务地址从当前项目配置或用户提供信息取得，不复用别部视频的内网 IP。依赖缺失时先补齐实际运行环境；随附脚本缺失则恢复完整技能目录，不能虚构接口或自动改用其他生成平台。远端节点与模型以实时 /object_info 为准；不静默替换模型、启用无关 LoRA，也不为兼容问题擅自升级远端 Python、PyTorch 或 CUDA。

### 当前二采基线

采样拓扑、模型清单、输入输出尺寸及首帧 Guide 接线统一见[工作流说明](workflow-guide.md)。实际工作流版本以项目中的锁定副本和运行快照为准。

### 实际支持的输入

| 模式 | 当前执行器支持 | 限制 |
| --- | --- | --- |
| 多参考 Ref2VA | 1–9 张图片；任务显式指定时 0–3 条参考音频；可选首帧 Guide；**可选尾帧 Guide**；可选 1–3 段参考视频 | 图片／音频／视频标签须连续且与数组顺序一致；视频用 `videos` → `VHS_LoadVideo` → `ref_videos.ref_video_0..2` |
| 专用 I2VA / 首尾帧 | 节点 265 为 `MiniMaxH3ImageToVideo` 的已适配 API 模板，1–2 张图依次为首帧和可选尾帧 | 不填 `anchor_image_index`，当前执行器不接受该模式的参考音频；共享 Ref2VA 模板不能直接冒充此模式 |
| 纯文生／尾帧单独约束 | 当前通用执行器没有对应的完整受支持绑定 | H3 提示词技能能写这些模式，不等于这里能提交；先按任务适配和验证，或说明缺失能力 |

**尾帧 Guide（2026-11-03 加入，实验性）**：Ref2VA 任务可加 `tail_image`（相对本视频目录的图片路径）与可选 `tail_frame_index`（默认 `-1`，负值从片尾数）。执行器在首帧 Guide 之后串一个 `MiniMaxH3AddGuide`（节点 `1266`），把尾帧图锚到指定帧，`223.conditioning` 接到它。尾帧图会随任务上传，但**不进入 `<Picture N>` 编号，也不绑定为 `ref_images`**，因此提示词里不必为它留编号。首帧 Guide 可省略，此时尾帧直接接 `265`。`MiniMaxH3ImageToVideo` 模板不支持该字段（用 `images` 第二张作尾帧）。

该节点本身还支持多帧片段锚定（5／22／39… 即 17k+5 帧）与音频锚定。**音频锚定执行器未绑定**；需要时先补能力再提交，不要只改任务字段就当成已支持。实测前不要假设两个 Guide 一定相容：串联后是否互相牵制、尾帧会不会压住首帧动作，都必须用真实片段验证。

**多帧片段 Guide（2026-11-03 加入，实验性）**：Ref2VA 任务可加 `clip_frames`（按顺序的 PNG 路径数组，≥5 张，尺寸必须一致）与可选 `clip_frame_index`（默认 `0`）。执行器把这几张图用 `ImageBatch` 串成一个 IMAGE 批次，交给 `1265 MiniMaxH3AddGuide` 当片段锚定；`clip_frames` 与 `anchor_image_index` 互斥。片段帧同样**不进入 `<Picture N>` 编号**。少于 5 帧只会用到第一张，所以执行器直接拒绝；段数会被节点裁到 17k+5，超过当前段数要求的帧要自己截。

用途：把上一镜实际采用的末几帧（5 帧 = 0.2 秒）锚到下一镜第 0 帧，比单张静帧更能带住运动方向和速度。取帧要来自该镜**实际剪辑区间**的末帧，并按 [连续性](continuity-and-review.md) 记录版本与帧号。同样未经实测：片段锚定会不会把上一镜的运镜惯性带过头，必须用真实片段验。

参考视频（2026-11-03 起绑定）：`ref_videos` 是 24fps 的 IMAGE 帧序列，2–15 秒、最多 3 段。任务加 `videos`（0–3 个文件），执行器上传后用 `VHS_LoadVideo`（`force_rate=24`、`frame_load_cap=0`、`format=AnimateDiff`）接 `ref_videos.ref_video_0..2`；提示词写 `<Video N>`。12fps 源按 24fps 读取，12 秒视频成为 288 帧。`ref_video_audios` 仍未绑定，参考视频的原声不自动进入生成。实测 `EP01_S01_v04` 已跑通（27 分钟）。

默认只用图片参考；参考音频／视频仅在任务显式设计时启用。不使用参考音频不等于关闭音频生成。参考音色、联合生成音轨和后期音乐是三个不同层次。

## 项目与任务最小契约

项目目录遵循[项目与素材约定](project-conventions.md)：`project.json`、入口说明、脚本与分镜、`01_角色/`、`02_场景/`、`03_道具/`、`04_声音/`、`05_提示词/`、`06_工作流/`、`07_任务/`、`08_输出/`、`09_交付/`、`99_归档/`。不需要的素材目录可不预先填充。不同片长使用对应分镜名称。

`project.json` 的执行器必要字段：

| 字段 | 约定 |
| --- | --- |
| `video_id` | 唯一标识，仅字母、数字、下划线、连字符 |
| `server` | 实际目标服务 URL |
| `jobs_file` | 相对项目目录的任务文件路径，通常 `07_任务/jobs.json` |
| `workflows` | profile 名称到本项目 API 文件的映射；`final` 名字本身不证明存在二采 |
| `defaults` | `profile`、`width`、`height`、`seconds`、`seed`；任务 `params` 覆盖它们 |

任务文件外层为 `{"version": 1, "jobs": [...]}`。每条任务必须有唯一 `id`、`enabled`、`status`、`prompt_file`、有序 `images`；按需要加 `params`、`audios`、`anchor_image_index`。镜头通常 `S01_v01`，技术测试用独立 `T00` 编号。

- `status: draft` 不可提交；输入和内容准备就绪才设 `ready`。`enabled: false` 不进入默认批次，显式 `--jobs` 可选其中已 ready 的任务。
- 清单顺序决定执行顺序，`--jobs` 的字符串排列不会重排。
- `depends_on` 等规划字段不能代替实际排程。执行器不会自动生成上游、抽尾帧、改写下游或级联重做；未解锁的下游保留 draft，不放进本轮 run 范围。
- 当前请求时长 4–15 秒；`base = round(seconds × 24)`，输出请求帧数为 `base + (5 - base % 17) % 17`。以实测源帧数和剪辑区间计算成片长度，不能把请求秒数当精确输出秒数。
- seed 为 0 到 `2**64-1` 的整数，绑定到 `RandomNoise.noise_seed`；不向 API 添加“fixed”字段。保存文件哈希、有效图、实际 seed、prompt_id 与回执。

素材和配置引用相对本视频目录。新增参考图更新素材清单（尺寸、字节数、SHA256）；重做用新版本，不覆盖已提交引用。身份静态参考图使用可用的内置图像生成能力；场景四图也可使用用户或本地规则已授权的 ComfyUI MOSS／Qwen 路线（对应生图工具和 API 工作流不随本技能附带，采用前另行准备并验证），后者占 GPU 并按授权执行。MOSS 提示词先经 moss-image-prompt-enhancer 编译。无适用能力时说明阻塞，不把文字方案当图片。

### 场景四图契约（新项目与新任务）

四图生图顺序及累积输入见[一致性资产 2.6.2](consistency-assets.md)：正面 → 反向平视回望（参考正面）→ 45°俯视斜角全景（参考前两张）→ 90°垂直正俯视完整平面（参考前三张）。这是图像生成阶段的依赖；下面字段用于随后的视频任务，不能代替生图记录或证明生图顺序已遵守。

新项目必须在 project.json 设置 require_scene_references=true，并按版本登记场景四图；已有项目的新修订任务也声明 scene_ids。示意配置：

```json
{
  "require_scene_references": true,
  "scene_reference_sets": {
    "room_v01": {
      "front": "02_场景/room_front_v01.png",
      "back": "02_场景/room_back_v01.png",
      "overhead_45": "02_场景/room_overhead45_v01.png",
      "top_90": "02_场景/room_top90_v01.png"
    }
  }
}
```

任务增加 scene_ids，例如 ["room_v01"]，并把四个路径全部放入实际 images 数组（顺序自行明确，不自动追加或重排）。每个路径仅出现一次，四张不得为相同内容复制；提示词 Picture 编号须覆盖所有实际图片。续接首帧可放第一张，再放四图与角色参考，anchor_image_index 按真实顺序设置。

预检要求：指定场景存在、四角色齐全且文件存在、四图逐张真实绑定、总图片数 1–9、使用 Ref2VA 模板、提示词引用完整。多个场景逐组检查。plan/prepare/check/run 共享该检查；有效 API 由原 images 顺序构建，回执保存角色、相对路径、哈希和 Picture 编号。结构检查不能证明四图的生成顺序、前序图实际参考情况、图片视角真实或提示词语义充分，仍需逐图检查和提示词审查。

确实无场景或用户明确允许例外时，任务使用 scene_reference_exception={"reason":"具体原因", "authorization":"可追溯用户授权依据"}，不同时声明 scene_ids；实际采用输入仍写 images 并正常校验。执行器检查记录非空，不验证授权真实性，agent 不得编造或用该字段自动绕过四图。

仅为兼容历史，未启用 require_scene_references 且没有新字段的旧任务保持原指纹。不要为恢复旧任务修改已提交输入；新任务必须声明契约，四图或契约变化后用新版本ID。登记场景组本身不会自动绑定到任务。

## 命令与提交范围

下面变量是命令形式示例：先将 `H3_SKILL_DIR` 设为本技能的实际绝对目录，`VIDEO_PROJECT` 设为真实项目配置的绝对路径，`JOB_IDS` 设为本次已就绪且获授权的范围。可从任意目录执行；项目内部素材仍使用相对项目路径：

```sh
python3 "$H3_SKILL_DIR/scripts/comfy_submit.py" plan --project "$VIDEO_PROJECT" --jobs "$JOB_IDS"
python3 "$H3_SKILL_DIR/scripts/comfy_submit.py" prepare --project "$VIDEO_PROJECT" --jobs "$JOB_IDS"
python3 "$H3_SKILL_DIR/scripts/comfy_submit.py" check --project "$VIDEO_PROJECT" --jobs "$JOB_IDS"
```

`plan` 离线校验，`prepare` 生成本地有效图预览；预估远端素材名不代表上传完成。`check` 只读查询服务、节点／模型和队列，不做 GPU 采样，也不能保证内容或显存通过。只有本次任务包含实际生成授权才执行：

```sh
python3 "$H3_SKILL_DIR/scripts/comfy_submit.py" run --project "$VIDEO_PROJECT" --jobs "$JOB_IDS"
```

一次只提交一条，前一条成功并下载后才下一条。技术失败停止，不继续烧掉整批预算。语义验收与技术执行分开：依赖上游选片的链条应分批运行，不能把所有下游提前就绪后期待执行器自动暂停等看片。

## 断线、失败与恢复

保存位置：`07_任务/state.json`、`runs/<运行ID>/<任务ID>/` 中的有效工作流、提交意图／回执、提交响应和历史；源片在 `08_输出/`。

- 已完成且输入指纹一致：执行器跳过；下载缺失时优先按原远端历史恢复，不重新采样。
- 断线、超时或提交响应丢失：按预存任务 ID 和队列／历史核实；停止本地等待不等于远端取消。结果不明时不得再次 POST。
- 已明确执行失败：修复后可在原授权范围用 `--retry-failed`；若输入／参数改变，则新建版本 ID。
- 内容不合格但技术成功：建立内容修订版，不用 `--retry-failed` 冒充技术失败；重生成服从当前范围。
- 不手动删除恢复依据或标记成功；不清空／中断他人任务。重试超出原授权范围或同一未知故障未解决时，先保留证据说明阻塞，不无界重跑。

## 本地辅助工具的真实边界

只有 `scripts/comfy_submit.py` 和 `scripts/review_h3_clip.py` 是随附生产工具。下列其他脚本是原仓库的可选历史工具，不是技能依赖；迁移后不假设它们存在。

- `review_h3_clip.py --project ... --job ... --duration ... --in-frame ... --revision ...`：仅支持恒定 24fps，从回执验证源片哈希，提取选段最后一帧；改变剪辑区间时新 evidence revision。依赖仍需人工核对，工具成功不是内容通过。
- `transcribe_h3_episode.py`：跨项目使用时显式传 `--jobs`，从该任务中文 `<d>` 读取期望对白；默认分支含旧项目台词，不通用。需要本地 numpy、faster-whisper、ffmpeg；其他语言先适配，不直接套中文 ASR。
- `prepare_h3_episode.py` / `render_h3_episode.py`：包含旧片角色、情节或固定规格，**不作为新作品的默认生成／渲染入口**。
- `prepare_h3_continuation.py`：有特定植物草稿字符串替换，还会改任务启用范围；不能当任意题材的自动续接工具。优先使用已验证的抽帧工具，按当前镜头补写续接并核对清单。
- `render_h3_timeline.py`：按帧区间渲染，但目前固定 24fps、竖版尺寸与本地字体等假设；不是跨画幅的通用渲染器。先核对实际 schema、画幅和声音处理，再决定复用或小范围适配。

后期优先使用适合当前项目的现有工具或 ffmpeg 可复现命令。不复制一套单片硬编码脚本作为技能附件。本技能新增的通用执行工具放技能 `scripts/` 并离线／模拟测试；远端节点实时核查和 GPU 小样分别在实际生成任务中完成，不因编辑技能就占用 GPU。

## 迁移与离线自检

完整复制本技能（含 scripts、references、assets），另准备 batter-h3-prompt-writing。只做规划无需连接 ComfyUI；写正式提示词、生成图片、提交视频时分别检查对应依赖。不要复制旧作品的 server、state.json 或 runs 充当新项目配置。

设置前述 H3_SKILL_DIR 后运行：

```sh
python3 "$H3_SKILL_DIR/scripts/comfy_submit.py" --help
python3 "$H3_SKILL_DIR/scripts/review_h3_clip.py" --help
python3 "$H3_SKILL_DIR/scripts/test_comfy_submit.py"
python3 "$H3_SKILL_DIR/scripts/test_review_h3_clip.py"
```

提交器测试使用标准库与模拟客户端，不连接真实服务。抽帧测试额外需要 Pillow、ffmpeg、ffprobe（Pillow 仅用于测试；生产抽帧脚本不依赖它）；缺少 ffmpeg 时测试会跳过，不能算抽帧已验证。新项目再按真实素材走 plan → prepare → check；仅 run 会提交生成。

抽帧示例（VIDEO_PROJECT 是配置文件路径，不是目录；仅支持恒定 24fps）：

```sh
python3 "$H3_SKILL_DIR/scripts/review_h3_clip.py" --project "$VIDEO_PROJECT" --job S01_v01 --duration 8 --in-frame 0 --revision 1
```

duration 和 in-frame 必须替换为实际选片区间；修改区间用新 revision，抽帧成功不等于内容验收。
