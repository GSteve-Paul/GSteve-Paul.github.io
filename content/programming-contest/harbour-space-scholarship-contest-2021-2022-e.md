---
title: Harbour.Space Scholarship Contest 2021-2022 E题
date: 2024-04-14
tags:
  - 算法题解
---
原题链接： https://codeforces.com/problemset/problem/1553/E

好题，一个思维层次比较高的题目。

# 题意：
- 首先，我们有一个长度为$n$的初始排列，即$[1,2,3,...,n]$。
- 然后，我们将排列往右循环移动$k$位，$0 \leq k \leq n - 1$。
- 最后，我们把排列中的任意两个数字交换，这个交换操作最多只能进行$m$次。

输入给定$n$,$m$和目标排列，需要我们找到所有可能的$k$的值。

# 题目分析

## 朴素想法

首先我们可以很朴素地想到一个做法：首先枚举$k$，然后判断这每一种循环移动后能不能在$m$次的交换次数内变成目标排列。

伪代码如下：

```c++
int origin_per[maxn];
int obj_per[maxn];
for (int k = 0; k <= n - 1; k++)
{
    moved_per := cycle_move(origin_per);
    if (count_swap(moved_per,obj_per) < m)
    {
        //这个k是合法的
    }
}
```

## count_swap()

对于如何编写`count_swap()`，我们可以抽象成以下问题：

有两个长度都为$n$的排列$A$,$B$，只有一种操作也就是把$A$中的任意两个数字进行交换，那么求使得$A$变成$B$的最小交换次数。

这是一个很经典的问题，我们可以建图来解决：对于$A$中的每一个数字$A[i]$，它必然是在$B$中出现了的，我们记这个数字在$B$中出现的地方为$idx$，那么我们连一条有向边$A[i] \rightarrow A[idx]$，最后会形成一个图，图里面有很多的环，我们记环的个数为$cyc$。交换的次数是$n -cyc$。

## 枚举k

刚才讲到的`count_swap()`过程的时间复杂度是$O(n)$的，如果真按这样子来，那么我们的算法的时间复杂度将来到$O(n^2)$，对于本题来说，这是不可接受的。所以我们也许需要一个更加聪明的枚举$k$的方法，比如说，如果我们可以轻松的跳过一些$k$那就好了。

我们考虑一下这个事情：

它在循环移动之后只有$m$次进行交换操作的机会。而一次交换最多可以使得两个数字可以回到它应该存在的位置。设$cnt$是循环移动$k$次后的排列与目标排列对的上的数字的个数，那么这个$k$可以是答案的前提就是$n - cnt \leq 2m$，也就是对不上号的数字的个数一定小于等于$2m$。那么这个前提条件也等价于：$cnt \geq n - 2m$，而根据题目数据，有$m \leq \frac{n}{3} $，所以但凡满足了$cnt \geq n - 2m$，肯定也能满足$cnt \geq \frac{n}{3}$。

我们再考虑一个问题：能满足$cnt \geq \frac{n}{3}$的$k$有多少个呢？首先我们还是要意识到$cnt$是循环移动$k$次后的排列与目标排列对的上的数字的个数。而对于目标排列上的任意一个数字$num$，有且只有一个$k$可以使得循环移动后数组的$num$的位置和目标排列中的$num$数字的位置一样。也就是说，式子$\sum^{n-1}_{k=0} cnt_k = n$是恒成立的。因此，能满足$cnt \geq \frac{n}{3}$的$k$不能超过3个。事实上，$cnt \geq n - 2m$是一个更加严格的条件，那么能满足的$k$那肯定只能更少了。

因此，我们只要在枚举$k$地同时，$O(1)$地得到$cnt$，那么我们就可以做到一个$O(n)$的时间复杂度了。

# 细节

## count_swap()算法的原理

https://blog.csdn.net/yunxiaoqinghe/article/details/113153795

## 如何得到$cnt$

遍历目标排列，对于里面的第$i$位上的数字$p[i]$，它的原始位置肯定就是$p[i]$，那么也就相当于是把这个数字从$p[i]$往右一直循环移动到了$i$这个地方来。循环滚动的次数就是$i - p[i]$或者是$n - p[i] + i$，总之可以写成是$(i - p[i] + n) \mod n$。那么我们就这样记录即可。

# 代码
```c++
#include <bits/stdc++.h>

using namespace std;

const int maxn = 3e5 + 5;

int n, m;
int p[maxn];
int idx[maxn];
int a[maxn];

int same[maxn];
int nxt[maxn];
int vis[maxn];

void solve()
{
    cin >> n >> m;
    for (int i = 1; i <= n; i++)
        cin >> p[i];
    for (int i = 1; i <= n; i++)
        idx[p[i]] = i;
    fill(same + 1, same + n + 1, 0);
    for (int i = 1; i <= n; i++)
        same[(i - p[i] + n) % n]++;
    vector<int> ans;
    for (int i = 0; i <= n - 1; i++)
    {
        if (same[i] < n - 2 * m) continue;
        int tot = 0;
        for (int j = n + 1 - i; j <= n; j++)
            a[++tot] = j;
        for (int j = 1; j <= n - i; j++)
            a[++tot] = j;
        for (int j = 1; j <= n; j++)
            nxt[a[j]] = a[idx[a[j]]];
        int cyc = 0;
        fill(vis + 1, vis + n + 1, 0);
        for (int j = 1; j <= n; j++)
        {
            if (vis[a[j]]) continue;
            cyc++;
            int tmp = a[j];
            vis[tmp] = 1;
            do
            {
                tmp = nxt[tmp];
                vis[tmp] = 1;
            } while (tmp != a[j]);
        }
        int res = n - cyc;
        if (res <= m)
            ans.push_back(i);
    }
    cout << ans.size() << " ";
    for (int item: ans)
        cout << item << " ";
    cout << "\n";
}


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
        solve();
    return 0;
}
```