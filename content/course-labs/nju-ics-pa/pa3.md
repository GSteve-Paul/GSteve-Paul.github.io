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

文件本质上就是字节序列。我们的文件系统就是为了管理文件到ramdisk中的位置的映射并为上层用户程序提供文件操作的接口。

不过这里的文件是抽象的，并不一定每个文件都有“名字”，所以用文件描述符表示一个正在打开的文件，让OS来维护文件描述符到具体文件的映射。

#### 文件偏移量和用户程序

如果偏移量放在了文件记录表中， 那么对于每一个进程而言它们所对应的文件系统的状态就是一样的。这就意味着无法让两个进程并发地读同一个文件，因为显然这需要这个文件为不同的进程提供不同的偏移量。

#### 让loader使用文件

现在引入了好几个系统调用，其中`lseek`其实有点说法。因为`lseek`可以直接指定一个文件的`offset`，这就意味着它所操作的文件（字节序列）一定要有“位置”的概念。像磁盘（块设备）中的文件就是有位置的概念的，它可以被`lseek`；但是像键盘（字符设备）输入、串口（字符设备）输出就是没有的，不能被`lseek`。因此需要在`FInfo`结构体里添加一个字段表示这个文件是在块设备上还是字符设备上。

```c title="nanos-lite/include/fs.h"
typedef size_t (*ReadFn) (void *buf, size_t offset, size_t len);
typedef size_t (*WriteFn) (const void *buf, size_t offset, size_t len);

typedef struct
{
    char *name;
    size_t size;
    size_t disk_offset;
    size_t open_offset;
    int not_support_lseek;
    ReadFn read;
    WriteFn write;
} Finfo;
```

```c title="nanos-lite/src/fs.c"
Finfo file_table[] __attribute__((used)) = {
    [FD_STDIN] = {"stdin", 0, 0, 0, 1, invalid_read, invalid_write},
    [FD_STDOUT] = {"stdout", 0, 0, 0, 1, invalid_read, serial_write},
    [FD_STDERR] = {"stderr", 0, 0, 0, 1, invalid_read, serial_write},
#include "files.h"
};

int fs_open(const char *pathname, int flags, int mode)
{
    size_t file_cnt = sizeof(file_table) / sizeof(Finfo);
    for (int i = 0; i < file_cnt; i++)
    {
        if (strcmp(file_table[i].name, pathname) == 0)
        {
            file_table[i].open_offset = 0;
            return i;
        }
    }
    panic("Invalid pathname: %s\n", pathname);
}

size_t fs_read(int fd, void *buf, size_t len)
{
    Finfo *fi = file_table + fd;
    ReadFn read_fn = fi->read;
    if (!read_fn)
        read_fn = &ramdisk_read;

    if (!fi->not_support_lseek)
        len = min(len, fi->size - fi->open_offset);
    size_t ret = read_fn(buf, fi->disk_offset + fi->open_offset, len);
    if (!fi->not_support_lseek)
        fi->open_offset += ret;
    return ret;
}

size_t fs_lseek(int fd, size_t offset, int whence)
{
    size_t *fi_open_offset = &(file_table[fd].open_offset);
    switch (whence)
    {
    case SEEK_SET:
        *fi_open_offset = offset;
        break;
    case SEEK_CUR:
        *fi_open_offset += offset;
        break;
    case SEEK_END:
        *fi_open_offset = file_table[fd].size + offset;
        break;
    default:
        panic("Undefined whence = %d\n", whence);
    }
    return *fi_open_offset;
}

int fs_close(int fd)
{
    return 0;
}
```

在此之后，我们就可以利用FS提供的接口去读取文件了，进而在加载程序这里也用上FS的接口。

```c title="nanos-list/src/loader.c"
static uintptr_t loader(PCB *pcb, const char *filename)
{
#if defined(__ISA_AM_NATIVE__)
#define EXPECT_TYPE EM_X86_64
#elif defined(__ISA_RISCV32__)
#define EXPECT_TYPE EM_RISCV
#else
#error Unsupported ISA
#endif
    int fd = fs_open(filename, 0, 0);
    Elf_Ehdr ehdr;
    fs_read(fd, &ehdr, sizeof(Elf_Ehdr));
    assert(ehdr.e_ident[EI_MAG0] == ELFMAG0);
    assert(ehdr.e_ident[EI_MAG1] == ELFMAG1);
    assert(ehdr.e_ident[EI_MAG2] == ELFMAG2);
    assert(ehdr.e_machine == EXPECT_TYPE);

    size_t phdr_num = ehdr.e_phnum;
    Elf_Phdr phdr;
    for (size_t i = 0; i < phdr_num; i++)
    {
        fs_lseek(fd, ehdr.e_phoff + i * sizeof(Elf_Phdr), SEEK_SET);
        fs_read(fd, &phdr, sizeof(Elf_Phdr));
        if (phdr.p_type != PT_LOAD)
            continue;
        void *mem = (void *)(uintptr_t)phdr.p_vaddr;
        fs_lseek(fd, phdr.p_offset, SEEK_SET);
        fs_read(fd, mem, phdr.p_filesz);
        mem += phdr.p_filesz;
        memset(mem, 0, phdr.p_memsz - phdr.p_filesz);
    }
    fs_close(fd);
    return (uintptr_t)ehdr.e_entry;
}
```

#### 实现完整的文件系统

其实上面我们已经实现了`fs_lseek`了，而事实上`fs_write`和`fs_read`的实现很类似，这里就不多做赘述。当然，还需要实现一下串口写的函数`serial_write`，不过这很简单。

最后，因为要让用户程序能用到我们新添加的FS，我们应该在系统调用处更新一下接口：

```c title="nanos-lite/src/syscall.c"
static int sys_write(Context *c, uintptr_t *a)
{
    int fd = a[1];
    uint8_t *buf = (void *)a[2];
    size_t count = a[3];
#ifdef CONFIG_STRACE
    extern Finfo file_table[];
    printf("%s %p %u\n", file_table[fd].name, buf, count);
#endif
    return fs_write(fd, buf, count);
}

static size_t sys_read(Context *c, uintptr_t *a)
{
    int fd = a[1];
    uint8_t *buf = (void *)a[2];
    size_t count = a[3];
#ifdef CONFIG_STRACE
    extern Finfo file_table[];
    printf("%s %p %u\n", file_table[fd].name, buf, count);
#endif
    return fs_read(fd, buf, count);
}

static size_t sys_lseek(Context *c, uintptr_t *a)
{
    int fd = a[1];
    size_t offset = a[2];
    int whence = a[3];
#ifdef CONFIG_STRACE
    extern Finfo file_table[];
    printf("%s %u %d\n", file_table[fd].name, offset, whence);
#endif
    return fs_lseek(fd, offset, whence);
}

static int sys_open(Context *c, uintptr_t *a)
{
    const char *pathname = (void *)a[1];
    int flags = a[2];
    int mode = a[3];
#ifdef CONFIG_STRACE
    printf("%s %d %d\n", pathname, flags, mode);
#endif
    return fs_open(pathname, flags, mode);
}

static int sys_close(Context *c, uintptr_t *a)
{
    int fd = a[1];
#ifdef CONFIG_STRACE
    extern Finfo file_table[];
    printf("%s\n", file_table[fd].name);
#endif
    return fs_close(fd);
}
```

这样我们的`file-test`就可以轻松通过了。

#### 支持sfs的strace

上面系统调用的实现中被`#ifdef`和`#endif`围起来的部分就是干这个事情的。

#### 用C语言模拟面向对象编程

之后再看看。

#### 把串口抽象成文件

之前实现时已经考虑到VFS的抽象了，所以这一点已经提前实现了。

#### 实现gettimeofday

本题难点在于读手册：

> If  either  tv or tz is NULL, the corresponding structure is not set or
   returned.  (However, compilation warnings will result if tv is NULL.)
>
 >The use of the timezone structure is obsolete; the tz  argument  should
   normally be specified as NULL.  (See NOTES below.)

意思差不多就是说，`tz`这个参数没啥用，一般传个`NULL`就得了。

对于`timeval`的定义，`man 3 timeradd`里有写，就是

```c
struct timeval {
   time_t      tv_sec;     /* seconds */
   suseconds_t tv_usec;    /* microseconds */
};
```

这俩类型其实都是`long`。

已知我们AM上的`__am_timer_uptime`会给出微秒数，根据简单的单位换算的数学知识，就能很快得到下面的代码了：

```c title="nanos-lite/src/syscall.c"
static int sys_gettimeofday(Context *c, uintptr_t *a)
{
    struct timeval *tv = (void *)a[1];
    struct timezone *tz __attribute__((unused)) = (void *)a[2];
#ifdef CONFIG_STRACE
    printf("%p %p\n", tv, tz);
#endif
    uint64_t us = io_read(AM_TIMER_UPTIME).us;
    tv->tv_usec = us % 1000000;
    tv->tv_sec = us / 1000000;
    return 0;
}
```

测试程序每半秒钟就会输出一句话，证明我们的实现是正确的。

#### 实现NDL的时钟

实现策略可以仿照原先的time-test，只是单位从半秒变成了毫秒而已：

```c title="$NAVY_HOME/libs/libndl/NDL.c"
uint32_t NDL_GetTicks()
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    uint32_t ret = tv.tv_sec * 1000 + tv.tv_usec / 1000;
    return ret;
}
```

然后这是修改后的time-test：

```c title="$NAVY_HOME/tests/timer-test/main.c"
#include <stdio.h>
#include <NDL.h>

int main()
{
    NDL_Init(0);
    int half_sec = 1;
    while (1)
    {
        while (1)
        {
            uint32_t res = NDL_GetTicks();
            res /= 500;
            if (res >= half_sec)
                break;
        }
        printf("%d half-seconds\n", half_sec);
        half_sec++;
    }
    NDL_Quit();
    return 0;
}
```

#### 把按键输入抽象成文件

首先实现一下`events_read()`，需要注意的是，虽然假设一次最多只会读出一个事件，但是也会有可能读出来半个事件，这时候我们就需要做一些特殊处理：

```c title="nanos-lite/src/device.c"
static char event_buf[300] = {0};
size_t events_read(void *buf, size_t offset, size_t len)
{
    size_t event_buf_len = strlen(event_buf);
    if (event_buf_len == 0)
    {
        AM_INPUT_KEYBRD_T keybrd = io_read(AM_INPUT_KEYBRD);
        if (keybrd.keycode == AM_KEY_NONE)
            return 0;
        sprintf(event_buf, "k%c %s\n", keybrd.keydown ? 'd' : 'u',
                keyname[keybrd.keycode]);
    }
    event_buf_len = strlen(event_buf);
    size_t ret = (event_buf_len < len ? event_buf_len : len);
    memcpy(buf, event_buf, ret);
    memmove(event_buf, event_buf + ret, event_buf_len - ret + 1);
    return ret;
}
```

也就是只有读了完整事件的时候才会重新从键盘设备获取新按的键，然后把事件字符串写到`buf`里，否则就只把`len`限制的部分写过去，留下剩下的残缺的事件字符串，等下次再读。

由于用户程序要读取键盘事件得靠VFS，所以得在文件目录中注册`/dev/events`：

```c
[FD_EVENT] = {"/dev/events", 0, 0, 0, 1, events_read, invalid_write},
```

最后是在用户程序那边的NDL库中包装一下获取键盘事件的过程：

```c title="$NAVY_HOME/libs/libndl/NDL.c"
int NDL_PollEvent(char *buf, int len)
{
    int fd = open("/dev/events", O_RDONLY);
    int ok = read(fd, buf, len);
    buf[ok] = '\0';
    close(fd);
    return ok != 0;
}
```

跑测试的时候会发现打印一个事件的字符串后会跟上一个空行。原因是事件本身有一个`\n`，然后event-test程序里又有一个`\n`。

#### 用fopen()还是open()?

当然是用`open()`，因为[[pa3#printf和换行|上面]]提到经过库包装后的可能会有缓冲区等等东西。我们在这里并不希望它会有缓冲。

#### 在NDL中获取屏幕大小

根据README.md中所说，应该这样实现`dispinfo_read()`：

```c
int screen_width, screen_height;
size_t dispinfo_read(void *buf, size_t offset, size_t len)
{
    char info_buf[100];
    size_t sz =
        sprintf(info_buf, "WIDTH:%d\nHEIGHT:%d\n", screen_width, screen_height);
    size_t ret = (sz < len ? sz : len);
    memcpy(buf, info_buf, ret);
    return ret;
}

void init_device()
{
    Log("Initializing devices...");
    ioe_init();
    AM_GPU_CONFIG_T conf = io_read(AM_GPU_CONFIG);
    screen_width = conf.width;
    screen_height = conf.height;
}
```

为了能让用户程序从系统调用来访问VFS，应该添加文件目录：

```c
[FD_FBINFO] = {"/proc/dispinfo", 0, 0, 0, 1, dispinfo_read, invalid_write},
```

在navy-app这边，则需要简单实现一下NDL库里的内容。我在`NDL_init()`的时候调用了`read_dispinfo`函数得到屏幕的长宽信息，然后才好实现`NDL_OpenCanvas`。

```c title="$NAVY_HOME/libs/libndl/NDL.c"
static int screen_w = 0, screen_h = 0;
static int canvas_w = 0, canvas_h = 0;

void NDL_OpenCanvas(int *w, int *h)
{
    if (getenv("NWM_APP"))
    {
        int fbctl = 4;
        fbdev = 5;
        screen_w = *w;
        screen_h = *h;
        char buf[64];
        int len = sprintf(buf, "%d %d", screen_w, screen_h);
        // let NWM resize the window and create the frame buffer
        write(fbctl, buf, len);
        while (1)
        {
            // 3 = evtdev
            int nread = read(3, buf, sizeof(buf) - 1);
            if (nread <= 0)
                continue;
            buf[nread] = '\0';
            if (strcmp(buf, "mmap ok") == 0)
                break;
        }
        close(fbctl);
    }
    if (*w == 0 && *h == 0)
    {
        *w = canvas_w = screen_w;
        *h = canvas_h = screen_h;
        return;
    }
    canvas_w = *w;
    canvas_h = *h;
}

static void read_dispinfo()
{
    int fd = open("/proc/dispinfo", O_RDONLY);
    char key[2][50], value[2][50];
    char buf[200] = {0};
    read(fd, buf, sizeof(buf));
    int ptr = 0;
    for (int i = 0; i < 2; i++)
    {
        int mid = ptr;
        while (buf[mid] != ':')
            mid++;
        strncpy(key[i], buf + ptr, mid - ptr);
        key[i][mid - ptr] = '\0';
        while (buf[ptr] != '\n')
            ptr++;
        strncpy(value[i], buf + mid + 1, ptr - mid - 1);
        value[i][ptr - mid - 1] = '\0';
        ptr++;
    }
    for (int i = 0; i < 2; i++)
    {
        char *k = key[i];
        char *v = value[i];
        if (strcmp(k, "WIDTH") == 0)
            sscanf(v, "%d", &screen_w);
        else if (strcmp(k, "HEIGHT") == 0)
            sscanf(v, "%d", &screen_h);
        else
            assert(0);
    }
}

int NDL_Init(uint32_t flags)
{
    if (getenv("NWM_APP"))
    {
        evtdev = 3;
    }
    read_dispinfo();
    return 0;
}
```

#### 把VGA显存抽象成文件

教程中说的很详细了，首先初始化`/dev/fb`的大小：

```c title="nanos-lite/src/fs.c"
void init_fs()
{
    // TODO: initialize the size of /dev/fb
    AM_GPU_CONFIG_T conf = io_read(AM_GPU_CONFIG);
    file_table[FD_FB].size = conf.vmemsz;
}
```

然后是实现`fb_write()`，这需要一点点小技巧。在AM的IOE里面给的接口是在屏幕上的一个矩形区域内填色，而这里只能连着填色。我们可以考虑成这两种情况：
1. 连着填只有一行：1个`io_write`就行了，因为一行本身就是一个矩形。
2. 连着多行：可能需要3个`io_write`，第1个`io_write`处理第1行（可能没填满），第2个`io_write`处理第2到倒数第2行（这些是全满的行，所以是一个大矩形），第3个`io_write`处理最后1行即可。

要记住在OS里的坐标都是屏幕坐标！

代码实现如下：

```c title="nanos-lite/src/device.c"
size_t fb_write(const void *buf, size_t offset, size_t len)
{
    assert(len % 4 == 0);
    assert(offset % 4 == 0);
    offset /= 4;
    len /= 4;
    int y = offset / screen_width;
    int x = offset % screen_width;
    int yy = (offset + len) / screen_width;
    int xx = (offset + len) % screen_width;
    size_t buf_off = 0;

    if (yy > y)
    {
        io_write(AM_GPU_FBDRAW, x, y, (void *)buf, screen_width - x, 1, false);
        buf_off += screen_width - x;
        io_write(AM_GPU_FBDRAW, 0, y + 1, (void *)buf + buf_off, screen_width,
                 yy - y - 1, false);
        buf_off += screen_width * (yy - y - 1);
        io_write(AM_GPU_FBDRAW, 0, yy, (void *)buf + buf_off, xx, 1, true);
    }
    else
    {
        io_write(AM_GPU_FBDRAW, x, y, (void *)buf, xx - x + 1, 1, true);
    }
    return len;
}
```

然后是在navy-app中实现NDL库。这里的画布是由用户程序通过`NDL_OpenCancas`创建的，它本身其实就是抽象给用户程序来绘图的，用户程序绘图到画布上的接口就是`NDL_DrawRect`。而画布究竟在屏幕的哪里完全取决于NDL库的实现。所以我做了一个函数`canvas2screen`表示画布的坐标所线性映射到的屏幕的坐标，然后在`NDL_DrawRect`中先把画布坐标转化为屏幕坐标，然后再调用系统调用去画。

```c title="$NAVY_HOME/libs/libndl/NDL.c"
static void canvas2screen(int cx, int cy, int *sx, int *sy)
{
    *sx = cx;
    *sy = cy;
}

void NDL_DrawRect(uint32_t *pixels, int x, int y, int w, int h)
{
    int sx, sy;
    canvas2screen(x, y, &sx, &sy);
    int fd = open("/dev/fb", 0);
    for (int i = sy; i < sy + h; i++)
    {
        int offset = i * screen_w + sx;
        offset = offset * 4;
        lseek(fd, offset, SEEK_SET);
        int len = w * 4;
        write(fd, pixels, len);
        pixels += w;
    }
    close(fd);
}
```

看上述代码就知道，我目前是把画布就当作屏幕的，所以画的东西会出现在屏幕的左上角。

测试程序如下：

![[Screenshot from 2025-08-10 01-41-32.png]]

#### 实现居中的画布

这其实就是换了一下坐标。具体实现上就是改一下`canvas2screen`就可以：

```c title="$NAVY_HOME/libs/libndl/NDL.c"
static void canvas2screen(int cx, int cy, int *sx, int *sy)
{
    *sx = cx + (screen_w - canvas_w) / 2;
    *sy = cy + (screen_h - canvas_h) / 2;
}
```

![[Pasted image 20250810014353.png]]

### 精彩纷呈的应用程序

#### 比较fixedpt和float

float的小数点是浮动的，这意味着它可以表示更加通过调整幂次等方法表示特别小或者特别大的数字，而用`fixedpt`只能保证精细度恒定在$2^{-8}$，无法表示特别小或者特别大的数字。

#### 神奇的fixedpt_rconst

注意到我们编译C源文件时采用的`CFLAGS`：

```make title="$NAVY_HOME/scripts/riscv32.mk"
CFLAGS += -march=rv32g -mabi=ilp32  #overwrite
```

ABI被设为ilp32，意味着只有整数，没有硬件上的浮点运算。阅读了RISC-V的手册后也会知道，ELF文件里的文件头的`e_flags`字段就会保存一些关于ABI的信息：例如ilp32对应的`EF_RISCV_FLOAT_ABI_SOFT`就是0，而在navy-apps里面以`make ISA=riscv32`编译出来的ELF也能发现其ELF头里的`e_flags`为0。

像这样的`EF_RISCV_FLOAT_ABI_SOFT`的软浮点，编译器就会用通用寄存器去模拟浮点过程，只是效率会很慢。

#### 实现更多的fixedptc API

对于一个`fixedpt`数a与一个整数B相乘，得到结果C可以用这样子的数学语言表达：

$$
A = a \cdot 2^{8}
$$
$$
C = c \cdot 2^8 = a \cdot B \cdot 2^8 = A \cdot B
$$

按照这个思路就可以实现这些函数了：

```c title="$NAVY_HOME/libs/libfixedptc/include/fixedptc.h"
/* Multiplies a fixedpt number with an integer, returns the result. */
static inline fixedpt fixedpt_muli(fixedpt A, int B)
{
	return A * B;
}

/* Divides a fixedpt number with an integer, returns the result. */
static inline fixedpt fixedpt_divi(fixedpt A, int B)
{
	return A / B;
}

/* Multiplies two fixedpt numbers, returns the result. */
static inline fixedpt fixedpt_mul(fixedpt A, fixedpt B)
{
	return (A * B) >> 8;
}

/* Divides two fixedpt numbers, returns the result. */
static inline fixedpt fixedpt_div(fixedpt A, fixedpt B)
{
	return (A / B) << 8;
}
```

由于定义里设定`a`的表示`A`的相反数就直接是补码相反数，所以`fixedpt_abs`也很简单：

```c title="$NAVY_HOME/libs/libfixedptc/include/fixedptc.h"
static inline fixedpt fixedpt_abs(fixedpt A)
{
	if (A >= 0)
		return A;
	else
		return -A;
}
```

注意`floor(x)`的定义是小于等于`x`的最大的整数。多亏了补码机制，直接将小数位清空即可。

```c title="$NAVY_HOME/libs/libfixedptc/include/fixedptc.h"
static inline fixedpt fixedpt_floor(fixedpt A)
{
	int mask = -256;
	return A & mask;
}
```

而`ceil(x)`的定义是大于等于`x`的最小的整数。由此需要先判一下小数部分有没有数，没有就是这个数本身，有就加个1再清空小数部分。

```c title="$NAVY_HOME/libs/libfixedptc/include/fixedptc.h"
static inline fixedpt fixedpt_ceil(fixedpt A)
{
	int mask = 255;
	if (A & mask)
		A += (1 << 8);
	int mask2 = -256;
	return A & mask2;
}
```

#### 如何将浮点变量转换成fixedpt类型?

虽然这个计算机没有浮点指令，但是我们可以用编译器从软件的角度解析浮点数。首先根据IEEE 754的原则，浮点数是$(-1)^s \times M \times 2^E$ ，设`f`是小数字段的值，`e`是阶码部分的值。`f`，`e`和`s`都可以直接从内存中读出。这里的`s`目前并不重要，所以先当作没有。

对于规格化的值，根据定义实际上浮点数的值是$(1 + f \times 2^{-23}) \times 2^{e - 127}$，对应到定点数可以表示成这样：
$$(1 + f \times 2^{-23}) \times 2^{e - 127} \times 2^8 = 2^{e - 119} + f \times 2^{e-142}$$

而对于非规格化的值，根据定义实际上浮点数的值是$f \times 2^{-23} \times 2^{-126}$，对应到定点数就直接表示成这样：
$$f \times 2^{-23} \times 2^{-126} \times 2^8 = f \times 2^{-141} $$
实际上这里非规格化的值、特殊值都不在`fixedpt`的表示范围中，所以只需要了解规格化的值就可以了。

刚才忽略了符号，如果是负数的话就直接给得到的定点数表示做一个相反数（补码）即可。

#### 神奇的LD_PRELOAD

首先我们看一下路径是如何改变的。如果注意到日志的内容这会很好寻找：

```c title="$NAVY_HOME/libs/libos/src/native.cpp"
static const char *redirect_path(char *newpath, const char *path)
{
    get_fsimg_path(newpath, path);
    if (0 == access(newpath, 0))
    {
        fprintf(stderr, "Redirecting file open: %s -> %s\n", path, newpath);
        return newpath;
    }
    return path;
}
```

是`get_fsimg_path`重定向了文件的路径。本质上是往前面添加了一个前缀。这个前缀有部分是依靠读环境变量`$NAVY_HOME`读出来的，这一块并不困难。

不过要想用到这个`redirect_path`得先调用`native.so`的`fopen`，`open`， `execve`函数，注意到这是个动态链接库，并不是静态链接上去的，于是注意到`native.mk`文件中是如何运行的：

```make title="$NAVY_HOME/scripts/native.mk"
run: app env
	@LD_PRELOAD=$(NAVY_HOME)/libs/libos/build/native.so $(APP) $(mainargs)
```

网上去man了一下LD_PRELOAD的意思：

>**LD_PRELOAD**
              A list of additional, user-specified, ELF shared objects to
              be loaded before all others.  This feature can be used to
              selectively override functions in other shared objects.
>
              The items of the list can be separated by spaces or colons,
              and there is no support for escaping either separator.  The
              objects are searched for using the rules given under
              DESCRIPTION.  Objects are searched for and added to the
              link map in the left-to-right order specified in the list.
>
              In secure-execution mode, preload pathnames containing
              slashes are ignored.  Furthermore, shared objects are
              preloaded only from the standard search directories and
              only if they have set-user-ID mode bit enabled (which is
              not typical).
>
              Within the names specified in the **LD_PRELOAD** list, the
              dynamic linker understands the tokens  _\$ORIGIN_, _\$LIB_, and
              _\$PLATFORM_ (or the versions using curly braces around the
              names) as described above in _Dynamic string tokens_.  (See
              also the discussion of quoting under the description of
              **LD_LIBRARY_PATH**.)
>
              There are various methods of specifying libraries to be
              preloaded, and these are handled in the following order:
>
              (1)  The **LD_PRELOAD** environment variable.
>
              (2)  The **--preload** command-line option when invoking the
                   dynamic linker directly.
>
              (3)  The _/etc/ld.so.preload_ file (described below).

总结一下就是，可以让可执行文件最早地加载某一些动态链接库，就能使这里的`native.so`里的`open`等函数覆盖掉其他的`open`函数。