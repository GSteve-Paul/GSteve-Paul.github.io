---
title: Edu Codeforces Round 136 D题
date: 2023-07-06
tags:
  - Codeforces
---
先贴一个题目链接[D. Reset K Edges](https://codeforces.com/contest/1739/problem/D)
<hr>

题意：通过剪掉一些边再接到1上，问你在最多$k$次操作之内使得这棵树的深度尽可能的小，最小是多少。

<hr>

首先想到如果最终的深度过小，需要的操作数就会很多；如果最终的深度过大，需要的操作数就很少。因此可以考虑二分这个答案。

在二分的时候，如何求在当前答案($asw$)下需要的操作次数呢？

考虑到最终的树的深度将会是$asw$，那么就是说原先的顶点中如果有其子树深度大于等于$asw$的都要被剪下来，为了让剪切的次数最少，我们考虑得从叶子向树根方向剪，如果遇到一个顶点的子树深度为$asw$，就将其剪掉，这样可以保证每次剪枝都是在尽可能靠近树根的地方减，分叉分的比较少，因此剪的次数少。

可以通过$dfs$的回溯来维护每个顶点的子树大小。注意，如果原本该顶点就与1相连，那么即便它的子树深度为$asw$，也用不着剪掉。

<hr>

AC代码：

```c++
#include <bits/stdc++.h>

using namespace std;

const int maxn = 2e5 + 5;
const int inf = 1e9;

vector<int> tree[maxn];
int d[maxn];
int n, k;

void dfs(int v, int depth, int fa, int &res) // from leaves to root
{
    d[v] = 1;
    for (int child: tree[v])
    {
        dfs(child, depth, v, res);
        d[v] = max(d[child] + 1, d[v]);
    }
    if (d[v] == depth && fa != 1)
    {
        res++;
        d[v] = 0;
    }
}

bool check(int mid)
{
    int res = 0;
    dfs(1, mid, 1, res);
    if (res > k) return false;
    else return true;
}

void solve()
{
    cin >> n >> k;
    for (int i = 1; i <= n; i++)
    {
        tree[i].clear();
    }
    for (int i = 2, tmp; i <= n; i++)
    {
        cin >> tmp;
        tree[tmp].emplace_back(i);
    }
    int l = 1, r = 2e5, mid;
    while (l < r)
    {
        mid = (l + r) >> 1;
        if (check(mid)) r = mid;
        else l = mid + 1;
    }
    cout << r << "\n";
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
