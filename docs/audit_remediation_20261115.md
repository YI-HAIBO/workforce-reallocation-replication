# 审计整改记录（2026-11-15）

> 对应：`data_code_audit_20261115.md`（数据与代码审计报告）
> 状态：P0–P2 整改全部完成；主文已满足 AEJ 9600 词上限；投稿文件夹已同步并重新编译验证。

## 一、整改完成项

### 1. 表 5 EPL 口径与“2025”误标（原 F7 / P1）
- 表 5 行标签由 `OECD EPL score (0--6), 2025` 改为 `Employment protection strictness (0--6)`（`\textsuperscript{a}` 上标）。
- 表 5 新增脚注：说明该指标为 IACI 构造序列，OECD 仅发布成员经济体 headline EPL；中国、印度值为 illustrative 且不可独立复现；删除“2025”误标。
- 韩国叙事 `OECD Employment Protection Legislation score` → `illustrative employment-protection strictness score`。
- 印度叙事 `its EPL score` → `its illustrative employment-protection strictness score`。

### 2. IACI 不可独立复现披露（P1）
- IACI 构造段新增披露：`The index is illustrative: the OECD does not publish the headline employment-protection indicator for non-member economies, and the component series are not independently reproducible from public sources (the automation series draws on the IFR licensed database).`
- 面板引言降级为 illustrative：`Because the index is illustrative and not independently reproducible from public sources, the estimates in Table 6 corroborate the case-study ordering rather than stand alone.`

### 3. 表 6 标题与脚注（P1）
- 表 6 标题改为 `Illustrative panel regression: IACI and automation and the employment outcome, 2000--2024`。
- 表 6 脚注披露交互项依赖 IFR licensed automation series 与 illustrative IACI。

### 4. 主文 Data availability 与模板声明合并（P1）
- 删除 References 后重复的独立 `\section*{Data availability}` 节。
- 将 IFR licensed (VDMA)、组件未存档、本地复现文件为 illustrative 等受限披露并入模板 `\section*{Data Availability Statement}`。
- 修正模板节中把 IFR World Robotics 误列为公开来源的错误。

### 5. 补充材料 S3 Data and reproduction note（P1）
- 新增 `\section*{S3. Data and reproduction note}`，声明国际面板复现文件为 illustrative，IFR 系列来自授权（VDMA）数据库不可自由复现，本地复现文件含占位序列不应重估指数；中国国内表（3–4 节）可复现。

### 6. 数据脚本口径注释（F7）
- `real_panel.py` 新增 docstring：注明 `ept` 列实为 OECD 临时合同保护严格度（EPT），非整体 EPL，口径错配见审计报告 F7。
- `l30_alt_panel.py` 新增 docstring：注明 EPL-only 实为 EPT 单成分，口径非整体 EPL。

### 7. 悬空补充材料 S3 引用清理（P1）
- 删除正文中指向 ALMP 稳健性的悬空 `Supplementary Material S3` 引用，相应句子改为不含补充材料引用。

## 二、压缩以满足 AEJ 字数上限

主文经四轮压缩，从审计修复后的 9926 词压至 9574 词（< 9600 上限，余量 26 词）：

| 轮次 | 脚本 | 说明 | 命中 |
|---|---|---|---|
| 1 | `compress_for_aej.py` | 去悬空 S3 引用、压缩面板解释、机械相关披露、IACI 说明性句（11/14 命中） | 11 |
| 2 | `compress_for_aej2.py` | 修正 4 条未命中（`~`、`\textit{Note:}` 精确匹配）：Data availability、表 5/6 脚注、面板说明性句 | 4 |
| 3 | `compress_for_aej3.py` | 面板解释段与结论段冗余（columns 3/4、codetermination static、cluster 阈值、wild-cluster bootstrap、11 国样本、contribution directional、conclusion 首句） | 8 |
| 4 | `compress_for_aej4.py` | Intro 数据来源预览与 contribution 预览冗余、roadmap | 3 |

字数轨迹：9926 → 9825 → 9732 → 9624 → 9569 → 9596（恢复方程）→ **9574（最终）**。

## 三、引用完整性（修复 undefined references）

- 主文 `eq:decomp1`、`eq:decomp2` 两方程定义在 AEJ 改造中丢失，但正文 3 处 `\eqref` 引用之。已从原稿 `manuscript_sced.tex` 恢复完整方程定义并加 label。
- 补充材料 5 个跨文件引用（`eq:cost`、`eq:gamma`、`eq:net`、`eq:scale`、`lem:theta`）在独立编译时无法解析，已改为文字引用（如“the net-change equation of the main text”、“Lemma 1 of the main text”）。
- 重编译后主文与补充材料 log 均无 undefined reference / citation。

## 四、最终验证结果

| 项 | 结果 |
|---|---|
| 主文字数 | 9574（MAIN 7822 + REFS 1752）< 9600 |
| 主文 PDF | 37 页，双 pass 编译 rc=0 |
| 补充 PDF | 5 页，双 pass 编译 rc=0 |
| 主文 undefined refs | 0 |
| 补充 undefined refs | 0 |
| 表 5 strictness 行 + 脚注 | 渲染存在 |
| 表 6 illustrative caption + 脚注 | 渲染存在 |
| Data Availability Statement | 存在（含受限披露） |
| S3 Data and reproduction note | 存在 |
| 投稿文件夹 `2026-11-15_AEJ_Submission/` | 已同步最新 tex/pdf/aux/log/out，内部双 pass 编译通过 |

## 五、剩余风险（已披露，非待修）

1. **国际面板结论为 illustrative**：β3=0.054 依赖 IFR 授权数据与 illustrative IACI，真实免费数据复现为负且不显著；论文已明确披露为“corroborate the case-study ordering rather than stand alone”，不再作为独立因果识别。
2. **中国国内表 3–4 节**：从 NBS/财政部/工信部公开来源可复现；审计核验表 1 自洽（566/234/331/γ=0.586）、表 3 机器人密度与 IFR CSV 一致。
3. **C 版 `l2_data/` 合成数据**：审计发现全部为合成线性斜坡，仅用于复现性检查，不作为论文证据；论文未引用其估计值。
4. **表 5/6 的 11 国样本**：聚类仅 11 个，低于 30 阈值；论文已改用 wild-cluster bootstrap 作为修正推断并明确“indicative”。

## 六、交付物清单

- `manuscript_AEJ.tex` / `.pdf`（主文，9574 词，37 页）
- `supplementary_AEJ.tex` / `.pdf`（补充，5 页，含 S1 证明、S2 识别设计、S3 数据说明）
- `2026-11-15_AEJ_Submission/`（投稿文件夹，已含全部最新投稿文件并编译验证）
- `Title_Page_AEJ.txt`、`Cover_Letter_AEJ.txt`、`Figure_1-6.jpg`、`bootstrap_results.csv`、两份 Editor Review
