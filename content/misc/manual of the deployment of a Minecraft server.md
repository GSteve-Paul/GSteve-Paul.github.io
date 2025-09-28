---
title: Minecraft服务器部署手册
tags:
  - Minecraft服务器
---
## 简介

本手册主要讲的是如何在Ubuntu 22.04 LTS上部署好一个Java版的Fabric模组服。这主要包含一下三个方面：

1. 搭设Java版的Fabric模组服服务端(./server)
2. 配置远程控制台(./mcrcon)
3. 支持与基岩版互通(./viaproxy)

阅读本手册后，你将会知道如何部署一个Fabric模组服，并且能够维护部署在工作室服务器上的MC服务端。

## 搭设Fabric服务端

首先我们需要在[Fabric的官方网站](https://fabricmc.net/use/server/)上下载Fabric模组服服务端的启动器，也就是执行一下CLI download板块中所给出的命令；接着可以通过Launch command中给出的命令启动服务端。

我在这里为了能更好地自定义服务端的Java版本和内存大小，手写了下面这个脚本。之后可以通过运行这个脚本启动服务端：

```bash title="./server/run.sh"
/usr/lib/jvm/java-21-openjdk-amd64/bin/java -Xmx16G -Xms8G -jar fabric-server-mc.1.21.3-loader.0.16.14-launcher.1.0.3.jar nogui
```

^9bdd12

在启动服务端后，可以在服务端控制台中输入stop停止服务端。

### 配置Fabric服务端

第一次启动服务端并不会成功启动起来，这是因为需要先同意./server/eula.txt。修改这个文件之后再次启动服务端就可以生成一些配置文件，其中./server/server.properties比较重要。接下来仅挑选其中较为重要的进行讲解：

1. `online-mode`：如果有盗版玩家，应该将其中的`online-mode`设置为`false`才可以正常玩耍。
2. `server-ip` ：因为服务端就在本机，所以留空即可。
3. `server-port`：设置服务端的端口号，我设置的是`25565`。

如果上面都没出现问题，修改./server/server.properties后重启服务端就可以使得配置生效。所以如果可能的话，可以试着在服务端所在机器上用MC客户端连接`127.0.0.1:SERVER-PORT`加入服务器，事实上从其他的机器也应该可以连接，不过这可能需要计算机网络相关的知识，不在本手册的讨论范围之内，不过如果你有疑惑，也很欢迎在本博客下方评论区提问😀！

### 安装模组

既然我们用的都是Fabric模组服的服务端，很显然应该是可以安装模组的。模组文件（一般是`.jar`）应该放在./server/mods/目录下。

因为很多基于Fabric的模组都需要有Fabric API的支持，所以应该先安装名叫Fabric API的模组。此外我还安装了一个名叫Essential Commands的模组，它提供了很多工具命令，让服务器玩起来更有意思。我建议在[modrinth网站](https://modrinth.com)上找模组，因为这个网站的模组大多会标明这个模组是客户端模组还是服务端模组（服务端模组只需要被安装在服务端上即可），选择模组时还应注意MC版本，版本不同可能会导致服务端无法启动。

## 配置远程控制台

我们所用的远程控制台是mcrcon这款软件，其安装流程如下（此处假定你的工作目录在./）：

```bash
git clone https://github.com/Tiiffi/mcrcon.git
cd mcrcon
make
sudo make install
```

这个mccron事实上是和MC服务端集成在一起的，在./server/server.properties有如下选项与之有关。

1. `enable-rcon`：如果你要启用远程控制台，那就设置为`true`。
2. `rcon.port`：mcrcon的监听端口，我设置的是`25575`。
3. `rcon.password`：mcrcon的密码。
4. `broadcast-rcon-to-ops`：设置mccron发送的命令回复是否发送给所有在线的OP。默认为`true`。

需要注意的是，不建议将mcrcon端口暴露在公网中，因为RCON协议是以明文发送所有数据的，包括认证所需的密码！

在上述配置完成后，可以在服务器上运行如下命令控制服务端：

```bash
/usr/local/bin/mcrcon -H localhost -P RCON.PORT -p RCON.PASSWORD
```

### 配置系统服务

为了方便管理，把服务端做成一个系统服务是有必要的。这个服务主要需要考虑的是它的启动脚本和停止脚本——启动服务端很简单，只需要运行[[manual of the deployment of a Minecraft server#^9bdd12|上面的脚本]]即可；而因为服务端进程在后台不能直接控制，所以应该用远程控制台关闭服务端，即`/usr/local/bin/mcrcon -H localhost -P RCON.PORT -p RCON.PASSWORD stop`。

根据上面的分析，可以写出以下的`.service`文件，此后可以使用`systemctl start mc-java-server`和`systemctl stop mc-java-server`两个命令很方便地对服务端进行启动、关闭。

```txt title="/etc/systemd/system/mc-java-server.service"
[Unit]
Description=Minecraft Server
After=network.target

[Service]
User=可以正常启动、关闭服务端的Linux用户，最好不要是root
Nice=1
KillMode=none
SuccessExitStatus=0 1
ProtectSystem=full
PrivateDevices=true
NoNewPrivileges=true
WorkingDirectory=你的server的目录
ExecStart=/bin/bash run.sh
ExecStop=/usr/local/bin/mcrcon -H localhost -P RCON.PORT -p RCON.PASSWORD stop

[Install]
WantedBy=multi-user.target
```

^6c7007

## 与基岩版互通

参考文档：[Geyser所支持的版本](https://geysermc.org/wiki/geyser/supported-versions/)

为了可以与基岩版互通，应当安装一个叫作Geyser的工具。这个工具作为一个媒介，能让基岩版的客户端经由它连接上Java版的服务端。然而，Geyser程序往往只能允许最新的基岩版客户端连接上最新的Java版的服务端，所以我们应当使用ViaProxy使得可以连接更老版本的Java版服务端，不过还是应当用最新的基岩版客户端。

### 搭设ViaProxy

因为Geyser-ViaProxy是作为插件形式放在ViaProxy里面的，所以应该先搭设ViaProxy。

要安装ViaProxy，你应该从[ViaProxy的Github仓库](https://github.com/ViaVersion/ViaProxy)下载最新的jar包，假定你目前的工作目录是./viaproxy，可以输入以下命令（对于不同版本可能会略有不同）：

```sh
wget https://github.com/ViaVersion/ViaProxy/releases/download/v3.4.4/ViaProxy-3.4.4.jar -O viaproxy.jar
```

下载完毕后，可通过`java -jar viaproxy.jar`运行这个jar包，并生成一些配置文件。其中./viaproxy/viaproxy.yml是ViaProxy的关键配置文件，其中的`target-address`应该设置为Java服务端的地址，我这里应该是`127.0.0.1:25565`。

此时，运行以下命令，如果一切正常，应该可以成功启动ViaProxy。

```sh
/usr/lib/jvm/java-21-openjdk-amd64/bin/java -jar viaproxy.jar config viaproxy.yml
```

### 搭设Geyser-ViaProxy

随后，我们就可以从[Geyser的下载页面](https://geysermc.org/download)下载ViaProxy的插件Geyser-ViaProxy，并放到刚才生成的./viaproxy/plugins目录中。这可以通过在./viaproxy/plugins中输入以下命令完成：

```sh
wget https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/viaproxy -O Geyser-ViaProxy.jar
```

此时可以重启ViaProxy，重启后ViaProxy会自动检测插件，并为插件生成一些必要的文件。其中`./viaproxy/plugins/Geyser/config.yml`是Geyser-ViaProxy的配置文件，其中的`bedrock.port`选项代表Geyser-ViaProxy所模拟出来的基岩版服务端的端口，也就是基岩版客户端应该连接的端口号。

### 配置系统服务

与上面类似的，编写一个系统服务方便管理。需要注意的是目前我没找到ViaProxy的远程控制台之类的东西，只好默认用kill停止服务了。如果你有一些更加优雅的实现，也希望能在评论区告诉我一下，谢谢🙏。

```txt title="/etc/systemd/system/mc-viaproxy-server.service"
[Unit]
Description=Minecraft ViaProxy
After=mc-java-server.service
Requires=mc-java-server.service
BindsTo=mc-java-server.service

[Service]
User=lijn
WorkingDirectory=/home/lijn/minecraft/viaproxy
ExecStart=/usr/lib/jvm/java-21-openjdk-amd64/bin/java -jar viaproxy.jar config viaproxy.yml

[Install]
WantedBy=multi-user.target
```

为了能让`mc-viaproxy-server`停止时让`mc-java-server`也停止，所以应当在[[manual of the deployment of a Minecraft server#^6c7007|/etc/systemd/system/mc-java-server.service]]的`[Unit]`中写入`PartOf=mc-viaproxy-server.service`选项。

完成以上工作后，可以使用`systemctl start mc-viaproxy-server`和`systemctl stop mc-viaproxy-server`两个命令很方便地对Java服务端以及ViaProxy进行启动、关闭。

### 升级Geyser-ViaProxy

在过去一段时间后，基岩版客户端很有可能会自动更新，导致Geyser-ViaProxy显得版本过旧。此时应该重新走一遍[[manual of the deployment of a Minecraft server#搭设Geyser-ViaProxy|搭设Geyser-ViaProxy]]的流程即可。

## 总结

做完以上工作应该就可以成功搭建出一个可堪一用的服务端了，并且可以通过管理`mc-viaproxy-server`这个系统服务管理整个服务端。

希望你能在Java和基岩版客户端上玩得愉快😊！如果你对本手册有任何疑问和建议，都请在下面的评论区发表哦~