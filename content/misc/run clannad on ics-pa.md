---
title: 在ICS-PA上运行CLANNAD
date: 2025-01-11
---
## 动机

之前我做了[[course-lab/nju-ics-pa/index|ICS 2024]]这个课程设计，其中PA4的一个选作任务（运行ONScripter模拟器）可以让我们在Nanos-lite上玩基于ONS的Galgame。教程里选作任务要求的是能跑星之梦即可，正好我也因此入了Key社的坑，便发现教程里给的示例图片是CLANNAD🤔。于是我就试着在ICS-PA上运行CLANNAD。

## 问题

在完成选作任务后，我的ICS-PA能够很好地运行星之梦。于是我直接下载了一个CLANNAD的ONS版去试着跑跑。多亏了ICS-PA中计算机抽象层的设计，我们得以一层一层地运行慢慢检测Bug。

- 在native上直接跑ONS，没问题。
- 在native上连带着Navy-app下面的库，跑ONS，没问题。
- 在AM native的Nanos-lite上跑ONS，坏事了。一开始还能跑，跑着跑着发现还没蹦出来Presented by Key就直接 Segment Fault 了。（在我的机器上，是ONS在加载 bj\Snap1.jpg 这个文件时崩溃的）

这个段错误中会给出所访问的错误的内存地址，说是 0x9000000 。如果对 abstract-machine/am/src/native/platform.c 比较熟悉的朋友可能就会判断出来这个是 am_native 下 heap 的尾地址；如果不熟悉的朋友（比如我），就得依靠Nanos-lite上的strace观察，于是乎就会发现是在调用`sys_brk()`的时候崩溃的。

接下来就很好判断了！肯定就是因为开的堆不够大，导致被ONS吃干抹净了。毕竟我们的玩具Nanos-lite里只能分配内存无法回收内存。

## 解决方案

### am_native

把 abstract-machine/am/src/native/platform.c 的 `PMEM_SIZE` 设大点，比如1G。这个内存大小就只和你的物理机的内存大小直接相关。

### NEMU

首先我们要考虑，我们内存究竟能设多大。考虑到 NEMU 里内存从 0x80000000 开始，而在0xa0000000 附近会开始有 MMIO 的映射，所以实际上就只能设个 0x20000000 这么大（512M）。

所以一方面，在 abstract-machine/am/src/platform/nemu/include/nemu.h 里修改 `PMEM_SIZE`；另一方面，在 NEMU 的 Kconfig 里面也要重新设置一下内存大小。

---

虽然在上述的操作后，可以在riscv32-NEMU上玩CLANNAD了，但是能在模拟器上玩也不太可能——实在是太卡了，光是Presented by Key这个动画都跑了几分钟才跑完。

![[Screenshot from 2025-11-01 15-43-04.png]]

![[simplescreenrecorder-2025-11-01_15.40.00.mp4]]

![[simplescreenrecorder-2025-11-01_15.51.25.mp4]]

最近我安装了Fedora Linux 43 (KDE Plasma Desktop Edition) x86_64这个系统，于是打算把ICS-PA从Ubuntu 24.04移植到Fedora 43上，虽然只是发行版不同，但是出现的Bug却真的很多。由于我实在是找不到一个能在Fedora (KDE) + Wayland上正常运行还带录音的录屏软件，我就只好截个图了。

正是因为这些Bug，我将长期保持我的电脑上有Windows 11，Ubuntu 24.04 和 Fedora 43的魔幻状态。如果实在是Bug太多，我将会装个Debian 13差不多得了。

![[Pasted image 20251101235551.png]]

之后安了个OBS专门来录屏，感觉有点大材小用了。

![[2025-11-02 16-49-07.mp4]]