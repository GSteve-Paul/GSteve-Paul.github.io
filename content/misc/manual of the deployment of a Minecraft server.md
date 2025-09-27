---
title: Minecraft服务器部署手册
tags:
  - Minecraft
  - 部署
---
## 简介

本手册主要讲的是如何在Ubuntu 22.04 LTS上部署好一个Java版的Fabric模组服。这主要包含一下三个方面：
1. 搭设Java版的Fabric模组服服务端(`./server`)
2. 配置远程控制台(`./mcrcon`)
3. 支持与基岩版互通(`./viaproxy`)

## 搭设Fabric服务端

首先我们需要在[Fabric的官方网站](https://fabricmc.net/use/server/)上下载Fabric模组服服务端的启动器，也就是执行一下CLI download板块中所给出的命令；接着可以通过Launch command中给出的命令启动服务端。

我在这里为了能更好地自定义Java版本和内存大小，手写了下面这个脚本：

```bash title="./server/run.sh"
/usr/lib/jvm/java-21-openjdk-amd64/bin/java -Xmx16G -Xms8G -jar fabric-server-mc.1.21.3-loader.0.16.14-launcher.1.0.3.jar nogui
```

### 配置Fabric服务端

第一次启动服务端会自己停止，这是因为需要同意./server/eula.txt。再次启动服务端可以生成一些配置文件，其中./server/server.properties比较重要，如果有盗版玩家，应该将其中的`online-mode`设置为`false`才可以正常玩耍。