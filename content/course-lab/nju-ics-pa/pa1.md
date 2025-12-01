---
title: PA1
tags:
  - 模拟器
  - 调试器
---
PA1中会指导我们补充NEMU框架，进而用C语言构建出一个最基本的计算机。

## 阶段1

### 在开始愉快的PA之旅之前

首先当然是在红白机模拟器里玩一玩俄罗斯方块。孩子，我其实就是个用软件模拟出来的硬件。
![](https://file.stevepaul.cc/2025-07-17-20-17-57.png)

我当然是选择了看上去最容易的RISCV32，我也并不是一边做实验一边写心得而是过了5个月才写的心得，~~所以相当于二刷了~~。

### 开天辟地的篇章

####  计算机可以没有寄存器吗? (建议二周目思考)

能。因为我们完全可以试着用内存模拟寄存器的操作。这样会把硬件提供的编程模型（见The RISC-V Instruction Set Manual Volume I的2.1节）中的寄存器都消灭掉，取而代之的是内存中的特殊内存块，以及相对应的专门操作这些特殊内存块的特殊指令。

####  从状态机视角理解程序运行

人脑模拟图灵机即可。这是为了引入“程序是一个状态机”这个思想。

### RTFSC

####  需要多费口舌吗?

当然是从`main`函数开始看啦。不过程序不是从`main`函数作为最开始的……不然`main`函数的参数又得从哪里来呢？这个问题我之后再说吧。


可以用`make -nB`让`make`程序以"只输出命令但不执行"的方式强制构建目标。

由于我用`clangd`作为`LSP`，所以我利用`bear`去产生`compile_commands.json`，即:
```bash
bear --output ./compile_commands.json -- make
```
进而辅助`LSP`分析项目。

####  kconfig生成的宏与条件编译

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

####  为什么全部都是函数?

分离模拟器里的各个部件，尽量解耦。

####  参数的处理过程

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

这里教程要求解决教程中故意留下的一个错误。解决这个错误很简单，只需要删去两行代码即可。
```diff title="$NEMU_HOME/src/monitor/monitor.c" showLineNumbers{35}
- Log("Exercise: Please remove me in the source code and compile NEMU again.");
- assert(0);
```

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

####  究竟要执行多久？

`cpu_exec`的函数原型长这个样子：
```c
void cpu_exec(uint64_t n);
```
这确保了这个`-1`会被认为是一个无符号数，也就是`uint64_t`下的最大的无符号数，结合到目前CPU的执行速度，这会让它跑尽可能长的时间。

####  潜在的威胁（建议二周目思考）

可以看下stackoverflow上的[这个问题](https://stackoverflow.com/questions/50605/signed-to-unsigned-conversion-in-c-is-it-always-safe)的高赞回答，引用的就是[C99 Standard文档](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf)的内容。按照这里的说法，`-1`将会被`+(ULONG_MAX + 1)`变成`ULONG_MAX`。对于补码机器，实际上就是内存里的位就没变。

####  谁来指示程序的结束?

通过后文知识可得，运行完`main`函数后一定会进行一个系统调用`sys_exit`以结束进程。

####  有始有终 (建议二周目思考)

从程序是个状态机的角度而言，其初始状态的构建即程序的开始，其状态机所转移到的终态即程序的结束。

对于 GNU/Linux上的程序，当一个进程调用一个系统调用`sys_execve`，开始把一个新程序的数据载入到内存并构建对应的进程上下文的时候，就算做这个程序的开始。而当这个进程调用一个系统调用`sys_exit`时，会结束进程并释放一些资源，这代表着这个程序的结束。

而对于NEMU里的程序，当将一个程序的镜像文件读入到内存，并把寄存器、PC等设置成合适的值的时候，也就是程序的开始。而当这个程序运行到了`nemu_trap`，也就是RISCV32里的`ebreak`指令的时候，就是程序的结束。

`nemu_trap`用于指示程序的结束，也表示这个程序的状态机不会再进行转移，否则这个状态机停不下来。而monitor可以方便程序员从程序运行时的状态观察程序，方便理解程序的行为。

####  为NEMU编译时添加GDB调试信息

由于GDB调试信息这种东西一定是从编译期间保留的，所以我们主要得去看Makefile的代码。这里我写一下我的一个方法：

1. 利用`make -nB`，打印没有添加GDB调试信息后的Makefile的输出信息，保存到文件命名为`debuginfo.txt`
2. 将`debuginfo.txt`用`sed`工具进行格式化，具体是这样:
   ```bash
	sed 's/$/\n/' debuginfo.txt | sed 's/ \+/\n/g' > debuginfo_better.txt
	```
	意思就是先将Makefile的每条输出信息间插空行，再将空格转化为换行。

	然后我们就可以看到这种更加人性化的信息：
	```sh
	echo
	+
	CC
	src/nemu-main.c
	
	mkdir
	-p
	/home/lijn/ics2024/nemu/build/obj-riscv32-nemu-interpreter/src/
	
	gcc
	-O2
	-MMD
	-Wall
	-Werror
	-I/home/lijn/ics2024/nemu/include
	-I/home/lijn/ics2024/nemu/src/isa/riscv32/include
	-I/home/lijn/ics2024/nemu/src/engine/interpreter
	-O3
	-flto
	-DITRACE_COND=true
	-DMTRACE_COND=true
	-DFTRACE_COND=true
	-DDTRACE_COND=true
	-DETRACE_COND=true
	-D__GUEST_ISA__=riscv32
	-c
	-o
	/home/lijn/ics2024/nemu/build/obj-riscv32-nemu-interpreter/src/nemu-main.o
	src/nemu-main.c
	```
	
	同理，在添加调试信息的情况下对Makefile的输出进行相同处理。

 3. 用`git diff`进行比对，就能发现区别了

当然，上述的生成信息的指令可以减化为
```sh
make -nB | sed 's/$/\n/' | sed 's/ \+/\n/g' > nodebuginfo_better.txt
```

而`git diff`会产生下面这样的东西
```diff
diff --git a/nodebuginfo_better.txt b/debuginfo_better.txt
index ffe5739..d4482c0 100644
--- a/nodebuginfo_better.txt
+++ b/debuginfo_better.txt
@@ -17,6 +17,8 @@ gcc
 -I/home/lijn/ics2024/nemu/src/engine/interpreter
 -O3
 -flto
+-Og
+-ggdb3
 -DITRACE_COND=true
 -DMTRACE_COND=true
 -DFTRACE_COND=true
@@ -58,6 +60,8 @@ gcc
 -I/home/lijn/ics2024/nemu/src/engine/interpreter
 -O3
 -flto
+-Og
+-ggdb3
 -DITRACE_COND=true
 -DMTRACE_COND=true
 -DFTRACE_COND=true
@@ -99,6 +103,8 @@ gcc
 -I/home/lijn/ics2024/nemu/src/engine/interpreter
 -O3
 -flto
+-Og
+-ggdb3
 -DITRACE_COND=true
```

所以我们在不查阅Makefile代码的情况下，就知道了添加GDB调试信息，其实就是在编译的时候加上几个flag而已。

然后呢，你可以从Makefile文件中得到证实：
```make title="$NEMU_HOME/Makefile" showLineNumbers{48}
CFLAGS_BUILD += $(if $(CONFIG_CC_DEBUG),-Og -ggdb3,)
```

而关于这两个flag呢，就可以看GCC的手册了，在`Options for Debugging Your Program`这一节就能看到这些内容：

`-Og`

> If you are not using some other optimization option, consider using -Og
   with  -g.   With no -O option at all, some compiler passes that collect
   information useful for debugging do not run at all,  so  that  -Og  may
   result in a better debugging experience.

`-ggdb`

> Produce  debugging  information  for use by GDB.  This means to use
   the most expressive format available (DWARF, stabs, or  the  native
   format if neither of those are supported), including GDB extensions
   if at all possible.

#### 优美地退出

从返回的错误信息可以知道，是`main`的返回值有问题。

这个主要考查使用GDB调试的能力，原因是在按`q`后的处理函数中没有将`nemu_state`正确设置为`NEMU_QUIT`，导致最后`is_exit_status_bad`函数返回错误。

所以简单的修改一下就可以：

```c title="$NEMU_HOME/src/monitor/sdb/sdb.c" 
static int cmd_q(char *args)
{
    nemu_state.state = NEMU_QUIT;
    return -1;
}
```

现在感觉PA1真的好简单，不过当时在做的时候还是挺慢的。

### 基础设施

虽然我把这些基础设施都实现了，不过我还是觉得这个假GDB并不是很好用……但是有一句话是真的：随着时间的推移,，发现同一个bug所需要的代价会越来越大。

#### 如何测试字符串处理函数?

可以生成一大堆测试用例，然后把自己写的字符串处理函数处理出的结果和glibc库里的做对比。

#### 实现单步执行，打印寄存器，扫描内存

单步执行就是调用一下`cpu_exec`即可，不多赘述。

单步执行的指令会被打印出来，是因为`cpu_exec`中设置了`g_print_step`的值，它直接决定了`execute`函数中`trace_and_difftest`中会不会打印信息。这些打印信息的获取在`exec_once`函数中有体现。
```c title="$NEMU_HOME/src/cpu/cpu-exec.c" {9-12}
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

因为寄存器是和ISA相关的，所以每种ISA都有自己的一个`isa_reg_display`函数。我的实现形式如下：

```c title="$NEMU_HOME/src/isa/riscv32/reg.c"
void isa_reg_display()
{
    int regs_cnt = sizeof(regs) / sizeof(const char *);
    for (int i = 0; i < regs_cnt; i++)
    {
        printf("%s %#x %u\n", regs[i], gpr(i), gpr(i));
    }
}
```


扫描内存就是使用`paddr_read`去读取某地址的某长度的内存。

## 阶段2
### 表达式求值

首先我们需要进行词法分析：把每一个token识别出来。在这里需要简单学习一些关于正则表达式的知识，可以通过[这个网站](https://regexlearn.com/zh-cn)进行学习。

```c title="$NEMU_HOME/src/monitor/sdb/expr.c"
static struct rule
{
    const char *regex;
    int token_type;
} rules[] = {

    /* TODO: Add more rules.
     * Pay attention to the precedence level of different rules.
     */

    {" +", TK_NOTYPE},        // spaces
    {"\\+", '+'},             // plus
    {"-", '-'},               // minus or neg
    {"\\*", '*'},             // multiply
    {"/", '/'},               // divide
    {"\\(", '('},             // left parenthesis
    {"\\)", ')'},             // right parenthesis
    {"[0-9]+", TK_DEC},       // decimal
};
```

`make_token`函数并不是很复杂，其含义就是遍历整个字符串，每次用一个正则表达式看能否匹配，能匹配上就生成一个新的token。

需要注意的是，对于十进制数我们需要在`tokens`里面记录新的token的`str`，这需要我们用`strncpy`这样的函数，而这个函数在某些情况下不会自己在末尾加`'\n'`。

对于缓冲区溢出的问题，我选择检查这个token的长度，若长度超过了31，把它当作一个非预期情况，直接`assert(0)`。这遵循了下面提到的KISS法则。

####  为什么printf()的输出要换行?

因为`printf`有一个缓冲区，遇到`'\n'`才会把缓冲内容送到输出设备。如果没有`\n`，那么很有可能程序因为某些原因崩溃而缓冲区内容没有输出出去。

stackoverflow上有一个类似的[问题](https://stackoverflow.com/questions/39180642/why-does-printf-not-produce-any-output)，也可以看看。

#### 实现算术表达式的递归求值

然后我们需要做的事情就是表达式求值，根据表达式的BNF定义，我们可以用分治法进行求值。

检查一个表达式的左右括号是否匹配，这是个很经典的问题，我们可以用栈去模拟括号匹配即可。

而我为了得到主运算符的位置特意编写了一个函数，这个函数首先用栈模拟了括号的匹配，当栈为空的时候才代表着所扫描到的符号不在括号内，然后就可以在这样的情形下记录优先级最小值。需要注意的是因为结合性的问题，我们应该找最后的优先级最小的符号。

```c title="$NEMU_HOME/src/monitor/sdb/expr.c"
for (int i = 0; i < tot2; i++)
{
	int curprior = prior(tokens[ops[i]].type);
	if (curprior <= mnprior)
	{
		mnprior = curprior;
		op_type = tokens[ops[i]].type;
	}
}
```

#### 实现带有负数的算术表达式的求值 (选做)

多了个负号，我们可以简单地扩展一下之前的BNF定义：

```
<expr> ::= <number>    
  | "(" <expr> ")"     
  | <expr> "+" <expr>  
  | <expr> "-" <expr>  
  | <expr> "*" <expr>
  | <expr> "/" <expr>
  | "-" <expr>
```

考虑如何区别减号和负号。根据第三条定义，减号的前面一定是一个表达式的最后一个字符。而跟据前两个定义，可以知道表达式的最后一个字符要么是一个数字，要么是右括号。因此减号前面必定是一个数字或一个右括号。同理进行分析，负号前面可以是：`'+'`，`'-'`，`'*'`，`'/'`，`'('`或者`ε`这些符号。这样，我们就可以通过`"-"`前面的字符进行区别减号和负号了。

我们不妨扩展一下，如果你把加减乘除号都当作二元运算符，而负号当作是一元运算符，那么按照上述的分析就是，所有的一元运算符号前面都会是二元运算符号或`'('`或`ε`。所有的二元运算符号前面都会是一个数字或一个右括号。因此上面的方法可以用于判断字符相同的一元和二元运算符。

除此之外，我们还需要考虑负号的优先级，它的优先级应该要比其他二元运算符更高。其结合性和二元运算符也不一样，它是最前面的符号被最后运算，因此寻找主运算符的位置的遍历顺序可能需要向下面类似地修改一下。
```c title="$NEMU_HOME/src/monitor/sdb/expr.c"
if (is_unary_operator(op_type))
{
	for (int i = 0; i < tot2; i++)
	{
		if (mnprior == prior(tokens[ops[i]].type))
		{
			op = ops[i];
			break;
		}
	}
}
else if (is_binary_operator(op_type))
{
	for (int i = tot2 - 1; i >= 0; i--)
	{
		if (mnprior == prior(tokens[ops[i]].type))
		{
			op = ops[i];
			break;
		}
	}
}
```

#### 表达式生成器如何获得C程序的打印结果?

框架代码里的`popen`非常有意思，通过`man 3 popen`就能够知道如何获得这个C程序的打印结果了。

> The return value from popen() is a normal standard I/O stream in  all
   respects  save  that  it  must  be  closed  with pclose() rather than
   fclose(3).  Writing to such a stream writes to the standard input  of
   the command; the command's standard output is the same as that of the
   process  that  called  popen(), unless this is altered by the command
   itself.  Conversely, reading from  the  stream  reads  the  command's
   standard output, and the command's standard input is the same as that
   of the process that called popen().

```c {4,5} title="$NEMU_HOME/tools/gen-expr/gen-expr.c"
fp = popen("/tmp/.expr", "r");
assert(fp != NULL);

int result;
ret = fscanf(fp, "%d", &result);

pclose(fp);
```

#### 为什么要使用无符号类型？(建议二周目思考)

首先，无符号数更加贴近于内存中的raw data的概念。此外，[无符号类型的溢出](https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Unsigned-Overflow.html)是有定义的，但是[有符号类型的溢出](https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Signed-Overflow.html)原则上是未定义的，所以我们除非阅读编译器的实现，否则不知道会算出来个什么东西。

为了保证表达式进行无符号运算，我们把所有的生成的数字后面跟上一个u就行了。

#### 除0的确切行为

它所构造的C源文件会包含有除0表达式，这在编译的时候就会发生警告，在运行的时候能跑但是输出的结果会不正确。

#### 过滤除0行为的表达式

因为除0表达式会导致编译器的警告，所以我在编译时带上`-Wall`，`-Werror`，这样就可以直接编译失败，返回错误码，进而过滤掉除0行为。

```c title="$NEMU_HOME/tools/gen-expr/gen-expr.c"
int ret = system("gcc /tmp/.code.c -Wall -Werror -O0 -g3 -o /tmp/.expr "
				 "1> /dev/null 2> /dev/null");
if (ret != 0)
	continue;
```

#### 实现表达式生成器

有了上面的实现，其实这里就变得很简单了。只需要一点点地慢慢测试和debug即可。

## 阶段3

### 监视点

#### 扩展表达式求值的功能

之前做负号的时候已经都讲明白了，现在只不过多添加几个token的type和相匹配的正则表达式，并且更新一下优先级、结合性即可。

#### 实现监视点池的管理

其实这是一个链表的练习。实现起来也很简单，就不多做赘述。我的代码稍微修改了一下函数原型，让它更容易使用。

```c title="$NEMU_HOME/src/monitor/sdb/watchpoint.c"
void init_wp_pool()
{
    int i;
    for (i = 0; i < NR_WP; i++)
    {
        wp_pool[i].NO = i;
        wp_pool[i].next = (i == NR_WP - 1 ? NULL : &wp_pool[i + 1]);
    }

    head = NULL;
    free_ = wp_pool;
}

static void get_wp(int NO, WP **ptr_before, WP **ptr_target, bool *success)
{
    *ptr_before = NULL;
    *ptr_target = head;
    *success = false;
    while (*ptr_target != NULL)
    {
        if ((*ptr_target)->NO == NO)
        {
            *success = true;
            return;
        }

        *ptr_before = *ptr_target;
        *ptr_target = (*ptr_target)->next;
    }
}

int new_wp(char *expression)
{
    if (free_ == NULL)
    {
        assert(0);
    }
    WP *res = free_;
    free_ = free_->next;
    strcpy(res->expression, expression);
    bool success = false;
    res->last_value = expr(expression, &success);
    assert(success);
    res->hit = 0;
    res->next = head;
    head = res;
    return res->NO;
}

void free_wp(int NO, bool *success)
{
    WP *ptr_before, *ptr_target;
    get_wp(NO, &ptr_before, &ptr_target, success);
    if (!*success)
    {
        return;
    }
    if (ptr_before != NULL)
    {
        ptr_before->next = ptr_target->next;
    }
    else
    {
        head = ptr_target->next;
    }
    ptr_target->next = free_;
    free_ = ptr_target;
}
```

#### 温故而知新

`static`关键字能够让这个全局变量/函数只能在本C源文件中被看到。这样可以体现封装性，只开放特定的接口。

#### 实现监视点

判断是否触发监视点十分简单，只需要遍历链表，对每个监视点的表达式求值即可，我的这一实现可以允许多个监视点的触发。

```c title="$NEMU_HOME/src/monitor/sdb/watchpoint.c"
bool check_wp()
{
    WP *ptr = head;
    bool watch_checked = false;
    while (ptr != NULL)
    {
        bool success = false;
        word_t current_value = expr(ptr->expression, &success);
        assert(success);
        if (current_value != ptr->last_value)
        {
            ptr->hit++;
            watch_checked = true;
            printf("Watch: NO="
                   "%d"
                   " expr="
                   "%s"
                   " old value=" MUXDEF(
                       PMEM64, "%#018x %lu",
                       "%#010x %u") " new value=" MUXDEF(PMEM64, "%#018x %lu",
                                                         "%#010x %u"
                                                         "\n"),
                   ptr->NO, ptr->expression, ptr->last_value, ptr->last_value,
                   current_value, current_value);
            ptr->last_value = current_value;
        }
        ptr = ptr->next;
    }
    return watch_checked;
}
```

然后修改一下`trace_and_difftest`函数的内容，添加一些条件宏语句。

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

最后在Kconfig中照猫画虎地写一个配置出来就行了。

```kconfig {3-5} title="$NEMU_HOME/Kconfig" showLineNumbers{127}
menu "Testing and Debugging"

config WATCHPOINT
	bool "Enable watchpoint"
	default y

config TRACE
  bool "Enable tracer"
  default y
```

这样，在`make menuconfig`中启用了监视点后，就会自动生成一个宏，进而能够启用了。

```c title="$NEMU_HOME/include/generated/autoconf.h" 
#define CONFIG_WATCHPOINT 1
```

#### 你会如何测试你的监视点实现?

可以通过生成特定的映像文件和CPU状态来确定一个特定的NEMU状态，然后在这个状态上运行一些监视点的命令，确保能够正常运作。

不过我在实际操作时选择的是边用边测……

#### 强大的GDB

我们先举一个很简单的段错误的例子：

```c title="main.c"
void bad_code() 
{
	int *p = 0;
	*p = 1;
}

int main() 
{
	bad_code();
	return 0;
}
```

用这个命令去编译：

```sh
gcc main.c -g -o main
```

接着用GDB进行调试，它会告诉你段错误的位置信息，方便你调试。

```sh
GNU gdb (Ubuntu 15.0.50.20240403-0ubuntu1) 15.0.50.20240403-git
Copyright (C) 2024 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from ./main...
(gdb) run
Starting program: /home/lijn/Templates/main 

This GDB supports auto-downloading debuginfo from the following URLs:
  <https://debuginfod.ubuntu.com>
Enable debuginfod for this session? (y or [n]) y
Debuginfod has been enabled.
To make this setting permanent, add 'set debuginfod enabled on' to .gdbinit.
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Program received signal SIGSEGV, Segmentation fault.
0x000055555555513d in bad_code () at main.c:4
4		*p = 1;
(gdb) backtrace 
#0  0x000055555555513d in bad_code () at main.c:4
#1  0x0000555555555158 in main () at main.c:9
(gdb) 
```

不过事实上不是每次都有时间对一个会崩溃的程序再次用GDB调试启动，所以系统提供了一个功能，能在程序崩掉的时候，将程序的状态机（比如内存、寄存器）记录下来保存到一个core文件里，这样就可以通过这个文件恢复崩溃时的状态。这需要我们用一些命令进行简单的配置。

首先解除生成core文件的大小限制：

```sh
ulimit -c unlimited
```

然后可以用以下`gdb`命令进行调试：

```sh
gdb [path-to-exe] [path-to-core-file]
```

可以参考[这个提问](https://askubuntu.com/questions/1349047/where-do-i-find-core-dump-files-and-how-do-i-view-and-analyze-the-backtrace-st)。

#### sanitizer - 一种底层的assert

它的实现原理之后再看看吧，挖坑。

#### 如何提高断点的效率 (建议二周目思考)

这是因为，每次执行一条指令，所有的监视点就会被扫描，表达式就会被在运行时重算。

我们可以不采用监视点的方式实现断点。可以专门给断点设置一个线性表，从数据结构的角度优化效率。也可以对表达式做一个依赖管理，如果它所依赖的寄存器、内存没有变化过，那么就不需要重新计算。

事实上断点是[这样](http://eli.thegreenplace.net/2011/01/27/how-debuggers-work-part-2-breakpoints)实现的，感觉做完ICS-PA后阅读这篇文章容易了许多。

#### 一点也不能长?

确实不能。详见上面[这篇文章](https://eli.thegreenplace.net/2011/01/27/how-debuggers-work-part-2-breakpoints)的More on int 3这一节。如果它的指令长度变成了2字节，那么有可能会覆盖到两个一个字节的指令，靠前的那个指令还能识别出这个`int3`，靠后的那个指令被覆盖的部分只是`int3`的后部分，识别不出`int3`。如果有一个跳转指令让PC指向了原本靠后的那个指令，会导致执行到无效指令使得程序挂掉。

#### 随心所欲的断点

很显然这是不可以的，因为这会导致指令被破坏而无法被恢复。

首先我们需要学会在某个地址打断点，GDB可能会告诉你地址不可访问，可以参考一下[这个问题](https://stackoverflow.com/questions/44368703/gdb-cannot-insert-breakpoint-cannot-access-memory-at-address-xxx)，原因估计是重定位。

于是就这样实验了一下，程序很成功地崩溃掉了：

```sh
GNU gdb (Ubuntu 15.0.50.20240403-0ubuntu1) 15.0.50.20240403-git
Copyright (C) 2024 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from main...
(gdb) break *0
Breakpoint 1 at 0x0
(gdb) run
Starting program: /home/lijn/Templates/main 
Warning:
Cannot insert breakpoint 1.
Cannot access memory at address 0x0

(gdb) delete 
Delete all breakpoints, watchpoints, tracepoints, and catchpoints? (y or n) y
(gdb) disassemble main 
Dump of assembler code for function main:
   0x000055555555518d <+0>:	endbr64
   0x0000555555555191 <+4>:	push   %rbp
   0x0000555555555192 <+5>:	mov    %rsp,%rbp
   0x0000555555555195 <+8>:	mov    $0x0,%eax
   0x000055555555519a <+13>:	call   0x555555555149 <good_code>
   0x000055555555519f <+18>:	mov    $0x0,%eax
   0x00005555555551a4 <+23>:	pop    %rbp
   0x00005555555551a5 <+24>:	ret
End of assembler dump.
(gdb) break *0x000055555555519c
Breakpoint 2 at 0x55555555519c: file main.c, line 10.
(gdb) continue
Continuing.

Program received signal SIGSEGV, Segmentation fault.
0x0000555555551e49 in ?? ()
(gdb) 
```

#### NEMU的前世今生

模拟器是一个可以模拟硬件的程序，而调试器是一个能够观察、控制另外一个程序的程序。GDB是如何调试程序的，看看[这些文章](https://eli.thegreenplace.net/tag/debuggers)就能够略知一二了。

### 如何阅读手册

#### 尝试通过目录定位关注的问题

用搜索功能搜一下就知道在5.1.3节了。

## 实验报告

~~前面几问太简单懒得写了~~

#### shell命令

在Makefile里追加一些内容就好。要回到之前的分支，直接`git switch pa0`即可。

```make title="$NEMU_HOME/Makefile" showLineNumbers{72} 
.PHONY: count

count:
	git ls-files | grep "\.[c|h]" | xargs cat | grep "\S" | wc -l
```

#### RTFM

`-Wall`表示会产生所有的警告，`-Werror`表示任意的警告都会是错误。

使用它们能够让程序员尽早知道程序的一些问题并解决，减少调bug的时间。

