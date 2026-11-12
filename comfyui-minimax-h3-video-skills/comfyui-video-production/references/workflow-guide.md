# 随附 ComfyUI 工作流说明

## 文件与用途

工作流随技能保存在 `assets/workflows/`，复制整个技能目录即可带走这些文件。

| 文件 | 用途 | 如何使用 |
| --- | --- | --- |
| [h3_direct_second_pass_v01.api.json](../assets/workflows/h3_direct_second_pass_v01.api.json) | 正式生产用完整二采 API **模板**，20 个基础节点 | 复制进本视频 `06_工作流/`，由 `scripts/comfy_submit.py` 注入提示词、参考素材和参数，再提交 |
| [h3_multireference_source_sanitized_v01.canvas.json](../assets/workflows/source/h3_multireference_source_sanitized_v01.canvas.json) | 原始多参考工作流的清理版画布，119 个节点 | 在 ComfyUI 中加载以查看和编辑原设计；不是当前生产 API 的等价可执行画布 |
| [manifest.json](../assets/workflows/manifest.json) | 文件角色、来源哈希、清理项及版本记录 | 校验搬运后的文件，追溯来源 |

**画布 JSON 与 API 模板不可互换。** 画布包含 Set/Get、组开关、Note 等前端结构；API 模板还包含待绑定变量，不能未经执行器处理就直接 POST `/prompt`。`prepare` 生成有效图预览，`run` 才上传并提交。

技能携带工作流、说明及 `scripts/` 内的执行工具，不包含模型权重、ComfyUI 节点插件、人物素材或已生成视频。迁移到别处仍需准备目标服务、所需节点／模型和本地运行依赖；依赖和接口见[执行适配](comfyui-h3.md)。

## 正式 API 的二采流程

一次任务内部完成两段采样，最终只解码二采结果：

```text
图片／可选声线 → 265 MiniMaxH3ReferenceToVideo
                        │ conditioning + 音视频 latent
                        ▼
223 BasicGuider → 226 第一采样（12步中的前8步）
                        ▼
139 分离视频／音频 latent
                        ▼
140 视频 latent 放大1.5倍、按32对齐
                        ▼
142 与原音频 latent 重新合并
                        ▼
224 BasicGuider → 144 第二采样（剩余4步）
                        ▼
116 视频解码 + 115 音频解码 → 214 视频与音轨合成
```

调度：`261 BasicScheduler` 为 beta、12 步、denoise 1.0；`289 SplitSigmas.step=8` 拆成 8+4；`255` 选择 euler。`256 RandomNoise` 接收实际 seed，两段使用模板既定噪声连线。后段需要前段输出，不是单独运行第二个采样节点。

以下配置是已用基线，不宣称对所有题材最优。源片仍须实际观看、听审，不能因工作流二采完成就认为内容通过。

## 模型与节点依赖

API 模板要求的模型文件名：

| 用途 | 文件名 |
| --- | --- |
| H3 主模型 | `minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors` |
| 加速 LoRA，权重 1.0 | `minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors` |
| 文本编码器 | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| 视频 VAE | `minimax_h3_video_vae_int8_convrot.safetensors` |
| 音频 VAE | `minimax_h3_audio_vae_fp32.safetensors` |
| latent 放大模型 | `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` |

需具备模板所列 H3 节点、音视频 latent 分离／合并与解码节点、`VHS_VideoCombine`，以及执行器按任务注入的 `LoadImage`、可选 `LoadAudio`／`MiniMaxH3AddGuide`。通过当前服务 `/object_info` 校验实际输入定义和可选模型；节点包缺失时先定位环境，不按近似名称静默替换。

API 没有额外风格 LoRA，也不含 SageAttention 补丁。不要因为源画布有某个分支就把它加入正式执行图。

## 输入参数和输出规格

| 模板变量／参数 | 配置位置与含义 |
| --- | --- |
| `{{PROMPT}}` | 任务 `prompt_file` 的全文；引用编号与实际图片、音频顺序相同 |
| `{{WIDTH}}` / `{{HEIGHT}}` | `project.json` 的 defaults 或任务 params；**第一段采样的输入尺寸**，至少32且为32的倍数 |
| `{{LENGTH}}` | 执行器根据 `seconds` 与24fps计算，并按H3帧数规则向上对齐 |
| `{{SEED}}` | defaults 或 params 的整数 seed，记录在有效图和回执中 |
| `{{PREFIX}}` | 执行器根据 video_id、job_id、run_id 生成，隔离不同输出 |
| `images` / `audios` | 任务指定的实际有序文件；执行器生成加载节点和引用连线 |
| `anchor_image_index` | 可选，指定哪张输入图片是首帧约束，序号从1开始 |

请求单段4–15秒。`base = round(seconds × 24)`，请求帧数 `base + (5 - base % 17) % 17`；实际成片取决于源片实测帧数及采用区间。按完整表演负载判断是否拆段，不设通用舒适区；超过本工作流请求上限须拆段，不压词或加速；拆镜与时长分配见[时长与流畅度](duration-and-flow.md)。

已测竖版基线是输入544×960、二采后832×1440。输入832×1440则曾输出1248×2176，不能把期望的二采输出尺寸直接填成输入。其他画幅按作品配置；尺寸对齐会影响精确比例，后期变换和续接约束使用同一坐标体系。

当前合成节点输出24fps、H.264、yuv420p、CRF19，保留生成音轨；这些是生成源片规格。最终交付尺寸、字幕、混音和片长在后期另行确定。二采潜空间放大与后期缩放分别记录。

## 场景四图输入

输入视频工作流前，四张静态图须按正面 → 参考正面生成反向平视回望 → 参考前两张生成45°俯视斜角全景 → 参考前三张生成90°垂直正俯视完整平面的顺序完成，逐步检查；详见[一致性资产 2.6.2](consistency-assets.md)。视频工作流不负责生成或验证这条生图依赖链。

每条涉及场景的视频任务默认通过 images 同时绑定前方向、后方向、45°俯视全景、90°垂直俯视全景四张图。使用 Ref2VA 模板；四图占四个独立参考槽位，角色、道具和首帧约束另外安排，总计不超过 9 张。不能因已有首帧或参考视频就删减四图。

任务与项目的 scene_reference_sets、scene_ids、require_scene_references 及例外契约见[执行适配](comfyui-h3.md)。prepare 后核对每张图的实际编号、LoadImage 和 ref_images 连线；首帧 Guide 的 anchor_image_index 指向实际首帧，不能误指俯视图。四图共同约束空间，不要求成片展示四图机位。

旧 360 工具与资产保留用于历史复现或显式专项需求，不再是新项目必备项，也不自动替代四图。

## 首帧续接如何连接

API 文件本身不固定某张图。任务设置 `anchor_image_index` 后，执行器增加 `1265 MiniMaxH3AddGuide`，将指定图片绑定 `frame_idx=0`，其 conditioning 接入第一段的 `223`。

第二段 `224` 继续使用 `265` 的原参考 conditioning，**不直接接原尺寸 Guide**。既有流程曾在放大后的第二段使用不匹配 Guide 时出现 shape mismatch，因此沿用当前接法。首帧引导不保证二采后像素完全不变，也不保证动作速度连续。

取上游最终采用版本的实际剪辑末帧，记录动作阶段、图像哈希和切点，再准备下游。具体选片、帧区间和连播方法见[连续性与验收](continuity-and-review.md)。

## 建立新视频项目的使用步骤

1. 先完成当前作品的脚本、分镜、全局基准及当前待生成镜的素材检查，选择目标画幅、时长、声音方案及已授权生成范围。
2. 将技能中的 `assets/workflows/h3_direct_second_pass_v01.api.json` **复制为普通文件**到本视频 `06_工作流/h3_direct_second_pass_v01.api.json`；不要直接让已提交任务引用会更新的技能资产。
3. 配置本视频 `project.json`。下面仅示范工作流映射和一组竖版参数；还须填写实际 `video_id`、`server`、`jobs_file`，并按执行适配登记 `scene_reference_sets`。服务器地址不能从示例或旧片猜测。

```json
{
  "require_scene_references": true,
  "workflows": {
    "final": "06_工作流/h3_direct_second_pass_v01.api.json"
  },
  "defaults": {
    "profile": "final",
    "width": 544,
    "height": 960,
    "seconds": 8,
    "seed": 12345
  }
}
```

4. 在 `jobs.json` 中声明 `scene_ids`，填写实际 `prompt_file`、包含完整场景四图的有序 `images`、按需 `audios` 和参数覆盖。首帧续接需要真实上游素材到位后再设 ready；不能只把依赖写在文本里就提前提交。
5. 按[执行适配](comfyui-h3.md#命令与提交范围)指定技能和项目路径，执行 `plan → prepare → check`。检查有效 API 的参考顺序、参数、两段采样和可选 Guide 接线；`check` 是只读预检，不占 GPU。
6. 当前任务已授权生成时才执行 `run`，逐条提交下载，保留回执。候选先内容检查再采用。命令形式、任务字段和失败恢复见[执行适配](comfyui-h3.md)。

## 源画布与正式 API 的差异

源画布来自原多参考工作流的 SageAttention 旁路版。随技能附带的清理副本删除了旧示例剧情、素材选择、媒体预览地址，并中性化输出前缀与两条说明文字；原始仓库文件未修改，来源 SHA256 见清单。

它保留原节点、连线、组开关、额外 LoRA 分支以及参考视频入口，便于追溯和手动编辑。它仍可能依赖额外前端扩展／节点，**加载成功与可运行需在实际 ComfyUI 环境核验**，不能直接点击排队就当作当前生产配置。尤其注意：

- 画布的参考视频分支不直接复制；当前执行器按任务 videos 注入 VHS_LoadVideo 与 ref_videos，使用前核对目标节点可用。
- 源画布的放大模型名称与生产 API 不同；正式执行使用上表的 `conv_v1` 文件。
- 源画布保留额外 LoRA 与前端控制分支；API 只保留既定生产模型栈和采样链。
- 源画布中的固定尺寸、提示说明及组开关状态属于来源设置，不覆盖本视频配置。

若需要一份与生产 API 完全等价、可直接在当前 UI 运行的画布，应基于实时节点定义另建版本，并完成导出 API 对照和获授权的小样验证。当前清理版仅做了离线 JSON 与结构检查，未声称已通过新的 UI 或 GPU 运行测试。

## 版本与维护

技能 `assets/workflows/` 是后续模板维护主位置；仓库旧 `templates/comfyui/h3_direct_second_pass_v01.api.json` 保留为初始快照，不再同步编辑。新项目从技能复制，已提交项目保持原锁定副本。

改模型、节点、采样或参数基线时建立新模板版本，更新清单与说明，并验证执行器绑定及实际输出；不能覆盖旧版本让旧片输入变化。搬运后可按 `manifest.json` 校验文件哈希。离线验证只证明格式与绑定，服务器环境和画面效果须在实际任务中另验。


## 插队提交（共享实例）

多人共用一个 ComfyUI 时，别人常常一次投很多条，按默认 FIFO 会排很久。执行器 `scripts/comfy_submit.py` 支持 `--front`：提交前读 `/queue`，把 POST body 的 `number` 设为当前所有 pending 项的最小值减一（无 pending 时取 running 最大值加 0.5），ComfyUI 会按这个序号把它排到前面。实测 `number=581.5` 排在他人 `582` 之前并立即执行。只在用户明确同意、且不打断正在跑的任务时使用。
