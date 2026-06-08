# Branch Handling Reference

## Shadow Repo Branch Mirroring

影子仓库为每个主仓库分支维护独立的 checkpoint 历史：

```
主仓库分支          影子仓库分支
master      ←→     ai-checkpoint/master
feature-a   ←→     ai-checkpoint/feature-a
feature-b   ←→     ai-checkpoint/feature-b
```

## Branch Switch Detection

分支切换在每次 `save` 时自动检测，通过比较 `branch-state.json` 中的 `last_branch` 和当前主仓库分支。

### Scenario 1: Clean Switch (branch clean, no uncommitted AI changes)

```
Before: 主仓库 feature-a, 工作树 clean, 影子 ai-checkpoint/feature-a 有 CK1-CK3
Action: git checkout feature-b
After:  主仓库 feature-b, 工作树 = feature-b 状态, 影子 HEAD 仍在 ai-checkpoint/feature-a
Next save: 
  → 检测到分支从 feature-a → feature-b
  → 影子仓库 symbolic-ref HEAD → ai-checkpoint/feature-b (或创建新分支)
  → 提交当前 feature-b 状态为初始 checkpoint
```

### Scenario 2: Switch with Uncommitted AI Changes (no conflict)

```
Before: 主仓库 feature-a, 工作树 = feature-a + AI 修改, 影子 ai-checkpoint/feature-a 有 CK1-CK3 (CK3 含 AI 修改状态)
Action: git checkout feature-b (git 允许，因文件不冲突)
After:  主仓库 feature-b, 工作树 = feature-b 文件 + AI 修改被带过来
Next save:
  → 检测到分支从 feature-a → feature-b
  → 如果 ai-checkpoint/feature-b 已存在: symbolic-ref 切换
  → 如果不存在: checkout --orphan 创建
  → 提交当前状态 (feature-b + AI 修改) 为 feature-b 分支的 checkpoint

Recovery: 切回 feature-a 时，rollback 到 CK3 可恢复原 AI 修改
```

### Scenario 3: Switch with Conflicts (git blocks)

```
Before: 工作树有 AI 修改 file-a.ts
Action: git checkout feature-b (远程 feature-b 也修改了 file-a.ts)
Result: git 阻止: "Your local changes would be overwritten"
Action: ai-checkpoint save "before branch switch"  → 保存当前状态
        然后选择: git stash / git commit / git checkout -- file-a.ts
        再 git checkout feature-b
```

## Recovery Commands

### Recover AI changes after switching back

```bash
# 切回原分支后，恢复未合并的 checkpoint 状态
ai-checkpoint list              # 查看 ai-checkpoint/feature-a 的检查点
ai-checkpoint rollback CK3      # 恢复文件到最后一次 checkpoint 状态
```

### Recover single file from a checkpoint

```bash
# 从影子仓库提取特定文件的特定版本
git --git-dir=.ai-git-worktree/.git show <checkpoint-sha>:path/to/file.ts > path/to/file.ts
```

### Find which checkpoint contains specific content

```bash
# 搜索影子仓库历史中的文件内容
git --git-dir=.ai-git-worktree/.git log --all --oneline -- path/to/file.ts
git --git-dir=.ai-git-worktree/.git show <sha>:path/to/file.ts
```

## Key Git Commands Used

| Operation | Command |
|-----------|---------|
| Switch shadow branch (existing) | `git --git-dir=.ai-git-worktree/.git symbolic-ref HEAD refs/heads/ai-checkpoint/<branch>` |
| Create new shadow branch | `git --git-dir=.ai-git-worktree/.git checkout --orphan ai-checkpoint/<branch>` |
| Save checkpoint | `git --git-dir=.ai-git-worktree/.git --work-tree=. add -A && commit` |
| List checkpoints | `git --git-dir=.ai-git-worktree/.git log --oneline` |
| Rollback files | `git --git-dir=.ai-git-worktree/.git --work-tree=. checkout <sha> -- .` |

## Why `symbolic-ref` Instead of `checkout`

`git symbolic-ref HEAD <ref>` 直接修改 `.git/HEAD` 文件内容，**只改变 HEAD 指向，不触碰 index，不触碰工作树**。这是切换影子分支的核心——工作树的文件由主仓库管理，影子仓库只需要更新 HEAD 指针来匹配。

对比 `git checkout <branch>`：会尝试更新 index 和工作树来匹配目标分支，这会和主仓库的工作树状态冲突。
