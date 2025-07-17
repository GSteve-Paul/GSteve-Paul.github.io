---
title: PA1
tags:
  - NJU-ICS-PA
  - RISC-V
---
PA1中会指导我们补充NEMU框架，进而用C语言构建出一个最基本的计算机。

## 在开始愉快的PA之旅之前

### NEMU是什么？

首先当然是在红白机模拟器里玩一玩俄罗斯方块。
![俄罗斯方块游戏截图](2025-07-17-20-17-57.png)

孩子，我其实就是个用软件模拟出来的硬件。

### 选择你的角色

我当然是选择了看上去最容易的RISCV32，我也并不是一边做实验一边写心得而是过了5个月才写的心得，~~所以相当于二刷了~~。

### 还等什么呢？

启动，希望我的心得不会烂尾。

## 开天辟地的篇章

### 最简单的计算机

> **计算机可以没有寄存器吗? (建议二周目思考)**

能。因为我们完全可以试着用内存模拟寄存器的操作。这样会把硬件提供的编程模型（见The RISC-V Instruction Set Manual Volume I的2.1节）中的寄存器都消灭掉，取而代之的是内存中的特殊内存块，以及相对应的专门操作这些特殊内存块的特殊指令。

### 重新认识程序：程序是个状态机

> **从状态机视角理解程序运行**

人脑模拟图灵机即可。这是为了引入“程序是一个状态机”这个思想。

## RTFSC

### 框架代码初探

> **需要多费口舌吗?**

当然是从`main`函数开始看啦。不过程序不是从`main`函数作为最开始的……不然`main`函数的参数又得从哪里来呢？这个问题我之后再说吧。

### 配置系统和项目构建

可以用`make -nB`让`make`程序以"只输出命令但不执行"的方式强制构建目标。

由于我用`clangd`作为`LSP`，所以我利用`bear`去产生`compile_commands.json`，即:
```bash
bear --output ./compile_commands.json -- make
```
进而辅助`LSP`分析项目。

### 准备第一个客户程序

>  **kconfig生成的宏与条件编译**

对于kconfig里的宏，需要这些宏的C源文件都会直接或者间接的`#include <generated/autoconf.h>`

下面详细分析一下这些奇怪的宏。我们就拿`MUXDEF(CONFIG_TRACE, "ON", "OFF")`举个例子，假设已经有`#define CONFIG_TRACE 1`，分析它的展开过程：

1. `MUXDEF(CONFIG_TRACE, "ON", "OFF")`
2. `MUX_MACRO_PROPERTY(__P_DEF_, 1, "ON", "OFF")`
3. `MUX_WITH_COMMA(concat(__P_DEF_, 1), "ON", "OFF")`
4. `MUX_WITH_COMMA(__P_DEF_1, "ON", "OFF")`
5. `CHOOSE2nd(X, "ON", "OFF")`
6. `"ON"`

而假设没有`#define CONFIG_TRACE 1`，其展开过程为：

1. `MUXDEF(CONFIG_TRACE, "ON", "OFF")`
2. `MUX_MACRO_PROPERTY(__P_DEF_, CONFIG_TRACE, "ON", "OFF")`
3. `MUX_WITH_COMMA(concat(__P_DEF_, CONFIG_TRACE), "ON", "OFF")`
4. `MUX_WITH_COMMA(__P_DEF_CONFIG_TRACE, "ON", "OFF")`
5. `CHOOSE2nd(__P_DEF_CONFIG_TRACE "ON", "OFF")`
6. `"OFF"`

这里有一个关于宏的知识的[文章](https://zhuanlan.zhihu.com/p/60998127)。

> **为什么全部都是函数?**

分离模拟器里的各个部件，尽量解耦。

> **参数的处理过程**

首先通过阅读C源代码可以知道这些参数都是从`main`函数传递过来的，所以就要找到程序在哪里被启动的。

从后文可以知道，在`nemu`目录下`make run`即可启动程序，所以通过阅读Makefile文件就能知道参数是从哪里来的了。
```make {1-2} title="$NEMU_HOME/scripts/native.mk" showLineNumbers{27} 
override ARGS ?= --log=$(BUILD_DIR)/nemu-log.txt 
override ARGS += $(ARGS_DIFF)

# Command to execute NEMU
IMG ?=
NEMU_EXEC := $(BINARY) $(ARGS) $(IMG)

run-env: $(BINARY) $(DIFF_REF_SO)

run: run-env
	$(call git_commit, "run NEMU")
	$(NEMU_EXEC)
```

### 运行第一个客户程序

使用`make run`启动NEMU模拟器：
```
[src/utils/log.c:30 init_log] Log is written to /home/lijn/ics2024/nemu/build/nemu-log.txt
[src/memory/paddr.c:50 init_mem] physical memory area [0x80000000, 0x87ffffff]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'serial' at [0xa00003f8, 0xa00003ff]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'rtc' at [0xa0000048, 0xa000004f]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'vgactl' at [0xa0000100, 0xa0000107]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'vmem' at [0xa1000000, 0xa10752ff]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'keyboard' at [0xa0000060, 0xa0000063]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'audio' at [0xa0000200, 0xa0000217]
[src/device/io/mmio.c:50 add_mmio_map] Add mmio map 'audio-sbuf' at [0xa1200000, 0xa120ffff]
[src/monitor/monitor.c:51 load_img] No image is given. Use the default build-in image.
[src/monitor/monitor.c:29 welcome] Trace: OFF
[src/monitor/monitor.c:33 welcome] Build time: 00:03:23, Jul 18 2025
Welcome to riscv32-NEMU!
For help, type "help"
(nemu) c
[src/cpu/cpu-exec.c:133 cpu_exec] nemu: HIT GOOD TRAP at pc = 0x8000000c
[src/cpu/cpu-exec.c:100 statistic] host time spent = 1 us
[src/cpu/cpu-exec.c:101 statistic] total guest instructions = 4
[src/cpu/cpu-exec.c:102 statistic] simulation frequency = 4,000,000 inst/s
(nemu) q
```

> **究竟要执行多久？**

`cpu_exec`的函数原型长这个样子：
```c
void cpu_exec(uint64_t n);
```
这确保了这个`-1`会被认为是一个无符号数，也就是`uint64_t`下的最大的无符号数，结合到目前CPU的执行速度，这会让它跑尽可能长的时间。

> **潜在的威胁（建议二周目思考）**

可以看下stackoverflow上的[这个问题](https://stackoverflow.com/questions/50605/signed-to-unsigned-conversion-in-c-is-it-always-safe)的高赞回答，引用的就是[C99 Standard文档](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf)的内容。

> **谁来指示程序的结束?**

通过后文知识可得，运行完`main`函数后一定会进行一个系统调用`sys_exit`以结束进程。