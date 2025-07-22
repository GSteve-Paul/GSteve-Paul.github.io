---
title: PA2
tags:
  - 模拟器
  - 调试器
  - RISC-V
---
## 阶段1

### 不停计算的机器

#### 理解YEMU如何执行程序

这里状态机就不画了……就简单讲讲YEMU是如何执行一条指令的。

根据图灵机的运行方式：

```c
while (1) 
{
  从PC指示的存储器位置取出指令;
  执行指令;
  更新PC;
}
```

教程中提到的代码中取指、更新PC已经很显然了。其中译码部分比较有意思，需要用到C语言中的union、struct的bit-field等技巧，其代码中先用指令的高4位确定其操作码，再根据不同的指令类型译出操作数，并对操作数进行执行。

我们的代码确定了状态机的每一步的状态转换。

### RTFSC(2)

这里我看的是《RISC-V开放架构设计之道》，它是中文的，我们很容易能知道这些RISC-V指令的编码

![[Pasted image 20250720162729.png]]
同时，具体每个指令的具体行为在附录-A里也有说明。

#### 立即数背后的故事

- 假设我们需要将NEMU运行在Motorola 68k的机器上(把NEMU的源代码编译成Motorola 68k的机器码)

问题主要出在内存访问上，也就是NEMU的内存（大端）和NEMU内运行的程序（小端）所认为的字节序不同。那么我们需要一字节一字节地按照小端模式把映像加载入NEMU，然后`pmem_read`和`pmem_write`函数也需要修改成一字节一字节地按照小端模式读取/存储。

- 假设我们需要把Motorola 68k作为一个新的ISA加入到NEMU中

现在则是NEMU的内存（小端）而NEMU运行的程序（大端）认为的字节序不同了。同理，那么需要一字节一字节地按照大端模式把映像加载入NEMU，然后`pmem_read`和`pmem_write`函数也要照样改动。

总之，就是要让NEMU的字节序去配合里面运行的程序。

#### 立即数背后的故事(2)

对于RISC-V32，`addi`可以加载一个放在低12位的立即数，而`lui`则可以加载一个高20位的立即数，两个拼一块就是32位的数字了。

#### 我要被宏定义绕晕了, 怎么办?

首先可以通过AI再用`man`确认了GCC编译时加个`-E`的flag就可以只让编译器输出预处理后的代码就行了。然后我们改改Makefile，把编译C源文件的地方加个`-E`即可。

```make {2,11} showLineNumbers{24} title="$NEMU_HOME/scripts/build.mk" /-E/ 
INCLUDES = $(addprefix -I, $(INC_PATH))
CFLAGS  := -O2 -MMD -Wall -Werror -E $(INCLUDES) $(CFLAGS)
LDFLAGS := -O2 $(LDFLAGS)

OBJS = $(SRCS:%.c=$(OBJ_DIR)/%.o) $(CXXSRC:%.cc=$(OBJ_DIR)/%.o)

# Compilation patterns
$(OBJ_DIR)/%.o: %.c
	@echo + CC $<
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -c -o $@ $<
	$(call call_fixdep, $(@:.o=.d), $@)
```

最后`make clean; make`，这样就能输出宏定义展开的内容，方便我们进行理解：

```c title="$NEMU_HOME$/build/obj-riscv32-nemu-interpreter/src/isa/riscv32/inst.o" 
static int decode_exec(Decode *s)
{
    int rd = 0;
    int rs1 = 0;
    int rs2 = 0;
    word_t src1 = 0, src2 = 0, imm = 0;
    s->dnpc = s->snpc;
# 126 "src/isa/riscv32/inst.c"
    { const void ** __instpat_end = &&__instpat_end_;;
    do { uint64_t key, mask, shift; pattern_decode("??????? ????? ????? ??? ????? 00101 11", (sizeof("??????? ????? ????? ??? ????? 00101 11") - 1), &key, &mask, &shift); if ((((uint64_t)((s)->isa.inst.val) >> shift) & mask) == key) { { decode_operand(s, &rd, &rs1, &rs2, &src1, &src2, &imm, TYPE_U); (cpu.gpr[check_reg_idx(rd)]) = s->pc + imm; }; goto *(__instpat_end); } } while (0)
                                ;
    do { uint64_t key, mask, shift; pattern_decode("??????? ????? ????? ??? ????? 01101 11", (sizeof("??????? ????? ????? ??? ????? 01101 11") - 1), &key, &mask, &shift); if ((((uint64_t)((s)->isa.inst.val) >> shift) & mask) == key) { { decode_operand(s, &rd, &rs1, &rs2, &src1, &src2, &imm, TYPE_U); (cpu.gpr[check_reg_idx(rd)]) = imm; }; goto *(__instpat_end); } } while (0);
    do { uint64_t key, mask, shift; pattern_decode("??????? ????? ????? 100 ????? 00000 11", (sizeof("??????? ????? ????? 100 ????? 00000 11") - 1), &key, &mask, &shift); if ((((uint64_t)((s)->isa.inst.val) >> shift) & mask) == key) { { decode_operand(s, &rd, &rs1, &rs2, &src1, &src2, &imm, TYPE_I); (cpu.gpr[check_reg_idx(rd)]) = vaddr_read(src1 + imm, 1); }; goto *(__instpat_end); } } while (0)
                                      ;
```

#### RTFSC理解指令执行的过程

1. 准备工作 在`exec_once`中设置decode结构体的pc和snpc为当前pc值。
2. 取指令 在`isa_exec_once`中第一行就从内存中的snpc处读入指令并放到decode结构体中。
3. 译码、执行 首先由`pattern_decode`生成NEMU中已实现的各个指令的掩码等信息，然后在`decode_exec`中顺着各个`INSTPAT`一个一个用函数`decode_operand`进行检测，若匹配上则执行该指令，若无一匹配则表明是无效指令。
4. 更新PC 用执行过程中可能会更改的dnpc更新pc值。

其中译码部分的宏值得一提：

1. 利用GCC提供的[标签地址](https://gcc.gnu.org/onlinedocs/gcc/Labels-as-Values.html)扩展进行跳转。
2. `pattern_decode`的生成的操作码（key），操作码的掩码（mask）和偏移（shift）。可能让我来写就是写一个循环遍历，但是框架代码中用的是利用宏递归的展开，然后去一个一个地从左往右得到信息。根据下面这段代码，能够理解这三个信息的用法：
	```c {6} title="$NEMU_HOME/include/cpu/decode.h"
	#define INSTPAT(pattern, ...)                                               \
	    do                                                                      \
	    {                                                                       \
	        uint64_t key, mask, shift;                                          \
	        pattern_decode(pattern, STRLEN(pattern), &key, &mask, &shift);      \
	        if ((((uint64_t)INSTPAT_INST(s) >> shift) & mask) == key)           \
	        {                                                                   \
	            INSTPAT_MATCH(s, ##__VA_ARGS__);                                \
	            goto *(__instpat_end);                                          \
	        }                                                                   \
	    } while (0)
	```
3. 关于`__VA_ARGS__`的[使用技巧](https://en.cppreference.com/w/cpp/preprocessor/replace)。
	> Note: some compilers offer an extension that allows `##` to appear after a comma and before `__VA_ARGS__`, in which case the `##` does nothing when the variable arguments are present, but removes the comma when the variable arguments are not present: this makes it possible to define macros such as `fprintf (stderr, format,  ##__VA_ARGS__)`. This can also be achieved in a standard manner using `__VA_OPT__`, such as `fprintf (stderr, format __VA_OPT__(, ) __VA_ARGS__)`.(since C++20)
4. 关于符号扩展`SEXT(x, len)`的技巧，其中用到了GCC的[语句表达式扩展](https://gcc.gnu.org/onlinedocs/gcc/Statement-Exprs.html)。对于这个代码
	```c  title="$NEMU_HOME/include/macro.h"
	#define SEXT(x, len) ({ struct { int64_t n : len; } __x = { .n = x }; (uint64_t)__x.n; })
	```
	里面还用到了位域的技巧，把一个`x`赋给这里的`n`，按照[[pa1#潜在的威胁（建议二周目思考）|PA1中讲到的整形转换问题]]的方法，这里的`n`将会存储成符号扩展成`len`长度的有符号数，然后转成无符号数。这些过程都只是添加了原有数字`x`前面的所谓的“符号位”。

不禁感叹会写宏的人都太牛了，况且宏还很难调试。

#### 为什么执行了未实现指令会出现上述报错信息

会匹配上最后一个`INSTPAT`，进而通过函数`invalid_inst`输出相关信息，并设置`nemu_state`为`NEMU_ABORT`，退出码为`-1`，这会决定`cpu_exec`函数中的退出日志。

#### 运行第一个客户程序

很简单，反复运行程序，查看报错信息对应的指令，查手册得到对应指令的含义并予以实现即可。

#### 实现更多的指令

当然需要模仿`immU`，实现其他指令类型的取立即数的方式，也需要添加大量其他的`INSTPAT`以实现指令。

需要注意的是`srai`指令是一个坑，对于一般的I型指令，其立即数和`srai`的shamt的域并不相同，shamt相对于立即数少了${2^{10}}$。

![[Pasted image 20250720233624.png]]
![[Pasted image 20250720233518.png]]
因此需要实现为：
```c title="$NEMU_HOME/src/isa/riscv32/inst.c"
INSTPAT("010000? ????? ????? 101 ????? 00100 11", srai, I, R(rd) = ((sword_t)src1 >> (imm - (1 << 10))));
```

#### mips32的分支延迟槽

还没学mips32，也许可以放进去一些没什么意义的指令，比如把某个寄存器的值复制到`R0`？反正`R0`始终会是0，所以不会有什么影响。

#### 指令名对照

伪指令本身的二进制表达肯定不是一个伪指令，所以可以试着对照指令集手册。

事实上还可以给`objdump`添加`-M no-aliases`以禁用伪指令：

```sh
riscv64-linux-gnu-objdump -M no-aliases -d unalign-riscv32-nemu.elf
```

## 阶段2

### 程序，运行时环境与AM

#### 这又能怎么样呢

解耦后，能在debug的时候更容易找到bug所存在的层次。例如库和上层程序，它俩是分离的能方便分别测试。

#### 为什么要有AM? (建议二周目思考)

AM给的运行时环境比较粗糙且简单，比较靠底层，并未为安全着想。而操作系统本身是运行在AM上的软件，其运行时环境更加复杂且多样，会更加考虑操作系统中的概念（例如进程、文件系统）以方便在操作系统上的程序的开发。

#### 了解一下`volatile`关键字：

> An object that has volatile-qualified type may be modified in ways unknown to the implementation or have other unknown side effects. Therefore any expression referring to such an object shall be evaluated strictly according to the rules of the abstract machine, as described in 5.1.2.3. Furthermore, at every sequence point the value last stored in the object shall agree with that prescribed by the abstract machine, except as modified by the unknown factors mentioned previously. What constitutes an access to an object that has volatile-qualified type is implementation-defined.
> 
> A volatile declaration may be used to describe an object corresponding to a memory-mapped input/output port or an object accessed by an asynchronously interrupting function. Actions on objects so declared shall not be ‘‘optimized out’’ by an implementation or reordered except as permitted by the rules for evaluating expressions.

再读一读C99手册里关于side effects的说法：

> Accessing a volatile object, modifying an object, modifying a file, or calling a function that does any of those operations are all side effects,11) which are changes in the state of the execution environment. Evaluation of an expression may produce side effects. At certain specified points in the execution sequence called sequence points, all side effects of previous evaluations shall be complete and no side effects of subsequent evaluations shall have taken place. (A summary of the sequence points is given in annex C.)

这样我们就会知道，volatile关键字的作用是把对这个volatile对象的读操作也视为一种side effects，这会让它的读操作不会被优化，而是严格按照语义执行。因此它事实上并不能用于多线程环境中。

#### 阅读Makefile

这一块的Makefile有点复杂，所以我们先直接在这里梳理一下AM中的程序是如何构建的。

对于`cpu_tests`里的小例子`dummy`，假设我们用这样的命令来运行：

```sh
make ARCH=riscv32-nemu ALL=dummy run
```

首先会通过`cpu_tests`里的Makefile生成一个Makefile.dummy，这个Makefile.dummy会include`$AM_HOME/Makefile`，使得`cpu_tests`里的东西和`abstract_machine`连动起来，同时会运行`$AM_HOME/Makefile`里的`run`目标。因此Makefile会打印如下信息：
```
# Building dummy-run [riscv32-nemu]
```

这个`run`目标也不是直接存在于`$AM_HOME/Makefile`的，而是通过里面的两层include，实际上在`$AM_HOME/scripts/platform/nemu.mk`里面。然后这个`run`目标依赖于`insert_arg`，又依赖于`image`，接着依赖于`image-dep`，最后可以看到在`$AM_HOME/Makefile`里`image-dep`又依赖于`$(LIBS)`和`$(IMAGE).elf`。接着读源码，这个`$(LIBS)`就可以又去make`$AM_HOME/Makefile`里的archieve目标，这个archieve目标就会去把库里的`.c`编译成`.o`后，用AR打包成一个[静态库](https://www.yolinux.com/TUTORIALS/LibraryArchives-StaticAndDynamic.html)。因此会打印如下信息：

```
# Building am-archive [riscv32-nemu]
+ CC src/platform/nemu/trm.c
+ CC src/platform/nemu/ioe/ioe.c
+ CC src/platform/nemu/ioe/timer.c
+ CC src/platform/nemu/ioe/input.c
+ CC src/platform/nemu/ioe/gpu.c
+ CC src/platform/nemu/ioe/audio.c
+ CC src/platform/nemu/ioe/disk.c
+ CC src/platform/nemu/mpe.c
+ AS src/riscv/nemu/start.S
+ CC src/riscv/nemu/cte.c
+ AS src/riscv/nemu/trap.S
+ CC src/riscv/nemu/vme.c
+ AR -> build/am-riscv32-nemu.a
```

以及：

```
# Building klib-archive [riscv32-nemu]
+ CC src/int64.c
+ CC src/string.c
+ CC src/stdlib.c
+ CC src/stdio.c
+ CC src/cpp.c
+ AR -> build/klib-riscv32-nemu.a
```

而这个`$(IMAGE).elf`则会先把`cpu_tests`里指定的`dummy.c`编译成`dummy.o`，然后用LD和之前已经构建好的`.a`静态库进行链接，得到elf文件，这样`image-dep`目标就已经完成了。所以会输出以下内容。

```
+ CC tests/dummy.c
# Creating image [riscv32-nemu]
+ LD -> build/dummy-riscv32-nemu.elf
```

然后在`$AM_HOME/scripts/platform/nemu.mk`里完成`image`目标，其实这里就是先用objdump进行反汇编，输出到一个txt文件中，再用objcopy创建一个bin文件。到这里`image`目标就完成了，然后再是完成`insert-arg`目标，最后在`run`目标中，把这个bin文件作为映像放到NEMU中运行。

#### 通过批处理模式运行NEMU

只要看了Makefile的源码，这块就变得十足的简单了。甚至考查的地方都是最简单的部分。整个AM中的Makefile和NEMU连动的地方有且只有`image`目标里，即：

```make title="$AM_HOME/scripts/platform/nemu.mk" showLineNumbers{29}
run: insert-arg
	$(MAKE) -C $(NEMU_HOME) ISA=$(ISA) run ARGS="$(NEMUFLAGS)" IMG=$(IMAGE).bin
```

注意到NEMU里面有一个参数`-b`（`--batch`），它可以通过函数`sdb_set_batch_mode`启用批处理模式，而通过阅读NEMU的Makefile，我们可以知道实际上上面传入的`ARGS`就是给NEMU运行时的参数：

```make title="$NEMU_HOME/scripts/native.mk" showLineNumbers{27} /$(ARGS)/
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

所以我们在`$AM_HOME/scripts/platform/nemu.mk`的`NEMUFLAGS`里添个`--batch`就行了。

```make title="$AM_HOME/scripts/platform/nemu.mk" showLineNumbers{15}
NEMUFLAGS += -l $(shell dirname $(IMAGE).elf)/nemu-log.txt --batch --elf=$(IMAGE).elf 
```

#### RISC-V指令测试

没有去真正测这么多……