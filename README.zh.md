# GhostSam S23

**中文** | [English](README.md)

面向国行 **三星 Galaxy S23（SM-S9110，固件 S9110ZCS8FZI1）** 的临时 root
应用，基于 [snothin/GhostSam](https://github.com/snothin/GhostSam) 适配。
本 fork 固定使用 DirtyFrag standalone 路径与官方 **KernelSU Manager 3.3.1**，
配套构建 UAPI 5 驱动和 ksud。

[下载 r2 测试版 APK](https://github.com/Lovest20018/GhostSam/releases/tag/s23-ksu-3.3.1-r2)
· [S23 构建与兼容说明](docs/KernelSU-3.3.1.zh.md)
· [应用首页与上游维护说明](docs/Home-copy-and-upstream.zh.md)

## 支持范围

| 项目 | 要求 |
| --- | --- |
| 机型 | 国行 Galaxy S23，SM-S9110 |
| 固件 | S9110ZCS8FZI1 |
| 编译编号 | BP4A.251205.006.S9110ZCS8FZI1 |
| 系统 | Android 16 / SDK 36 |
| 完整内核版本 | 5.15.189-android13-8-3251900-abS9110ZCS8FZI1 |
| KMI | android13-5.15 |
| 管理器 | 官方 KernelSU Manager 3.3.1 |

应用在执行前核对目标信息，不匹配时停止。这台设备虽然运行 Android 16，
内核仍为 android13-5.15。其他机型、其他固件，以及上游的 S22 / S26 / Z Fold8
支持范围，均不能视为本 S23 专用构建的兼容承诺。

## 使用方法

1. 安装 **GhostSam S23** 和官方 **KernelSU Manager 3.3.1**。
   S23 版包名为 `com.snothin.ghostsam.s23`，可与原版 GhostSam 同时安装。
2. 首次使用或完整重启后，打开 GhostSam S23，执行获取临时 root。
   S23 版固定使用 standalone 和官方 KernelSU。
3. 如果 KSU 已显示 **“已越狱”**，先进入 KSU 的 **“超级用户”**，
   授予 **GhostSam S23** su 权限，再返回应用。单次 su 检测失败不能说明需要重新加载。
4. 应用验证 su 可用后，首页显示 **“KernelSU 已启用”**。
   从该卡片打开 KSU，再使用管理器中的软重启。

用户已在上述目标设备上反馈：授予 GhostSam su 权限后，从 GhostSam 打开 KSU，
软重启可以正常使用。临时 root 在完整重启后需要重新获取；测试新版驱动时，
软重启不能替代完整重启来切换已加载的驱动。

## 源码与安装包状态

| 版本 | 状态 |
| --- | --- |
| r2 | 已发布的测试版 APK，安装注意事项见对应 Release |
| r3（`0.2.3-s23-uapi5-r3`，build 63） | 当前 `main` 源码，包含新的首页状态和授权提示；尚未构建或发布 r3 APK |

r3 首页区分正在检测、管理器未安装、准备执行、执行中、已加载待授权、已启用。
这些界面改动需要安装新构建才能看到；GitHub 源码更新不会自动更新手机上的 r2。

## 构建

完整构建可进入 [Actions](https://github.com/Lovest20018/GhostSam/actions/workflows/kernelsu-331.yml)，
选择 **Build GhostSam S23**，在 **Run workflow** 中选择 `main` 手动运行。
工作流从固定源码重建三星 KernelSU 驱动与 ksud，再构建、校验 S23 APK。
成功后下载该次运行的 `ghostsam-s23-uapi5-apk` artifact。

当前推送 `main` 不会自动启动该工作流。手动构建 `main` 会产出 artifact；
历史 r2 的 Release 发布步骤只对原分支开放。

本地构建需要 JDK 21、SDK 37.0、NDK 30.0.16248370、CMake 3.22.1，
以及同源重建的 UAPI 5 payload。先按[构建说明](docs/KernelSU-3.3.1.zh.md)
准备 payload，再执行：

```bash
cd app
./gradlew :app:testDebugUnitTest :app:assembleDebug -Ps23Only=true --no-daemon --no-configuration-cache
```

S23 版只打包 ksud 与 android13-5.15 安装辅助模块，排除其他 KMI、
KernelSU-Next 和 companion APK。

## 与上游的关系

本 fork 的 S23 改动已合入 **`main` 主线**。原项目为
[snothin/GhostSam](https://github.com/snothin/GhostSam)，当前基于 v0.2.3
（`818faef`）。上游完整工具包和机型列表见
[上游原版说明](https://github.com/snothin/GhostSam/blob/818faef4a278353a22c3481a01a6eaedf8088a3d/README.zh.md)。
S23 首页状态与中英文文案放在独立文件中，方便后续审查、合并上游更新。

在已配置 `upstream` 远程的本地仓库中检查上游变化：

```bash
python scripts/check-upstream.py --fetch
```

检查器列出新增提交和需要审查的 S23 文件。后续在临时分支合并，验证后再整合到
`main`，具体步骤见[维护说明](docs/Home-copy-and-upstream.zh.md)。
KernelSU 单独固定在 `snothin/KernelSU` 的
`abbd7be7fb5e0af607c2a85e02efae03044bba86`；同步 GhostSam 不会自动升级驱动基线。

## 致谢与许可

- [snothin/GhostSam](https://github.com/snothin/GhostSam)：原始应用、共享基础设施，
  以及 Ghostlock / DirtyFrag 集成。
- [snothin/KernelSU](https://github.com/snothin/KernelSU) 与
  [KernelSU](https://github.com/tiann/KernelSU)：三星驱动、ksud 和管理器工作。
  上游源码同时保留了 [KernelSU-Next](https://github.com/snothin/KernelSU-Next) 集成。
- [ghostlock-s26](https://github.com/snothin/ghostlock-s26)、@diabl0w 的 Z Fold8 移植输入，
  以及 [DFRoot](https://github.com/diabl0w/DFRoot)：上游利用链和公开 DirtyFrag 技术来源。

本项目用于你拥有并控制设备的安全研究。内核利用可能导致崩溃或重启，
系统更新后需重新审查兼容性。许可为 [Apache-2.0](LICENSE)，
第三方来源声明与致谢保留在 [NOTICE](NOTICE)。
