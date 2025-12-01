---
title: 别了，RTL8852BE网卡
date: 2025-11-09
---
今年 1 月份买了个联想的 ThinkBook 14 G7 AHP 轻薄本，于是把原先装在 Acer 游戏本上的 Ubuntu 给移植了过来。

用着用着吧，感觉蓝牙这一块老是扯皮，连个蓝牙耳机甚至需要不断配对，一般而言是配对一次之后就能直接连接的；此外就是还特别爱掉蓝牙鼠标，掉了之后就连不上，必须重启。紧接着还发现网卡有跳 ping 的问题，非常的抽象。

原以为是 Ubuntu 24.04 LTS的问题，于是乎装了 NixOS, Fedora, Debian 发现都有这个问题，而且时不时的掉网卡问题会导致 Debian 13反复进入睡眠状态——我这才明白——看来我电脑的网卡确有问题！

![](https://file.stevepaul.cc/maodie.gif)

---

我随后在网上发现我电脑里自带的是🦀 RTL8852BE，这个网卡的性能实在是难以恭维，基本上是 Wi-Fi 6 网卡里最拉的，与其说是网卡不如说是卡网。遂在淘宝上买了个英特尔的 AX210 网卡。

我买英特尔的 AX210 网卡是有原因的。首先它是 2020 年发行的老网卡了，本着在 Linux 中买旧不买新（怕驱动支持差）的原则，它比较合适；此外我看了一些评测，似乎其表现也比较稳定，性能也不错，于是就钦定好买它了。

新装的 AX210:

![](https://file.stevepaul.cc/Pasted%20image%2020251109234741.png)

![](https://file.stevepaul.cc/Pasted%20image%2020251109234835.png)

卸下来的 RTL8852BE：

![](https://file.stevepaul.cc/Pasted%20image%2020251109235013.png)

![](https://file.stevepaul.cc/Pasted%20image%2020251109235036.png)

现在还没测过速，其实我对这方面也不是很感冒。但至少从直观上而言，没有老是掉蓝牙了。

---

这周周末基本上是在折腾 Linux 了，我的最新折腾成果：

<p><video controls src="https://file.stevepaul.cc/Screencast_20251109_235314.webm"></video></p>

下周我打算读读更多 ANF 相关的论文，顺便做个简单的 ANF 的 DPLL 算法。虽然 DPLL 算法挺简单的，但是要优美、高效地实现起来，可也一点也不简单呐！关于接下来的博客内容，大概率是和故宫以及 ANF 相关的了。