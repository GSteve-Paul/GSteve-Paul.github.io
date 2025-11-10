---
title: 可重复组合数的计算
date: 2025-11-09
tags:
  - 数学
---
## 概念

可重复组合数和常规的组合数并不相同。可重复组合数是指，给出 $n$ 种物品（假设 $n$ 种物品都是足够的，且同种物品都是等价的），要求从这 $n$ 种物品中拿出 $k$ 个物品有多少种组合。
### 例子

显然，生活中有很多这样的例子。就例如一个简单的数学问题，设代数 $x_1, x_2, x_3$，求问这 3 个代数可以生成多少个二次项？

建模成上面的概念也就是，有 3 种物品（分别是 $x_1, x_2, x_3$），要求计算出这 3 种物品中拿出 2 个物品的组合数。

通过简单的枚举法，可以发现能够 $x_1^2, x_2^2, x_3^2, x_1x_2, x_1x_3, x_2x_3$ 总共 6 个二次项。

## 算法

显然我们不可以每次都依赖手动枚举，这样效率太低。为了方便叙述，我们先用下面这个符号表示从这 $n$ 种物品中拿出 $k$ 个物品的组合数。

$$
\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right)
$$

首先给出结论

$$
\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right) = \binom{n + k - 1}{k}
$$

^f1b958

## 证明

### 数学归纳法

#### 递推式

首先我们考虑一下 $\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right)$ 是否存在有一个递推式。答案是有的。这里也是首先给出结论：

$$
\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right) = \sum_{i=0}^k{\left (\!\left ( \begin{matrix} n - 1 \\ i \end{matrix} \right)\!\right)}
$$

^181b65

还是刚才的[[#例子|例子]]，对于 $x_3$ 而言，这 6 个二次项可以分为 3 类：

1. $x_1^2,x_2^2,x_1x_2$
2. $x_1x_3,x_2,x_3$
3. $x_3^2$

这样的分类很自然：毕竟生成的二次项中，$x_3$ 要么是 0 次，1 次或者 2 次。

那么，对于 $x_3$ 为 0 次项的时候，它结合的就是 $x_1, x_2$ 生成的 2 次项；对于 $x_3$ 为 1 次项的时候，它结合的则是 $x_1, x_2$ 生成的 1 次项……以此类推，你就明白了上面的这个递推式。

此外，不难定义一些边界：

1. 生成 0 次项：

$$
\forall{n \in \mathbb{Z}^+ },k=0, \;\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right) = 1
$$

2. 单个物品：

$$
\forall{k \in \mathbb{Z}^+ },n=1, \;\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right) = 1
$$

#### 数学归纳法证明

首先对于上面提到的这些边界，显然是符合[[#^f1b958|结论]]的。也就是说：

$$
\forall{k\in\mathbb{N}} \;\land\;n=1, \;\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right)=\binom{n + k - 1}{k}
$$

那么假设当 $n=s$ 时，$\forall{k\in\mathbb{N}^+}, \;\left (\!\left ( \begin{matrix} s \\ k \end{matrix} \right)\!\right)=\binom{s + k - 1}{k}$，试证明当 $n=s+1$ 时，有 $\forall{k\in\mathbb{N}}, \;\left (\!\left ( \begin{matrix} s+1 \\ k \end{matrix} \right)\!\right)=\binom{s+1 + k - 1}{k}=\binom{s+k}{k}$

引入我们之前提到的[[#^181b65|递推式]]，其实就是试证：

$$
\sum_{i=0}^k{\left (\!\left ( \begin{matrix} s \\ i \end{matrix} \right)\!\right)}=\binom{s+k}{k}
$$

我们把假设带入进上式，并把组合数改写成阶乘的形式，其实就是试证：

$$
\frac{(s+k-1)!}{k!(s-1)!}+\frac{(s+k-2)!}{(k-1)!(s-1)!}+\ldots+\frac{(s-1)!}{0!(s-1)!}=\frac{(s+k)!}{s!k!}
$$

我们稍加整理，实际上就是试证：

$$
\frac{(s+k-1)!s}{s!k!}+\frac{(s+k-2)!sk}{s!k!}+\ldots+\frac{(s-1)!sk(k-1)\ldots1}{s!k!}=\frac{(s+k)!}{s!k!}
$$

现在既然通分了，自然可以只看分子了。所以其实就是试证：

$$
(s+k-1)!s+(s+k-2)!sk+\ldots+(s-1)!sk(k-1)\ldots1=(s+k)!
$$

这个时候我们不妨对等式两边不断地减去等号左边的单项式，我们会发现它具有一定的规律：

这是减去了第一个单项式：

$$
\begin{aligned}
&(s+k-2)!sk+\ldots+(s-1)!sk(k-1)\ldots1\\=&(s+k)!-(s+k-1)!s\\=&
(s+k-1)!(s+k)-(s+k-1)!s\\=&(s+k-1)!k
\end{aligned}
$$
接着减去第二个单项式：

$$
\begin{aligned}
&(s+k-3)!sk(k-1)+\ldots+(s-1)!sk(k-1)\ldots1\\=
&(s+k-1)!k-(s+k-2)!sk\\=
&(s+k-2)!k(s+k-1)-(s+k-2)!sk\\=
&(s+k-2)!k(k-1)
\end{aligned}
$$

最后不断地减下去……显然，剩下的会是这样：

$$
\begin{aligned}
&0\\=
&(s+k-k)!k(k-1)\ldots1-(s+k-(1+k))!sk(k-1)\ldots1\\=
&(s+k-(1+k))!k(k-1)\ldots1(s+k-k)-(s+k-(1+k))!sk(k-1)\ldots1\\=
&(s+k-(1+k))!k(k-1)\ldots1(k-k)\\=
&0
\end{aligned}
$$

因此得证有：当 $n=s+1$ 时，有 $\forall{k\in\mathbb{N}}, \;\left (\!\left ( \begin{matrix} s+1 \\ k \end{matrix} \right)\!\right)=\binom{s+1 + k - 1}{k}=\binom{s+k}{k}$

所以：

$$
\left (\!\left ( \begin{matrix} n \\ k \end{matrix} \right)\!\right) = \binom{n + k - 1}{k}
$$

### 一种形象的证明

这个证明来源于[维基百科](https://en.wikipedia.org/wiki/Combination#Number_of_combinations_with_repetition)：

首先我们可以这个问题看作是如下一个方程的自然数解的数量：

$$
x_1+x_2+\ldots+x_n=k
$$

关于上述丢番图方程（Diophantine equation）的解，可以用如下方式表示： 

先画出 $x_1$ 个星星（★），接着放一个分隔符（竖线 |），  再画出 $x_2$ ​ 个星星，然后再放一个分隔符，  以此类推。

在这种表示法中，星星的总数是 $k$，而分隔符的数量是 $n - 1$（因为要把一个整体分成  $n$ 份，需要 $n-1$ 个分隔符）。  

因此，一串包含 $k + n - 1$（或写作 $n + k - 1$）个符号（星星与竖线）的序列，如果其中有 $k$ 个位置放的是星星，那么就对应一个方程的解。

换句话说：  每一个解都可以通过在这 $k + n - 1$ 个位置中选择 $k$ 个位置放星星（剩下的放竖线）来表示。

例如，方程

$$x_1 + x_2 + x_3 + x_4 = 10$$

（其中 $n = 4$，$k = 10$）的一个解

$$x_1 = 3, \; x_2 = 2, \; x_3 = 0, \; x_4 = 5$$

可以表示为：

★ ★ ★ | ★ ★ | | ★ ★ ★ ★ ★