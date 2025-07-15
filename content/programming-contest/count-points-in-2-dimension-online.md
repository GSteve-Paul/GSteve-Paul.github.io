---
title: 求解二维数点问题-在线
date: 2025-06-07
tags:
  - 算法学习
---
二维数点问题的一般化形式已在[求解二维数点问题-离线](count-points-in-2-dimension-offline.md#一般化形式)给出，这里就不多赘述。

这是2025年我的第一篇博客，虽然现在正在保研阶段，但是仍想要抽出点时间来把之前挖的坑填上。

## 在线的求解方案

### 前置知识

可持久化线段树

### 基本思想

普通的值域线段树能够维护一个一维下的信息。宏观的看，可持久化线段树从修改时间的角度上维护了一连串值域线段树的前缀和，如果我们把修改时间看作另一维度，就可以发现**可持久化线段树天生可以维护二维信息**，所以我们尝试把它拿去解决二维数点问题。

在这里，我用值域线段树来维护$y_i$的个数，把$x_i$当作修改时间。

### 算法流程

#### 数据预处理

为了防止存不下，可以对$x_i$和$y_i$做离散化。

1. 将$P_i(x_i,y_i)$ 按照$x_i$从小到大排序，相当于排好修改时间。
2. 建好一颗可持久化线段树$Tree$，其内部的值域线段树值域为$y_i$的值域，而修改次数则是$x_i$的个数。
3. 将第一步排好序的$P_i(x_i,y_i)$逐个修改$Tree$，修改方式是$node[y_i].val + 1$，在可持久化线段树的策略下，这会给整个线段树添加一条新链，这个新链则维护了本次修改的信息。然后我们记录下这次修改的$i$和所对应的$Tree$的根节点到一个$map$映射中。

上述过程的时间复杂度为$O(n\log{n})$
#### 查询

1. 可以通过"二分"$map$找到$a$对应的$lroot = map[\max_{x_i < a}{i}]$ 与$b$对应的 $rroot = map[\max_{x_i \le b}{i}]$ ，这样从前缀和的角度，这两个根节点所代表的值域线段树的差$rroot-lroot$则能表示所有$P_i(x_i,y_i), a \le x_i \le b$。
2. 此时可以采用传统值域线段树的区间查询方式，以$c \le y \le d$为区间统计数量即可。由于是在可持久化线段树中，会略显复杂，这里附上一点代码以供参考。
	```c++
	int query(int lroot, int rroot, int c, int d)
	{
		int l = a[lroot].l;
		int r = a[lroot].r;
		int mid = (l + r) >> 1;
		if (l == c && r == d)
			return a[rroot].val - a[lroot].val;
		if (d <= mid)
			return query(a[lroot].lnode, a[rroot].lnode, c, d);
		else if (c > mid)
			return query(a[lroot].rnode, a[rroot].rnode, c, d);
		else
			return query(a[lroot].lnode, a[rroot].lnode, c, mid) + query(a[lroot].rnode, a[rroot].rnode, mid + 1, d);
	}
	```

上述过程的时间复杂度为$O(q\log{n})$
## 例题

### [Codeforces Round 909 Div.3 G. Unusual Entertainment](https://codeforces.com/contest/1899/problem/G)

题意就不多赘述，大致解法请见[[count-points-in-2-dimension-offline#Codeforces Round 909 Div.3 G. Unusual Entertainment|这个]]

下面是采用可持久化线段树在线解决该问题的代码，其效率比之前离线方式的更好。

注意到这里并没有[[count-points-in-2-dimension-online#查询|查询操作的二分步骤]]，这是因为本题抽象出的$P_i(x_i,y_i)$的$x_i$数组是严格的步长为$1$的等差数列$[1,2,...,n]$，所以直接访问数组下标即可。

```c++
#include <bits/stdc++.h>

using namespace std;

struct segtree
{
    struct node
    {
        int l, r;
        int lnode, rnode;
        int val;

        node() = default;

        node(int l, int r, int lnode, int rnode, int val)
            : l(l), r(r), lnode(lnode), rnode(rnode), val(val)
        {
        }

        node(const node &that)
            : node(that.l, that.r, that.lnode, that.rnode, that.val)
        {
        }
    };

    vector<node> a;
    vector<int> his;
    int tot;

    segtree(int n, int change_cnt)
        : a(vector<node>((n + 1) * 4 + change_cnt * 30)),
          his(vector<int>(change_cnt + 1)), tot(1)
    {
    }

    void build(int l, int r)
    {
        int k = tot;
        a[k].l = l;
        a[k].r = r;
        if (l == r)
        {
            a[k].val = 0;
            ++tot;
            return;
        }
        int mid = (l + r) / 2;
        ++tot;
        a[k].lnode = tot;
        build(l, mid);
        a[k].rnode = tot;
        build(mid + 1, r);
        update(k);
    }

    void update(int k)
    {
        a[k].val = a[a[k].lnode].val + a[a[k].rnode].val;
    }

    void change(int idx, int add, int k)
    {
        int now = tot;
        a[now].l = a[k].l;
        a[now].r = a[k].r;
        if (idx == a[k].l && idx == a[k].r)
        {
            a[now].val = add + a[k].val;
            ++tot;
            return;
        }
        int mid = (a[k].l + a[k].r) / 2;
        ++tot;
        if (idx <= mid)
        {
            a[now].lnode = tot;
            a[now].rnode = a[k].rnode;
            change(idx, add, a[k].lnode);
        }
        else
        {
            a[now].lnode = a[k].lnode;
            a[now].rnode = tot;
            change(idx, add, a[k].rnode);
        }
        update(now);
    }

    int query(int kl, int kr, int mn, int mx)
    {
        int l = a[kl].l;
        int r = a[kl].r;
        int mid = (l + r) >> 1;
        if (l == mn && r == mx)
            return a[kr].val - a[kl].val;
        if (mx <= mid)
            return query(a[kl].lnode, a[kr].lnode, mn, mx);
        else if (mn > mid)
            return query(a[kl].rnode, a[kr].rnode, mn, mx);
        else
            return query(a[kl].lnode, a[kr].lnode, mn, mid) +
                   query(a[kl].rnode, a[kr].rnode, mid + 1, mx);
    }
};

void solve()
{
    int n, q;
    cin >> n >> q;
    vector<vector<int>> tree(n + 1);
    for (int i = 1; i <= n - 1; i++)
    {
        int u, v;
        cin >> u >> v;
        tree[u].emplace_back(v);
        tree[v].emplace_back(u);
    }
    vector<int> p(n + 1);
    for (int i = 1; i <= n; i++)
        cin >> p[i];

    vector<int> dfn(n + 1), dfo(n + 1);
    int dfs_cnt = 1;
    function<void(int, int)> dfs = [&](int node, int fa) {
        dfn[node] = dfs_cnt;
        dfs_cnt++;
        for (const int nei : tree[node])
        {
            if (nei == fa)
                continue;
            dfs(nei, node);
        }
        dfo[node] = dfs_cnt - 1;
    };
    dfs(1, 0);

    segtree st(n, n);
    st.build(1, n);
    st.his[0] = 1;
    for (int i = 1; i <= n; i++)
    {
        st.his[i] = st.tot;
        st.change(dfn[p[i]], 1, st.his[i - 1]);
    }

    while (q--)
    {
        int l, r, x;
        cin >> l >> r >> x;
        int lroot = st.his[l - 1];
        int rroot = st.his[r];
        int mn = dfn[x];
        int mx = dfo[x];
        int ans = st.query(lroot, rroot, mn, mx);
        if (ans)
            cout << "Yes\n";
        else
            cout << "No\n";
    }
}

int main()
{
#ifdef lijn
    freopen("/home/lijn/acm_practice/.build/input.in", "r", stdin);
    freopen("/home/lijn/acm_practice/.build/output.out", "w", stdout);
#endif
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t = 1;
    cin >> t;
    while (t--)
        solve();
}
```