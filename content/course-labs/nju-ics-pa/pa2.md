---
title: PA2
tags:
  - RISC-V
  - 图灵机
  - 冯·诺伊曼计算机系统
---
欢迎来到PA2，个人感觉是ICS2024中任务量最重的一个。

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

首先会通过`cpu_tests`里的Makefile生成一个Makefile.dummy，这个Makefile.dummy会include`$AM_HOME/Makefile`，使得`cpu_tests`里的东西和`abstract_machine`连动起来，**同时会运行**`$AM_HOME/Makefile`里的`run`目标。因此Makefile会打印如下信息：
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

没专门去下载测试用例去测试，懒了。

#### 实现字符串处理函数

为了跑通`cpu-tests`中的`string`，只需要实现`strcmp`、`strcat`、`strcpy`、`memcmp`、`memset`这几个函数就够了，不过查阅手册是很重要的。比如你会在`man strcpy`发现这个东西：

> The strings src and dst may not overlap.

试想一下，如果没有这个假设，那么两个重叠的字符串的`strcpy`的实现将会变得更加复杂一些。这是我的`strcmp`的实现：

```c title="$AM_HOME/klib/src/string.c"
int strcmp(const char *s1, const char *s2)
{
    size_t i = 0;
    int diff = 0;
    while (!diff)
    {
        diff = s1[i] - s2[i];
        if (s1[i] == '\0' || s2[i] == '\0')
            break;
        i++;
    }
    return diff;
}
```

下面教程中的警告也提示了这一内容，真的很贴心了，不断地警告你每个细节都要有详细真实的手册作为支撑。

#### UB, 编译优化和datalab

之后再学习一下整数溢出的知识吧~

不过根据下面截取自cppreference的描述，虽然有符号数的溢出是UB，但是似乎好像对于（C++ 20及以上）的有符号数的溢出都是wrap around的结果了。

> #### Overflows
>
>  Unsigned integer arithmetic is always performed modulo 2n  
  where n is the number of bits in that particular integer. E.g. for unsigned int, adding one to [UINT_MAX](https://en.cppreference.com/w/cpp/types/climits.html "cpp/types/climits") gives ​0​, and subtracting one from ​0​ gives [UINT_MAX](https://en.cppreference.com/w/cpp/types/climits.html "cpp/types/climits").
>
 > When signed integer arithmetic operation overflows (the result does not fit in the result type), the behavior is undefined, — the possible manifestations of such an operation include:
>
> - it wraps around according to the rules of the representation (typically [two's complement](https://en.cppreference.com/w/cpp/language/types.html#Range_of_values "cpp/language/types")),
> - it traps — on some platforms or due to compiler options (e.g. `-ftrapv` in GCC and Clang),
> - it saturates to minimal or maximal value (on many DSPs),
> - it is completely [optimized out by the compiler](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know_14.html).

> However, all C++ compilers use [two's complement](https://en.wikipedia.org/wiki/Two%27s_complement "enwiki:Two's complement") representation, and as of C++20, it is the only representation allowed by the standard, with the guaranteed range from $-2^{N-1}$  to $+2^{N-1} -1$ (e.g. **−128** to **127** for a signed 8-bit type).

#### 实现sprintf

孩子们，我并不是那么容易实现。思路很简单，但是写的比较屎山，如果要改得更加易读还是觉得用正则表达式比较好。而且可以把`sprintf`中的一部分放到`vsprintf`中去做，这样能避免重复性代码。唯一可能不太熟悉的就是C语言里面可变参数的使用，我在下一小节会简单介绍。

```c title="$AM_HOME/klib/src/stdio.c"
static void putchar_to_c_str(const char ch, int *tot, char **out) {
	*((*out)++) = ch;
	(*tot)++;
}

static bool isalpha(char ch) {
	return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z');
}

static void analyze_fmtch(const char* fmt, size_t *i, int *tot, void (*out_func)(const char, int *, char **), char **out, va_list *args) {
#define OUT(ch) do {out_func(ch, tot, out); } while (0)
	if (fmt[*i] == '%') {
		size_t l = *i;
		size_t r = *i;
		size_t dot = *i;
		bool left_align = false;
		bool sign = false;
		while (!isalpha(fmt[*i])) (*i)++;
		r = *i - 1;
		char pre = ' ';
		size_t width = 1;
		bool fnum = true;
		for (size_t j = l; j <= r; j++) {
			if (fmt[j] == '.')  {
				dot = j;
				break;
			}
		}
		for (size_t j = l; j < dot; j++) {
			switch (fmt[j]) {
				case '-':
					left_align = true;
					break;
				case '+':
					sign = true;
					break;
				case ' ':
					pre = ' ';
					break;
				default:
					if (fmt[j] == '0' && fnum)
						pre = '0';
					if (fnum)
						width = 0;
					width *= 10;
					width += fmt[j] - '0';
					fnum = false;
			}
		}
		switch (fmt[*i]) {
			case 's':
				char *str = (char *)va_arg(*args, const char *);
				while (*str) {
					OUT(*str);
					str++;
				}
				break;
			case 'c':
				char ch = va_arg(*args, int);
				OUT(ch);
				break;
			case 'i':
			case 'x':
			case 'o':
			case 'd':
				int tmp_num = va_arg(*args, int);
				unsigned int num = abs(tmp_num);
				char num_str[15];
				int j = 0;
				int base = 10;
				switch (fmt[*i]) {
					case 'i':
					case 'd':
						base = 10;
						break;
					case 'x':
						base = 16;
						break;
					case 'o':
						base = 8;
						break;
				}
				do {
					int bit = num % base;
					char ch_bit = bit < 10 ? bit + '0' : bit - 10 + 'a';
					num_str[j++] = ch_bit;
					num /= base;
				} while(num);
				size_t num_len = j;
				if (tmp_num < 0 || (tmp_num > 0 && sign))
					num_len++;
				if (!left_align && pre == ' ') {
					for (int cnt = width - num_len; cnt > 0; cnt--)
						OUT(' ');
				}
				if (tmp_num < 0)
					OUT('-');
				if (tmp_num > 0 && sign)
					OUT('+');
				if (!left_align && pre == '0') {
					for (int cnt = width - num_len; cnt > 0; cnt--)
						OUT('0');
				}
				for (--j ;j >= 0; j--) {
					OUT(num_str[j]);
				}
				if (left_align) {
					for (int cnt = width - num_len; cnt > 0; cnt--)
						OUT(' ');
				}
				break;
			default:
				panic("Not implemented");
		}
	}
	else {
		OUT(fmt[*i]);
	}
	(*i)++;
#undef OUT
}

int sprintf(char *out, const char *fmt, ...) {
	va_list args;
	va_start(args, fmt);
	int tot = 0;
	size_t i = 0;
	while (fmt[i]) {
		analyze_fmtch(fmt, &i, &tot, putchar_to_c_str, &out, &args);
	}
	*out = '\0';
	va_end(args);
	return tot;
}
```

#### stdarg是如何实现的?

观察到实际上我们的klib中include的`stdarg.h`是直接include的本地host机上的`stdarg.h`，即`/usr/lib/gcc-cross/riscv64-linux-gnu/13/include/stdarg.h`，于是简单地看一下，就会发现有这些内容：

```c title="/usr/lib/gcc-cross/riscv64-linux-gnu/13/include/stdarg.h"
#if defined __STDC_VERSION__ && __STDC_VERSION__ > 201710L
#define va_start(v, ...)	__builtin_va_start(v, 0)
#else
#define va_start(v,l)	__builtin_va_start(v,l)
#endif
#define va_end(v)	__builtin_va_end(v)
#define va_arg(v,l)	__builtin_va_arg(v,l)
#if !defined(__STRICT_ANSI__) || __STDC_VERSION__ + 0 >= 199900L \
    || __cplusplus + 0 >= 201103L
#define va_copy(d,s)	__builtin_va_copy(d,s)
#endif
#define __va_copy(d,s)	__builtin_va_copy(d,s)
```

从cppreference里面可以知道这些：

> `va_list` is a complete object type suitable for holding the information needed by the macros `va_start`, `va_copy`, `va_arg`, and `va_end`.

> If a `va_list` instance is created, passed to another function, and used via `va_arg` in that function, then any subsequent use in the calling function should be preceded by a call to `va_end`.

可以看到，对于C99标准，首先利用的是`va_start`把`va_list`用可变参数前面的那一个参数初始化一下，然后再用`va_arg`去遍历，最后用`va_end`去结束。由于不同的ISA的函数调用ABI不同，像GCC里面就是用的GCC内建函数。

先看下GCC是如何实现的，我们简单地编写了这么一段代码如下：

```c
#include <stdio.h>
#include <stdarg.h>

int good_code(int count, ...) {
	va_list args;
	va_start(args, count);
	return 1;
}

int main() 
{
	int sum = good_code(3, 1, 2, 3);
	printf("sum = %d.", sum);
	return 0;
}
```

然后把它编译、汇编后看看它的汇编代码：

```asm {6-13, 48-51, 19-23}
00000000 <good_code>:
   0:	fb010113          	addi	sp,sp,-80
   4:	02112623          	sw	ra,44(sp)
   8:	02812423          	sw	s0,40(sp)
   c:	03010413          	addi	s0,sp,48
  10:	fca42e23          	sw	a0,-36(s0)
  14:	00b42223          	sw	a1,4(s0)
  18:	00c42423          	sw	a2,8(s0)
  1c:	00d42623          	sw	a3,12(s0)
  20:	00e42823          	sw	a4,16(s0)
  24:	00f42a23          	sw	a5,20(s0)
  28:	01042c23          	sw	a6,24(s0)
  2c:	01142e23          	sw	a7,28(s0)
  30:	00000797          	auipc	a5,0x0
  34:	0007a783          	lw	a5,0(a5) # 30 <good_code+0x30>
  38:	0007a703          	lw	a4,0(a5)
  3c:	fee42623          	sw	a4,-20(s0)
  40:	00000713          	li	a4,0
  44:	02040793          	addi	a5,s0,32
  48:	fcf42c23          	sw	a5,-40(s0)
  4c:	fd842783          	lw	a5,-40(s0)
  50:	fe478793          	addi	a5,a5,-28
  54:	fef42423          	sw	a5,-24(s0)
  58:	00100793          	li	a5,1
  5c:	00078713          	mv	a4,a5
  60:	00000797          	auipc	a5,0x0
  64:	0007a783          	lw	a5,0(a5) # 60 <good_code+0x60>
  68:	fec42683          	lw	a3,-20(s0)
  6c:	0007a783          	lw	a5,0(a5)
  70:	00f6c7b3          	xor	a5,a3,a5
  74:	00000693          	li	a3,0
  78:	00078663          	beqz	a5,84 <.L3>
  7c:	00000097          	auipc	ra,0x0
  80:	000080e7          	jalr	ra # 7c <good_code+0x7c>

00000084 <.L3>:
  84:	00070513          	mv	a0,a4
  88:	02c12083          	lw	ra,44(sp)
  8c:	02812403          	lw	s0,40(sp)
  90:	05010113          	addi	sp,sp,80
  94:	00008067          	ret

00000098 <main>:
  98:	fe010113          	addi	sp,sp,-32
  9c:	00112e23          	sw	ra,28(sp)
  a0:	00812c23          	sw	s0,24(sp)
  a4:	02010413          	addi	s0,sp,32
  a8:	00300693          	li	a3,3
  ac:	00200613          	li	a2,2
  b0:	00100593          	li	a1,1
  b4:	00300513          	li	a0,3
  b8:	00000097          	auipc	ra,0x0
  bc:	000080e7          	jalr	ra # b8 <main+0x20>
  c0:	fea42623          	sw	a0,-20(s0)
  c4:	fec42583          	lw	a1,-20(s0)
  c8:	00000517          	auipc	a0,0x0
  cc:	00050513          	mv	a0,a0
  d0:	00000097          	auipc	ra,0x0
  d4:	000080e7          	jalr	ra # d0 <main+0x38>
  d8:	00000793          	li	a5,0
  dc:	00078513          	mv	a0,a5
  e0:	01c12083          	lw	ra,28(sp)
  e4:	01812403          	lw	s0,24(sp)
  e8:	02010113          	addi	sp,sp,32
  ec:	00008067          	ret
```

在`main`函数里，若干个参数被传入，显然是把这些参数放在了寄存器里面。然后在`good_code`里，首先把这些参数从寄存器里挪到了内存里面去。然后`va_start`的实现看上去就是把`va_list`
当作一个指针指向了可变参数里的第一个参数。

这样就能揣摩出这几个宏是怎么实现的了。首先声明一下，下面的`sizeof`对应的大小都是跟4字节对齐了的`sizeof`，比如一个`short`是2字节的，也得当作4字节。首先，`va_start`需要传入`va_list`和可变参数前面的那一个参数，于是我们可以取得这个参数的地址，然后加上`sizeof`这个参数，就可以得到可变参数里的第一个参数的地址，并赋给`va_list`。

然后`va_arg`就对应的是遍历参数，这里我们的实现思路就是：根据给出的不同的类型，解引用当前的`va_list`，得到这个参数，然后给`va_list`加上`sizeof`这个类型。

最后的`va_end`就当作给`va_list`赋值为空指针吧。

另外还有个`va_copy`，在这里就被直接当作普普通通的指针的复制就行了。

### 基础设施(2)

现在我们又回到了NEMU去完成一些必要的基础设施。

#### 指定trace输出的时机和条件

根据教程中所说，很容易能找到记录itrace的地方，而指定其输出条件的地方则是在这里：

```c title="$NEMU_HOME/src/cpu/cpu-exec.c"
static void trace_and_difftest(Decode *_this, vaddr_t dnpc)
{
#ifdef CONFIG_ITRACE_COND
    if (ITRACE_COND)
    {
        log_write("%s\n", _this->logbuf);
    }
#endif
    if (g_print_step)
    {
        IFDEF(CONFIG_ITRACE, puts(_this->logbuf));
    }
    IFDEF(CONFIG_DIFFTEST, difftest_step(_this->pc, dnpc));
#ifdef CONFIG_WATCHPOINT
    bool check_wp();
    bool checked = check_wp();
    if (checked)
    {
        nemu_state.state = NEMU_STOP;
    }
#endif
}
```

而这个`ITRACE_COND`一开始是在Kconfig生成出来的一个C语言的宏`CONFIG_ITRACE_COND`，然后通过Makefile中给cflags添进去的宏：

```make title="$NEMU_HOME/Makefile"
CFLAGS_TRACE += -DITRACE_COND=$(if $(CONFIG_ITRACE_COND),$(call remove_quote,$(CONFIG_ITRACE_COND)),true)
```

itrace因为是大佬们写的，所以输出挺规整的。因此可以考虑用`grep`，`awk`，`sed`等等工具进行筛选处理。这些我还都不是很熟。之后学学吧。

#### 实现iringbuf

说实话，如果实现成像教程里面那样的格式还挺难的，一般来说我只能保证最后一行是导致崩溃的那一条指令。因为在之后添加了输入、中断机制等等之后没有办法去预测接下来会执行的指令。

不过还是照样可以用ring buffer来实现的。很典型的要用两个指针来表示数据的开头和结尾。不过需要注意的是为了判断空和满需要特殊处理，因为这两个状态下的两个指针的相对状态都一样。

核心代码如下：

```c title="$NEMU_HOME/src/cpu/iringbuf.c"
static size_t nxt_idx(int idx)
{
    return (idx + 1) % NR_IRINGBUF;
}

IR *push_ir()
{
    IR *tmp = iringbuf + tail;
    if (tail == head && !first)
    {
        head = nxt_idx(head);
    }
    tail = nxt_idx(tail);
    first = false;
    return tmp;
}

void print_ir()
{
    if (first)
        return;
    size_t idx = head;
    puts(iringbuf[idx].logbuf);
    log_write("%s\n", iringbuf[idx].logbuf);
    idx = nxt_idx(idx);
    while (idx != tail)
    {
        puts(iringbuf[idx].logbuf);
        log_write("%s\n", iringbuf[idx].logbuf);
        idx = nxt_idx(idx);
    }
}
```

这是使用方式：

```c title="$NEMU_HOME/src/cpu/cpu-exec.c" {31-32, 41}
static void exec_once(Decode *s, vaddr_t pc)
{
    s->pc = pc;
    s->snpc = pc;
    isa_exec_once(s);
    cpu.pc = s->dnpc;
#ifdef CONFIG_ITRACE
    char *p = s->logbuf;
    p += snprintf(p, sizeof(s->logbuf), FMT_WORD ":", s->pc);
    int ilen = s->snpc - s->pc;
    int i;
    uint8_t *inst = (uint8_t *)&s->isa.inst.val;
    for (i = ilen - 1; i >= 0; i--)
    {
        p += snprintf(p, 4, " %02x", inst[i]);
    }
    int ilen_max = MUXDEF(CONFIG_ISA_x86, 8, 4);
    int space_len = ilen_max - ilen;
    if (space_len < 0)
        space_len = 0;
    space_len = space_len * 3 + 1;
    memset(p, ' ', space_len);
    p += space_len;

    void disassemble(char *str, int size, uint64_t pc, uint8_t *code,
                     int nbyte);
    disassemble(p, s->logbuf + sizeof(s->logbuf) - p,
                MUXDEF(CONFIG_ISA_x86, s->snpc, s->pc),
                (uint8_t *)&s->isa.inst.val, ilen);

    IR *new_ir = push_ir();
    strcpy(new_ir->logbuf, s->logbuf);
#endif
}

...

void assert_fail_msg()
{
    isa_reg_display();
    print_ir();
    statistic();
}
```

效果如图，这是模拟器自带的映像跑得结果，和itrace的输出格式上长的一模一样：

```
0x80000000: 00 00 02 97 auipc   t0, 0
0x80000004: 00 02 88 23 sb      zero, 0x10(t0)
0x80000008: 01 02 c5 03 lbu     a0, 0x10(t0)
0x8000000c: 00 10 00 73 ebreak
```

#### 实现mtrace

实现方式很简单，就像教程里面所说的一样。

```c title="$NEMU_HOME/src/memory/paddr.c"
static void print_paddr_read(paddr_t addr, int len, word_t res)
{
#ifdef CONFIG_MTRACE
    if (MTRACE_COND)
    {
        log_write(FMT_WORD ",%d,r"
                           ": " FMT_WORD "\n",
                  addr, len, res);
    }
#endif
    //		printf(FMT_WORD ",%d,r" ": " FMT_WORD "\n", addr, len, res);
}

word_t paddr_read(paddr_t addr, int len)
{
    word_t res = 0;
    if (likely(in_pmem(addr)))
    {
        res = pmem_read(addr, len);
        print_paddr_read(addr, len, res);
        return res;
    }
    IFDEF(CONFIG_DEVICE, res = mmio_read(addr, len); return res);
    out_of_bound(addr);
    return 0;
}

static void print_paddr_write(paddr_t addr, int len, word_t res)
{
#ifdef CONFIG_MTRACE
    if (MTRACE_COND)
    {
        log_write(FMT_WORD ",%d,w"
                           ": " FMT_WORD "\n",
                  addr, len, res);
    }
#endif
    //		printf(FMT_WORD ",%d,w" ": " FMT_WORD "\n", addr, len, res);
}

void paddr_write(paddr_t addr, int len, word_t data)
{
    if (likely(in_pmem(addr)))
    {
        pmem_write(addr, len, data);
        print_paddr_write(addr, len, data);
        return;
    }
    IFDEF(CONFIG_DEVICE, mmio_write(addr, len, data); return);
    out_of_bound(addr);
}
```

然后我们可以照猫画虎地，像itrace一样做一个mtrace的Kconfig的配置：

```kconfig
config MTRACE
	depends on TRACE && TARGET_NATIVE_ELF && ENGINE_INTERPRETER
	bool "Enable memory tracer"
	default y

config MTRACE_COND
	depends on MTRACE
	string "Only trace memory when the condition is true"
	default "true"
```

然后测试一下NEMU自带的映像，会输出这样的内存访问踪迹：

```
0x80000000,4,r: 0x00000297
0x80000004,4,r: 0x00028823
0x80000010,1,w: 0x00000000
0x80000008,4,r: 0x0102c503
0x80000010,1,r: 0x00000000
0x8000000c,4,r: 0x00100073
```

#### 消失的符号

原因是这些东西不会被`add.c`以外的文件所用到，所以也就不必出现在符号表中。

参考《Learning Linux Binary Analysis》书中对ELF符号的定义：

> Symbols are a symbolic reference to some type of data or code such as a global variable or function.

而对于宏而言，它既不是变量也更不是函数，所以也不会出现在符号表中。

#### 寻找"Hello World!"

写个简单Hello World之后，发现事情并不简单。利用上述方法，首先发现这个字符串放在了ELF文件的0x2000附近：

```
00002000  01 00 02 00 48 65 6c 6c  6f 20 57 6f 72 6c 64 21  |....Hello World!|
```

然后观察到，它实际上是在.rodata这个section里面。

```
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
...
  [18] .rodata           PROGBITS         0000000000002000  00002000
       0000000000000011  0000000000000000   A       0     0     4
...
  [29] .strtab           STRTAB           0000000000000000  000033a0
       00000000000001da  0000000000000000           0     0     1
```

猜测可能是因为字符串字面量属于是一种不可变的量，然后把它放在rodata里更合适。更重要的是，程序运行并不需要有.strtab，也就是说它都不用被载入到内存中去，如果Hello World被放在这.strtab里面那运行时都找不到了。

#### 实现ftrace

实现ftrace的主要难点在于读明白`man 5 elf`，然后就会写了。

关于ELF文件的知识，教程里已经说的很详细了，不过要注意的是，在Section Headers里面识别出每个Section的名字当然是需要另一个特别给出的字符串表，即.shstrtab。它所在的section下标能在ELF的head里面找到。另外，由于ELF格式是跨平台的，为了include解析ELF文件内容所需要的`elf.h`，可以直接include host机上的`elf.h`。

我的ftrace实现策略如下：

1. 在`parse_args`中添加一个参数选项，允许放一个ELF文件的文件路径在那儿。
2. 在程序运行前初始化ftrace，读入符号表识别其中的所有函数，把函数的地址信息、名字放到NEMU的一个线性表里。
3. 阅读riscv32手册后，会知道`ra`是放返回地址的寄存器。显然如果要函数返回的话，必须从`ra`读出值来，所以肯定是让`jalr`来做的。而函数调用则既可以用`jal`来小跳，也可以用`jalr`来大跳，具体可以参考伪指令`call`和`ret`。然后就在之前指令执行的地方稍微改改代码就可以了。
4. 修改一下Kconfig等等内容，让它更加易用。

下面是我的实现：

```c title="$NEMU_HOME/src/isa/riscv32/inst.c"
INSTPAT("??????? ????? ????? ??? ????? 11011 11", jal    , J, 
		R(rd) = s->snpc; 
		s->dnpc = imm + s->pc; 
		call_trace(s->pc, s->dnpc);
		);
INSTPAT("??????? ????? ????? 000 ????? 11001 11", jalr   , I, 
		R(rd) = s->snpc;
		s->dnpc = (src1 + imm) & (~1);
		if (rd == 0 && rs1 == 1)
			return_trace(s->pc);	
		else
			call_trace(s->pc, s->dnpc);
		);
```

```c title="$NEMU_HOME/src/cpu/ftrace.c"
#include <cpu/ftrace.h>
#include <elf.h>
#include <common.h>

#define TYPE_CALL true
#define TYPE_RETURN false

static Elf32_Off strtab_off;
static uint32_t strtab_size;
static Elf32_Off symtab_off;
static uint32_t symtab_size;
static uint16_t	sh_off;
static uint16_t sh_size;
static uint16_t sh_num;
static size_t func_num = 0;
static int spaces = 0;

typedef struct Func_Info {
	union {
		char name[255];
		uint32_t idx;
	};
	paddr_t addr;
	paddr_t size;
} FI;

FI *finfo = NULL;

void init_ftrace(const char *elf_file) {
	func_num = 0;
	spaces = 0;
	//use assert() to make sure elf_file is a valid elf file.
	FILE *f = fopen(elf_file, "rb");
	assert(f);
	Elf32_Ehdr ehdr;
	size_t fread_res = 0;
	fread_res = fread(&ehdr, 1, sizeof(ehdr), f);
	assert(fread_res);
	assert(ehdr.e_ident[EI_MAG0] == ELFMAG0);
	assert(ehdr.e_ident[EI_MAG1] == ELFMAG1);
	assert(ehdr.e_ident[EI_MAG2] == ELFMAG2);
	sh_off = ehdr.e_shoff;
	sh_size = ehdr.e_shentsize;
	sh_num = ehdr.e_shnum;
	
	Elf32_Shdr shdr;
	uint16_t shstrndx = ehdr.e_shstrndx;
	fseek(f, sh_off + shstrndx * sizeof(shdr), SEEK_SET);
	fread_res = fread(&shdr, 1, sizeof(shdr), f);
	Elf32_Off shstrtab_off = shdr.sh_offset;	

	char buf[255];
	for (int i = 0; i < sh_num; i++) {
		fseek(f, sh_off + i * sizeof(shdr), SEEK_SET);
		fread_res = fread(&shdr, 1, sizeof(shdr), f);
		assert(fread_res);
		if (shdr.sh_type == SHT_SYMTAB) {
			symtab_off = shdr.sh_offset;
			symtab_size = shdr.sh_size;
		}
		else if (shdr.sh_type == SHT_STRTAB) {
			uint32_t name = shdr.sh_name;
			fseek(f, shstrtab_off + name, SEEK_SET);
			char *_ = fgets(buf, 255, f);
			assert(_);
			if (strcmp(buf, ".strtab") == 0) {
				strtab_off = shdr.sh_offset;
				strtab_size = shdr.sh_size;
			}
		}
	}
	
	Elf32_Sym stbl;
	size_t sym_num = symtab_size / sizeof(stbl); 
	fseek(f, symtab_off, SEEK_SET);
	for (size_t i = 0; i < sym_num; i++) {
		fread_res = fread(&stbl, 1, sizeof(stbl), f);
		assert(fread_res);
		func_num += stbl.st_info == 18;
	}
	finfo = (FI *)malloc(sizeof(FI) * func_num);

	fseek(f, symtab_off, SEEK_SET);
	size_t idx = 0;
	for (size_t i = 0; i < sym_num; i++) {
		fread_res = fread(&stbl, 1, sizeof(stbl), f);
		assert(fread_res); 
		if (stbl.st_info != 18)
			continue;
		finfo[idx].addr = stbl.st_value;
		finfo[idx].size = stbl.st_size;
		finfo[idx++].idx = stbl.st_name;
	}

	char *_ = NULL;
	for (size_t i = 0; i < func_num; i++) {
		fseek(f, strtab_off + finfo[i].idx, SEEK_SET);
		_ = fgets(finfo[i].name, 255, f);
		assert(_);
	}
	fclose(f);
}

__attribute__((unused)) static void print_trace(vaddr_t inst_addr, size_t func_idx, bool type) {
/*
  printf(FMT_WORD ": " , inst_addr);
	for (int j = 0; j < spaces; j++)
		printf(" ");
	if (type)
		printf("call ");
	else
		printf("ret  ");
	printf("[%s@" FMT_WORD "]\n", finfo[func_idx].name, finfo[func_idx].addr);
*/
#ifdef CONFIG_FTRACE
	if (FTRACE_COND) {
		log_write(FMT_WORD ": ", inst_addr);
		for (int j = 0; j < spaces; j++)
			log_write(" ");
		if (type)
			log_write("call ");
		else
			log_write("ret  ");
		log_write("[%s@" FMT_WORD "]\n", finfo[func_idx].name, finfo[func_idx].addr);
	}
#endif
}

void call_trace(vaddr_t inst_addr, vaddr_t pc) {
#ifdef CONFIG_FTRACE
	for (size_t i = 0; i < func_num; i++) {
		if (pc == finfo[i].addr) {
			print_trace(inst_addr, i, TYPE_CALL);
			spaces += 2;
			break;
		}
	}
#endif
}

void return_trace(vaddr_t inst_addr) {
#ifdef CONFIG_FTRACE
	for (size_t i = 0; i < func_num; i++) {
		if (inst_addr >= finfo[i].addr &&
				inst_addr < finfo[i].addr + finfo[i].size) {
			spaces -= 2;
			print_trace(inst_addr, i, TYPE_RETURN);
			break;
		}
	}
#endif
}
```

其他的诸如修改Kconfig、改NEMU参数传入的事情就和之前的差不多，这里就不过多赘述。

这是跑`cpu-tests/tests/string.c`的一个ftrace的输出案例：
```
0x8000000c: call [_trm_init@0x8000012c]
0x8000013c:   call [main@0x80000028]
0x80000044:     call [strcmp@0x800001ec]
0x80000214:     ret  [strcmp@0x800001ec]
0x8000004c:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x80000058:     call [strcmp@0x800001ec]
0x80000214:     ret  [strcmp@0x800001ec]
0x80000060:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x80000074:     call [strcmp@0x800001ec]
0x80000214:     ret  [strcmp@0x800001ec]
0x8000007c:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x80000090:     call [strcmp@0x800001ec]
0x80000214:     ret  [strcmp@0x800001ec]
0x80000098:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x800000ac:     call [strcmp@0x800001ec]
0x80000214:     ret  [strcmp@0x800001ec]
0x800000b4:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x800000c8:     call [strcpy@0x8000014c]
0x80000178:     ret  [strcpy@0x8000014c]
0x800000d0:     call [strcat@0x80000188]
0x800001dc:     ret  [strcat@0x80000188]
0x800000d8:     call [strcmp@0x800001ec]
0x80000214:     ret  [strcmp@0x800001ec]
0x800000e0:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x800000f4:     call [memset@0x80000218]
0x80000234:     ret  [memset@0x80000218]
0x80000100:     call [memcmp@0x80000238]
0x80000270:     ret  [memcmp@0x80000238]
0x80000108:     call [check@0x80000010]
0x80000014:     ret  [check@0x80000010]
0x8000011c:   ret  [main@0x80000028]
```

这里的`_trm_init`函数没有返回很正常，因为根据`$AM_HOME/am/src/platform/nemu/trm.c`，它跑完`main`函数的东西就直接进了个`halt`函数，这个函数直接触发`NEMU_TRAP`了，也就是直接一个ebreak指令，然后机器就停机了，所以那肯定没有返回。

#### 不匹配的函数调用和返回

由于编译器不同，我的函数调用踪迹略显不同，但是仍然具有代表性：

```
0x8000000c: call [_trm_init@0x80000258]
0x80000268:   call [main@0x800001cc]
0x800001ec:     call [f0@0x80000010]
0x80000050:       call [f3@0x80000108]
0x8000016c:         call [f2@0x800000a4]
0x800000f0:           call [f1@0x8000005c]
0x80000098:             call [f0@0x80000010]
0x80000050:               call [f3@0x80000108]
0x8000016c:                 call [f2@0x800000a4]
0x800000f0:                   call [f1@0x8000005c]
0x80000098:                     call [f0@0x80000010]
0x80000050:                       call [f3@0x80000108]
0x8000016c:                         call [f2@0x800000a4]
0x800000f0:                           call [f1@0x8000005c]
0x80000098:                             call [f0@0x80000010]
0x80000050:                               call [f3@0x80000108]
0x8000016c:                                 call [f2@0x800000a4]
0x800000f0:                                   call [f1@0x8000005c]
0x80000098:                                     call [f0@0x80000010]
0x80000050:                                       call [f3@0x80000108]
0x8000016c:                                         call [f2@0x800000a4]
0x800000f0:                                           call [f1@0x8000005c]
0x80000098:                                             call [f0@0x80000010]
0x80000058:                                             ret  [f0@0x80000010]
0x80000100:                                           ret  [f2@0x800000a4]//注释
```

比如这里的注释处的call和ret并不匹配，正好出现在`f0`作为一个叶子函数被`f1`调用的时候。

为了更好的理解这一行为，我们可以对照地看一下`f1`的C语言实现和反汇编：

```asm {16, 17}
8000005c <f1>:
8000005c:	00000797          	auipc	a5,0x0
80000060:	27878793          	addi	a5,a5,632 # 800002d4 <lvl>
80000064:	0007a703          	lw	a4,0(a5)
80000068:	00b75463          	bge	a4,a1,80000070 <f1+0x14>
8000006c:	00b7a023          	sw	a1,0(a5)
80000070:	00000717          	auipc	a4,0x0
80000074:	26870713          	addi	a4,a4,616 # 800002d8 <rec>
80000078:	00072783          	lw	a5,0(a4)
8000007c:	00178793          	addi	a5,a5,1
80000080:	00f72023          	sw	a5,0(a4)
80000084:	00a05c63          	blez	a0,8000009c <f1+0x40>
80000088:	00158593          	addi	a1,a1,1
8000008c:	fff50513          	addi	a0,a0,-1
80000090:	00000797          	auipc	a5,0x0
80000094:	2347a783          	lw	a5,564(a5) # 800002c4 <func>
80000098:	00078067          	jr	a5
8000009c:	00100513          	li	a0,1
800000a0:	00008067          	ret
```

```c {4}
int f1(int n, int l) {
  if (l > lvl) lvl = l;
  rec ++;
  return n <= 0 ? 1 : func[0](n - 1, l + 1);
};
```

然后我们设想一下，已知这个`f1`函数一定是另一个函数（比如`f2`）调用的，然后假设`f1`里面参数`n`被传入的是一个1，那么`f1`又调用了`f0`函数，那么就一定会有`f0`的返回值被返回给`f1`，然后`f1`又将它原封不动地返回给了`f2`。所以，如果你是编译器，为什么不直接把`f0`的返回值直接给`f2`呢？

于是，编译器就是这么做的：`f1`在调用`f0`采取的是`jr`伪指令，其实就是`jalr x0, 0(rs1)`，这就意味着他不会把`f1`的返回地址保存到`ra`寄存器里，而是让`ra`寄存器仍然保存的是`f2`处的返回地址，这样，当`f0`返回时，就会直接返回到`f2`了，能够提升一些效率。

#### 冗余的符号表

经过试验，hello程序可以运行。很显然，符号表里面存储的ELF符号信息对于程序的执行并没有什么作用。而且从ELF文件的Program Headers里面并不需要加载这些符号信息到内存中去也证实了这一点。

用缺失了符号表的hello.o去尝试链接自然是不行的，例如一个程序要从`_start`开始，这个外部的`_start`要去调用hello.o里的`main`，结果在符号表里根本找不到`main`，就直接链接不上了。

#### trace与性能优化

暂时还没给我的NEMU做过任何优化，跑个马里奥都卡卡的。

#### 如何生成native的可执行文件

之前的解耦的架构起了效果，现在可以试着把AM里的软件先在`native`上调对再来运行！不过为了弄懂`native`，还是看看Makefile比较好。

接上文的[[pa2#阅读Makefile|AM中的程序是如何构建的]]，为数不多的区别就在于，`$AM_HOME/Makefile`里include的是`$AM_HOME/scripts/native.mk`，并且所用的工具链都是本机的原生工具链，没有进行交叉编译。

#### 奇怪的错误码

对于为什么错误码是1，我们可以先假设一下`check`失败。所以我们可以看一下`check`函数的`native`实现：

```c title="am-kernels/tests/cpu-tests/include/trap.h"
__attribute__((noinline)) void check(bool cond)
{
    if (!cond)
        halt(1);
}
```

这里会调用TRM的halt，参数为1。而`native`里面TRM是这样实现的`halt`：

```c title="$AM_HOME/am/src/native/trm.c"
void halt(int code)
{
    const char *fmt = "Exit code = 40h\n";
    for (const char *p = fmt; *p; p++)
    {
        char ch = *p;
        if (ch == '0' || ch == '4')
        {
            ch = "0123456789abcdef"[(code >> (ch - '0')) & 0xf];
        }
        putch(ch);
    }
    __am_exit_platform(code);
    putstr("Should not reach here!\n");
    while (1)
        ;
}
```

这里有关输出退出码信息到串口上的方式感觉非常炫技，挺有意思。不过更重要的是在`__am_exit_platform`中干了调用了`exit(code)`，因此这个运行在Linux上的`native`程序的退出码是1。

对于make程序如何得到这个错误码，我认为应该是因为make程序作为父进程，可以读它的子进程（运行在`native`上的软件）结束后的PCB所记录的退出码。在这里我用系统调用踪迹证实了这一点。

这是我的检查步骤：

1. 我略微修改了`$AM_HOME/tests/cpu-tests/tests/add.c`，让它一定会`check`失败。
2. 我把`$AM_HOME/tests/cpu-tests/Makefile`中删除掉了“删除生成的`Makefile.add`的命令”
3. 利用strace进行追踪，并用nvim看内容。具体而言是`strace -f make -s -f Makefile.add ARCH=native run &| nvim -`这条命令

下面就是strace的输出内容了：

```sh {30-31}
...

clone3({flags=CLONE_VM|CLONE_VFORK|CLONE_CLEAR_SIGHAND, exit_signal=SIGCHLD, stack=0x7babf327c000, stack_size=0x9000}, 88strace: Process 342900 attached
 <unfinished ...>
[pid 342900] rt_sigprocmask(SIG_BLOCK, NULL, ~[KILL STOP], 8) = 0
[pid 342900] getuid()                   = 1000
[pid 342900] setresuid(-1, 1000, -1)    = 0
[pid 342900] getgid()                   = 1000
[pid 342900] setresgid(-1, 1000, -1)    = 0
[pid 342900] rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
[pid 342900] execve("/home/lijn/ics2024/am-kernels/tests/cpu-tests/build/add-native.elf", ["/home/lijn/ics2024/am-kernels/te"...], 0x5bab3011c4c0 /* 86 vars */ <unfinished ...>

...

[pid 342900] write(1, "E", 1E)           = 1
[pid 342900] write(1, "x", 1x)           = 1
[pid 342900] write(1, "i", 1i)           = 1
[pid 342900] write(1, "t", 1t)           = 1
[pid 342900] write(1, " ", 1 )           = 1
[pid 342900] write(1, "c", 1c)           = 1
[pid 342900] write(1, "o", 1o)           = 1
[pid 342900] write(1, "d", 1d)           = 1
[pid 342900] write(1, "e", 1e)           = 1
[pid 342900] write(1, " ", 1 )           = 1
[pid 342900] write(1, "=", 1=)           = 1
[pid 342900] write(1, " ", 1 )           = 1
[pid 342900] write(1, "0", 10)           = 1
[pid 342900] write(1, "1", 11)           = 1
[pid 342900] write(1, "h", 1h)           = 1
[pid 342900] write(1, "\n", 1)          = 1
[pid 342900] exit_group(1)              = ?
[pid 342900] +++ exited with 1 +++
<... wait4 resumed>[{WIFEXITED(s) && WEXITSTATUS(s) == 1}], 0, NULL) = 342900
write(2, "make: *** [/home/lijn/ics2024/ab"..., 82make: *** [/home/lijn/ics2024/abstract-machine/scripts/native.mk:21: run] Error 1
) = 82
rt_sigprocmask(SIG_BLOCK, [HUP INT QUIT TERM XCPU XFSZ], NULL, 8) = 0
rt_sigprocmask(SIG_UNBLOCK, [HUP INT QUIT TERM XCPU XFSZ], NULL, 8) = 0
chdir("/home/lijn/ics2024/am-kernels/tests/cpu-tests") = 0
close(1)                                = 0
exit_group(2)                           = ?
+++ exited with 2 +++
```

显然pid为342900的进程就是跑的测试程序，也就是`add-native.elf`，而make程序用一个wait4系统调用去获取了它所clone3出来的进程的退出信息。由于退出码为1，所以make程序就这样输出出来了。

感觉这个问题有点超纲，我是做了清华大学的rCore-OS进而对操作系统有了更深入的了解之后才能够合理猜测出来的。