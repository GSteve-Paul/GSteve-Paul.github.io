---
title: 如何在Linux平台部署网络扫描仪
created: 2025-06-11T22:54:00
modified: 2025-06-12T12:07:00
---
## 介绍

如果你用过网络打印机，你能很好地理解网络扫描仪是什么——网络扫描仪就是在一个网络中共享的扫描仪。具体而言它的作用就是，可以在一个扫描仪接入一个主机后，让这个主机所在的网络里的其他主机通过网络连接这个网络扫描仪而不用把这个扫描仪直接接入其他主机。这省去了很多麻烦。

从这里，我们引入几个名词：
**扫描仪服务器**：扫描仪直接连入的主机。
**客户端主机**：与扫描仪服务器处于同一网络下，能与扫描仪服务器通信的主机。

这个教程会教会你如何在Ubuntu上部署SANE服务以建立网络打印机，并让客户端顺利连接访问。

参考教程：
- https://help.ubuntu.com/community/SaneDaemonTutorial
- https://penguin-breeder.org/sane/saned/
- https://wiki.archlinux.org/title/SANE

## 前提环境

为了让这个教程更加易懂，先给出一个环境：

1. 网络是192.168.114.0/24
2. 扫描仪服务器（扫描仪直接接入的主机）的IP地址是192.168.114.1
3. 扫描仪服务器系统是Ubuntu 22.04 LTS

## 服务器配置

### 确保扫描仪服务器可以连接扫描仪

请确保你的扫描仪服务器可以直接连接这个扫描仪，这可能需要安装这个扫描仪对应的一些驱动程序。

可以通过以下命令查询能连接的扫描仪：
```sh
scanimage -L
```

如果成功会打印如下类似的信息：
```
device `brother4:bus1;dev5' is a Brother MFC-7480D USB scanner
```
### 共享你的扫描仪

打开这个配置文件：
```sh
vim /etc/sane.d/saned.conf
```
找到如下所示的地方，这里配置的就是客户端可以从哪里访问服务器：
```
## Access list
# A list of host names, IP addresses or IP subnets (CIDR notation) that
# are permitted to use local SANE devices. IPv6 addresses must be enclosed
# in brackets, and should always be specified in their compressed form.
#
# The hostname matching is not case-sensitive.

#scan-client.somedomain.firm
#192.168.0.1
#192.168.0.1/29
#[2001:db8:185e::42:12]
#[2001:db8:185e::42:12]/64
```
因此我们做如下改动：
```diff
	## Access list
	# A list of host names, IP addresses or IP subnets (CIDR notation) that
	# are permitted to use local SANE devices. IPv6 addresses must be enclosed
	# in brackets, and should always be specified in their compressed form.
	#
	# The hostname matching is not case-sensitive.
	
	#scan-client.somedomain.firm
	#192.168.0.1
	#192.168.0.1/29
	#[2001:db8:185e::42:12]
	#[2001:db8:185e::42:12]/64
+   192.168.1.0/24
```

### 启动SANE服务

输入如下命令：
```sh
systemctl start saned.socket
```
如果你希望它每次开机都会自启动，请输入以下命令：
```sh
systemctl enable saned.socket
```
## 客户端配置

### Linux

我这里客户端主机的系统也是Ubuntu 22.04 LTS。

首先打开这个配置文件：
```sh
vim /etc/sane.d/net.conf
```
找到如下所示的地方，这个地方填写的主机就是让你的客户端自动扫描有没有网络扫描仪的主机：
```
## saned hosts
# Each line names a host to attach to.
# If you list "localhost" then your backends can be accessed either
# directly or through the net backend.  Going through the net backend
# may be necessary to access devices that need special privileges.
```
所以需要做如下改动：
```diff
	## saned hosts
	# Each line names a host to attach to.
	# If you list "localhost" then your backends can be accessed either
	# directly or through the net backend.  Going through the net backend
	# may be necessary to access devices that need special privileges.
+	192.168.114.1
```
现在在你的客户端主机上查询能连接的扫描仪：
```sh
scanimage -L
```
若一切正常，将会显示如下类似的信息：
```
device `net:192.168.114.1:brother4:bus1;dev5' is a Brother MFC-7480D USB scanner
```

#### 可用软件

scanimage, Document Scanner

### Windows

待补充
