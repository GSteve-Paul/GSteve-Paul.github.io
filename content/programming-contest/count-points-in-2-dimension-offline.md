---
title: 求解二维数点问题-离线
date: 2023-11-18
tags:
  - 算法学习
---
# 一般化形式

给出平面上$n$个点的坐标$P_i(x_i,y_i)$，有$q$次查询，每次查询在$a \leq x \leq b$ 且 $c \leq y\leq d$区间范围内有多少个点($x_i,y_i,a,b,c,d >= 1$)。

# 离线的求解方案

## 基本做法

1. 类似于概率论与数理统计中求二维随机变量的一个随机点在某个矩形区域落点的概率，设$f(a,b)$表示矩形区域$0 \leq x \leq a$ 且 $0 \leq y\leq b$上点的数量，那么每次询问的答案就可以被写作是（画图理解）

$$
f(b,d) - f(a-1,d) - f(b,c-1) + f(a-1,c-1)
$$

2. 那么，我们只需要求出这些$f$的函数值，就能计算出每次询问的答案了。对于$f(a,b)$，要求出其函数值，只需要考虑那些$x \leq a$ 的点即可。如何维护在满足这个$x$的条件下，$0 \leq y \leq b$点的个数，可以利用线段树或者树状数组，此时这个数据结构只用来维护$y$的区间和。
3. 所以我们把所有的点$P(x,y)$和$f(x,y)$按照$x$从小到大分别排序，顺次遍历$f_i(x_i,y_i)$，每次将所有$x  \leq x_i$的点都放到线段树中，也就是单点修改$y_i$，操作为$+1$，然后再区间查询，区间为$0 \leq y \leq y_i$，得到的值就是$f_i(x_i,y_i)$。这样一来，时间复杂度就来到了优秀的$O(n + n \log n + q \log q + q \log n)$

## 提醒

1. 如果这些点有可能是负数，可以对其进行离散化后操作，当然也可以适当对坐标同时加上一些数字，类似于坐标原点平移。
2. 注意线段树在$build()$操作的时候，保证建树的区间得在$0 \leq y \leq max(y_i)$，右侧很容易理解，左侧是因为上文中$f(b,c - 1)$，否则会段错误。

# 例题

## Codeforces Round 909 Div.3 G. Unusual Entertainment

[链接](https://codeforces.com/contest/1899/problem/G)

这里直接写做法：

1. 要判断一个点$p$是否是点$q$的后继，只需要跑一次$dfs()$。因为$dfs$序有如下性质：一个顶点的子树中的顶点一定是连号的，因此只需要记录一下每个顶点$i$的$dfn[i]$和$out[i]$即可，也就是$dfs$刚进入顶点时的$cnt$和刚退出时的$cnt$。然后只要满足以下式子：$dfn[q] \leq dfn[q] \leq out[p]$，那么$q$就是$p$的后继。
2. 对于每个询问$l,r,c$（这里为了容易表达，把$x$换成了$c$），设点就是$(i,dfn[p[i]])$,那么其实就是在询问矩形区域$ l\leq x \leq r$且$dfn[c] \leq y=dfn(p[x]) \leq out[c]$中的点的个数。

因为这道题目不是强制在线的，所以可以直接套用离线的解决方案，非常好用。

因为人菜，没怎么优化，代码跑的贼慢，交上去运行了3分钟才弹出来Accepted，但是好歹能过。
```c++
#include <bits/stdc++.h>

#define rson 2 * k + 1
#define lson 2 * k
#define me k
#define mid (a[me].l + a[me].r) / 2
using namespace std;

const int maxn = 1e5 + 5;

struct SegmentTree
{
    struct node
    {
        int l, r;
        int sum;
        int lazy;

        node() { l = r = sum = lazy = 0; }
    };

    int num[maxn]{};
    node a[4 * maxn];

    void update(int k)
    {
        a[me].sum = a[lson].sum + a[rson].sum;
    }

    void build(int k, int l, int r)
    // 当前在k上,建树
    {
        a[me] = node();
        a[me].l = l;
        a[me].r = r;
        if (l == r)
        {
            a[me].sum = num[l];
            return;
        }
        build(lson, a[me].l, mid);
        build(rson, mid + 1, a[me].r);
        update(k);
    }

    void pushdown(int k)
    {
        if (a[me].l == a[me].r)
        {
            a[me].lazy = 0;
            return;
        }
        a[lson].sum += (a[lson].r - a[lson].l + 1) * a[me].lazy;
        a[rson].sum += (a[rson].r - a[rson].l + 1) * a[me].lazy;
        a[lson].lazy += a[me].lazy;
        a[rson].lazy += a[me].lazy;
        a[me].lazy = 0;
    }

    int query(int k, int l, int r) // 区间查询
    // 当前在k上,问l~r的和
    {
        if (a[me].lazy)
            pushdown(k);
        if (a[me].l == l && a[me].r == r)
            return a[me].sum;
        if (r <= mid)
            return query(lson, l, r);
        else if (l > mid)
            return query(rson, l, r);
        else
            return query(lson, l, mid) + query(rson, mid + 1, r);
    }

    void changeSegment(int k, int l, int r, int x) // 区间修改
    // 当前在k上,修改l~r,全部加上x
    {
        if (a[k].l == l && a[k].r == r)
        {
            a[k].sum += (r - l + 1) * x;
            a[k].lazy += x;
            return;
        }
        pushdown(k);
        if (r <= mid)
            changeSegment(lson, l, r, x);
        else if (l > mid)
            changeSegment(rson, l, r, x);
        else
        {
            changeSegment(lson, l, mid, x);
            changeSegment(rson, mid + 1, r, x);
        }
        update(k);
    }

    void change(int k, int x, int y)
    // 当前在k上,把第x修改成y
    {
        if (a[me].l == a[me].r)
        {
            a[me].sum = y;
            return;
        }
        if (x <= mid)
            change(lson, x, y);
        else
            change(rson, x, y);
        update(k);
    }
};

vector<int> g[maxn];
int cnt = 0;
int in[maxn];
int out[maxn];
int p[maxn];
int l[maxn];
int r[maxn];
int x[maxn];
SegmentTree st;

void dfs(int i)
{
    if (in[i]) return;
    cnt++;
    in[i] = cnt;
    for (int ele: g[i])
    {
        dfs(ele);
    }
    out[i] = cnt;
}

void solve()
{
    int n, q;
    cin >> n >> q;
    for (int i = 1; i <= n; i++)
    {
        g[i].clear();
        fill(in + 1, in + n + 1, 0);
        cnt = 0;
    }
    for (int i = 1; i <= n - 1; i++)
    {
        int u, v;
        cin >> u >> v;
        g[u].push_back(v);
        g[v].push_back(u);
    }
    dfs(1);
    vector<pair<int, int>> points;
    map<pair<int, int>, int> query;
    for (int i = 1; i <= n; i++)
    {
        cin >> p[i];
        p[i] = in[p[i]];
        points.push_back({i, p[i]});
    }
    for (int i = 1; i <= q; i++)
    {
        cin >> l[i] >> r[i] >> x[i];
        int ll = in[x[i]];
        int rr = out[x[i]];
        //find x , l <= x <= r &&  ll <= p[x] <= rr
        query[{r[i], rr}] = 0;
        query[{l[i] - 1, rr}] = 0;
        query[{r[i],ll - 1}] = 0;
        query[{l[i] - 1, ll - 1}] = 0;
    }
    sort(points.begin(), points.end());
    st.build(1, 0, n);
    auto it2 = points.begin();
    for (auto it = query.begin(); it != query.end(); ++it)
    {
        while (it2 != points.end() && it2->first <= it->first.first)
        {
            st.changeSegment(1, it2->second, it2->second, 1);
            ++it2;
        }
        it->second = st.query(1, 0, it->first.second);
    }
    for (int i = 1; i <= q; i++)
    {
        int ll = in[x[i]];
        int rr = out[x[i]];
        int ans = query[{r[i], rr}] - query[{l[i] - 1, rr}] - query[{r[i],ll - 1}] + query[{l[i] - 1, ll - 1}];
        if (ans > 0)
            cout << "Yes\n";
        else
            cout << "No\n";
    }
}

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    int t;
    cin >> t;
    while(t--) solve();
}
```