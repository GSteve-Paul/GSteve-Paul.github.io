---
title: 为素晴日（Steam版）安装中文补丁后，在Linux上运行出现乱码问题的解决方案
date: 2026-10-25
tags:
  - 游戏
---
我用的补丁是 https://tieba.baidu.com/p/11037491522 ，非常感谢这个大佬的贡献。

不过我在 Linux 上的 Steam 版素晴日上打这个补丁之后发现会乱码。一方面，补丁里面的中文是按照GBK编码的；另一方面，Steam Proton兼容层的Wine并没用GBK去解读。这就导致会出现这样的问题：

![image.png](https://file.stevepaul101.net/Screenshot_20261024_202130.png)
Steam Proton兼容层正好会接收一个环境变量 `HOST_LC_ALL`，它可以指定启动 Wine 时应使用的 `LC_ALL` 值，覆盖其他的 locale 设置。因此需要在 Steam 游戏的属性 → 通用 → 启动选项 里面写入 `HOST_LC_ALL=zh_CN %command%` ，这样一来 Wine 就会按 GBK 解析字符串的字节了。

![image.png](https://file.stevepaul101.net/Screenshot_20261024_202651.png)

![image.png](https://file.stevepaul101.net/Screenshot_20261024_202743.png)

在此感谢一下 Codex 和 GPT-6-Astra 大人，是他们去读开源仓库的源码进而找到了以上问题的原因。