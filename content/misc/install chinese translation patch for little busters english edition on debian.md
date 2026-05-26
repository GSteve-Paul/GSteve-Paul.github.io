---
title: 在Debian上为Little Busters English Edition安装中文补丁
date: 2026-01-27
---
这里我采用的中文补丁是： https://github.com/Jack-Myth/LBEE_TranslationPatch ，非常感谢这位大佬的贡献。

要在 Linux 上做这件事情，本质上是让这个补丁在 WINE 环境里运行。原仓库作者已经给出了在 WINE 环境下使用的一些提示，不过我在实际使用中发现还需要一些额外的详细说明。

## 步骤

1. 将 LBEE_TranslationPatch.exe 作为非 Steam 游戏添加到 Steam
2. 使用 Proton 9.0 兼容层运行补丁程序
3. 添加 Little Busters English Edition 的游戏启动选项： `WINEDLLOVERRIDES=dsound.dll=n,b %command%`

## 说明

问题主要出在补丁程序在运行时需要从一个打开文件对话框中选中 Little Busters English Edition 的可执行文件。一般来说，在 Debian 里这个路径应该是
`$HOME/.steam/debian-installation/steamapps/common/Little Busters! English Edition/LITBUS_WIN32.exe`。但鉴于这个对话框里似乎无法显示隐藏文件，所以可以用 `ln -s $HOME/.steam/debian-installation/steamapps/common/Little\ Busters!\ English\ Edition/ lb` 做一个软链接，然后再通过软链接定位到具体的程序。

![image.png](https://file.stevepaul101.net/20260127233712659.png)
