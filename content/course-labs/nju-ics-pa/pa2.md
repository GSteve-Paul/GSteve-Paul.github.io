---
title: PA2
tags:
  - 模拟器
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

## 基础设施(2)