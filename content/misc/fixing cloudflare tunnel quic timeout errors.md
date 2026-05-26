---
date: 2026-02-28
title: 解决Cloudflare Tunnel无法用QUIC协议创建隧道的问题
---
最近突发奇想，想部署 ZeroClaw 当一个猫娘助手。我把这个 ZeroClaw 部署到了我的阿里云 ECS 服务器上，想要用 Cloudflare 的 Tunnel 功能让我从远程也能相对安全地连接到 ZeroClaw 服务。

根据 Cloudflare 的文档，需要在我的 ECS 服务器上安装 cloudflared，这个软件会建立向外的连接（也就是说不用修改 ECS 的网络入方向规则）以建立一个隧道。默认的协议是 QUIC 协议。

问题就出在隧道建立的过程上，在国内往往会出现这样的报错信息：

```
2026-02-28T03:00:59Z WRN Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2 event=0 ip=198.41.200.193  
2026-02-28T03:00:59Z INF Retrying connection in up to 2s connIndex=2 event=0 ip=198.41.200.193  
2026-02-28T03:01:00Z WRN Connection terminated error="failed to dial to edge with quic: timeout: no recent network activity" connIndex=2  
2026-02-28T03:01:11Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveP256] connIndex=2 event=0 ip=198.41.200.53  
2026-02-28T03:01:11Z INF Registered tunnel connection connIndex=2 connection=85e74ffe-9639-4f75-a8e5-22e737a9e6f9 event=0 ip=198.41.200.53 location=lax06 protocol=quic
```

而为什么 QUIC 协议就没办法建立隧道呢？可以看下维基百科对 QUIC 的说法：

>  QUIC improves performance of connection-oriented [web applications](https://en.wikipedia.org/wiki/Web_application "Web application") that previously relied on [Transmission Control Protocol](https://en.wikipedia.org/wiki/Transmission_Control_Protocol "Transmission Control Protocol") (TCP).[[2]](https://en.wikipedia.org/wiki/QUIC#cite_note-LWN-2)[[9]](https://en.wikipedia.org/wiki/QUIC#cite_note-TechCrunch-9) It does this by establishing a number of [multiplexed](https://en.wikipedia.org/wiki/Multiplexed "Multiplexed") connections between two endpoints using [User Datagram Protocol](https://en.wikipedia.org/wiki/User_Datagram_Protocol "User Datagram Protocol") (UDP), and it is designed to obsolete TCP at the transport layer for many applications.

就正因为 QUIC 协议往往是由 UDP 驱动的，而国内网络环境对 UDP 的支持又很差，就很容易断连。而恰好Cloudflare 实际上提供了另一种建立隧道的方式，即 http/2 的方式。我们只需要动手在 Cloudflare 的启动参数添加 `--protocol http2` 就好了。

而 ZeroClaw 上面似乎也没办法让我们自定义启动 cloudflared 的参数，所以我们只好自己手动修改成如下形式并启动 cloudflared 服务。

```
[Unit]  
Description=cloudflared  
After=network-online.target  
Wants=network-online.target  
  
[Service]  
TimeoutStartSec=15  
Type=notify  
ExecStart=/usr/bin/cloudflared --no-autoupdate tunnel run --protocol http2 --token <TOKEN> 
Restart=on-failure  
RestartSec=5s  
  
[Install]  
WantedBy=multi-user.target
```