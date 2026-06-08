---
name: ai-checkpoint
description: Shadow git repository checkpoint system for AI code modifications. Use when the user wants to (1) Initialize an independent shadow git repo that snapshots the project after each AI modification, (2) Save named checkpoints at any point during development, (3) List and rollback to previous checkpoints when AI makes mistakes, (4) Recover from destructive git operations like checkout/reset, or (5) Manage checkpoints across multiple branches and sessions. Core principle: no conflict, no risk, protect code. The shadow repo is completely independent from the main repo and never pollutes its git history.
---

# AI Checkpoint

基于影子 Git 仓库的 AI 代码修改检查点系统。影子仓库（`.ai-git-worktree/.git/`）完全独立于主仓库（`.git/`），通过 `--work-tree=.` 指向项目根目录，记录每一次 AI 修改后的项目完整状态。

**核心原则**：影子仓库是纯备份系统。它只做两件事——`add -A && commit`（保存快照）和 `checkout <commit> -- .`（回退文件）。**从不向主仓库写入任何内容。**

## AI 行为规范（必须遵守）

### 自动保存检查点

每次完成一个逻辑单元后，**自动执行** `/ai-checkpoint save "<简短描述>"`。逻辑单元的定义：
- 完成一个 feature 或 bugfix
- 完成一次重构
- 用户说 "保存一下"、"checkpoint" 或类似表述
- 进行了可能需要回退的大范围修改

**不要每改一行就 save**，在逻辑边界处保存。

### 破坏性操作前强制保存

在执行以下**任何破坏性 git 命令之前**，**必须先执行** `/ai-checkpoint save "before <command>"`：
- `git checkout .` 或 `git checkout -- <files>`
- `git reset --hard`
- `git clean -fd`
- `git stash drop`
- `git rebase --abort` / `git merge --abort`
- 任何可能覆盖或删除未提交修改的操作

### 用户手动命令

用户也可以随时手动调用：
- `/ai-checkpoint save "描述"` —— 手动保存
- `/ai-checkpoint list` —— 查看所有检查点
- `/ai-checkpoint rollback <ref>` —— 回退到指定检查点
- `/ai-checkpoint status` —— 查看当前状态

---

## 命令详解

### `/ai-checkpoint init`

初始化影子仓库（每个项目只需执行一次）。

```
init:
  1. 检查 .ai-git-worktree/.git 是否已存在
     → 已存在则报告 "影子仓库已初始化"，跳过创建，但仍检查 .gitignore
  2. mkdir -p .ai-git-worktree
  3. git --git-dir=.ai-git-worktree/.git init
  4. 写入 .ai-git-worktree/.git/info/exclude:
       .git/
       .ai-git-worktree/
  5. 复制主仓库 .gitignore 的规则追加到 exclude（减少 add -A 噪音）
  6. 确保 .ai-git-worktree/ 在主仓库 .gitignore 中
     → 如果不存在该行，追加到 .gitignore
  7. 创建初始 branch-state.json:
       {
         "last_branch": "<current-branch>",
         "last_main_head": "<current-head-sha>",
         "last_shadow_commit": null
       }
  8. 创建初始快照:
     git --git-dir=.ai-git-worktree/.git --work-tree=. add -A
     git --git-dir=.ai-git-worktree/.git --work-tree=. commit -m "ai-checkpoint: initial snapshot [main:<short-sha>]"
     更新 branch-state.json 中的 last_shadow_commit
  9. 报告: "影子仓库初始化完成。初始快照: <sha>"
```

### `/ai-checkpoint save [描述]`

保存当前项目状态为检查点。执行 8 步处理逻辑：

```
save(description):
  ── 1. 收集当前状态 ──
  current_branch    = git rev-parse --abbrev-ref HEAD
  current_main_head = git rev-parse HEAD
  shadow_dir        = ".ai-git-worktree/.git"
  work_tree         = "."
  timestamp         = date +"%Y-%m-%d %H:%M:%S"

  ── 2. 读取上次记录 ──
  如果 .ai-git-worktree/branch-state.json 不存在:
    报告 "影子仓库未初始化，请先运行 /ai-checkpoint init"
    返回
  state = 读取 branch-state.json
  last_branch    = state.last_branch
  last_main_head = state.last_main_head

  ── 3. 分支切换检测 ──
  if current_branch != last_branch:
      shadow_branch = "ai-checkpoint/" + current_branch
      
      检查影子仓库中是否已有该分支:
      if git --git-dir=<shadow_dir> rev-parse --verify <shadow_branch> >/dev/null 2>&1:
        分支存在 →
          git --git-dir=<shadow_dir> symbolic-ref HEAD refs/heads/<shadow_branch>
          （只移动 HEAD 指针，不触碰 index，不触碰工作树）
        分支不存在 →
          git --git-dir=<shadow_dir> checkout --orphan <shadow_branch>
          （创建空分支，index 被清空，工作树不变）
      
      更新 state.last_branch = current_branch
      标记: "已切换到分支 <current_branch>"

  ── 4. 主仓库新提交检测 ──
  if current_main_head != last_main_head AND current_branch == last_branch:
      标记: "主仓库在此分支上有新提交（pull 或手动 commit）"
      （此步骤仅用于报告，不影响后续处理）

  ── 5. 检查工作树是否有变更 ──
  git --git-dir=<shadow_dir> --work-tree=<work_tree> status --porcelain
  if 输出为空:
      报告 "无变更，跳过 checkpoint"
      返回

  ── 6. 保存快照 ──
  short_sha = git rev-parse --short <current_main_head>
  git --git-dir=<shadow_dir> --work-tree=<work_tree> add -A
  
  if 描述不为空:
      commit_msg = "ai-checkpoint: <timestamp> [main:<short_sha>] - <描述>"
  else:
      commit_msg = "ai-checkpoint: <timestamp> [main:<short_sha>]"
  
  git --git-dir=<shadow_dir> --work-tree=<work_tree> commit -m <commit_msg>
  new_sha = git --git-dir=<shadow_dir> rev-parse --short HEAD
  files_changed = git --git-dir=<shadow_dir> diff --stat HEAD~1..HEAD 的统计

  ── 7. 更新状态文件 ──
  state.last_main_head    = current_main_head
  state.last_shadow_commit = new_sha
  写入 .ai-git-worktree/branch-state.json

  ── 8. 报告 ──
  输出: "Checkpoint <new_sha> saved (<N> files changed)"
  if 第 3 步检测到分支切换:
      输出: "已切换到分支 <current_branch>"
  if 第 4 步检测到主仓库有新提交:
      输出: "主仓库有新的提交"
```

### `/ai-checkpoint list [N]`

列出当前影子分支的最新 N 个检查点（默认 20）。

```
list(N=20):
  1. 获取当前影子分支:
     shadow_branch = git --git-dir=.ai-git-worktree/.git symbolic-ref --short HEAD
  2. 列出检查点:
     git --git-dir=.ai-git-worktree/.git log --oneline -<N>
  3. 格式化输出:
     序号  Commit SHA  时间  描述
     -----------------------------------------
     1    abc1234      2026-06-04 14:30:52  完成 feature X
     2    def5678      2026-06-04 14:15:03  修复 bug Y
     ...
```

### `/ai-checkpoint status`

显示当前影子仓库和主仓库的综合状态。

```
status:
  1. 读取 branch-state.json
  2. 当前分支: <branch>
  3. 影子仓库分支: ai-checkpoint/<branch>
  4. 检查点总数: git --git-dir=.ai-git-worktree/.git rev-list --count HEAD
  5. 最近检查点: <sha> (<timestamp>)
  6. 主仓库 HEAD: <sha>
  7. 主仓库是否有新提交: 比较 last_main_head vs current_main_head
  8. 未保存的修改:
     git --git-dir=.ai-git-worktree/.git --work-tree=. status --short
  9. 影子仓库磁盘占用: du -sh .ai-git-worktree/.git
```

### `/ai-checkpoint rollback <ref>`

回退项目文件到指定检查点。`<ref>` 可以是：序号（来自 list）、commit SHA、或简短 SHA。

**安全机制：回退前自动保存当前状态。**

```
rollback(ref):
  ── 1. 解析 ref ──
  if ref 是数字（序号）:
      从 list 输出中解析对应的 commit SHA
  else:
      full_sha = git --git-dir=.ai-git-worktree/.git rev-parse <ref>
      如果失败: 报告 "无效的检查点引用: <ref>"，返回

  ── 2. 自动保存当前状态 ──
  检查工作树是否有未保存变更:
  git --git-dir=.ai-git-worktree/.git --work-tree=. status --porcelain
  如果有变更:
      save("auto-save before rollback to <ref>")
      输出: "已自动保存当前状态为 checkpoint"

  ── 3. 展示将丢失的检查点 ──
  git --git-dir=.ai-git-worktree/.git log --oneline <ref>..HEAD
  输出: "以下检查点将被回退（文件将恢复到 <ref> 时的状态）："
  列出所有将被回退的检查点

  ── 4. 强调等待用户确认 ──
  输出: "WARNING: 这将修改工作树中的所有文件到检查点 <ref> 的状态。"
  输出: "当前 HEAD 之后的所有检查点不会被删除（仍可通过 commit SHA 访问），"
  输出: "但工作树文件将被覆盖。"
  要求用户明确确认（如输入 "yes"）

  ── 5. 执行回退 ──
  git --git-dir=.ai-git-worktree/.git --work-tree=. checkout <full_sha> -- .
  输出: "已回退到检查点 <ref> (<full_sha>)。"
  输出: "N 个文件已恢复。"
  输出: "提示：如果反悔，可 rollback 到刚才自动保存的检查点。"
```

**注意**：`git checkout <ref> -- .` 只修改工作树文件，不移动影子仓库的 HEAD。这意味着：
- 旧的检查点仍然保留在影子仓库历史中
- 下次 save 会基于当前工作树状态创建新检查点
- 任何时候都可以通过 commit SHA 访问任意历史检查点

### `/ai-checkpoint diff [ref1] [ref2]`

显示检查点之间或与当前状态的差异。

```
diff(ref1, ref2):
  ── 无参数：当前未保存修改 vs 最新检查点 ──
  git --git-dir=.ai-git-worktree/.git --work-tree=. diff HEAD

  ── 一个参数：指定检查点 vs 最新检查点 ──
  git --git-dir=.ai-git-worktree/.git diff <ref1>..HEAD

  ── 两个参数：两个检查点之间 ──
  git --git-dir=.ai-git-worktree/.git diff <ref1>..<ref2>
```

### `/ai-checkpoint branch-list`

列出影子仓库中所有分支及各自检查点概况。

```
branch-list:
  1. 列出所有 ai-checkpoint/* 分支:
     git --git-dir=.ai-git-worktree/.git branch --list 'ai-checkpoint/*'
  2. 对每个分支显示:
     - 分支名及对应的主仓库分支
     - 检查点数量
     - 最近检查点时间和描述
```

### `/ai-checkpoint cleanup`

清理维护操作。

```
cleanup:
  1. 检查 .ai-git-worktree/.lock 是否存在:
     → 存在且修改时间超过 5 分钟: 视为过期锁，自动清理
     → 存在且修改时间在 5 分钟内: 警告 "可能有其他 session 正在操作，跳过清理"
  2. 运行 git gc 压缩影子仓库:
     git --git-dir=.ai-git-worktree/.git gc --auto
  3. 显示影子仓库磁盘占用:
     du -sh .ai-git-worktree/.git
  4. 可选：压缩旧检查点（用户确认后执行）:
     → 将超过 7 天的检查点压缩为单个 commit（保留最终状态）
```

---

## 影子仓库原理

### 与主仓库的物理隔离

```
项目根目录/
├── .git/                          ← 主仓库 (git add / git commit 操作这里)
│   ├── objects/
│   └── refs/heads/
│
└── .ai-git-worktree/
    ├── .git/                      ← 影子仓库 (ai-checkpoint 操作这里)
    │   ├── objects/               ← 独立的 commit/blob/tree 数据库
    │   ├── refs/heads/ai-checkpoint/  ← 独立的分支（与主仓库分支一一对应）
    │   └── info/exclude           ← 排除 .git/ 和 .ai-git-worktree/
    └── branch-state.json          ← 分支追踪元数据
```

两个 `.git/` 目录物理隔离，object 数据库互不可见。主仓库的 `git log` 永远不会显示影子仓库的提交。

### 正向工作流

```
AI 修改文件 → 影子仓库 snapshot（备份）
     ↓
用户审查 git status / git diff
     ↓
用户 git add && git commit（正常提交流程，与影子仓库无关）
```

### 回退工作流

```
AI 出错 / git checkout . / reset --hard
     ↓
ai-checkpoint rollback <ref>
     ↓
影子仓库 checkout 恢复文件
```
