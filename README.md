# GhostSam S23

**English** | [中文](README.zh.md)

A Samsung Galaxy S23 temporary root app, adapted from
[snothin/GhostSam](https://github.com/snothin/GhostSam) for the China-market
**SM-S9110 on firmware S9110ZCS8FZI1**. This fork uses DirtyFrag standalone
and official **KernelSU Manager 3.3.1**, with matching UAPI 5 components.

[Download the r2 test APK](https://github.com/Lovest20018/GhostSam/releases/tag/s23-ksu-3.3.1-r2)
· [S23 build details (中文)](docs/KernelSU-3.3.1.zh.md)
· [Home states and upstream maintenance (中文)](docs/Home-copy-and-upstream.zh.md)

## Supported target

| Item | Required value |
| --- | --- |
| Device | Galaxy S23, China-market SM-S9110 |
| Firmware | S9110ZCS8FZI1 |
| Build | BP4A.251205.006.S9110ZCS8FZI1 |
| System | Android 16 / SDK 36 |
| Kernel | 5.15.189-android13-8-3251900-abS9110ZCS8FZI1 |
| KMI | android13-5.15 |
| Manager | Official KernelSU Manager 3.3.1 |

The app checks the target before running and stops on a mismatch. Android 16
on this device still uses an android13-5.15 kernel. Support for other models,
firmware versions, or the upstream S22 / S26 / Z Fold8 targets is outside
this S23 build's validated scope.

## Using the S23 app

1. Install **GhostSam S23** and official **KernelSU Manager 3.3.1**. The S23
   package is `com.snothin.ghostsam.s23` and can coexist with upstream GhostSam.
2. On first use or after a full reboot, open GhostSam S23 and run the temporary
   root flow. This edition uses standalone mode and official KernelSU.
3. If KSU already shows **Jailbroken**, open KSU and grant **GhostSam S23**
   su access under **Superuser**, then return to the app. A denied su check
   alone does not mean KernelSU needs to be loaded again.
4. After the app verifies su access, its home card shows **KernelSU enabled**.
   Open KSU from that card to use the manager's soft reboot action.

On the user's target phone, granting GhostSam su access and then opening KSU
from GhostSam allowed the manager's soft reboot action to work. Temporary
root lasts until a full reboot; a soft reboot does not replace an already
loaded driver when testing an updated build.

## Source and APK versions

| Version | Status |
| --- | --- |
| r2 | Previously published test APK; see the release notes for installation details |
| r3 (`0.2.3-s23-uapi5-r3`, build 63) | Current source on `main`; includes the revised home states and authorization hints; no r3 APK has been built or published yet |

The r3 home card distinguishes checking, manager missing, ready, running,
loaded but awaiting su access, and enabled. These changes require a new APK;
pushing source to GitHub does not update the installed r2 app.

## Building

For a complete build, open [Actions](https://github.com/Lovest20018/GhostSam/actions/workflows/kernelsu-331.yml),
select **Build GhostSam S23**, choose `main`, and use **Run workflow**.
The workflow rebuilds the Samsung KernelSU driver and ksud from the pinned
source, then builds and verifies the S23 APK. Download the
`ghostsam-s23-uapi5-apk` artifact from a successful run.

Pushes to `main` currently do not trigger this workflow. Manual builds from
`main` produce artifacts; the historical r2 publication step is gated to its
original branch.

Local builds require JDK 21, SDK 37.0, NDK 30.0.16248370, CMake 3.22.1, and
the matching rebuilt UAPI 5 payloads. Follow the
[build guide](docs/KernelSU-3.3.1.zh.md) to prepare the payloads first, then run:

```bash
cd app
./gradlew :app:testDebugUnitTest :app:assembleDebug -Ps23Only=true --no-daemon --no-configuration-cache
```

The S23 build packages only ksud and the android13-5.15 installation module.
It excludes other KMIs, KernelSU-Next, and the companion APK.

## Upstream maintenance

`main` is this fork's current S23 integration branch. The upstream source
remains [snothin/GhostSam](https://github.com/snothin/GhostSam), based on
v0.2.3 (`818faef`). The original toolkit and its device coverage are described
in the [upstream README](https://github.com/snothin/GhostSam/blob/818faef4a278353a22c3481a01a6eaedf8088a3d/README.md).
S23 home states and localized copy live in separate files to help review
future upstream merges.

Check upstream changes from a local checkout with the configured `upstream`
remote:

```bash
python scripts/check-upstream.py --fetch
```

The command reports incoming changes and files needing S23 review. Merge
reviewed updates through a temporary branch, validate them, then integrate
into `main`. See the [maintenance guide](docs/Home-copy-and-upstream.zh.md).
KernelSU is pinned separately to `snothin/KernelSU` commit
`abbd7be7fb5e0af607c2a85e02efae03044bba86`; updating GhostSam does not change
that driver baseline automatically.

## Credits and license

- [snothin/GhostSam](https://github.com/snothin/GhostSam): the original app,
  shared infrastructure, and Ghostlock / DirtyFrag integration.
- [snothin/KernelSU](https://github.com/snothin/KernelSU) and
  [KernelSU](https://github.com/tiann/KernelSU): the Samsung driver, ksud,
  and manager work. The upstream tree also includes
  [KernelSU-Next](https://github.com/snothin/KernelSU-Next) integration.
- [ghostlock-s26](https://github.com/snothin/ghostlock-s26), @diabl0w's
  Z Fold8 porting input, and [DFRoot](https://github.com/diabl0w/DFRoot):
  upstream exploit work and public DirtyFrag research.

For security research on devices you own and control. Kernel exploitation
can cause crashes or reboots; compatibility must be reviewed after a system
update. Licensed under [Apache-2.0](LICENSE). Third-party provenance and
acknowledgements are preserved in [NOTICE](NOTICE).
