---
title: Codeforces Round 725(Div.3) F题
date: 2023-06-29
tags:
  - Codeforces
---
先贴一个题目链接[F. Interesting Function](https://codeforces.com/contest/1538/problem/F)

<hr>

题意：

从$l$一直$+1$到$r$，问你在这一过程中数位变化的多少。

例如 $199+1 = 200 $数位变化了3位。

<hr>

运用我们的小学知识，我们可以知道每次$+1$至少会有个位会变化，而假如有后缀的9，因为会有进位，那么改变的数位会变多，比如$19 + 1 = 20$。

根据进位的性质，可以看出对于每个数字而言，其$+1$所引发变化的数位个数为后缀9的个数+1。

所以这个问题就变成了求$[l,r-1]$区间中 每个数字的后缀9的个数+1 的和。

这个问题可以转化为求$[0,r-1]$区间中 每个数字的后缀9的个数+1 的和 减去 $[0,l-1]$区间中 每个数字的后缀9的个数+1 的和。

<hr>

接下来可以引出两种解法,本质是相同的：

**一：**

假设我们并不知道数位DP。

如何求解$[0,1189]$ 区间中 每个数字的后缀9的个数+1 的和呢？

后面0个9的贡献：1189

后面1个9的贡献：因为该数字为1189，所以有119个。（0009，0019，...，1179，1189）

后面2个9的贡献：11个。（0099，0199，...，0999，1099）

...

以此类推，其实规律就变得很明显了。
代码大体这样：

```c++
#include <bits/stdc++.h>

using namespace std;
using ll = long long;

void solve()
{
    ll l, r;
    cin >> l >> r;
    ll asw = r - l;//对于0个9的贡献的简便处理
    r = r - 1;
    bool flag1 = 1;
    while(r)
    {
        if (r % 10 != 9)
        {
            flag1 = 0;
        }
        r /= 10;
        if (flag1)
        {
            asw += r + 1;
        }
        else
        {
            asw += r;
        }
    }
    l = l - 1;
    bool flag2 = 1;
    while(l)
    {
        if (l % 10 != 9)
        {
            flag2 = 0;
        }
        l /= 10;
        if (flag2)
        {
            asw -= l + 1;
        }
        else
        {
            asw -= l;
        }
    }
    cout << asw << "\n";
}

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) solve();
    return 0;
}
```

**二：**

假如你知道了数位DP：

根据以上规律，可以总结出这样的DP状态：

$dp[i][j]$：$i$表示已经填写了$len->pos+1$的数字，$j$表示此时的后缀$9$的个数

根据[大佬的思路](https://zhuanlan.zhihu.com/p/613107701)可以写出如下的记忆化搜索版本的数位DP：

```c++
#include <bits/stdc++.h>

using namespace std;
using ll = long long;

const int maxn = 9 + 5;

int a[maxn];
ll dp[maxn][maxn];

ll dfs(int pos, bool limit, int cnt)
{
    if (pos == 0) return cnt + 1;
    if (!limit && dp[pos][cnt]!=-1) return dp[pos][cnt];
    ll res = 0;
    int up = limit ? a[pos] : 9;
    for (int i = 0; i <= up; i++)
    {
        res = res + dfs(pos - 1, limit && i == up, i == 9 ? cnt + 1 : 0);
    }
    if(!limit) dp[pos][cnt] = res;
    return res;
}

void solve()
{
    ll l, r;
    cin >> l >> r;
    ll asw = 0;
    int len = 0;
    r--;
    while (r)
    {
        a[++len] = r % 10;
        r /= 10;
    }
    asw += dfs(len,true,0);
    len = 0;
    l--;
    while (l)
    {
        a[++len] = l % 10;
        l /= 10;
    }
    asw -= dfs(len,true,0);
    cout << asw << "\n";
}

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    fill(*dp,*(dp+maxn),-1);
    int t;
    cin >> t;
    while (t--) solve();
    return 0;
}
```

两种写法都是58行，很凑巧。