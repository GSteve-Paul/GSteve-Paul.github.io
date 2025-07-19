---
title: Codeforces Round 882(Div.2) D题
date: 2023-07-14
tags:
  - 算法题解
---
先贴一个题目链接[D. Professor Higashikata](https://codeforces.com/contest/1847/problem/D)

<hr>

题意很好理解，就是求最小的交换次数使得$t(s)$的字典序最大。

<hr>

根据字典序的贪心性质，我们知道，得先把$t[1]$的那些数字变成$1$，然后再是$t[2],t[3]...$。简而言之我们可以找到一个填写$1$的优先级，具体到某一个位来讲，就是看它最先出现在哪个区间，出现的区间越是早，那么它的优先级就越高。因此，我们可以把字符串$s$按照每一个位的优先级重新排序。

然后就是如何计算交换的次数：假如该字符串中有 $cnt1$ 个 $1$，那么我们只需要找排序后的$s$中前$cnt1$个位中$0$的个数$ sum $，把它们全部变成$1$即可，所以答案就是 $sum$.

这里有一个特判(Test 13):假如说$t(s)$的区间没有把整个$s$覆盖完全，那么剩下的部分对$t(s)$的字典序的大小就是毫无贡献的，那么只需要考虑在$t(s)$的那些位全部变成$1$就可以了，那些剩下的就不用管。

<hr>

这里的代码与上面题解有所不同，我是找的$s$中前$cnt1$位中$1$的个数，然后再用$cnt1 - 1$的个数来求答案的。因为这样利于用线段树维护。

AC代码：

```c++
#include <bits/stdc++.h>

#define rson 2 * k + 1
#define lson 2 * k
#define me k
#define mid (a[me].l + a[me].r) / 2

using namespace std;

const int maxn = 2e5 + 5;

struct SegmentTree
{
    struct node
    {
        int l, r;
        int sum;
        int lazy;

        node() { l = r = sum = lazy = 0; }
    };

    int num[maxn];
    node a[4 * maxn];

    void update(int k)
    {
        a[me].sum = a[lson].sum + a[rson].sum;
    }

    void build(int k, int l, int r)
    // 当前在k上,建树
    {
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
} tree;

set<int> set1;
pair<int, int> segs[maxn];
int pos[maxn];

void solve()
{
    int n, m, q;
    cin >> n >> m >> q;
    string s;
    cin >> s;
    s = " " + s;
    /*
     * 将这些下标按照在t(s)中的优先级进行排序
     */
    for (int i = 1; i <= n; i++)
    {
        set1.insert(i);
    }
    for (int i = 1, l, r; i <= m; i++)
    {
        cin >> l >> r;
        segs[i].first = l;
        segs[i].second = r;
    }
    int prio = 0;
    int tmp;
    for (int i = 1; i <= m; i++)
    {
        auto it = set1.lower_bound(segs[i].first);
        while (it != set1.end() && *it <= segs[i].second)
        {
            prio++;
            pos[*it] = prio;
            tree.num[prio] = s[*it] - '0';
            it = set1.erase(it);
        }
    }
    tmp = prio;
    for (int elem: set1)
    {
        prio++;
        pos[elem] = prio;
        tree.num[prio] = s[elem] - '0';
    }
    int cnt1 = count(tree.num + 1, tree.num + n + 1, 1);
    tree.build(1, 1, n);
    int asw;
    for (int i = 1, x; i <= q; i++)
    {
        cin >> x;
        if (tree.query(1, pos[x], pos[x]) == 1)
        {
            cnt1--;
            tree.changeSegment(1, pos[x], pos[x], -1);
            if (cnt1 < 1) asw = min(tmp, cnt1);
            else asw = tree.query(1, 1, min(tmp, cnt1));
            cout << min(tmp, cnt1) - asw << "\n";
        }
        else
        {
            cnt1++;
            tree.changeSegment(1, pos[x], pos[x], 1);
            if (cnt1 < 1) asw = min(tmp, cnt1);
            else asw = tree.query(1, 1, min(tmp, cnt1));
            cout << min(tmp, cnt1) - asw << "\n";
        }
        /*
         * 找1~cnt1的1的个数，然后答案就是cnt1 - 它
         */
    }
}

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    solve();
    return 0;
}

```