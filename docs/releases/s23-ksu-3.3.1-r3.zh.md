国行 **Galaxy S23 专用 r3 测试版**，版本 `0.2.3-s23-uapi5-r3`（build 63）。
应用显示名为 **GhostSam S23**，包名为 `com.snothin.ghostsam.s23`。

适用设备：**SM-S9110 / S9110ZCS8FZI1 / Android 16**。
完整内核：`5.15.189-android13-8-3251900-abS9110ZCS8FZI1`，KMI `android13-5.15`。
管理器：官方 **KernelSU Manager 3.3.1**。

本版改动：

- 首页区分正在检查授权、管理器未安装、准备获取临时 root、执行中、已加载等待授权、KernelSU 已启用。
- KSU 已显示“已越狱”、GhostSam 尚未获得 su 权限时，提示进入“超级用户”授权，避免把一次 su 检测失败误解为必须再次执行。
- 授权后返回首页重新检测，验证通过后显示“KernelSU 已启用”。点击主卡打开 KSU，可从管理器使用软重启。
- S23 首页状态和中英文文案独立维护，仓库首页统一为 GhostSam S23，补充后续同步上游的流程。
- 延续 r2 的 UAPI 5、Samsung KDP/DEFEX/RKP 和管理器安装监听修复；KernelSU 源码基线保持不变，从同一份源码重建驱动与 ksud。

安装与使用：

1. 保留官方 KernelSU Manager 3.3.1，下载附件 `GhostSam-S23-KernelSU-3.3.1.apk`。
2. 本版使用本次 CI 的 debug 签名，与旧测试版可能不同。先尝试升级安装；如提示签名冲突，保存需要的设置和日志后卸载旧 GhostSam S23，再安装本版。卸载会清除该应用的数据。
3. 首次使用或完整重启后，从 GhostSam S23 获取临时 root。如果 KSU 已显示“已越狱”，先在“超级用户”中授予 GhostSam S23 su 权限，再返回应用确认状态。
4. 显示“KernelSU 已启用”后，从 GhostSam 首页打开 KSU，再使用软重启。完整重启后临时 root 需要重新获取；切换已加载的驱动时也需完整重启。

用户已反馈 r2 在目标设备上授权后可正常使用软重启。**本 r3 安装包通过 CI 构建、单元测试、版本与包名检查、APK 载荷和签名校验，尚未进行 r3 真机验证。**

附件包含 APK、`BUILD-INFO.txt` 和 `SHA256SUMS`，可用 `sha256sum -c SHA256SUMS` 校验下载文件。
