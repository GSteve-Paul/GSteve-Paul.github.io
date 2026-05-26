---
title: printf中的"\n"与缓冲区的刷新
date: 2025-11-09
tags:
---
这周周四跑实验的时候遇到一个问题。我明明在 `printf()` 输出的字符串末尾添加了 `\n`，却没给输出出去，换句话说，就是没有刷新缓冲区。

---

## 问题代码

```bash {5}
exec 3>&1
exec > "${RUN_LOG}" 2>&1

set -x
MAX_ID=$(timeout 10 "${SOLVER_BIN}" -i "${INSTANCE_FILE}" -x | ${GET_MAX_ID} || true) 
REAL_SOLVER_BIN="${SOLVER_BIN}_${MAX_ID}"
time timeout "${TIMEOUT}" "${REAL_SOLVER_BIN}" -i "${INSTANCE_FILE}" -x || true
set +x

cat "${RUN_LOG}" | "${ANALYZER}" >&3
```

上面是一段丑陋的 bash 脚本，其中高亮行会启动求解器，并收集它在 10 秒钟之内所输出的内容。如果我直接把它放在 shell 里跑，那么它确实是会立马输出一些东西出来的。但是在这里，它输出不出来。

## 问题原因

输出不出来的表面原因其实有两个，在这里我分开地进行解释。

### 输出重定向到了一个普通文件

注意代码中的 `exec > "${RUN_LOG}"`，它导致之后的输出会被重定向。根据 [cpp reference](https://en.cppreference.com/w/cpp/io/c/std_streams.html) 中的说法，stdout 流有可能会变成 fully buffered 而非一般形式上的 line buffered，也就是说，它不会因为 `\n` 刷新缓冲区了。

所以这里就表明真正做缓冲的是流本身，跟 `printf()` 没什么关系。去观察 `setvbuf` 的 API 之后也会明白，其实它的缓冲模式也只是和具体哪一个流相关罢了。

下面给出一个小例子：

```c title="main.c"
#include <stdio.h>

int main() {
	printf("Hello World!\n");
	while (1) ;
	return 0;
}
```

```bash title="run.sh"
#!/usr/bin/bash

exec > "./log"

timeout 10 ./main
```

运行这个脚本，果不其然，log 文件中并没有 "Hello World!"。

### 管道

管道何尝不也是一种重定向呢？左边的进程的 stdout 被重定向到了管道的写端，而右边的进程的 stdin 被重定向到了管道的读端。

在这里我们沿用上面小例子里的 main.c 文件。对 bash 进行一个改动：

```bash title="run.sh"
#!/usr/bin/bash

timeout 10 ./main | xargs echo
```

运行这个脚本，果不其然，`echo` 没有输出 "Hello World"。

## 管道+重定向

根据上面的解释，那肯定是无法正常地按 `\n` 刷新缓冲区了。

## 解决方案

既然自动挡（`\n`）开不了了，那么就手动挡  `fflush()` 就行了。

```c title="main.c"
#include <stdio.h>

int main() {
	printf("Hello World!\n");
	fflush(stdout);
	while (1) ;
	return 0;
}
```

此外，我们也可以通过 `setvbuf()` 设置缓冲模式，比如我这里强行设置为了 line buffering，就可以成功刷新缓冲区了。

```c title="main.c"
#include <stdio.h>
#include <stdlib.h>

int main() {
	setvbuf(stdout, NULL, _IOLBF, 4096);
	printf("Hello World!\n");
	while (1) ;
	return 0;
} 
```