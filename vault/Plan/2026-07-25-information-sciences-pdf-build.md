---
status: completed
created: 2026-07-25
updated: 2026-07-25
---

# Information Sciences 模板 PDF 构建

## 目标

将 `vault/Writing/paper_draft.md` 编译为基于 Information Sciences 官方 Elsevier CAS 单栏类的 PDF。最终 PDF 放在 Markdown 所在目录；转换、LaTeX 辅助文件、日志、渲染页和检查结果全部放在 `outputs/information-sciences-pdf-20260725/`。

## 步骤

- [x] 核对本机 `cas-sc.cls`、Pandoc、XeLaTeX、所需包与图片路径。
- [x] 在 `outputs/` 建立 Markdown 到 CAS LaTeX 的可复现构建工作区。
- [x] 编译并将最终 PDF 复制到 `vault/Writing/`。
- [x] 检查编译日志、参考文献、字体、页数和关键页面渲染。
- [x] 将产物位置规则写入 `AGENTS.md`，并同步项目计划。

## 决策

- 不在 `vault/Writing/` 保存 `.tex`、`.aux`、`.log`、`.out`、`.bbl`、页面 PNG 或其他中间产物。
- 若官方 CAS 类或其依赖缺失，不静默安装；先记录精确包名和错误。
- `cas-sc.cls` 与 `cas-common.sty` 已安装；`stfloats.sty` 由用户授权安装的 MiKTeX `sttools` 包提供。

## 错误

- 2026-07-25：`kpsewhich stfloats.sty` 返回 `MISSING`。为避免 MiKTeX 自动安装，未启动 XeLaTeX 编译。
- 2026-07-25：`mpm --install=stfloats` 报告未知包名；更新包数据库后确认包 ID 为 `sttools`，已通过 `miktex packages install sttools` 安装并由 `kpsewhich stfloats.sty` 验收。
- 2026-07-25：Pandoc 生成的 `frontmatter` 环境和 `\LTcaptype{none}` 与本机 `cas-sc` 2.4 不兼容；已改用该类的 `\maketitle` 前置语法，并在中间 LaTeX 中移除冲突包装。

## 结果

- 已使用 `cas-sc.cls` 2.4 和 XeLaTeX 生成 25 页 A4 PDF：`vault/Writing/paper_draft.pdf`。
- 构建工作区为 `outputs/information-sciences-pdf-20260725/`；其中保留 wrapper、转换源、日志、页面渲染图和中间 PDF。
- 双通讯作者、37 条编号参考文献、页 1/3/17/18/21/22/25 的版式均已检查。字体均嵌入。保留 1 个 CAS `\maketitle` 内部空盒 overfull 警告和 3 个 underfull 段落警告；抽样页面无裁切、重叠或越界。

## 状态

已完成并复制最终 PDF；所有中间产物保留在 `outputs/`。
