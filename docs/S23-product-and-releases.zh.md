# GhostSam S23：独立产品与发布规则

生效日期：2026-10-16。

GhostSam S23 按目标 S23 固件的使用需求、验证结果和维护进度独立发布。
保留 GhostSam 的来源、许可证、Git 历史和上游引用，按需采用上游修复。
上游发布新版本本身不构成 S23 发版理由。

## 产品与版本

- 产品名：GhostSam S23；包名：`com.snothin.ghostsam.s23`。
- 主线：`main`；默认 Gradle 构建为 S23，原有通用构建需显式 `-Ps23Only=false`。
- 版本唯一来源：`app/s23-version.properties`，不继承 `app/version.properties`。
- 当前开发版：`0.3.0-dev`，`versionCode=64`。不是已发布 APK。
- 最新已发布：r3，`0.2.3-s23-uapi5-r3`，build 63，原下载链接继续使用。
- `versionCode` 由维护者随可分发更新显式递增，必须高于最新已发布版本。
  构建、测试和重跑 CI 均不修改版本文件。
- 标签为 `s23-v<versionName>`，例如候选版本 `0.3.0-rc.1` 对应
  `s23-v0.3.0-rc.1`。版本号按本产品维护，不对应 GhostSam 或 KernelSU 版本。

当前保持测试版发布渠道。即使版本名不带后缀，新工作流也将其发布为 prerelease。
正式稳定版的发布策略需在积累真机验证记录后调整；不因本次版本独立而宣称稳定。

## 构建与发布

`Build GhostSam S23` 保留原工作流路径 `kernelsu-331.yml`，避免已有链接失效。

| 触发方式 | 结果 |
| --- | --- |
| 推送 `main` / PR / 手动运行 | 从固定 KernelSU 源码完整构建、测试，生成 artifact |
| 推送匹配的 `s23-v…` 标签 | 先验证版本与发布说明，全部构建通过后发布测试版 |
| `-dev` 版本的发布标签 | 拒绝发布；开发版本只用于 artifact |
| 历史 `s23-ksu-3.3.1-r2/r3` 标签 | 不触发新发布流程；既有 Release 与附件保留 |

artifact 名称为 `ghostsam-s23-apk`，包含 `GhostSam-S23.apk`、`BUILD-INFO.txt`
与 `SHA256SUMS`。构建信息同时记录 S23 产品版本、构建源码、KernelSU 固定提交、
KMI、三星兼容配置及验证范围。历史 r3 artifact 与附件仍使用原名称。

准备下一测试版时：

1. 先完成 r3 的真机回归记录，确认授权、软重启及完整重启后的行为。
2. 在 `app/s23-version.properties` 设置候选版本，例如 `0.3.0-rc.1`；
   build 高于维护清单中 `product.latest_published` 记录的已发布版本。
3. 新建 `docs/releases/s23-v0.3.0-rc.1.zh.md`，记录变化、设备范围、
   构建与真机验证结果、安装方式和已知限制。
4. 主线构建通过后，推送与版本文件完全匹配的标签。工作流再次完整构建，
   核对 APK 版本、包名、载荷、签名、附件摘要及标签源码，再发布测试版。
5. 发布成功后，在进入下一开发版本的提交中更新维护清单的最新已发布版本、
   README 下载说明，并把版本文件切换到更高 build 的下一 `-dev` 版本。

本地预检：

```bash
python scripts/s23-release.py
python scripts/s23-release.py --tag s23-v0.3.0-rc.1
python -m unittest discover -s tests -p 'test_*.py' -v
```

第二条仅在版本文件已经改成该候选版且对应发布说明存在时通过。
发布脚本保留既有 Release 附件的校验，不覆盖已发布文件。

包名继续兼容现有 S23 安装，但当前 CI 使用每次运行生成的 debug 签名；
版本号递增不消除签名差异。遇到签名冲突时仍按既有安装说明处理。

## 底层与上游

KernelSU 固定 `abbd7be7fb5e0af607c2a85e02efae03044bba86`，继续应用已有
UAPI 5 和 Manager 安装监听补丁，并启用 KDP/DEFEX/RKP。此次不变更
DirtyFrag、helper 或 ksud 产物，不合并 v0.2.4。

`maintenance/s23-baseline.json` 分别记录：

- `baseline`：实际整合的 GhostSam 基线，当前为 v0.2.3 / `818faef`。
- `reviewed_commit`：最近已完成审查的上游位置，当前为 v0.2.4 / `8fa2f68`。
- `review_log`：审查结论与候选改动。
- `adopted_changes`：选择性采用的补丁来源、本地提交与验证记录，当前为空。

优先完成当前产品验证，再单独评估 DirtyFrag 和新版 KernelSU 的可用修复。
companion 与其他机型代码精简另开改动，不与底层升级或本次发布流程调整混合。
