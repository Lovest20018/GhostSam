# 国行 S23 专用版：KernelSU Manager 3.3.1 兼容修复

本构建只面向用户提供截图中的设备与固件：

| 项目 | 目标 |
| --- | --- |
| 机型 | 国行 Galaxy S23，SM-S9110 |
| 固件 | S9110ZCS8FZI1 |
| 编译编号 | BP4A.251205.006.S9110ZCS8FZI1 |
| 系统 | One UI 8.5 / Android 16（SDK 36） |
| 完整内核版本 | 5.15.189-android13-8-3251900-abS9110ZCS8FZI1 |
| KMI | android13-5.15 |
| 管理器 | 官方 KernelSU Manager 3.3.1 |

Android 系统版本不决定 KMI。该手机升级到 Android 16 后仍使用
android13-5.15 内核，因此不能打包 android16-6.12 模块。

## 修复内容

Manager 3.3.1 要求 UAPI 5，而原 APK 的定制 ksud 及其内嵌 KernelSU
模块使用 UAPI 2，导致首页显示“需要更新内核”。升级管理器不会替换它们。

构建使用 `snothin/KernelSU` 三星分支提交
`abbd7be7fb5e0af607c2a85e02efae03044bba86`。已核对该提交的 su 会话 FD、
EVENT_SERVICES 和 app profile v4 接口；它具有 UAPI 5 的相关行为，但为了
搭配旧管理器显式把 `KERNEL_SU_UAPI_VERSION` 锁为 2。

`scripts/prepare-kernelsu.py` 仅对这个指定提交恢复 UAPI 5，拒绝其他提交
和额外源码修改。随后从同一份头文件重建 ksud 及唯一的
`android13-5.15_kernelsu.ko`，保留三星 KDP/DEFEX、加载前 staging、加载后
`finish_install()`。不混用旧驱动或只替换二进制中的版本字符串。

专用 APK 使用 DirtyFrag standalone 路径，固定官方 KernelSU，不提供
Ghostlock 或 KernelSU-Next 切换。无需把 S23 填进原系列表或猜测偏移。
打包只保留 ksud 和 `dfr_lkm-android13-5.15.ko`；后者是安装辅助模块，
不是内嵌的 KernelSU 驱动，无需因为这次 UAPI 变化重编译。

APK 显示名称为 **GhostSam S23**，包名为 `com.snothin.ghostsam.s23`，
可与原 GhostSam 同时安装。开始执行前核对机型、编译编号、SDK 和完整内核
版本，不匹配时停止；系统更新后需要重新审查目标信息。

## 在 fork 中构建

1. 将修复文件提交到 fork 的 `codex/fix-s23-kernelsu-331` 分支。
   push 会启动 **Build GhostSam S23**。也可以合并工作流后从 Actions
   手动执行该工作流。
2. 工作流依次构建 Samsung KernelSU 模块、嵌入该模块的 ksud、S23 APK。
   APK 构建使用 JDK 21、SDK 37.0、NDK 30.0.16248370 和 CMake 3.22.1。
3. 成功后下载 `ghostsam-s23-uapi5-apk` artifact，内含
   `GhostSam-S23-KernelSU-3.3.1.apk`、构建信息和 `SHA256SUMS`。
   在解压目录执行 `sha256sum -c SHA256SUMS` 核对文件。

APK 是标准 debug 签名的测试版本。工作流验证包名、APK 签名、两个 payload
与本次构建输入完全一致，以及 arm64 standalone JNI 库存在。
不需要上传私有 release 签名密钥。不同环境的 debug 签名可能不同，后续
升级安装需要保持同一签名，或先卸载测试版再安装。

本地构建需要先用上述流程生成 UAPI 5 ksud，再覆盖
`app/app/src/main/assets/payloads/ksud/ksud`，执行：

```bash
cd app
./gradlew :app:testDebugUnitTest :app:assembleDebug -Ps23Only=true --no-daemon --no-configuration-cache
```

`verifyPayloads` 拒绝旧 UAPI 的 ksud 和错误格式的辅助模块。
`scripts/verify-s23-apk.py` 检查最终 APK，拒绝旧资产、其他 KMI、Next 和
companion APK。版本标记用于发现误打包；兼容性仍依靠源码核对、同源编译
和真机验证。

## 真机验证

1. 安装 S23 专用 APK 和官方 KernelSU Manager 3.3.1。
2. **重启手机**后运行 GhostSam S23 的 standalone 安装流程。
   late-load 不会替换本次启动已经加载的旧 KernelSU，重启才能切换驱动。
3. 检查 KernelSU Manager 是否识别驱动且不再显示“需要更新内核”。
   验证 root 授权、`su -c id`、授权名单及现有模块。
4. 如果失败，保存完整 GhostSam 日志及管理器截图，特别是模块加载、
   KDP/DEFEX 和内核接口有关的错误。

源码测试和 Actions 成功不等于该固件已通过真机测试。5.15 在现有
DirtyFrag 兼容窗口中属于预测支持；三星厂商内核配置和安全补丁是否允许
安装、模块初始化是否成功，需要这台 SM-S9110 实测确认。
