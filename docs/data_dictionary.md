# 全网采集数据字典（来源 / URL / 口径 / 覆盖 / 验证）

> 触发：用户"请全网采集数据，尽量穷尽各种方法"。
> 记录 2026-11-14 全网采集（含此前 WDI/IFR 与本轮 OECD/OWID/ILO/Comtrade 探测）的所有**可得**数据集，附来源、URL、口径、覆盖与质量核验。

---

## 一、已采集数据集（11 国面板相关）

| 数据集 | 文件 | 来源 / URL | 口径 | 覆盖 | 核验 |
|---|---|---|---|---|---|
| **失业率 Q** | `wdi_panel.csv` | World Bank WDI API `SL.UEM.TOTL.ZS`（https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS） | 年失业率 %（ILO 模型估计） | 11 国 × 2000–2024 = 275/275 完整 | 德 3.40 / 西 11.40 / 美 4.02 合理 |
| **人均 GDP X** | `wdi_panel.csv` | WDI `NY.GDP.PCAP.CD` | 现价美元/人 | 11 国 × 2000–2024 | 0.97k–86.2k 合理 |
| **城市化 X** | `wdi_panel.csv` | WDI `SP.URB.TOTL.IN.ZS` | 城镇人口 % | 11 国 × 2000–2024 | 36.4–92.2 合理 |
| **IFR 机器人密度（AUTO）** | `ifr_density_2023_2024.csv` | OWID 转存 IFR `industrial-robots-in-operation-per-1000-employees.csv` | 每 10,000 制造雇员（×10 换算） | **10 国**（除巴西）× 2023+2024 | 与 IFR 官方逐值一致：德 44.9×10=449✓ 韩 122×10=1220✓ 中 16.6×10=166✓ |
| **IFR 年安装量（替代口径）** | `owid_robots_installed.csv` | OWID 转存 IFR/AI Index `annual-industrial-robots-installed.csv` | 年新增安装量（台） | 中/德/日/韩/美 × 2011–2024 + 世界 | 中国 2024=295,000、2023=276,000 与 IFR 一致 |
| **EPL 就业保护（临时合同）** | `epl_panel_11.csv` | Statizoid 转存 OECD `strictness-of-employment-protection-temporary-contracts/<国>.csv` | 0–6 标度 | 11 国 369 行（9 国 1985–2025、韩/墨 1990–2025、中/巴 2008–2012） | 德国 1.00（temporary）；**注意：论文 IACI 用综合 EPL**（Germany 3.29/Korea 2.35/China 3.26，Table 5）——口径不同 |
| **劳动权利合规（共决/集体谈判代理）** | `labor_rights_11panel.csv` | OWID-ILO SDG 8.8.2 `level-of-national-compliance-with-labor-rights.csv` | 0–10（形式合规） | 11 国 × 2015–2024 = 110 观测（每国 10/10） | 中国 9.13（高）、德国 0.38、瑞典 0.00——**概念为形式合规，非调整容量** |
| **机器人进口额（AUTO 代理）** | `comtrade_robot_import.csv` | UN Comtrade 公共预览 `comtradeapi.un.org/public/v1/preview/C/A/HS?cmdCode=847950&flowCode=M` | 年进口额 USD（HS 8479.50 工业机器人） | **10 国**（法国预览库无记录）× 2020–2024 | 中国 2023≈12.5 亿 USD、德国 5.1 亿、美国 6.2 亿；429 限流需节流重试 |

---

## 二、探测但受阻的数据集（免费通道穷尽）

| 数据 | 尝试的渠道 | 结果 |
|---|---|---|
| **AUTO 2000–2022 密度长序列** | IFR 付费墙（唯一）；Graetz-Michaels Dataverse 10.7910/DVN/5JWBXU（163MB 7z，**2000–2007 欧美韩 6 国**，行业级需 EU KLEMS 转换）；CSDN 1993–2023（**付费**）；Bekhtiar 2024（IFR **专有**，已从复现包删除）；OWID 6 候选 slug | ❌ 免费仅 2023/24 截面 + 5 国安装量；长序列唯一 IFR 付费 |
| **EPL 综合（论文口径）** | OECD SDMX v1/v2（406/404/400/500）、stats.oecd.org rest（404）、dotstat-store（DNS 失败）、data-viewer（JS 单页）、dotstat-search（400）、Eurostat（无） | ❌ 仅论文 Table 5 综合 EPL 4 国（China 3.26/Germany 3.29/Korea 2.35/India 3.29） |
| **ALMP 强度** | Eurostat 9 个 LMP 候选码（全 404）、OWID 6 slug（404）、OECD SDMX LMP（406/502） | ❌ 免费受阻 |
| **培训覆盖** | OWID 7 slug（404）、Eurostat CVTS、OECD | ❌ 免费受阻 |
| **共决（集体谈判/工会）** | OWID collective-bargaining/union slug（全 404）、ILO STAT（DNS 失败 + 403） | 🟡 已采 OWID-ILO 8.8.2 作代理 |
| **Q 补充口径** | ILO STAT（DNS 失败） | ❌ WDI 已覆盖 |
| **城市级构成（§5.3）** | NBS 官方未公布 | ❌ 硬缺口（CMDS 申请/用户独占/七普） |

---

## 三、采集结论
- **面板 Q、X：100% 已采集**（WDI，11 国 × 25 年）。
- **AUTO**：免费可得 2023/24 截面（10 国）+ 5 国安装量 2011–24 + Comtrade 机器人进口额代理（**12 国** × 2020–24，含 **印度** 2026-11-15 新增）；**2000–2022 密度长序列仅 IFR 付费**。
- **IACI 子成分**：EPL（temporary，Statizoid-OECD，11 国）+ 劳动权利（OWID-ILO，11 国 2015–24）已获；综合 EPL/ALMP/培训**免费受阻**（论文 IACI 沿用既定值，Germany 4.46/US 1.16/China 2.07）。
- **城市级构成：官方未公布硬缺口**。
- **新增可得**：UN Comtrade 机器人进口额代理（HS 8479.50，免费预览，429 限流可控）。
- **新增印度（2026-11-15，填 Table 5 "n.p."）**：Comtrade HS 8479.50 印度进口额——2024=**1.721 亿美元**、2020–24 **+115.8%**；相对人均 GDP 强度 **66,382 > 中国 48,501**（自动化暴露相对其发展水平高于中国）。OWID/IFR 密度序列无印度（低于公布阈值）。
