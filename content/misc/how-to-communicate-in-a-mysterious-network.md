---
title: 如何在复杂网络环境下通信
created: 2025-06-08T23:22:00
modified: 2025-06-10T11:12:00
---
## 背景

假设我们现在处在一个复杂的无线网络环境下，即这样的无线网络环境：
- 存在无线AP隔离
- 禁止TCP协议通信

显然这并不是现实生活中我们会遇到的网络环境。此刻你穿越到了一个叫做安东星的地方，这个星球上的网络环境就是如此！此时BVVD向你提出一个难题：在不修改上述网络环境的情况下，如何让两台接入Wi-fi的笔记本电脑进行通信。该怎么办呢？

以防你没有学习过计算机网络，下面介绍一下相关名词。

### 无线AP隔离

> 无线AP隔离在连接的无线设备之间创建虚拟边界，它阻止无线设备之间的直接通信。但是，它仍然允许设备访问互联网。

有了对无线AP隔离的概念，我进行了一些测试，得到了如下有关这个复杂无线网络环境的信息：

#### 确认相距较近两台无线设备之间是无法通信的

由上述无线AP隔离定义可得，这个**相距较近**接下来再解释。

#### 在相距较远的地方，两台无线设备可以通信。

先讲原因：因为相距较远，这两台无线设备的AP不同。

如何检查AP是否相同？ 只需要查看网关即可，例如在Linux中，我可以这样检查我的默认网关：
```sh
ip route show | grep default
```

虽然无线AP隔离失效了，但是它们还是会处在这个大网络下的，因此TCP通信同样被禁用。

#### 不确定一台无线设备和有线设备是否可以通信。

距离上次测试时间太久了，我已经记不清了。

#### 连接到Wi-fi的无线设备可以与路由器通信。

这是显然的。否则，无线设备将无法访问互联网。

### TCP通信

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