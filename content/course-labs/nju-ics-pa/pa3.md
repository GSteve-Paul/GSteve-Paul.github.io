---
title: PA3
tags:
  - RISC-V
  - 系统调用
  - 文件系统
---
虽然更复杂，需要思考的内容比PA2要更多（主要是因为我没有书去学习理论知识，在做这个实验之前都没听说过系统调用和中断/异常的知识），但是PA3的代码量相比PA2有所减少。

## 阶段1

### 最简单的操作系统

#### 什么是操作系统? (建议二周目思考)

操作系统是管理计算机资源的软件，它将各个进程和操作系统内核做隔离，并给予各个进程所需的资源。

### 穿越时空的旅程

#### 特殊的原因? (建议二周目思考)

不能。例如对于riscv32，若不在硬件中实现保存mepc，mstatus，mcause的操作，那么用户态程序在发起一个异常的时候就需要用户态程序自己去设定这些寄存器，但是为了处理器安全，用户态是不可以访问这些寄存器的，所以只能让硬件去实现。

#### 另一个UB

看`$AM_HOME/scripts/linker.ld`的内容，AM提供的栈的大小是0x8000字节。

#### 实现异常响应机制

在`cte_init()`中，模板代码用一个内嵌汇编设置了异常入口地址是`__am_asm_trap`，它定义在`$AM_HOME/am/src/riscv/nemu/trap.S`。

具体需要实现的新指令就是`ecall`：

```c title="$NEMU_HOME/src/isa/riscv32/inst.c"
INSTPAT("0000000 00000 00000 000 00000 11100 11", ecall, I,
		s->dnpc = isa_raise_intr(11, s->pc));
```

而异常响应的具体操作，即`isa_raise_intr`应当这样实现：

```c tiele="$NEMU_HOME/src/isa/riscv32/system/intr.c"
word_t isa_raise_intr(word_t NO, vaddr_t epc)
{
    /* TODO: Trigger an interrupt/exception with ``NO''.
     * Then return the address of the interrupt/exception vector.
     */
    csr(MEPC) = epc;
    csr(MCAUSE) = NO;
    return csr(MTVEC);
}
```

这里我的`csr`是用宏实现的，用了语句表达式等特性，具体如下：
```c title="$NEMU_HOME/src/isa/riscv32/local-include/reg.h"
#define MSTATUS 0x300
#define MTVEC 0x305
#define MEPC 0x341
#define MCAUSE 0x342
#define _csr(idx)                                                              \
    ({                                                                         \
        word_t *ret = NULL;                                                    \
        switch (idx)                                                           \
        {                                                                      \
        case MSTATUS:                                                          \
            ret = &(cpu.mstatus);                                              \
            break;                                                             \
        case MTVEC:                                                            \
            ret = &(cpu.mtvec);                                                \
            break;                                                             \
        case MEPC:                                                             \
            ret = &(cpu.mepc);                                                 \
            break;                                                             \
        case MCAUSE:                                                           \
            ret = &(cpu.mcause);                                               \
            break;                                                             \
        default:                                                               \
            panic("no such csr, wrong csr number is %d.", idx);                \
        }                                                                      \
        ret;                                                                   \
    })

#define csr(idx) (*_csr(idx))
```
#### 让DiffTest支持异常响应机制

这个任务就需要我们去好好读一读RISCV的手册了，也就是说我们的异常响应机制应该要和Spike做的一样。不过我研究了很久也没弄懂Spike的机制，所以先放着。

#### 异常号的保存

对于用户态的进程而言并不可以，因为用户态不能够直接操作mcause这个寄存器。不过可以让用户态的进程把异常号放在一个通用寄存器中，然后让异常入口处的软件程序把这个通用寄存器的值保存到mcause中去。

#### 对比异常处理与函数调用

首先是因为CTE不存在一个“被调用者保存寄存器”，所以要把大多数通用寄存器都存下来。而CTE的返回地址其实就是进入CTE之前的pc+4，所以要保存pc。处理器状态自然也要保存，因为特权级发生了变动。此外，保存异常号是为了能让异常处理程序知道关于这个异常的信息。最后地址空间是因为在PA4中会引入进程的概念，为了安全，异常调用有可能会切换地址空间而函数调用却不会。

#### 诡异的x86代码

以后再说吧。

#### 重新组织Context结构体

保存上下文的工作是软件做的，具体而言是在`$AM_HOME/am/src/riscv/nemu/trap.S`里面做的。下面的高亮代码就是其保存上下文的实现：

```asm {2-12} title="$AM_HOME/am/src/riscv/nemu/trap.S"
__am_asm_trap:
  addi sp, sp, -CONTEXT_SIZE

  MAP(REGS, PUSH)

  csrr t0, mcause
  csrr t1, mstatus
  csrr t2, mepc

  STORE t0, OFFSET_CAUSE(sp)
  STORE t1, OFFSET_STATUS(sp)
  STORE t2, OFFSET_EPC(sp)

  # set mstatus.MPRV to pass difftest
  li a0, (1 << 17)
  or t1, t1, a0
  csrw mstatus, t1

  mv a0, sp
  call __am_irq_handle

  LOAD t1, OFFSET_STATUS(sp)
  LOAD t2, OFFSET_EPC(sp)
  csrw mstatus, t1
  csrw mepc, t2

  MAP(REGS, POP)

  addi sp, sp, CONTEXT_SIZE
  mret
```

这里可以注意到文件后缀名是.S，代表的是这个汇编代码是会被预处理的。 而这里宏太多了，可以预处理一下再查看，通过下面的命令输出预处理后的结果。

```sh
gcc -E trap.S -o trap.s
```

得到以下的汇编程序：

```asm
__am_asm_trap:
  addi sp, sp, -((32 + 4) * 8)

  sd x1, (1 * 8)(sp); sd x3, (3 * 8)(sp); sd x4, (4 * 8)(sp); sd x5, (5 * 8)(sp); sd x6, (6 * 8)(sp); sd x7, (7 * 8)(sp); sd x8, (8 * 8)(sp); sd x9, (9 * 8)(sp); sd x10, (10 * 8)(sp); sd x11, (11 * 8)(sp); sd x12, (12 * 8)(sp); sd x13, (13 * 8)(sp); sd x14, (14 * 8)(sp); sd x15, (15 * 8)(sp); sd x16, (16 * 8)(sp); sd x17, (17 * 8)(sp); sd x18, (18 * 8)(sp); sd x19, (19 * 8)(sp); sd x20, (20 * 8)(sp); sd x21, (21 * 8)(sp); sd x22, (22 * 8)(sp); sd x23, (23 * 8)(sp); sd x24, (24 * 8)(sp); sd x25, (25 * 8)(sp); sd x26, (26 * 8)(sp); sd x27, (27 * 8)(sp); sd x28, (28 * 8)(sp); sd x29, (29 * 8)(sp); sd x30, (30 * 8)(sp); sd x31, (31 * 8)(sp);

  csrr t0, mcause
  csrr t1, mstatus
  csrr t2, mepc

  sd t0, ((32 + 0) * 8)(sp)
  sd t1, ((32 + 1) * 8)(sp)
  sd t2, ((32 + 2) * 8)(sp)

  # set mstatus.MPRV to pass difftest
  li a0, (1 << 17)
  or t1, t1, a0
  csrw mstatus, t1

  mv a0, sp
  call __am_irq_handle

  ld t1, ((32 + 1) * 8)(sp)
  ld t2, ((32 + 2) * 8)(sp)
  csrw mstatus, t1
  csrw mepc, t2

  ld x1, (1 * 8)(sp); ld x3, (3 * 8)(sp); ld x4, (4 * 8)(sp); ld x5, (5 * 8)(sp); ld x6, (6 * 8)(sp); ld x7, (7 * 8)(sp); ld x8, (8 * 8)(sp); ld x9, (9 * 8)(sp); ld x10, (10 * 8)(sp); ld x11, (11 * 8)(sp); ld x12, (12 * 8)(sp); ld x13, (13 * 8)(sp); ld x14, (14 * 8)(sp); ld x15, (15 * 8)(sp); ld x16, (16 * 8)(sp); ld x17, (17 * 8)(sp); ld x18, (18 * 8)(sp); ld x19, (19 * 8)(sp); ld x20, (20 * 8)(sp); ld x21, (21 * 8)(sp); ld x22, (22 * 8)(sp); ld x23, (23 * 8)(sp); ld x24, (24 * 8)(sp); ld x25, (25 * 8)(sp); ld x26, (26 * 8)(sp); ld x27, (27 * 8)(sp); ld x28, (28 * 8)(sp); ld x29, (29 * 8)(sp); ld x30, (30 * 8)(sp); ld x31, (31 * 8)(sp);

  addi sp, sp, ((32 + 4) * 8)
  mret
```

这就能很清楚的知道实现细节了：首先是在栈里预留`CONTEXT_SIZE`大小的空间用来存放上下文，然后是由低地址到高地址按次序存放通用寄存器、`mcause`、`mstatus`、`mepc`这几个寄存器。

所以`Context`结构体也应该这样摆放成员：

```c title="$AM_HOME/am/include/arch/riscv.h"
struct Context
{
    uintptr_t gpr[NR_REGS], mcause, mstatus, mepc;
    void *pdir;
};
```

不过注意到一个事实：因为有`pdir`，虽然暂时没用，但是我们的Context的实际大小也应该是$(32 + 4) \times 4$ 个字节，所以要修改`trap.S`的`CONTEXT_SIZE`宏。这很重要，因为我当时在做PA3的时候就没改，然后在PA4中因此造成的栈溢出的问题让我感到十分诡异，很难debug。

要实现的指令就是`csrrs`指令，看看手册轻松秒杀。

```c title="$NEMU_HOME/src/isa/riscv32/inst.c"
INSTPAT("??????? ????? ????? 010 ????? 11100 11", csrrs, I,
		word_t t = csr(imm);
		csr(imm) = t | src1; R(rd) = t;);
```

#### 给一些提示吧

好像也没这么难吧，我没有ICS课本一样瞪眼法瞪出来了。

#### 我乱改一通, 居然过了, 嘿嘿嘿

我可没有乱改，都是有依据的。

#### 必答题(需要在实验报告中回答) - 理解上下文结构体的前世今生

查看RISC-V手册就会知道这个`a0`通用寄存器就是用来放函数的第一个参数的。看看[[pa3#重新组织Context结构体|上面的汇编]]就会发现是`mv a0, sp`把参数给传给`__am_irq_hendle`这个函数了。为什么要传`sp`寄存器呢？由于我们把上下文从低地址到高地址相对于`sp`存的，所以`sp`实际上就是上下文结构体的首地址了，所以把它当作指针的值传过去也很合理吧。

这里面成员的赋值的位置，看看刚才的预处理后的结果就知道了，都是相对于`sp`的分别的一个偏移处。

这四部分的联系：

1. `riscv.h`指定了上下文结构体的定义，方便CTE去使用上下文。
2. `trap.S`负责异常发生后对之前的程序状态进行保存，然后调用`__am_irq_handle`进一步处理异常，然后再恢复之前的程序状态。
3. 上面的讲义文字把这一切的大纲给阐明了。
4. 实现的新指令让这些东西能在NEMU上作为一个个指令能执行得动。具体而言`ecall`让程序具有了跳到异常处理程序的能力，`csrrw`和`csrrs`使得可以读取、写入CSR，让保存、恢复CSR的状态成为可能。

#### 识别自陷事件

其实这里有点怪。因为从RISC-V的手册中没有任何一个异常叫作自陷异常，自然是没有对应的异常号的：

![[Screenshot from 2025-08-08 16-01-48.png]]

而我们这里都是在M模式引发的`ecall`，自然，异常号都是11。那我们只能猜测是`yield`实现中的设置`a7`为-1表示一个自陷事件。

```c title="$AM_HOME/am/src/riscv/nemu/cte.c"
void yield()
{
#ifdef __riscv_e
    asm volatile("li a5, -1; ecall");
#else
    asm volatile("li a7, -1; ecall");
#endif
}
```

所以我们这样实现`__am_irq_handle`：

```c
Context *__am_irq_handle(Context *c) 
{
	if (user_handler) 
    {
		Event ev = {0};
	    switch (c->mcause) 
	    {
		case 11:
			if (c->gpr[17] == -1) // $a7 == -1 
				ev.event = EVENT_YIELD;
			break;
		default:
			ev.event = EVENT_ERROR;
			break;
	    }
	    c = user_handler(ev, c);
	    assert(c != NULL);
	}
	return c;
}
```

这样，就能在注册的异常处理函数`user_handler`，即`simple_trap`中识别出来是`EVENT_YIELD`，进而输出一个`y`。

#### 从加4操作看CISC和RISC

CISC交给硬件做，可能会效率更高；RISC交给软件做，那么就需要在识别出`EVENT_YIELD`之后就把`Context`里的mepc修改了，也就是在`__am_irq_handle`里加一行就完事儿。

感觉得把x86的做一下才能锐评一下谁更合理。

#### 恢复上下文

实现这个指令，它可以用来恢复csr寄存器。其他软件上的东西什么也不用动，因为框架软件程序已经完成了上下文恢复的逻辑。然后就是`mret`指令，用来恢复一下`pc`：

```c title="$NEMU_HOME/src/isa/riscv32/inst.c"
INSTPAT("??????? ????? ????? 001 ????? 11100 11", csrrw, I,
		word_t t = csr(imm);
		csr(imm) = src1; R(rd) = t;);
INSTPAT("0011000 00010 00000 000 00000 11100 11", mret, R,
	s->dnpc = csr(MEPC););
```

#### 必答题(需要在实验报告中回答) - 理解穿越时空的旅程

`yield()` -> 在`a7`寄存器放入自陷的标志，并要求执行`ecall`指令-> NEMU根据之前设定的异常处理入口，让`pc`指到异常处理入口`__am_asm_trap`-> 保存通用寄存器和CSR到栈上->以刚才保存的上下文为参数，调用`__am_irq_handle`-> 根据上下文的信息识别事件类型，修改`mepc`，并调用注册好了的`simple_trap`->输出`y`-> 从栈上恢复CSR和通用寄存器->调用`mret`->NEMU根据`mepc`的实现，恢复`pc`到`mepc`-> 继续跑之前的程序。

#### mips32延迟槽和异常

不懂mips32😭

#### 实现etrace

这当然秒杀了~，在`ecall`的实现处输出一下异常号和异常所在的地址即可。

## 阶段2

### 用户程序和系统调用

为了了解系统调用的概念，现在开始做一些简单的操作系统相关的东西了！

#### 操作系统是个C程序

这个C程序，用不了之前我们写的C程序所用的操作系统的环境，只能用AM的环境。

#### 为Nanos-lite实现正确的事件分发

很简单，知道`init_irq`是用来注册事件处理程序，因此修改事件处理程序的代码即可：

```c title=nanos-lite/src/irq.c
static Context *do_event(Event e, Context *c)
{
    switch (e.event)
    {
    case EVENT_YIELD:
        printf("yield\n");
        break;
    default:
        panic("Unhandled event ID = %d", e.event);
    }

    return c;
}
```

#### Nanos-lite上的用户程序的链接位置

教程里说的查看的Makefile文件不对，对于riscv而言，应该看`$NAVY_HOME/scripts/riscv/common.mk`。

#### 堆和栈在哪里?

堆是程序被加载到内存时操作系统给它分配的，而堆是进程运行过程中动态找操作系统分配的空间。这些都不是ELF文件所能控制的，而是操作系统应该管的事情。

#### 如何识别不同格式的可执行文件?

很简单，ELF文件有一个魔数，`assert()`一下就知道了。

#### 冗余的属性?

阅读手册可知，`FileSiz`表示这个segment在文件映像中占有的字节数量，而`MemSiz`表示这个segment在内存映像中占有的字节数量。

对于`Type`属性为`PT_LOAD`的段，因为是要把这个段从文件搬到内存中去，所以应该让其在内存映像中的字节数量更多，才能搬得过去。并且也明确了文件映像的大小一定不能比内存映像大。至于为什么有时候内存映像比文件映像更大，可以看下这个[问题](https://stackoverflow.com/questions/27958743/difference-between-p-filesz-and-p-memsz-of-elf32-phdr)。

#### 为什么要清零?

手册中说内存映像中多出来的部分应当用0初始化，不过看了上面的问题后，可以猜测是`.bss`段的问题。根据定义`.bss`段要求在程序准备运行时应当初始化为0。

#### 实现loader

由于现在还没有引入虚拟内存，其实这个问题还挺简单的。就是把需要加载的程序段放入内存中对应的地方，然后设定程序入口地址即可。

```c title="nanos-lite/src/loader.c"
size_t ramdisk_read(void *buf, size_t offset, size_t len);

static uintptr_t loader(PCB *pcb, const char *filename) 
{
#if defined(__ISA_AM_NATIVE__)
#define EXPECT_TYPE EM_X86_64
#elif defined(__ISA_RISCV32__)
#define EXPECT_TYPE EM_RISCV
#else 
#error Unsupported ISA
#endif
	Elf_Ehdr ehdr;
	ramdisk_read(&ehdr, 0, sizeof(Elf_Ehdr));
	assert(ehdr.e_ident[EI_MAG0] == ELFMAG0);
	assert(ehdr.e_ident[EI_MAG1] == ELFMAG1);
	assert(ehdr.e_ident[EI_MAG2] == ELFMAG2);
	assert(ehdr.e_machine == EXPECT_TYPE);

	size_t phdr_offset = ehdr.e_phoff;
	size_t phdr_num = ehdr.e_phnum;
	Elf_Phdr phdr;
	for (size_t i = 0; i < phdr_num; i++) 
	{
		size_t off = phdr_offset + i * sizeof(Elf_Phdr);
		ramdisk_read(&phdr, off, sizeof(Elf_Phdr));
		if (phdr.p_type != PT_LOAD) continue;
		void *mem = (void *)(uintptr_t)phdr.p_vaddr;
		ramdisk_read(mem, phdr.p_offset, phdr.p_filesz);
		mem += phdr.p_filesz;
		memset(mem, 0, phdr.p_memsz - phdr.p_filesz);	
	}
    return (uintptr_t)ehdr.e_entry;
}
```

被触发的未处理事件，其实就是之后要讲的系统调用。

#### 检查ELF文件的魔数

已做，[[pa3#如何识别不同格式的可执行文件?|上面]]已说明。

#### 检测ELF文件的ISA类型

已做。ELF头里有个`e_machine`，表示这个ELF文件对应的架构。而这个宏定义在这里：

```make {2}
CFLAGS   += -O2 -MMD -Wall -Werror $(INCFLAGS) \
            -D__ISA__=\"$(ISA)\" -D__ISA_$(shell echo $(ISA) | tr a-z A-Z)__ \
            -D__ARCH__=$(ARCH) -D__ARCH_$(shell echo $(ARCH) | tr a-z A-Z | tr - _) \
            -D__PLATFORM__=$(PLATFORM) -D__PLATFORM_$(shell echo $(PLATFORM) | tr a-z A-Z | tr - _) \
            -DARCH_H=\"$(ARCH_H)\" \
            -fno-asynchronous-unwind-tables -fno-builtin -fno-stack-protector \
            -Wno-main -U_FORTIFY_SOURCE -fvisibility=hidden
```

#### 系统调用的必要性

是必须的。首先它破坏了操作系统的一层屏蔽和封装，导致批处理程序实质上运行在了AM上，能做任何它想做的事情，变得不安全。并且，批处理系统要求程序一个接一个完成，而如果没有系统调用，单个程序的结束只能靠`halt`来停机，这下整个NEMU都停机了，没办法运行下一个程序了。

#### 识别系统调用

查看`dummy.c`知道它是调用了一个`_syscall_`函数，然后找到它的定义在这里：

```c title="$NAVY_HOME/libs/libos/src/syscall.c"
intptr_t _syscall_(intptr_t type, intptr_t a0, intptr_t a1, intptr_t a2) {
    register intptr_t _gpr1 asm (GPR1) = type;
    register intptr_t _gpr2 asm (GPR2) = a0;
    register intptr_t _gpr3 asm (GPR3) = a1;
    register intptr_t _gpr4 asm (GPR4) = a2;
    register intptr_t ret asm (GPRx);
    asm volatile (SYSCALL : "=r" (ret) : "r"(_gpr1), "r"(_gpr2), "r"(_gpr3), "r"(_gpr4));
    return ret;
}
```

阅读这个C源文件的宏定义，可以知道对于riscv32而言，这个函数实际上就发起了一个`ecall`指令，并以`a7`作为系统调用的类型；`a0`，`a1`，`a2`作为系统调用的参数；`a0`作为系统调用的返回值。为了支持系统调用，我们首先需要改AM里的CTE，使其通过`a7`识别系统调用事件：

```c title="$AM_HOME/am/src/riscv/nemu/cte.c" {11-12}
Context *__am_irq_handle(Context *c)
{
    if (user_handler)
    {
        Event ev = {0};
        switch (c->mcause)
        {
        case 11:
            if (c->GPR1 == -1) // $a7 == -1
                ev.event = EVENT_YIELD;
            else if (c->GPR1 <= 19)
                ev.event = EVENT_SYSCALL;
            c->mepc += 4;
            break;
        default:
            ev.event = EVENT_ERROR;
            break;
        }

        c = user_handler(ev, c);
        assert(c != NULL);
    }

    return c;
}
```

而且CTE里面`GPR1`、`GPR2`等等宏定义也得改改，因为这些东西都是AM环境，OS会用到的。实际上，`GPR1`对应系统调用的类型；`GPR2`，`GPR3`，`GPR4`对应系统调用的参数；而`GPRx`对应系统调用的返回值。

至于为什么这里有`c->GPR1 <= 19`，这是因为这个头文件表明了所有可能的系统调用，最大的一个也才是19：

```c title="$NAVY_HOME/libs/libos/src/syscall.h"
#ifndef __SYSCALL_H__
#define __SYSCALL_H__

enum {
  SYS_exit,
  SYS_yield,
  SYS_open,
  SYS_read,
  SYS_write,
  SYS_kill,
  SYS_getpid,
  SYS_close,
  SYS_lseek,
  SYS_brk,
  SYS_fstat,
  SYS_time,
  SYS_signal,
  SYS_execve,
  SYS_fork,
  SYS_link,
  SYS_unlink,
  SYS_wait,
  SYS_times,
  SYS_gettimeofday
};

#endif
```

然后是修改OS中的事件处理模块，使其对于系统调用事件做出合适的反应：

```c title=nanos-lite/src/irq.c
static Context *do_event(Event e, Context *c)
{
    switch (e.event)
    {
    case EVENT_YIELD:
        printf("yield\n");
        break;
    case EVENT_SYSCALL:
        do_syscall(c);
        break;
    default:
        panic("Unhandled event ID = %d", e.event);
    }

    return c;
}
```

#### 实现SYS_yield系统调用

很简单，改改`do_syscall`的实现就好了。之前的`GPR?`宏都已经完成好了。

```c title="nanos-lite/src/syscall.c"
void do_syscall(Context *c)
{
    uintptr_t a[4];
    a[0] = c->GPR1;
    a[1] = c->GPR2;
    a[2] = c->GPR3;
    a[3] = c->GPR4;

	switch (a[0])
    {
    case SYS_yield:
        yield();
        c->GPRx = 0;
        break;
    default:
        panic("Unhandled syscall ID = %d", a[0]);
    }
}
```

关于为什么在发生`SYS_yield`后又会发生一个`SYS_exit`，可以了解一个navy-app的执行全过程。首先从程序入口`_start`开始，这会跳到`call_main`去。

```c title="$NAVY_HOME/libs/libos/src/crt0/crt0.c"
int main(int argc, char *argv[], char *envp[]);
extern char **environ;
void call_main(uintptr_t *args) {
  char *empty[] =  {NULL };
  environ = empty;
  exit(main(0, empty, empty));
  assert(0);
}
```

这个`call_main`会调用用户程序中的`main`函数，然后以这个`main`函数的返回值作为参数调用`exit`函数，而这个`exit`最终会调用`SYS_exit`系统调用。

#### 实现SYS_exit系统调用

很简单啊，改一下`do_syscall`的实现就好了。

```c title="nanos-lite/src/syscall.c"
void do_syscall(Context *c)
{
    uintptr_t a[4];
    a[0] = c->GPR1;
    a[1] = c->GPR2;
    a[2] = c->GPR3;
    a[3] = c->GPR4;

	switch (a[0])
    {
    case SYS_yield:
        yield();
        c->GPRx = 0;
        break;
    case SYS_exit:
	    halt(a[1]);
	    break;
    default:
        panic("Unhandled syscall ID = %d", a[0]);
    }
}
```

#### RISC-V系统调用号的传递

也许是因为`a0`在函数调用中往往被当作是第一个参数和返回值，因此就被当作是系统调用的第一个参数了。

#### 实现strace

实现`strace`是一个简单的任务，但是要做的漂亮有点麻烦。只需要在`do_syscall`里添加一点代码，记录系统调用号、参数和返回值就可以了。

为了让它能打印系统调用的名字，我特地做了这么个数组：

```c
const char *syscall_names[] = {"SYS_exit",   "SYS_yield",       "SYS_open",
                               "SYS_read",   "SYS_write",       "SYS_kill",
                               "SYS_getpid", "SYS_close",       "SYS_lseek",
                               "SYS_brk",    "SYS_fstat",       "SYS_time",
                               "SYS_signal", "SYS_execve",      "SYS_fork",
                               "SYS_link",   "SYS_unlink",      "SYS_wait",
                               "SYS_times",  "SYS_gettimeofday"};
```

#### 在Nanos-lite上运行Hello world

实现`write()`也并不困难，首先在`libos`库里修改一下`_write`的实现，这里的具体接口要查手册：

```c title="$NAVY_HOME/libs/libos/src/syscall.c"
int _write(int fd, void *buf, size_t count) 
{
	_syscall_(SYS_write, fd, (intptr_t)buf, count);
    return 0;
}
```

因为现在的`SYS_write`只需要输出到`stdout`或者是`stderr`就可以了，所以简单实现一下，将`buf`里的各个字符输出即可。注意它的返回值是实际写出去的字节数。

```c title="nanos-lite/src/syscall.c"
static int sys_write(Context *c, uintptr_t *a) 
{
	int fd = a[1];
	uint8_t *buf = (void *)a[2];
	size_t count = a[3];
	int ret = 0;
	switch (fd) 
	{
	case 1:
	case 2:
		for (size_t i = 0; i < count; i++) 
		{
			putch(buf[i]);
			ret++;
		}
		break;
	default:
		panic("Invalid fd = %d\n", fd);
	}
	return ret;
}

void do_syscall(Context *c)
{
    uintptr_t a[4];
    a[0] = c->GPR1;
    a[1] = c->GPR2;
    a[2] = c->GPR3;
    a[3] = c->GPR4;

	switch (a[0])
    {
    case SYS_yield:
        yield();
        c->GPRx = 0;
        break;
    case SYS_exit:
	    halt(a[1]);
	    break;
	case SYS_write:
		c->GPRx = sys_write(c, a);
		break;
    default:
        panic("Unhandled syscall ID = %d", a[0]);
    }
}
```

#### 实现堆区管理

教程里已经写的很详细了。关于`_end`的问题在[[pa2#理解volatile关键字|之前]]已经了解过了。不过这里可以简单地详细讲一下：这个`_end`会在链接后出现在ELF文件的符号表中，并不是`$NAVY_HOME/libs/libos/src/syscall.c`编译出来的`syscall.o`会生成的符号，所以要用`extern`声明变量`end`。

```c title="$NAVY_HOME/libs/libos/src/syscall.c"
extern uintptr_t end;
static uintptr_t brk_offset = 0;
void *_sbrk(intptr_t increment) 
{
	uintptr_t old_brk = (uintptr_t)&end + brk_offset;
	int ret = _syscall_(SYS_brk, old_brk + increment, 0, 0);
	if (ret)
		return (void *)-1;
	// OK
	brk_offset += increment;
	return (void *)old_brk;
}
```

在OS上的实现先简单处理一下，实际上就是随便`sbrk`：

```c title="nanos-lite/src/syscall.c"
static int sys_brk(Context *c, uintptr_t *a)
{
    void *addr __attribute__((unused)) = (void *)a[1];
    return 0;
}
```

#### 缓冲区与系统调用开销

之后再实验一下。

#### printf和换行

其实也就是这一小段代码：

```c title="$NAVY_HOME/libs/libc/src/stdio/wbuf.c"
if (++n == fp->_bf._size || (fp->_flags & __SLBF && c == '\n'))
	if (_fflush_r (ptr, fp))
	    return EOF;
```

不过更加应该让人关注的是，要记住`fread`和`fwrite`不会立即处理，而是放缓冲区里把多次化一次系统调用处理。

#### 必答题(需要在实验报告中回答) - hello程序是什么, 它从而何来, 要到哪里去

##### hello程序一开始在哪里?

hello程序在编译后一开始人为地放在了`build/ramdisk.img`的磁盘映像中。

##### 它是怎么出现内存中的?

OS启动后通过`naive_uload`去读取磁盘映像中的ELF文件，将ELF文件的需要加载到内存里的program segment放在内存中的指定位置。

##### 为什么会出现在目前的内存位置？

首先，在链接时`LDFLAGS`规定了`-Ttext-segment $(LNK_ADDR)`，其中`$(LNK_ADDR)`为0x83000000，这代表着被链接到了0x83000000。因此在ELF文件中地址就长这样了。然后我们也没有引入虚拟内存，所以ELF文件里被链接到哪儿就载入到内存的哪儿。

##### 它的第一条指令在哪里?

观察到它的程序入口在0x830000bc，实际上就是_start，默认的入口符号名。

##### 究竟是怎么执行到它的第一条指令的?

在`naive_uload`的`loader`结束后，拿到了程序的入口，然后直接把它强转成了一个没有参数，返回值为void的函数指针然后去调用了。

##### hello程序在不断地打印字符串, 每一个字符又是经历了什么才会最终出现在终端上?

hello程序调用`printf`->OS上的libc->系统调用`write()`->指令`ecall`，并给对应寄存器附上参数->（...异常处理程序到保存上下文的流程...)->调用事件处理程序->识别事件类型->调用OS给的处理程序->识别为系统调用->识别为`SYS_write`系统调用->读保存在上下文的寄存器参数，遍历`buf`并利用AM的`putch`打印字符出去->访问了串口对应的内存地址->一个访存指令->NEMU解释其为访问设备，并调用设备的回调函数进行处理->调用了本Linux机的`putc`，输出到了终端上。

#### 支持多个ELF的ftrace

这个东西之后再做吧。

## 阶段3

### 文件系统