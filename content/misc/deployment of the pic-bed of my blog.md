---
title: 我的博客图床部署
date: 2025-12-02
tags:
  - 部署
---
最近几天我在 Cryptominisat 的基础上尝试添加 ANF 模块和一些策略，总体来说改起来是比较麻烦的。一方面原求解器代码比较冗长、复杂；另一方面要添加的策略在我看来实在是太重，造成时间上、空间上的开销比较大，需要改动的地方也很多。这样的工作确实是繁重且累人的。所以我忙里偷闲，想要优化一下我的博客网站，于是就从我的附件管理部分入手了。

在之前，我的附件其实就挂在 content 目录下的一个特殊的 data 目录下。这样做的好处显而易见，它特别方便，也和 Obsidian 配合得很好；坏处就是过于冗杂，和 Quartz 博客框架耦合在一起，之后迁移起来比较麻烦。因为我之后打算把博客从 Quartz 迁移到其他框架下，所以我便打算用图床对我的附件进行管理。

在这里，我采用阿里云 OSS 作为图床仓库，并使用 PicGo 作为图床管理工具。

## OSS 

### 购买 OSS 服务

阿里云有一个 OSS 服务免费使用 3 个月的活动，我就是这样白嫖的三个月，之后再打算进行付费购买。

### 配置 OSS 服务

刚才所购买只是服务，要对资源进行管理应该创建一个 Bucket。这个 Bucket 才是一个支持文件读写的仓库。

如果你和我一样，都是白嫖的三个月，你也许就会找到如图所示的资源包列表：

![image.png](https://file.stevepaul.cc/20251202165826141.png)

需要注意的是，下行流量包（中国内地）其实就是公网流出的额度，这玩意儿一个月 2 G 对于图床来说还是挺有可能不够用的。但考虑到内网流出的额度就是完全免费的，所以之后我将会用一个之前我买过 ECS 做代理。

#### 配置访问权限

考虑图床，也就是这个存储桶的用法：

1. 博主（我）需要能上传文件到里面，同时也可以查看里面的所有文件；此外其他的功能也应该应有尽有。
2. 访客应该只能读取其中的文件。

所以我们应该在 Bucket 授权策略中添加对应的授权策略。这里十分建议创建一个 RAM 用户作为授权用户完全控制该存储桶。

上面提到用 ECS 作为代理，不让公网上的访客直接访问存储桶，所以还应该添加一个只读的策略，规定 IP 源只能是这个 ECS 服务器。（注意：既然是利用 ECS 和 OSS 处于同一个内网下的这么一个事实，那么这个 IP 自然应该填 ECS 的内网 IP）。我的配置如下：

![image.png](https://file.stevepaul.cc/20251202172411078.png)

## ECS 

在这里我们采用 Nginx 进行代理：

```nginx 
server {  
       listen 443 ssl;  
       ssl_certificate /etc/letsencrypt/live/file.stevepaul.cc/cert.pem;  
       ssl_certificate_key /etc/letsencrypt/live/file.stevepaul.cc/privkey.pem;  
       server_name file.stevepaul.cc;  
       location / {  
               proxy_pass Bucket的内网访问URL;   
       }  
}  
  
server {  
       listen 80;  
       server_name file.stevepaul.cc;  
       return 301 https://file.stevepaul.cc$request_uri;  
}
```

这样，我们访问 https://file.stevepaul.cc/xxx 就可以访问到图床（存储桶）的 xxx 文件了。

关于 ECS 服务器购买、域名备案和SSL 证书之类的问题，就不在本篇的讨论范围之内了。

## PicGo

PicGo 实际上就是拥有该存储桶完全控制权限的用户。还记得创建 RAM 用户时生成的用户信息嘛？把 RAM 用户的 KeyId 和 KeySecret 配置到 PicGo 的阿里云 OSS 图床设置里面，再用阿里云上 Bucket 的外网访问 URL 填写 PicGo 里的 Bucket 和存储区域，就可以利用 PicGo 上传附件了。

上传附件后 PicGo 会给你附件的外链，你会发现这个外链可能还是 OSS 的域名，而你当然希望返回的是关联到 ECS 的域名。这可以通过在 PicGo 中设定自定义域名进行修改——比如我就会设定为 https://file.stevepaul.cc 。

## Obsidian

### 自动上传插件

从社区安装 Image auto upload插件，并如图所示进行配置。注意，你应当确保 PicGo 设置中的 Server 是默认启用着的。

![image.png](https://file.stevepaul.cc/20251202175559310.png)

这个插件可以在你粘贴图片的时候自动帮你上传，并把 PicGo 返回的图片外链自动插入到 Obsidian 中。很方便吧？

### 让 Obsidian 正确预览

也正是因为现在附件都是外链，所以不能使用 Obsidian 中的 `![[]]` 语法了。这就是 Obsidian 中一切不幸的开端。

#### 配置 Nginx

如果你直接把上传的图片链接以标准 Markdown 图片的语法插入到 Obsidian 中，Obsidian 将无法正常预览。这是因为这个 OSS 外链会设置HTTP 的 `Content-Disposition` 响应头为 `attachment`，进而强制让浏览器把附件下载下来而不是放在网页中。所以我们需要对之前的 Nginx 配置做一点点小修改：

```nginx {8-9}
server {  
       listen 443 ssl;  
       ssl_certificate /etc/letsencrypt/live/file.stevepaul.cc/cert.pem;  
       ssl_certificate_key /etc/letsencrypt/live/file.stevepaul.cc/privkey.pem;  
       server_name file.stevepaul.cc;  
       location / {  
               proxy_pass https://stevepaul-blog.oss-cn-chengdu-internal.aliyuncs.com;  
               proxy_hide_header Content-Disposition;  
               add_header Content-Disposition inline;  
       }  
}  
  
server {  
       listen 80;  
       server_name file.stevepaul.cc;  
       return 301 https://file.stevepaul.cc$request_uri;  
}
```

#### 修改附件表示方式

- 图片：`![](图片外链)`
- 音频：`<p><audio controls="" src="音频外链"></audio></p>`
- 视频：`<p><video controls="" src="视频外链"></video></p>`

按上述表示方式，就可以既让 Obsidian 正确预览，也让博客网站正确渲染。

如果你错误采用 `![[外部链接]]` 的形式，一方面它在 Obsidian 中无法正确预览，另一方面音频内容会被 Quartz 错误地放在 `<video></video>` 标签里面，导致这个块显示出来是个没有视频的视频块🤣