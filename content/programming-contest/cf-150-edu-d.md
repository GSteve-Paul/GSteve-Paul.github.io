---
title: Edu Codeforces Round 150 D题
date: 2023-06-24
---
先贴一个题目链接[D. Pairs of Segments](https://www.codeforces.com/problemset/problem/1841/D)
<hr>
题意：

给出$n$个区间，让你删除尽可能少的区间，使得剩下的区间可以成对地配对。配对指的是两两有交集，而与其他的没有交集。

问你能删除的最少的区间数量是多少。

<hr>

首先考虑删除后的区间数组。由于在同一对中两个相交，而在不同的对中一定不相交，那么它们的同一对中的两两形成的并区间也一定不相交。

而这些并区间其实就是给出的$n$个区间两两并运算后得到的集合的元素。现在需要使得删除的区间数量最少，也就是剩下的区间的数量最大，也就是说从这$n$个区间两两并运算后得到的集合中选出最多数量的区间，使得这些区间互不相交。

于是就变成了典题：[最大不相交区间数量](https://blog.csdn.net/yl_puyu/article/details/109681226)

一种贪心的做法就是：
1. 区间按右端点从小到大排序，用一个变量$flag$来存储最右边的$r$

1. 从前往后依次枚举每个区间：如果当前区间不是严格在$flag$右边的，就跳过，否则就$cnt++$并且更新$
flag$
<hr>

最终答案就是$n-2×cnt$

AC代码：
```c++
#include <bits/stdc++.h>

using namespace std;

const int maxn = 2005;

pair<int, int> segs[maxn];
vector<pair<int, int>> unionsegs;

bool cmp(const pair<int, int> &p1, const pair<int, int> &p2)
{
    return p1.second < p2.second;
}

void solve()
{
    int n;
    cin >> n;
    unionsegs.clear();
    for (int i = 1; i <= n; i++)
    {
        cin >> segs[i].first >> segs[i].second;
    }
    for (int i = 1; i <= n; i++)
    {
        for (int j = i + 1; j <= n; j++)
        {
            auto [l1, r1] = segs[i];
            auto [l2, r2] = segs[j];
            if (r1 >= l2 && l1 <= r2 || r2 >= l1 && l2 <= r1)
                unionsegs.emplace_back(min(l1, l2), max(r1, r2));
        }
    }
    sort(unionsegs.begin(), unionsegs.end(), cmp);
    int flag = -1e9;
    int cnt = 0;
    for (auto &unionseg: unionsegs)
    {
        if (unionseg.first > flag)
        {
            cnt++;
            flag = unionseg.second;
        }
        else
        {
            continue;
        }
    }
    int asw = n - 2 * cnt;
    cout << asw << "\n";
    cout.flush();
}

int main()
{
    int t;
    cin >> t;
    while (t--) solve();
    return 0;
}
```