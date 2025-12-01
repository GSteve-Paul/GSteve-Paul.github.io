---
title: Nginx学习入门
date: 2023-09-13
tags:
  - 蓝旭2023秋季学习
---
# 概念

Nginx是一个开源的Web服务器，同时Nginx也提供了反向代理和负载均衡的功能。
Nginx通常作为负载均衡器暴露在外网接受用户请求，同时也使用其反向代理的功能，将用户的请求转发到实际提供服务的内网服务器。 

一般来说，如果需要高性能的资源读取，那就去用Nginx吧！

# 安装 Nginx

网页：http://nginx.org/en/download.html

解压后在根目录下打开cmd，输入start nginx

如果访问localhost:80能出现有关Nginx的网页，说明就配置成功了。

# Nginx 配置文件

考虑到刚才访问localhost:80能弹出来如此的网页，考察根目录下conf/nginx.conf文件，找到这段：

```properties
server {
        listen       80;
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
            root   html;
            index  index.html index.htm;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

        # proxy the PHP scripts to Apache listening on 127.0.0.1:80
        #
        #location ~ \.php$ {
        #    proxy_pass   http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        #location ~ \.php$ {
        #    root           html;
        #    fastcgi_pass   127.0.0.1:9000;
        #    fastcgi_index  index.php;
        #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
        #    include        fastcgi_params;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #    deny  all;
        #}
    }
```

发现其实下面直接有一个例子可供修改：

```properties
# HTTPS server
    #
    #server {
    #    listen       443 ssl;
    #    server_name  localhost;

    #    ssl_certificate      cert.pem;
    #    ssl_certificate_key  cert.key;

    #    ssl_session_cache    shared:SSL:1m;
    #    ssl_session_timeout  5m;

    #    ssl_ciphers  HIGH:!aNULL:!MD5;
    #    ssl_prefer_server_ciphers  on;

    #    location / {
    #        root   html;
    #        index  index.html index.htm;
    #    }
    #}
```

细节配置：https://www.yuque.com/deepwindshenlan/ltswqg/yn79u0a7shwc9diy

配置修改后可以用命令`nginx -t` 测试配置是否合法
然后再用命令`nginx -s reload`重新加载Nginx

# 配置

## 正向代理

如果把局域网外的Internet想象成一个巨大的资源库，则局域网中的客户端要访问Internet，则需要通过代理服务器来访问，这种代理服务就称为正向代理（也就是大家常说的，通过正向代理进行上网功能）


![](https://file.stevepaul.cc/85d82da0ed814dc3a0d148023b9fb4c3.png)

配置server:

```properties
server {
        listen       478;
        server_name  localhost;

        location / {
            proxy_pass http://localhost:9999;
        }
    }
```

其含义即为如果有客户端访问本机的localhost:478，则自动将其转换到http://localhost:9999

如果需要处理域名，也可以运用resolver

## 反向代理

其实客户端对代理是无感知的，因为客户端不需要任何配置就可以访问，我们只需要将请求发送到反向代理服务器，由反向代理服务器去选择目标服务器获取数据后，在返回给客户端，此时反向代理服务器和目标服务器对外就是一个服务器，暴露的是代理服务器地址，隐藏了真实服务器 IP 地址。

![](https://file.stevepaul.cc/d7389090199744f9931e08d0b64f5a18.png)

实际上配置方法和正向代理完全一样，只是逻辑有所不同而已

此处的意思为：nginx 反向代理服务监听 192.168.17.129的80端口，如果有请求过来，则转到proxy_pass配置的对应服务器上，仅此而已。