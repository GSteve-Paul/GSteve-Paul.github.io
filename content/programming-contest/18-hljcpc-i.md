---
title: 第18届黑龙江省赛 I题
date: 2023-05-19
tags:
  - 算法题解
---
先贴个题目链接[I-Club](https://codeforces.com/gym/104363/problem/I)

这就是2023年黑龙江CCPC省赛的一个较难题目.

题面的英文质量不佳,简而言之就是有n个俱乐部,有m种奖章,要把奖章分发给这些俱乐部.其中一种奖章可以分发给多个俱乐部,一个俱乐部只能有一种奖章.

参赛选手每到一个俱乐部玩儿一次就可以得到这个俱乐部所对应的那一种奖章,可以重复地玩同一个俱乐部,需要求解的是得到所有奖章的玩的次数的最小期望.

<hr>

显然我们应该把这些奖章平摊给这些俱乐部,也就是使得每种奖章发配给俱乐部的数量尽量相同.比如n=9,m=3,每种奖章就应该发配给3个俱乐部.这样才会使得期望能够最小.

但是考虑到有n=8,m=3这种无法直接整除的情况,我们可以把奖章分为两类:

*   A类中的一种发配给俱乐部的数量是$\lceil \frac{n}{m} \rceil$
*   B类中的一种发配给俱乐部的数量是$\lceil \frac{n}{m} \rceil - 1$

因此,根据m,n恒定的原则,可以列出以下方程,来计算A类奖章的数量和B类奖章的数量.

$$
\begin{cases}
\ A + B = m\\
\ A × \lceil \frac{n}{m} \rceil + B × (\lceil \frac{n}{m} \rceil - 1) = n\\
\end{cases}
$$

解得:

$$
\begin{cases}
\ A = n + m - m × \lceil \frac{n}{m} \rceil \\
\ B = m - A\\
\end{cases}
$$

也能够很容易地得出要在玩耍时得到A类中某一种奖章的概率是 $p = \frac{\lceil \frac{n}{m} \rceil}{n}$

同理,在玩耍时得到B类中某一种奖章的概率是 $q = \frac{\lceil \frac{n}{m} \rceil - 1}{n}$

<hr>

为了求解这一问题,需要使用期望DP

设$dp_{i,j}$的含义是A类奖章还差$i$种就可以选完,B类奖章还差$j$种就可以选完的情况下需要进行的游戏次数.

那么易得$dp_{0,0} = 0$,毕竟奖章都拿全了,就不需要再玩了.

dp递推方程是:

$$
dp_{i,j} = (1 − p×i − q×j)×(dp_{i,j}+1) + p×i×(dp_{i−1,j}+1) + q×j×(dp_{i,j−1}+1)
$$

答案就是$dp_{A,B}$,就是奖章一个也没拿的情况.

下面给出解释:

试想一下: 假如这时候状态为A类奖章还差$i$种就可以选完,B类奖章还差$j$种就可以选完,而你现在决定要在某个俱乐部玩一把,则有三种情况:

1.  你玩到了新的A类奖章:概率为$p×i$(拿到某一种A类奖章的概率是$p$,此时还剩下$i$种A类的还没选),得到了之后的玩的次数将会是$dp_{i-1,j}$,算上这一次,则是$dp_{i-1,j}+1$
2.  同理,如果玩到了新的B类奖章:概率为$q×j$,玩的次数是$dp_{i,j-1}+1$
3.  压根没选到新的:概率为$1-p×i-q×j$,玩的次数是$dp_{i,j}+1$

最后对这个dp方程进行化简,得到:

$$
dp_{i,j} = \frac{p×i} {pi + qj} × dp_{i−1,j} + \frac{q×j}{ pi + qj }×dp_{i,j−1} + \frac{1} {pi + qj}
$$

<hr>

下面是AC代码: 需要注意判断一下边界条件,其他地方基本上没有坑点,属于是把DP方程想明白就能轻松过题.

```c++
#include <bits/stdc++.h>

using namespace std;

const int maxn = 1e5 + 5;
const int maxm = 5005;

int main()
{
    vector<vector<double>> dp;
    int n, m;
    cin >> n >> m;
    int A = n + m - m * ceil((double) n / m);
    int B = m - A;
    dp.resize(A + 1);
    for (auto &elem: dp)
        elem.resize(B + 1);
    double p = ceil((double) n / (double) m) / n;
    double q = (ceil((double) n / (double) m) - 1) / n;
    for (int i = 0; i <= A; i++)
    {
        for (int j = 0; j <= B; j++)
        {
            if (i == 0 && j != 0)
                dp[i][j] = q * j / (p * i + q * j) * dp[i][j - 1] + 1 / (p * i + q * j);
            else if (i != 0 && j == 0)
                dp[i][j] = p * i / (p * i + q * j) * dp[i - 1][j] + 1 / (p * i + q * j);
            else if (i == 0 && j == 0)
                dp[i][j] = 0;
            else
                dp[i][j] = p * i / (p * i + q * j) * dp[i - 1][j] + q * j / (p * i + q * j) * dp[i][j - 1] +
                           1 / (p * i + q * j);
        }
    }
    cout.precision(9);
    cout.setf(ios::fixed);
    cout << dp[A][B] << endl;
    return 0;
}
```
