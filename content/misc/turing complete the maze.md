---
title: 图灵完备——迷宫关
date: 2026-06-22
tags:
  - 游戏
---
Steam 上有一款游戏叫作 [Turing Complete](https://store.steampowered.com/app/1444480/Turing_Complete/)， 这款游戏会从基本的门电路开始手把手带你搭建一个计算机出来。我感觉这个游戏挺有意思的，所以我去年把它买了，稍微玩了一会儿，就只是做了几个很简单的门电路。最近突然又想要继续玩这个游戏，于是把游戏原存档重置之后又是开玩！大概过去一天时间，我已经搭建出来了一个很简单的计算机，并且在上面可以运行很简易的程序。

在搭建出简易计算机后，这个游戏有一个关卡是让你写一段程序让机器人可以逃出迷宫。这个程序接受的输入是机器人所感知到的前方的方块信息，然后可以向机器人输出接下来的行动方式，进而控制机器人走向出口。

![](https://file.stevepaul101.net/20260623003952_1.jpg)


> [!warning] 一定要通关
> 只有成功通过这个关卡，才能不被外星人吃掉！所以，一定要活下来啊！！！


观察到迷宫路线是单连通的，迷宫的入口和出口都在迷宫的最边缘上。所以我们可以认为这个入口和出口处于迷宫的同一面墙皮上。因此我们可以使用[沿墙法](https://zh.wikipedia.org/w/index.php?title=%E8%A7%A3%E8%BF%B7%E5%AE%AE%E6%BC%94%E7%AE%97%E6%B3%95&section=3#%E6%B2%BF%E7%89%86%E6%B3%95)解决这个问题。

在实现中，我使用沿墙法的右手规则。机器人的行走实际上是一个循环的过程——在每一次迭代中，机器人首先会观察周围的方块是否是出口。如果是出口，就直接出门即可；如果没有任何一个方向是出口，机器人就会按照右、前、左、后的顺序依次判定是否可走。如此循环往复，就会发现机器人会沿着迷宫边缘墙皮一直前进，并且最终到达出口。

---

具体实现如下：

> [!info] 汇编指令
> `jz` = jump if zero；
> `j` = always jump

```text
const LEFT 0
const FORWARD 1
const RIGHT 2
const IDLE 3
const INTERACT 4
const ATTACK 5

const EMPTY 0
const WALL 1
const DOOR 3
const COIN 8

label loop

# check door
DOOR
reg0_to_reg2
in_to_reg1
sub
finish
jz
RIGHT
reg0_to_out
in_to_reg1
sub
finish
jz
RIGHT
reg0_to_out
in_to_reg1
sub
finish
jz
RIGHT
reg0_to_out
in_to_reg1
sub
finish
jz

# back to original direction
RIGHT
reg0_to_out

# try right
RIGHT 
reg0_to_out
return1
reg0_to_reg4
try_forward
j
label return1

# try original direction
LEFT
reg0_to_out
return2
reg0_to_reg4
try_forward
j
label return2

# try left
LEFT
reg0_to_out
return3
reg0_to_reg4
try_forward
j
label return3

# try left + left(backwards)
LEFT
reg0_to_out
try_forward
j

label finish
INTERACT
reg0_to_out

label try_forward
in_to_reg1
EMPTY
reg0_to_reg2
sub
forward
jz
COIN
reg0_to_reg2
sub
forward
jz
reg4_to_reg0
j

label forward
FORWARD
reg0_to_out
loop
j
```

可以发现我的 `label try_forward`的设计是有点意思的。这段代码的语义是，针对目前机器人的朝向判断前方是否可以前进，如果可以则前进，如果不可以则尝试下一个。不妨把跳转到`try_forward`的指令看作一次“简陋”的函数调用，我将`try_forward`失败后应该返回的PC提前写入到了reg4中，并且在`try_forward`的最后把reg4恢复到了reg0中，并强行跳转回去，就实现了一次“简陋”的函数调用。

同时，我的代码中没有label的地址超过了63，这就意味着我在跳转到某个label时只需要一个立即数即可，不需要额外构造出一些较大的数字。

<p><video controls src="https://file.stevepaul101.net/turing_complete_maze_video.mp4"></video></p>

另外，写这个代码给我的感觉还挺独特的。这种底层语言终究是没有类似于C这样的高级语言写起来顺手，但是在目前这个LLM辅助编程大行其道的时代，古法编程一次性写出来了这样的代码倒是很有成就感。