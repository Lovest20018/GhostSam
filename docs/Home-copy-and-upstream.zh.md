# S23 首页文案与上游同步说明

整理日期：2026-10-15。

本文描述 fork 主线 `main` 的当前源码。源码版本为 `0.2.3-s23-uapi5-r3`（build 63），
已经生成的 r2 APK 不包含本轮界面整理。
[r3 测试版](https://github.com/Lovest20018/GhostSam/releases/tag/s23-ksu-3.3.1-r3)
已由 [Actions #6](https://github.com/Lovest20018/GhostSam/actions/runs/38679062368)
完整构建并发布，源码为 `14f1343`；r3 真机验证尚未进行。

仓库中英文首页均以 **GhostSam S23** 为项目展示名，介绍 S23 的目标固件、
授权流程和构建方式；应用显示名和首页标题也使用此名称。
GitHub 仓库路径为 `Lovest20018/GhostSam`。

## 当前首页

S23 构建固定使用 standalone 路径和官方 KernelSU。首页标题为 **GhostSam S23**。
首页状态、主卡点击动作和授权提示由同一个状态映射确定。

| 条件 | 主卡标题 | 主卡说明 | 点击行为 |
| --- | --- | --- | --- |
| 已安装管理器，正在检测本应用 su | 正在检查授权 | 请稍候，正在确认 KernelSU 和本应用 su 权限 | 等待检测，不启动执行 |
| 未安装管理器 | 请先安装 KernelSU | 安装官方 KernelSU Manager 3.3.1 后返回 | 不启动执行 |
| 未确认加载，本应用没有 su | 准备获取临时 root | 首次使用或完整重启后，点击开始 | 启动执行；启用自定义文件时先选择文件 |
| 正在执行 | 正在获取临时 root | 请保持等待，进度见执行日志 | 进入执行页，不启动第二次执行 |
| 已确认加载，本应用没有 su | 已加载，等待授权 | 点击打开 KSU，在“超级用户”中授权本应用 | 打开 KSU |
| 已验证本应用 su 可用 | KernelSU 已启用 | 点击打开 KSU；可在管理器中进行软重启 | 打开 KSU |

执行中状态优先于其他状态，避免模块先加载、执行尚未结束时跳到管理器。
检测未完成前不提供执行动作，避免刚打开首页时误点。

未确认加载时，授权提示卡显示：

> 如果 KSU 已显示“已越狱”，无需再次执行。点击打开 KSU，在“超级用户”中
> 授予 GhostSam S23 su 权限，再返回确认状态。

已确认加载、但本应用未获得 su 时，授权提示卡显示：

> KernelSU 已加载。点击打开 KSU，在“超级用户”中授予 GhostSam S23 su 权限后返回。
> 显示“已启用”后，可从首页打开 KSU 进行软重启。

提示卡启动管理器的首页，用户再进入“超级用户”；当前未使用未经验证的
管理器内部页面跳转链接。

“已加载”的证据来自已有模块探测、本次开机记录或当前执行成功结果；
仅凭一次 su 检测失败不能判断模块不存在。无加载证据时使用条件提示，
不误报“已经加载”或“必须再次执行”。

授权后返回首页会重新检测 su，验证成功后同步启用状态和本次开机记录。
设备信息、SELinux、系统工具和可选的自定义文件配置入口继续保留。

## 文件隔离

| 用途 | 文件 |
| --- | --- |
| S23 状态与动作 | `app/app/src/main/java/com/snothin/ghostsam/ui/screen/s23/S23HomeState.kt` |
| S23 主卡与授权提示 | `app/app/src/main/java/com/snothin/ghostsam/ui/screen/s23/S23HomeCard.kt` |
| S23 英文文案 | `app/app/src/main/res/values/strings_s23.xml` |
| S23 中文文案 | `app/app/src/main/res/values-zh-rCN/strings_s23.xml` |
| 通用页面接入点 | `app/app/src/main/java/com/snothin/ghostsam/ui/screen/HomeScreen.kt` |
| 通用授权返回刷新 | `app/app/src/main/java/com/snothin/ghostsam/ui/screen/HomeEvidence.kt` |

使用独立资源名，不增加重复定义的 source set。S23 的目标不匹配说明和
管理器版本说明也移入上述资源文件。通用首页被改动的三条授权相关文案已恢复为
上游基线值，`HomeCards.kt` 保持上游实现。共享的模块加载日志仍在通用文案中，
因为它与通用 standalone 结果处理对应。

## 本地分支与基线

- `origin`：用户 fork `Lovest20018/GhostSam`。
- `upstream`：原作者仓库 `snothin/GhostSam`。
- `main`：fork 的 S23 主线，已合入此前的 3 个维护提交并推送到 `origin/main`。
- `upstream-track`：本地跟踪 `upstream/main`。
- `s23/maintenance`：保留此前整理的本地分支，后续同步从最新 `main` 开始。
- 上游基线：`818faef4a278353a22c3481a01a6eaedf8088a3d`，v0.2.3。
- 既有源码保存提交：`5492115`。本轮整理在其后单独提交。
- 已补齐上游可用历史；2026-10-15 查询到上游 main 仍为上述基线。

机器可读的基线、目标设备、KernelSU 固定版本及重点审查路径保存于
`maintenance/s23-baseline.json`。

当前 KernelSU 继续固定为 `snothin/KernelSU` 的
`abbd7be7fb5e0af607c2a85e02efae03044bba86`，UAPI 5、Manager 3.3.1、
KMI `android13-5.15`。本轮不升级内核或 ksud。

## 后续检查与合并

在仓库根目录运行：

```powershell
python scripts/check-upstream.py --fetch
```

不访问网络、只检查本地已经获取的上游引用：

```powershell
python scripts/check-upstream.py --json
```

检查器验证上游地址和基线祖先关系，列出新增提交及 S23 重点审查文件。
它只生成报告，不执行合并、不改源码、不移动维护分支。报告不是兼容性验证。

决定同步后，先保存工作目录，再在临时分支合并。下列临时分支名称仅作示例：

```powershell
git switch main
git status --short
git switch -c s23/merge-review
git merge upstream/main
```

工作目录有未保存改动时先处理，不能直接覆盖。冲突解决后检查 S23 目标限制、
首页状态和点击动作、standalone 结果处理、资源、构建脚本及 payload 校验。
验证通过后，将临时分支的结果合并回 `main` 并推送；不要把 S23 提交写入 `upstream-track`。
同时将 `maintenance/s23-baseline.json` 中的 GhostSam 基线更新为已经接受的
上游提交，再运行检查器和测试；后续报告才只包含下一批增量。

应用与 Samsung KernelSU 属于两份独立上游。应用合并期间继续保留固定 KernelSU
提交；内核升级另行核对接口并同源重建产物。

## 构建与验证

维护分支已加入 `Build GhostSam S23` 构建触发范围。该分支运行构建与测试。
`s23-ksu-3.3.1-r3` 标签会触发完整构建，发布步骤只对这个标签开放，
并核对源码提交、APK 版本、三个附件及其 SHA256，不覆盖旧 r2。
当前 `main` 不在 push 自动构建范围内，可从 Actions 手动选择 `main` 运行，
成功后下载 artifact。r3 的上述标签构建已通过并发布，普通主线推送仍不会启动构建。

完整 Android 构建仍需要仓库指定的 JDK 21、SDK 37.0、NDK 30、CMake 及同源
UAPI 5 payload。不能使用旧资产跳过检查：

```powershell
cd app
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebug -Ps23Only=true --no-daemon --no-configuration-cache
```

本轮验证包括首页状态和动作测试、S23 目标机型测试、独立资源与通用文案检查、
APK 打包校验测试、上游检查器的隔离 Git 仓库测试，以及 Android 资源编译。
完整 APK 构建和真机验证结果需另行记录，不能由这些检查推定成功。

真机仍需覆盖：首次执行、未授权重开、授权后返回、从 GhostSam 打开 KSU、
软重启、完整重启后重新获取权限、目标信息不匹配时停止执行。

原工作目录缺失的 `app/app/src/main/assets/payloads/s26/preload.so` 是本轮之前
已有的删除，保存基线及本轮提交均不包含该删除记录。
