---
title: 图灵完备——全成就指南
date: 2026-08-29
---
Steam 上的图灵完备一共有10个成就，我在这里分享一下各个成就的达成方法：

## 图灵完备

这一成就只需要完成“图灵完备”这一关卡即可，按照游戏关卡一步步搭建即可。如果有问题可参考游戏中的提示和答案。

## 五门全加器

全加器相对于半加器额外多了一个进位输入$C_{i-1}$。因此对于全加器的总和输出$S_i$，实际上就是多加了一个进位输入$C_{i-1}$，也就是多异或一次即可，也就是说：

$$S_i=A_i \oplus B_i \oplus C_{i-1}$$

对于进位输出$C_i$，不妨分类讨论输入$A_i$和输入$B_i$的赋值为真的个数的情况。如果$A_i = B_i = 1$，必然是需要进位的。如果$A_i = B_i = 0$,即便$C_{i-1} = 1$，也无法进位。而当$A_i$和$B_i$中有1个为1，且$C_i$也为1，那么是需要进位的。因此可以得到如下等式： ^520312

$$C_i = (A_i \land B_i) \lor ((A_i \lor B_i) \land C_{i-1})$$

不过如果直接套用上面的公式，会用到三个门。所以我们要想办法简化一下。注意到上面我们把[[#^520312|上面的有1个为1]]翻译成了$\lor$，而实际上也可以翻译成$\oplus$，也就是：

$$C_i = (A_i \land B_i) \lor ((A_i \oplus B_i) \land C_{i-1})$$

这样就可以借用$S_i$里面用到的异或门，因而能只用五个门实现全加器。 

![](https://file.stevepaul101.net/20260829151600_1.jpg)

## 4 NAND = XOR

这关的要求是用4个与非门实现1个异或门。如果不考虑要求只用与非门，正常点的思路就是把或门里面输入都为1的情况去掉就好了。也就是：

$$A \oplus B = (A \operatorname{OR} B) \operatorname{AND} (A \operatorname{NAND} B)$$

然后用一些神秘的逻辑等值技巧，可以写成如下形式：

$$A \oplus B=\left(A \operatorname{NAND} (A \operatorname{NAND} B)\right)\operatorname{NAND}\left(B \operatorname{NAND} (A \operatorname{NAND} B)\right)$$

注意到里面的$A \operatorname{NAND} B$可以复用，所以实际上4个与非门就够了。

![](https://file.stevepaul101.net/20260829155014_1.jpg)

## 对称计算单元

这个成就要求不使用布尔元件通过“逻辑整合”关卡，实际上就是让玩家尽量用之前做好了的8位与非、8位非门和2-4译码器来通过本关，所以这个成就要想拿不到才比较费事。。。

![](https://file.stevepaul101.net/20260829155859_1.jpg)

## 七次和乘

这个成就要求你所实现的乘法器最多包含7个加法器。不妨考虑1个输入为$A$和$B$的8位乘法器该如何实现。由于$B$是一个8位二进制数，所以可以把它拆成$B_0,B_1, \ldots, B_7$。根据乘法的结合律，有：

$$AB = A\sum_{i=0}^{7}{2^iB_i}=\sum_{i=0}^{7}{2^iAB_i}$$
因此在电路中只需要把这7轮的$2^iAB_i$相加即可，正好就是7个加法器。具体到内部，这个$2^i$可以用逻辑左移实现，而$B_i$控制的就是是加上$0$还是加上$2^iA$。

![](https://file.stevepaul101.net/20260829161826_1.jpg)

## 十项条“件”

这个成就要求玩家用不超过10个元件实现条件判断。我个人在电路设计的角度上觉得这是最难达成的成就。但我在看了全球榜单后，意外发现这个成就有3.9%的达成率，并不是垫底的。而真正垫底的是汉诺塔，也许大家还是差点毅力吧😂。

![](https://file.stevepaul101.net/20260829162835_1.jpg)

不难看出，奇数条件码正好是和比它小1的偶数条件码的语义是相反的。所以我们可以先实现偶数条件码的语义（在作用范围上可以包含奇数条件码），然后用XOR判断一下条件码的最低位来实现。

- 永不成立可以先不管。
- 对于`value = 0`，可以通过把输入的8位全部或起来再取反来实现，并让这个判断的作用在所有`某1某`形式的条件码上，这样一来这个判断可以为条件码2、6提供正确值，而为条件码3、7提供错误值。
- 对于`value < 0`，只需要关心输入符号位（最高位）即可，并让这个判断的作用在所有`1某某`形式的条件码上，这样一来这个判断可以为条件码4、6提供正确值，而为条件码5、7提供错误值。

上面的叙述可能有点抽象。不过当你理解了之后就会发现另一个性质——条件码2,4和6存在这么一个关系：$2 \operatorname{bitor} 4 = 6$  ； $value = 0 \operatorname{OR} value < 0 = value \leq 0$。所以只需要把上面针对`value = 0`和`value < 0`的电路或起来，就可以正确处理所有偶数条件码情况了。

因此具体实现如下：

![](https://file.stevepaul101.net/20260829173408_1.jpg)

## 高速加法器

这一成就要求使用延迟量不超过17的电路通过“单字节加法”关卡。先不看延迟量的约束，如果单纯实现单字节加法有一个很朴素的方法是把7个全加器串联起来就好了，但是这样一来延迟全落在各个全加器上，就会很高。

注意到第$i$位的加法总是依赖于第$i-1$位加法的进位。而众所周知这个进位要么是0，要么是1。所以我们可以预先算好两种进位下第$i$位的加法结果，也就是先预处理出来 $A_i + B_i + 1$和 $A_i+B_i$ 。
然后再根据上一位的进位来选取对应的加法结果即可。

同样的道理，原先的全加器也可以进行改造：

![](https://file.stevepaul101.net/20260829232557_1.jpg)

而这一关的解法可以是如下电路：

![](https://file.stevepaul101.net/20260829232931_1.jpg)

## 二进制速算家

注意这关最高是7级，但是解锁7级需要先打通关6级一次才可以进入。第7级没有总和提示，所以~~可以在手机上算出具体的二进制数~~勤学苦练💪去吧！

## 除法器

这玩意儿可以模拟竖式除法，也就是每一位都进行试商，最后拼一块就能得到结果。大致的算法流程如下：

```python
quotient = 0
remainder = dividend

for i in range(BIT_WIDTH - 1, -1, -1):
    shifted_divisor = divisor << i

    # 当前余数足够减去这一位对应的除数
    if remainder >= shifted_divisor:
        remainder -= shifted_divisor
        quotient += 1 << i

return quotient, remainder
```

![](https://file.stevepaul101.net/20260829183001_1.jpg)

## 汉诺塔

这一成就只需要完成最后一关就好。这一关的关卡说明已经把算法透露得差不多了，如果还是不懂可以直接在网上查汉诺塔相关的算法讲解。这关需要注意的是在函数调用前后是需要保存一些寄存器的。

完成了这个关卡后，我才更加深入的理解了为什么RISCV里面会把寄存器分为调用方保存的寄存器和被调用方保存的寄存器。

代码如下：

```asm
in r1
in r2
in r4
in r3
call move

move: 
// r1 = disk_nr, r2 = source, r3 = spare, r4 = destination
cmp r1, 0
jne recursive_move
call print_move
ret
recursive_move:
push r1
push r2
push r3
push r4
push r5
sub r1, r1, 1
mov r5, r3
mov r3, r4
mov r4, r5
call move
pop r5
pop r4
pop r3
pop r2
pop r1
call print_move
push r1
push r2
push r3
push r4
push r5
sub r1, r1, 1
mov r5, r2
mov r2, r3
mov r3, r5
call move
pop r5
pop r4
pop r3
pop r2
pop r1
ret

print_move:
out r2
out 5
out r4
out 5
ret
```