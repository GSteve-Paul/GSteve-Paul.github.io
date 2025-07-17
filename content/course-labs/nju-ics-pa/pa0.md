---
title: PA0
tags:
  - NJU-ICS-PA
---
## 开发环境

PA0主要是让我们配置一下开发环境，我在这里列出一下我的开发环境吧，具体那些教程中已经详细列出的我就不再列出了。

- 操作系统：Ubuntu 24.04 LTS（教程里建议使用Ubuntu 22.04 LTS）
- 中文输入：fcitx5-rime，雾凇拼音
- 编辑器：Visual Studio Code，采用Vim插件；Neovim（教程里建议直接使用vim，但是我懒得配置了）

关于环境变量`NEMU_HOME`，`AM_HOME`，由于我用的是`fish`，所以我做了以下配置：
```js title="~/.config/fish/config.fish" /NEMU_HOME/ /AM_HOME/
set -x NEMU_HOME /home/lijn/ics2024/nemu
set -x AM_HOME /home/lijn/ics2024/abstract-machine
```


## 感想

PA0大概就是教会学计算机的新手们学会简单的环境配置、学会好的提问和用STFW、RTFM、RTFSC方式去解决问题。不过现在很多已有解决方案的问题已经不用STFW、RTFM了，比如像`man`这样的工具，直接把文档丢给AI显然比自己看更快，还有就是可以用AI教你Vim的键位等等事情。不过AI也并非是万能的，当前它的创新能力、思考能力还显得不足，你也很难给它提供解决一个问题所需要的所有上下文，因此目前还得是让人来干事。

## 番外

一些其他的好课：
1.  [计算机教育中缺失的一课](https://missing.csail.mit.edu/)
2.  [Git学习](https://learngitbranching.js.org/)
