---
name: tailwind-semantic-starter
description: Semantic CSS variable starter for Tailwind CSS projects. Use when the user wants to (1) Create a new Tailwind CSS project with light/dark dual-mode theming from scratch, (2) Initialize a semantic CSS variable system using `@theme inline` without any `dark:` prefixes, (3) Generate new components using semantic variables like `text-heading`/`bg-surface`/`border-divider`, (4) Review existing code for `dark:` prefixes or hardcoded colors and suggest semantic replacements, or (5) Extend an existing CSS variable theme with new semantic variables. Companion to `tailwind-dark-migrator` (which handles migrating existing projects that already use `dark:`).
---

# Tailwind Semantic Starter

新项目从第一天起就使用 `@theme inline` + CSS 变量双模式主题，零 `dark:` 前缀，零硬编码颜色。

| 用本 skill 当... | 用 `tailwind-dark-migrator` 当... |
|----------------|----------------------------------|
| 新建项目 | 已有项目到处用了 `dark:` |
| 向已配置变量的项目添加新组件 | 需要扫描/审计 dark 模式 |
| 从零搭建 Tailwind + CSS 变量体系 | 将硬编码颜色转换为语义变量 |

---

## 核心工作流

### Step 1：检测项目状态

| 状态 | 检测方式 | 操作 |
|------|----------|------|
| 空项目 / 新项目 | 无 `package.json`，无 Tailwind 文件 | 复制 `assets/starter-template/` 作为起点 |
| 已有 Tailwind v4 | CSS 中有 `@import "tailwindcss"` | 向现有 CSS 注入 `@theme inline` + 变量 |
| 已有 Tailwind v3 | 存在 `tailwind.config.js` | 扩展 `theme.extend.colors` + 添加 CSS 变量 |
| 已有变量体系 | 存在 `@theme inline` 或 `--color-heading` | 跳过初始化，直接用现有变量生成组件 |
| 使用 shadcn/ui | 存在 `components.json` | 向已有体系追加 L1 shadcn 基础变量 |

### Step 1.5：提取项目现有色彩方案（已有项目必做，新项目跳过）

> ⚠️ **核心原则**：references 中的颜色值（oklch 数值、teal/sky 等 Tailwind 色号）仅为**示例默认值**，用于全新空项目。
> 对于已有项目，必须先从项目中提取真实色彩，再写入 `:root` / `.dark` 的变量值。

按以下顺序读取项目现有色彩：

1. **读取设计 token 文件**（如存在）：`tailwind.config.js` 的 `theme.colors`、`src/tokens.css`、`src/design-system.css` 等
2. **读取全局 CSS**：找出 `:root` 下已有的 CSS variables 和最常用的 Tailwind 颜色类
3. **搜索品牌主色**：
   ```bash
   grep -rn "primary\|brand\|accent\|--color" src/ --include="*.css" | head -30
   ```
4. **归纳色彩方案**，记录以下信息，后续步骤写入变量值时以此为准：
   - 主色调（hue）：如蓝色系、紫色系、绿色系
   - 中性色基底：如 zinc / slate / gray / neutral
   - 强调色列表：项目已在用的 accent 色
   - 品牌色具体值（如有）

如果项目是全新空项目，则直接使用 `assets/starter-template/src/index.css` 中的默认值。

---

### Step 2：初始化 / 注入配置

> ⚠️ **颜色值来源规则**：
> - `@theme inline` 中的**变量名称**（`--color-heading` 等）→ 固定，直接使用本 skill 定义的名称
> - `:root` / `.dark` 中的**颜色数值** → 必须来自 Step 1.5 提取的项目色彩，而非照搬 references 中的示例值

#### Tailwind v4

向全局 CSS（如 `src/index.css`）添加：

```css
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

@theme inline {
  /* L2 文本语义 */
  --color-heading: var(--heading);
  --color-body: var(--body);
  --color-caption: var(--caption);
  --color-hint: var(--hint);
  --color-placeholder: var(--placeholder);
  --color-inverse: var(--inverse);

  /* L2 背景语义 */
  --color-surface: var(--surface);
  --color-surface-hover: var(--surface-hover);
  --color-surface-faint: var(--surface-faint);
  --color-elevated: var(--elevated);
  --color-inset: var(--inset);
  --color-overlay: var(--overlay);

  /* L2 边框语义 */
  --color-divider: var(--divider);
  --color-divider-subtle: var(--divider-subtle);
  --color-divider-strong: var(--divider-strong);

  /* L3 强调色（按需添加） */
  --color-accent-sky: var(--accent-sky);
  --color-accent-teal: var(--accent-teal);
}

:root {
  --heading: oklch(0.21 0.006 285.885);
  --body: oklch(0.37 0.013 285.805);
  /* ... 亮色模式赋值 ... */
}

.dark {
  --heading: oklch(0.985 0 0);
  --body: oklch(0.871 0.006 286.286);
  /* ... 暗色模式赋值 ... */
}
```

> 完整生产级模板见 `assets/starter-template/src/index.css`。

#### Tailwind v3

```js
// tailwind.config.js
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        heading: "var(--heading)",
        body: "var(--body)",
        // ...
      }
    }
  },
};
```

在全局 CSS 中添加 `:root` / `.dark` 变量赋值（不带 `color-` 前缀）。

> 详见 `references/tailwind-v3-setup.md` 和 `references/tailwind-v4-setup.md`。

### Step 3：生成组件

用 `references/component-patterns.md` 中的模板。**强制规则**：

#### 颜色规则

| 需求 | 使用 | 禁止使用 |
|------|------|----------|
| 主标题文字 | `text-heading` | `text-zinc-900`, `text-white` |
| 正文文字 | `text-body` | `text-zinc-700`, `text-zinc-300` |
| 辅助文字 | `text-caption` | `text-zinc-500`, `text-zinc-400` |
| 提示/占位 | `text-hint`, `text-placeholder` | `text-zinc-400` |
| 卡片/页面背景 | `bg-surface` | `bg-white`, `bg-zinc-900` |
| 浮起层 | `bg-elevated` | `bg-zinc-50`, `bg-zinc-800` |
| 输入框 | `bg-inset` | `bg-zinc-100`, `bg-zinc-950` |
| 悬停背景 | `hover:bg-surface-hover` | `hover:bg-black/5 dark:hover:bg-white/5` |
| 标准边框 | `border-divider` | `border-zinc-200 dark:border-white/10` |
| 信息/主色调 | `text-accent-sky` | `text-sky-500 dark:text-sky-400` |
| 成功色 | `text-accent-teal` | `text-teal-600 dark:text-teal-400` |
| 警告色 | `text-accent-amber` | `text-amber-500 dark:text-amber-400` |
| 错误色 | `text-accent-red` | `text-red-500 dark:text-red-400` |

#### 结构规则
- 圆角：卡片用 `rounded-xl`，按钮/输入框用 `rounded-lg`，徽章用 `rounded-full`
- 间距：卡片 `p-5`，按钮 `px-4 py-2`，flex 容器 `gap-4`
- 过渡：交互元素用 `transition-all duration-200`，按钮按压用 `active:scale-[0.98]`

#### 零容忍禁令
- ❌ 任何 `dark:` 前缀
- ❌ 硬编码文字颜色：`text-zinc-*`、`text-slate-*`、`text-white`、`text-black`
- ❌ 硬编码背景：`bg-white`、`bg-black`、`bg-zinc-*`（`bg-zinc-500/10` 强调色调例外）
- ❌ 硬编码边框：`border-white/10`、`border-black/10`、`border-zinc-*`

### Step 4：代码审查

发现以下违规时报告并给出修复方案：

| 违规类型 | 检测正则 | 修复方向 |
|----------|----------|----------|
| dark: 前缀 | `dark:\S+` | 替换为等价语义变量 |
| 硬编码文字色 | `text-(zinc\|slate\|gray)-(900\|800\|700\|600\|500\|400\|300\|200\|100)` | 映射到 `text-heading/body/caption/hint` |
| 硬编码背景色 | `bg-(white\|black\|zinc\|slate\|gray)-(50\|100\|200\|800\|900\|950)` | 映射到 `bg-surface/elevated/inset` |
| 硬编码边框色 | `border-(white\|black)/(5\|10\|20)\|border-(zinc\|slate\|gray)-(200\|300\|600)` | 映射到 `border-divider/*` |

**输出格式**：
```
## 审查结果

### 违规1：dark: 前缀
- 文件：`src/components/Button.tsx`，第 15 行
- 发现：`dark:bg-zinc-800`
- 修复：`bg-elevated`

## 汇总
- dark: 前缀：3 处
- 硬编码颜色：7 处
- 建议：合并前修复全部违规
```

### Step 5：扩展变量

新增颜色时按此决策树：

```
需要新颜色？
├── L2 变量能覆盖？
│   ├── 文字 → text-heading/body/caption/hint
│   ├── 背景 → bg-surface/elevated/inset
│   └── 边框 → border-divider/subtle/strong
├── 已有 L3 强调色能覆盖？
│   ├── 信息/主色 → accent-sky
│   ├── 成功 → accent-teal/emerald/green
│   ├── 警告 → accent-amber/orange/yellow
│   └── 错误 → accent-red/rose
├── 被 ≥2 个组件复用？
│   └── YES → 新建 L3 变量（在 @theme inline + :root + .dark 中各注册一次）
└── 仅1个组件使用？
    └── YES → L4 组件级变量（在组件文件中定义 CSS var 或用 inline style）
```

**新增 L3 示例**：
```css
/* @theme inline */ --color-accent-purple: var(--accent-purple);
/* :root */         --accent-purple: oklch(0.6 0.2 300);
/* .dark */         --accent-purple: oklch(0.75 0.18 300);
```

**L4 组件级示例**：
```tsx
<div style={{ "--chart-bar": isDark ? "#818cf8" : "#6366f1" } as React.CSSProperties}>
```

---

## 变量层级

```
L1: shadcn/ui 基础  → background, foreground, primary, border
L2: 语义层          → heading, body, caption, surface, elevated, divider
L3: 强调色/状态     → accent-sky, accent-teal, option-active, glass, glow
L4: 组件级局部      → 在单个组件文件中定义的自定义变量
```

> 规则：优先使用高层变量。L3 仅在颜色跨组件复用时创建，L4 仅用于单组件独有需求。

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/semantic-variables-cheatsheet.md` | 所有变量的亮/暗色值速查表 |
| `references/component-patterns.md` | 12 个可直接复制的组件模板 |
| `references/tailwind-v4-setup.md` | v4 初始化分步指南 |
| `references/tailwind-v3-setup.md` | v3 初始化分步指南 |
| `assets/starter-template/src/index.css` | 完整生产级变量配置 |
| `assets/starter-template/src/App.tsx` | 示例根组件 |
| `assets/starter-template/src/components/ExampleCard.tsx` | 示例可复用组件 |
| `assets/starter-template/tailwind.config.js` | 完整 v3 配置备份 |
