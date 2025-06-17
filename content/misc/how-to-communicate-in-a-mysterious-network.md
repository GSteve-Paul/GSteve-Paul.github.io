---
title: 如何在复杂网络环境下通信
created: 2025-06-08T23:22:00
modified: 2025-06-18T00:10:00
---
## 背景

现在给你介绍一个奇怪的网络环境：
- 存在AP隔离
- 禁止TCP协议通信

在这样的网络环境下，给你提一个难题：**在不修改上述网络环境的情况下，如何让两台接入Wi-fi的笔记本电脑进行通信。**

你该怎么办呢？

以防你没有学习过计算机网络，下面介绍一下相关名词。

### AP隔离

> AP隔离在连接的无线设备之间创建虚拟边界，它阻止无线设备之间的直接通信。但是，它仍然允许设备访问互联网。

有了对AP隔离的概念，我进行了一些测试，得到了如下有关这个复杂无线网络环境的信息：

#### 确认相距较近两台无线设备之间是无法通信的

由上述AP隔离定义可得，这个**相距较近**接下来再解释。

#### 在相距较远的地方，两台无线设备可以通信。

先讲原因：因为相距较远，这两台无线设备的AP不同。

如何检查AP是否相同？ 只需要查看网关即可，例如在Linux中，我可以这样检查我的默认网关：
```sh
ip route show | grep default
```

虽然AP隔离失效了，但是它们还是会处在这个大网络下的，因此TCP通信同样被禁用。

#### 不确定一台无线设备和有线设备是否可以通信。

距离上次测试时间太久了，我已经记不清了。

#### 连接到Wi-fi的无线设备可以与路由器通信。

这是显然的。否则，无线设备将无法访问互联网。

### TCP

> The Transmission Control Protocol (TCP) is one of the main protocols of the Internet protocol suite. It originated in the initial network implementation in which it complemented the Internet Protocol (IP). Therefore, the entire suite is commonly referred to as TCP/IP. TCP provides reliable, ordered, and error-checked delivery of a stream of octets (bytes) between applications running on hosts communicating via an IP network. Major internet applications such as the World Wide Web, email, remote administration, and file transfer rely on TCP, which is part of the transport layer of the TCP/IP suite. SSL/TLS often runs on top of TCP. 
> 
> 翻译：
> 传输控制协议（Transmission Control Protocol，简称TCP）是互联网协议套件的核心协议之一。其起源可追溯至最初的网络架构，在该架构中它与网际协议（Internet Protocol，简称IP）形成互补关系，因此整个协议套件通常被统称为TCP/IP。TCP协议通过在IP网络通信的主机之间建立连接，为应用程序提供可靠、有序且具有差错校验的字节流传输服务。万维网、电子邮件、远程管理及文件传输等主要互联网应用均依赖TCP协议，该协议隶属于TCP/IP套件的传输层。安全套接层（SSL）及其继任者传输层安全协议（TLS）通常基于TCP协议运行。

不清楚禁用TCP通信的技术是如何实现的，可能是在IP层进行抓包吧。但是在试验中我们能得到以下信息：

#### TCP通信被禁用

这个禁用并非是所有TCP流量都失效，而是在这个大网络中的任意两台主机无法利用TCP进行通信（除非你在这个大网络的白名单中）。而大网络中一台主机是可以和互联网上的主机进行通信的。

#### UDP通信未被禁用

没啥好说的，在Linux中利用`nc`进行测试即可。

有了上述信息，现在可以简单画出来这个网络的示意图了：

![网络拓扑图](web-struct.png)
## AP隔离解决方案


由于这是单一AP下的问题，我们先把视角切到单独一个AP下：

![AP隔离图](ap-isolation.png)
看到这个图，我们可以提出如下猜想：既然无线设备A与无线设备B无法直接通信，而它们各自却可以直接与网关通信，有没有方法能让A与B之间通信所发送的包先走一遍网关再走到终点呢？

答案是：**有**。

我们先回想一下计算机网络的TCP/IP五层模型：

- 应用层
- 传输层
- 网络层
- 数据链路层
- 物理层

接下来思考一下A在应用层发送给B一个数据包会发生什么：上面两层（应用层和传输层）的内容我们先不管，因为不太重要。

在网络层会封装一个网络层的头部，主要内容就是添加源IP地址和目的IP地址。在这里我们假设源IP地址为10.118.203.165，目标IP地址为10.118.203.170，网络掩码都是255.255.0.0。顺带一提，网关的IP地址为10.118.0.1。

紧接着来到数据链路层，则会封装一个MAC帧的头部。虽然Wifi所遵守的802.11标准与传统的Ethernet II的MAC帧并不相同，但是大致是会有源MAC和目标MAC的地址字段。源MAC很显然就是A的MAC地址。而对于目标MAC地址，既然B在和A相同的链路中，就直接在ARP表中查找B的IP（10.118.203.170）所对应的MAC地址了……不对！如果按照这样传统的做法，就绕不开AP隔离了！

下面我们介绍两种绕过的方法。这两种方法本质是一样的。

### 修改路由表

在上文中数据链路层的封装过程，我们提到了“B在与A相同的链路中”的问题。那我们该如何破坏这个条件呢？

答案是修改路由表，让B看起来和A不在同一链路下。

首先通过以下指令观察一下路由表：
```sh
route -n
```
举个例子，会打印如下信息：
```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.118.0.1      0.0.0.0         UG    600    0        0 wlp3s0
10.118.0.0      0.0.0.0         255.255.0.0     U     600    0        0 wlp3s0
```
这里路由表中的第二行就是罪魁祸首。因此我们可以这样删掉它。
```sh
ip route delete 10.118.0.0
```
为了防止路由表自动更新，我们可以添加这么一行路由防止之前的罪魁祸首复活：
```sh
ip route add 10.118.0.0/16 via 10.118.0.1 metric 1
```

这样一来，在A发送给B一个数据包的数据链路层就会发生这样的事：要找到目的MAC地址，就先看看B是不是在链路上，观察一下路由表，发现并不是。于是就走默认路由了，也就是下一跳会跳到网关10.118.0.1，接着找到ARP表里10.118.0.1对应的MAC，最后填入MAC帧的目的MAC地址字段。

紧接着，这个MAC帧会被发送到网关。此时路由器会解开MAC帧，查看网络层的内容：发现这个包最终会发给B（10.118.203.170），然后根据路由器自身的路由表和ARP表得到B的MAC，最终重新封装一个MAC帧发送给B。

这样一来，之前A直接到B的过程就变成了A到路由器再到B，同理，在B这边也做相似的路由表修改操作，就能让B直接到A的过程变成B到路由器再到A。这在多了一次转发的开销下绕过了AP隔离，让A与B可以通信。

但是，这似乎有个前提：寄希望于AP隔离不会做在网络层。虽然AP隔离大概率是在数据链路层做的（毕竟MAC地址直接与设备有关），但是假如在网络层中也有如此的（IP转MAC再判断是否隔离）过程，这个方法就会失效。不过鉴于本方法能奏效，我们就可以确信AP隔离是工作在数据链路层的。具体而言就是在路由器解开MAC帧时，会检查源MAC地址和目的MAC地址是否是自己AP下的两台无线设备，如果是，就丢掉这个帧。

### 修改ARP表

这同样也是一个方法，只是作用点不同。先说操作方案：将A主机的ARP表中B主机的IP（10.118.203.170）对应的MAC地址，改成路由器的MAC地址。

首先查看一下本机ARP表：
```sh
arp -n
```
可能会打印一下信息：
```
Address                  HWtype  HWaddress           Flags Mask            Iface
10.118.203.170           ether   TTTTTTTTTTTTTTTTT   C                     wlp3s0
10.118.0.1               ether   RRRRRRRRRRRRRRRRR   C                     wlp3s0
```
利用这个命令修改ARP表：
```sh
ip neigh change 10.118.203.170 lladdr <路由器的MAC地址> nud reachable dev <网卡>
```
这样一来，在A发送给B一个数据包的数据链路层就会发生这样的事：要找到目的MAC地址，就先看看B是不是在链路上，观察一下路由表，发现是的。于是把修改过的B主机的MAC地址（实际上是路由器的MAC地址）填入MAC帧的目的MAC地址字段。

于是，这个帧就会被传输到网关，进而与上文改路由表的路径达成了一致。同理，B主机的ARP表也要进行修改。但是我觉得这种方式对网络具有一定的破坏性——毕竟A主机无法区分B主机和网关的MAC地址，可能会引起一些稀奇古怪的bug。

## TCP禁用解决方案

在传统的TCP/IP五层模型下，TCP是以IP数据报为载体进行发送的，这样的TCP包会被拦截掉，那我们可以尝试在发送端把TCP的包放在一种特殊的UDP的包的数据段，以一种特殊的UDP为载体进行发送。在接收端把这些特殊的UDP包解包后提取出TCP即可。

这样的软件已经有人做过了，名叫[WireGuard](https://www.wireguard.com/)。

>WireGuard® is an extremely simple yet fast and modern VPN that utilizes **state-of-the-art [cryptography](https://www.wireguard.com/protocol/)**. 

以防你不知道什么是VPN，这里摘了一段维基百科的内容：

> **Virtual private network** (**VPN**) is a [network architecture](https://en.wikipedia.org/wiki/Network_architecture "Network architecture") for virtually extending a [private network](https://en.wikipedia.org/wiki/Private_network "Private network") (i.e. any [computer network](https://en.wikipedia.org/wiki/Computer_network "Computer network") which is not the public [Internet](https://en.wikipedia.org/wiki/Internet "Internet")) across one or multiple other networks which are either untrusted (as they are not controlled by the entity aiming to implement the VPN) or need to be isolated (thus making the lower network invisible or not directly usable).[[1]](https://en.wikipedia.org/wiki/Virtual_private_network#cite_note-NIST-1)

而WireGuard就是利用UDP隧道打洞，其会把VPN中的各主机间的TCP包放在UDP的数据段里发送（会做一些加密等措施进行混淆）。我们这里只是利用它会建立UDP隧道这一特性。

这需要在A、B两台主机上安装WireGuard，进行如下配置：

A主机：
```
[Interface]
Address = 192.168.114.2/32
PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

# B
[Peer]
PublicKey = YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
AllowedIPs = 192.168.114.0/24
EndPoint = 10.118.203.170:51820 
PersistentKeepalive = 25

```

B主机：
```
[Interface]
Address = 192.168.114.1/24
ListenPort = 51820
PrivateKey = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# A
[Peer]
PublicKey = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
AllowedIPs = 192.168.114.2/32

```

这样，A与B之间借助WireGuard就能够正常进行TCP通信了。在这里A主机和B主机做EndPoint都没问题，原因是它们本来就在网络内可以正常用UDP互相进行通信。

这里有WireGuard配置的更详细内容： https://www.skyone.host/2024/wireguard-configure 。

## 结语

聪明的朋友可能看出来了这篇文章其实具有一定的实际意义，但作者建议你最好是能够合理、合法地运用知识方便生活而不是破坏和谐社会。

如果你对文章中的想法和实践有疑惑或者建议，也欢迎在下面留言。


