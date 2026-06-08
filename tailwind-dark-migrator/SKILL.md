---
name: tailwind-dark-migrator
description: Migrate Tailwind CSS projects from `dark:` hardcoded prefixes to a semantic CSS variable dual-mode system. Use when the user wants to (1) Remove all `dark:` class prefixes from a Tailwind project, (2) Set up a light/dark dual-mode theme using CSS custom properties, (3) Convert hardcoded zinc/slate colors to semantic variables like `text-heading` / `bg-surface` / `border-divider`, (4) Refactor a Tailwind v3 or v4 project to use `@theme inline` or `theme.extend` based color variables, or (5) Audit and fix inconsistent dark-mode color patterns across a frontend codebase. Supports React, Vue, Svelte, and plain HTML with Tailwind CSS v3 or v4.
---

# Tailwind Dark Mode Migrator

将 Tailwind CSS 项目从 `dark:` 硬编码前缀迁移到 CSS 变量双模式主题系统。

**配套 skill**：`tailwind-semantic-starter`（新项目或新组件从零搭建语义变量体系时使用）

## 工作流（10 步）

### Step 1：检测环境

读取 `package.json` 和项目文件结构，确认：
1. **Tailwind 版本**：检查 `dependencies`/`devDependencies` 中的 `tailwindcss` 版本
2. **框架类型**：`.tsx/.jsx`（React）/ `.vue`（Vue）/ `.svelte`（Svelte）/ `.html`
3. **配置入口**：v4 找 `index.css`（含 `@import "tailwindcss"`）；v3 找 `tailwind.config.js`
4. **已有变量**：检查全局 CSS 是否已有 CSS variables

未找到 Tailwind 则中止并报告。

### Step 2：扫描 dark: 模式

运行脚本（`SKILL_DIR` 为本 skill 目录的绝对路径）：

```bash
python <SKILL_DIR>/scripts/scan_dark_patterns.py <project_root> -o dark-report.json
```

读取生成的 `dark-report.json`，了解：
- 含 `dark:` 的文件总数、出现次数
- 按类别分组（text_color / bg_color / border_color / accent_color / gradient / utility_class / focus_ring / disabled / other）
- 每个文件的模式及行号

> 若报告显示 0 次，询问用户是否继续。

### Step 3：规划变量架构

根据扫描结果设计 L1/L2/L3 变量层级。

> ⚠️ **变量名称 vs 变量的值**：
> - **变量名称**（如 `text-heading`、`bg-surface`）：由本 skill 定义，固定使用
> - **变量的值**（即 `:root` / `.dark` 中写什么颜色）：必须从项目现有的 `dark:` 对中提取，
>   `references/` 中的颜色值仅为**语义映射示例**，不得直接撬起写入项目

**L2 基础变量（始终创建）**：
```
text-heading, text-body, text-caption, text-hint, text-placeholder, text-inverse
bg-surface, bg-elevated, bg-inset, bg-overlay, bg-surface-hover, bg-surface-faint
border-divider, border-divider-subtle, border-divider-strong
```

**L3 变量（按扫描结果按需创建）**：
- 存在强调色（sky/teal/emerald 等）→ `accent-*` 变量
- 存在激活/选中态 → `option-active-*` 变量
- 存在渐变 → 场景渐变变量
- 存在 badge 颜色 → `badge-*-text` 变量
- 存在工具类含 `dark:` → `glass-*` / `glow-hover-*` 变量
- 存在 focus-ring → `ring-offset` 变量
- 存在 disabled → `disabled` 变量

完整映射表（语义对应关系）见 `references/common-patterns.md`。

### Step 4：注册变量到 Tailwind 配置

#### Tailwind v4（CSS 配置）

编辑全局 CSS 文件（通常 `src/index.css`）：
1. 确保存在 `@import "tailwindcss"` 和 `@custom-variant dark`
2. 添加 `@theme inline` 块，注册所有 `--color-*`
3. 添加 `:root` 块（亮色值）和 `.dark` 块（暗色值）

> ⚠️ **`:root` / `.dark` 中的颜色值必须从项目现有的 `dark:` 对中提取**，例如：
> `text-zinc-900 dark:text-zinc-100` → 亮色取 zinc-900 的实际色値，暗色取 zinc-100 的实际色値
> 不得把 `references/tailwind-v4-setup.md` 里的示例 oklch 数字直接拷贝到项目中

完整模板结构见 `references/tailwind-v4-setup.md`。

#### Tailwind v3（JS 配置）

编辑 `tailwind.config.js`：
1. 确保 `darkMode: 'class'`
2. 在 `theme.extend.colors` 中添加所有变量映射
3. 在全局 CSS 中添加 `:root` / `.dark` 变量赋值

完整模板见 `references/tailwind-v3-setup.md`。

> **关键**：每个在 `@theme inline`（v4）或 `theme.extend.colors`（v3）中注册的变量，必须在 `:root` 和 `.dark` 中都有对应赋值。

### Step 5：替换 L2 语义模式（批次 1）

在所有源文件中替换最常见模式：

```
text-zinc-900 dark:text-zinc-100   → text-heading
text-zinc-700 dark:text-zinc-300   → text-body
text-zinc-600 dark:text-zinc-400   → text-caption
text-zinc-500 dark:text-zinc-400   → text-caption
text-zinc-400 dark:text-zinc-600   → text-placeholder
text-zinc-400 dark:text-zinc-500   → text-hint
bg-white dark:bg-zinc-900          → bg-surface
hover:bg-black/5 dark:hover:bg-white/5 → hover:bg-surface-hover
border-black/10 dark:border-white/10   → border-divider
```

用 `grep` + `sed` 或编辑器批量替换，每批处理 5-10 个文件。

### Step 6：替换 L3 强调色与场景模式（批次 2）

```
text-sky-500 dark:text-sky-400         → text-accent-sky
text-teal-500 dark:text-teal-400       → text-accent-teal
text-emerald-500 dark:text-emerald-400 → text-accent-emerald
bg-teal-500/10 dark:bg-teal-500/20 text-teal-600 dark:text-teal-300
  → bg-option-active-bg text-option-active-text
from-red-50 to-white dark:from-red-950/10 dark:to-slate-900
  → from-alert-urgent-from to-alert-urgent-to
```

完整映射表见 `references/common-patterns.md`。

### Step 7：替换工具类与特殊模式（批次 3）

1. **自定义工具类**（`.glass-panel`、`.glow-hover`）：替换内部 `dark:` 为 CSS 变量，更新 `@layer utilities`
2. **Focus ring offset**：`ring-offset-white dark:ring-offset-zinc-900` → `ring-offset-ring-offset`
3. **Disabled 状态**：`text-zinc-300 dark:text-zinc-700` → `text-disabled`
4. **Scrollbar 样式**（`@layer base`）：替换 `.dark` 选择器为 CSS 变量
5. **原生元素样式**（`option`、`body` 背景）：替换 `.dark option` 为变量
6. **渐变背景**（App 级环境光）：`dark:bg-[radial-gradient(...)]` → `bg-[radial-gradient(...,var(--ambient-to))]`

### Step 8：清理与审计

```bash
# 检查剩余 dark:
grep -rn "dark:" src/ --include="*.{tsx,jsx,vue,svelte,html,css,scss}"

# 检查硬编码 zinc 颜色
grep -rn "text-zinc-\|bg-zinc-\|border-zinc-" src/ --include="*.{tsx,jsx,vue,svelte}"
```

对剩余模式分类：
- 预期例外（动画 keyframes、有意保留的 badge 颜色）
- 真正遗漏 → 添加对应变量或直接替换

### Step 9：验证构建

```bash
# TypeScript 检查（如适用）
npx tsc --noEmit

# 生产构建
npm run build
```

预期结果：CSS 体积略有减少（消除 `dark:` 规则重复），无构建错误。

构建失败时：检查 TypeScript 未使用变量报错 / `@theme inline` CSS 语法错误，逐一修复后重试。

### Step 10：输出报告

```
=== 迁移完成 ===
修改文件数：    X
移除 dark:：    Y 处
新增变量数：    Z（L2: a，L3: b）
构建状态：      PASS / FAIL
CSS 体积变化：  -X KB（典型）

剩余 dark:（应为 0 或仅预期例外）
- 例外1: 原因
- 例外2: 原因
```

## 重要规则

1. **迁移过程中禁止新增 `dark:` 前缀**
2. **变量必须注册在 3 处**：`@theme inline`（或 `theme.extend`）+ `:root` + `.dark`
3. **优先使用 L2 变量**，L2 覆盖不到才用 L3
4. **保留业务语义色**：Badge 颜色（red/amber/sky）、状态指示（emerald 在线、zinc 离线）保留色相，仅将 `dark:` 部分迁移到变量
5. **每批替换后验证**：不要一次性替换全部文件后再验证

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/common-patterns.md` | 50+ 个 dark: 模式到变量的完整映射表 |
| `references/tailwind-v3-setup.md` | v3 config.js + CSS 变量配置指南 |
| `references/tailwind-v4-setup.md` | v4 @theme inline + CSS 变量配置指南 |
| `references/framework-guides.md` | React/Vue/Svelte/HTML 扫描差异说明 |
