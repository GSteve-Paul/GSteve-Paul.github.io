---
title: 浅谈Tailscale——子网路由
date: 2025-10-23
---
## 前言

### 迷惑现象

事情是这样的。最近我买了一个便携式的路由器（GL-iNet 的GL-XE300，有电池、4G LTE 功能），它默认路由器下面的网段是 192.168.8.0/24，因而路由器对应的配置页面也就顺理成章的是 http://192.168.8.1 。这一切都显得很正常。

按往常一样，在接入互联网之前，我在我的电脑上通过上面这个网址便大致配好了路由器。但是在我接通互联网之后，想要再次进入 http://192.168.8.1 进行配置，却意外发现给我跳转到了另一个神秘的路由器的配置页面。

这是一个十分迷惑的现象。总不能是被劫持了吧🤣？！

### 原因

实际上，也确实是被“劫持”了。是我自己配置的 Tailscale “劫持”了这个 IP。还好我以前听说过 `traceroute` 这个工具，我用这个工具追踪了路由到 192.168.8.1 的过程：

```bash
traceroute 192.168.8.1
```

从它的输出中，我发现它先被路由到了我的 Tailscale 网络中一台主机，然后又路由到了那台主机所在网段中的 192.168.8.1 的那个路由器去了。

之所以会被"劫持"到 Tailscale 里面去，是因为 Tailscale 里有一个很好用的功能：子网路由。

## 子网路由

### 是什么

Tailscale 官网文档是这样讲的：

>  Subnet routers let you extend your Tailscale network (known as a tailnet) to include devices that don't or can't run the Tailscale client. They act as gateways between your tailnet and physical subnets, enabling secure access to legacy devices, entire networks, or services without installing Tailscale everywhere. This capability maintains Tailscale's security model while providing flexibility for complex network environments.

用人话就是说，一个子网路由器就是 Tailscale 网络里的一个网关，可以让 Tailscale 网络里的设备访问到子网路由器所设定的一个特定的子网，并且不会影响其他网络的路由。后面这一点就是它和 Tailscale 里的 exit nodes 的一个区别。

对于刚才的奇怪现象，显然就是在我的 Tailscale 网络里有一个子网路由器，它设定的路由的特定子网是 192.168.8.0/24 。

### 配置

#### 子网路由器

首先当然是安装 Tailscale 并且确保在这个 Tailscale 网络里。

接着需要启用 IP 转发，可以用下面的命令启用：

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

然后需要在 Tailscale 中指定可转发的子网，比如我这里可以这样子：

```bash
sudo tailscale set --advertise-routes=192.168.8.0/24
```

最后就是在 Tailscale 的管理页面允许一下就好了。

#### Tailscale 网络里的其他设备

为了能用上子网路由器所提供的路由功能，其他设备也需要做一个小配置：

```bash
sudo tailscale set --accept-routes
```

### 参考资料

1. [Tailscale文档](https://tailscale.com/kb/1019/subnets)