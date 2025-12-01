---
title: Git学习入门
date: 2023-09-07
tags:
  - 蓝旭2023秋季学习
---
# 概念

Git 是一个开源的分布式版本控制系统，用于敏捷高效地处理任何或小或大的项目，处理这些项目的版本控制。

# git分层结构

git工作分为三层，有远程仓库，本地仓库，暂存区和工作目录。后三个是在本地的，头一个是在外部服务器的。

工作目录其实就是之后执行文件操作的地方，也就是在Windows资源管理器下能直接看得到的。

暂存区和本地仓库都是在git init后生成的.git文件夹下的。

远程仓库在服务器那边。可以让我们的本地的同步到远程(push)，也能让远程的同步到本地(pull)。

分层结构
![](https://file.stevepaul.cc/a3a76cc2e65b45418cf19254f5205879.png)

文件状态

![](https://file.stevepaul.cc/4c011c74884e44d497e48ff0137b9e9f.png)

# git的初始化

网上下载并安装好git后，找到想要成为工作目录的文件夹，右键进入Git Bash，首先配置好全局的一些变量：

`git config --global user.name "用户名"`，配置全局用户名

`git config --global user.email "邮箱"`，配置全局用户邮箱

`git config --list`，列出所有的配置信息

接着呢，就可以`git init` 创建本地空仓库，然后就会发现在这个文件夹下新生成了一个隐藏文件夹名叫.git。

# 从 工作目录 到 远程仓库

## 基本逻辑

如上图所示，首先要把某个文件纳入到版本管理的范围中去！

`git add 文件名`

这样这个文件就从untracted变到了staged，且进入了缓存区

然后再将该文件纳入到本地仓库中去！

`git commit -m "我是注释"`

这样这个文件就变成了unmodified文件

最后就是提交到远程仓库了，但在此之前，还应该指明远程仓库在哪儿

`git remote add origin 远程仓库的地址`

这个地址能在github的仓库中找得到

接着就可以传送到远程仓库了，这里得挂个梯子，不然连不上(Connection was reset)

`git push --set-upstream origin master`

至此，上github看能发现空仓库里多了个文件，并且文件内的内容是恰好和你commit的时候一样的。

## 其他功能

### git rm

如果想删除远程库文件，则需要使用

`git rm --cached "文件路径"`

注意到他是不会删除工作区里的文件的，但是会把这次删除放入暂存区

如果想同时把工作区的文件删了，可以用

`git rm --f "文件路径"`

### git commit -a

`git commit -a "文件路径"`

设置修改文件后不需要执行 git add 命令，直接来提交

### git reset 

`git reset 文件路径`

如果想取消之前的git add，可以用这个方法让文件状态不再是staged

# 从远程仓库 到 工作目录

## 基本逻辑

首先得把远程服务器上的文件下载到本地仓库，也就是

`git fetch`

注意到这个时候还不会到工作目录里去

然后可以看更改情况，也就是

`git log`

然后就可以把远程服务器的更改应用到工作目录上去

`git merge`

此时就把更改合并了，当然也可以设置分支

## 更方便的方法

`git pull` = `git fetch` + `git merge`