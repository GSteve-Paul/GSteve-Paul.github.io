---
title: 2026年东北师范大学校赛 G题
tags:
  - 校赛
  - 原创题目
---
先贴一个题目链接 [G. Rewrite你的最短路算法](https://codeforces.com/gym/658176/problem/G)，正如题目所示，本题背景基于游戏Rewrite。

## 题意概括

有一个无向带权图，要从 `1` 走到 `n`。

- 走普通道路 `(u, v)`，花费是边权 `w`。
- 如果当前在特殊点 `x`，可以直接到另一个特殊点 `y`，花费$x + 2y + \left\lfloor \frac{n}{2} \right\rfloor$
- 最多可以使用 `k` 次超能力。
- 每次使用超能力，可以让“一次移动”的花费变成 `0`。
- 这次移动既可以是普通道路，也可以是一次特殊点到特殊点的传送。

## 前置知识

如果你是25级同学，请确保你已经掌握了以下知识，如果没有掌握可以上网搜索或询问ChatGPT，否则阅读下面的内容可能会有困难。

- C with STL
- 估算时间复杂度、空间复杂度
- 图论的基本概念、图的表示方法
- Dijkstra 最短路算法（使用堆优化）
- 分层图

## 大致解法

这题本质上是求一个最短路。注意到建出来的图里面各个边的权值均非负，所以我们可以对Dijkstra最短路算法进行改写，进而解出本题。

由于题目中加入了一些策略，所以我们需要分三步进行考虑：

### 把“用了多少次超能力”也放进状态

我们先假设没有特殊点。

设 `dist[u][c]` 表示到达点 `u`且已经用了 `c` 次超能力时的最小代价

这样每个原图点会被拆成 `k + 1` 层，即建立一个分层图。

如此一来，在Dijkstra算法中的转移模块就需要改写成如下方式：

对于普通道路 `(u, v, w)`：

- 不用超能力：
  `(u, c) -> (v, c)`，代价 `w`
- 用一次超能力：
  `(u, c) -> (v, c + 1)`，代价 `0`

当然对于每个状态还是要取最小值。

### 用虚点压缩特殊点之间的转移

我们先假设没有超能力。

如果从特殊点 `x` 传送到特殊点 `y`，代价是：

$$
x + 2y + \left\lfloor \frac{n}{2} \right\rfloor
$$

把它拆开：

$$
\left(x + \left\lfloor \frac{n}{2} \right\rfloor\right) + 2y
$$

这说明它由两部分组成：

- 只和起点 `x` 有关的一部分
- 只和终点 `y` 有关的一部分

于是可以新增一个虚点 `A`：

- `x -> A`，边权 `x + floor(n / 2)`
- `A -> y`，边权 `2y`

这样从 `x` 走到 `A` 再走到 `y`，总代价就是原式。

这样就把原本 $p^2$ 条特殊边，压成了：

- 每个特殊点连向 `A` 一条边
- `A` 连向每个特殊点一条边

总共只要 `O(p)` 条。

### 超能力和虚点结合

如果一次特殊传送使用了超能力，那么整次传送的代价应该直接变成 `0`。

这时候不能走上面的 `x -> A -> y`，因为那条路可能会导致多次计算超能力次数，或者有一半用了超能力而另一半没用超能力，这都是不合法的。

所以对于上面的虚点`A`，我们只能表示“这次特殊传送不使用超能力”：

- 从特殊点 `x` 出发，如果不使用超能力：  
  `(x, c) -> (A, c)`，代价 `x + floor(n / 2)`
- 从 `A` 到任意特殊点 `y`：  
  `(A, c) -> (y, c)`，代价 `2y`

为了表示使用超能力进行传送，应该再建一个虚点 `B`：

- 从特殊点 `x` 出发，如果使用超能力：  
  `(x, c) -> (B, c + 1)`，代价 `0`
- 再从 `B` 到任意特殊点 `y`：  
  `(B, c + 1) -> (y, c + 1)`，代价 `0`

这样就表示“这整次特殊传送被超能力完全免费”。

## 复杂度分析

设特殊点个数为 `p`。

- 节点数是 `O(nk)`
- 普通道路边数是 `O(km)`
- 从虚点 `A`、`B` 向所有特殊点扩展的边数是 `O(kp)`

因此总复杂度可以写成：

$$
O((k(m + p + n)) \log (kn))
$$

## 番外

本题出题人为22级黎江楠（有且只有本题）。

本题末尾有彩蛋：“如果赛时无人过题，出题人自会含愧而死”。这是因为上一次校赛（2025年东北师范大学程序设计竞赛）中，出题人出了两道题，结果赛时只有一个很板的线段树题让一个选手过了，而且这位选手还是22级同学，并非是校赛的主力军（23，24级同学），导致出题人非常尴尬。因此这次出题人特地出了一道不算很难的题目，想让对图论略知一二的选手们能够过题，结果赛时并没有正式选手解出，还好中途被一位老资历学姐拯救，出题人差一点又一次含愧而死了。

这个东西的具体实现方式是将文字颜色调成白色。比如：`${\color{white}{如果赛时无人过题，出题人自会含愧而死}}$`

## 实现

```cpp
#include <bits/stdc++.h>

using namespace std;
using i64 = int64_t;

constexpr i64 INF = 1e18;

struct State
{
    i64 dist;
    int node;
    int used;

    bool operator<(const State &other) const
    {
        return dist > other.dist;
    }
};

void solve(int t)
{
    int n, m, k;
    cin >> n >> m >> k;
    vector<vector<pair<int, i64>>> g(n + 1);
    for (int i = 1; i <= m; i++)
    {
        int u, v;
        i64 w;
        cin >> u >> v >> w;
        g[u].emplace_back(v, w);
        g[v].emplace_back(u, w);
    }
    int p;
    cin >> p;
    vector<int> special(p + 1);
    vector<int> is_special(n + 1, 0);
    for (int i = 1; i <= p; i++)
    {
        cin >> special[i];
        is_special[special[i]] = 1;
    }
    vector<vector<i64>> dist(n + 3, vector<i64>(k + 1, INF));
    dist[1][0] = 0;
    priority_queue<State> pq;
    pq.push({0, 1, 0});
    while (!pq.empty())
    {
        auto [d, u, used] = pq.top();
        pq.pop();
        if (d > dist[u][used])
            continue;

        if (u == n + 1)
        {
            for (int v : special)
            {
                i64 w = 2LL * v;
                if (dist[v][used] > d + w)
                {
                    dist[v][used] = d + w;
                    pq.emplace(dist[v][used], v, used);
                }
            }
        }
        else if (u == n + 2)
        {
            for (int v : special)
            {
                if (dist[v][used] > d)
                {
                    dist[v][used] = d;
                    pq.emplace(dist[v][used], v, used);
                }
            }
        }
        else
        {
            for (auto &[v, w] : g[u])
            {
                if (used < k && dist[v][used + 1] > d)
                {
                    dist[v][used + 1] = d;
                    pq.emplace(dist[v][used + 1], v, used + 1);
                }
                if (dist[v][used] > d + w)
                {
                    dist[v][used] = d + w;
                    pq.emplace(dist[v][used], v, used);
                }
            }
            if (is_special[u])
            {
                i64 w = u + n / 2;
                if (used < k && dist[n + 2][used + 1] > d)
                {
                    dist[n + 2][used + 1] = d;
                    pq.emplace(dist[n + 2][used + 1], n + 2, used + 1);
                }
                if (dist[n + 1][used] > d + w)
                {
                    dist[n + 1][used] = d + w;
                    pq.emplace(dist[n + 1][used], n + 1, used);
                }
            }
        }
    }

    i64 ans = INF;
    for (int i = 0; i <= k; i++)
        ans = min(ans, dist[n][i]);
    if (ans == INF)
        cout << -1 << "\n";
    else
        cout << ans << "\n";
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t = 1;
    // cin >> t;
    while (t--)
        solve(t);
    return 0;
}
```