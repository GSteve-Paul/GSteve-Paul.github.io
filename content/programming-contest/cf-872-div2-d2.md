---
title: Codeforces Round 872(Div.2) D2题
date: 2023-05-10
tags:
  - 算法题解
---
先贴个题目链接 [D2-LuoTianyi and the Floating Islands](https://codeforces.com/contest/1825/problem/D2)

D2难就难在它k不只是1,2,3了.

先还是看看[D1](cf-872-div2-d1.md)中对k(奇数)永远输出1的证明.

> 证明：称每个点到选定的 $k$ 个特殊点的距离之和称为距离和。假设目前 $x$ 和 $y$ 两个点都是“好点”，设定 $x$ 为这棵树的根，来考虑 $x$ 移动到 $y$ 过程中距离和的变化。设当前的距离和为 $dis$，当前点子树内共有 $s$ 个特殊点，那么从 $x$ 移动到其某一个儿子后，因为与子树内的特殊点的距离均 $−1$，与子树外的特殊点距离均 $+1$，距离和改变为 
> 
> $
> dis−s+(k−s)=dis+(k−2s)
> $。
> 
> 又由于 $x$ 为“好点”，则此时 $k−2s≥0$。而 $k$ 是奇数，所以 $k−2s>0$。又由于这个变化量是所有的变化量中最小的，故移动到点 $y$ 时，距离和一定会比 $dis$ 大，与题设矛盾，所以猜想成立。

<hr>

则设若$k$为偶数,那么只要上述证明中$k=2s$,由下图很容易理解:

![IMG_20230509_225924.jpg](../data/programming-contest/cf-872-div2-d2/444940eaf501451b83e63d3e25d99f07~tplv-k3u1fbpfcp-watermark.image)

那么我们也可以知道对于k(偶数),其某种方案下的好点的分布也是在一条链上,因此对于任意的方案,好点的个数$=$串起来的边数$+1$.那么我们最终要求的就是所有串起来的边数+$C(n,k)$.

为了解决这个问题,我们不可以从方案处入手,也就是不能考察在一个方案下能通过几个边.而应该从边入手,考察一个边能被哪几种方案所通过.然后把每个边的这个加起来.

由上述证明可知,通过某个边的方案数即是$C(sz[v],k/2)×C(n-sz[v],k/2)$.

然后答案也就显而易见了.

<hr>

下面是AC代码:

```c++
#include <bits/stdc++.h>

using namespace std;
using ll = long long;

const ll maxn = 2e5 + 5;
const ll mod = 1e9 + 7;

vector<ll> adj[maxn]{};
ll sz[maxn]{};
ll fact[maxn]{};
ll invfact[maxn]{};

ll asw = 0;
ll n, k;

ll exgcd(ll a, ll b, ll &x, ll &y)
{
    if (b == 0)
    {
        x = 1;
        y = 0;
        return a;
    }
    ll d = exgcd(b, a % b, y, x);
    y -= (a / b) * x;
    return d;
}


ll modinv(ll a, ll mod)
{
    ll x, y;
    ll gcd = exgcd(a, mod, x, y);
    if (gcd != 1)
        return -1;
    else
        return (x % mod + mod) % mod;
}

void init()
{
    fact[0] = 1;
    invfact[0] = modinv(1, mod);
    for (ll i = 1; i < maxn; i++)
    {
        fact[i] = fact[i - 1] * i % mod;
        invfact[i] = modinv(fact[i], mod);
    }
}

ll C(ll n, ll m)
{
    if (n < m)
        return 0;
    else
        return (fact[n] * invfact[m] % mod) * (invfact[n - m] % mod) % mod;
}

int dfs(int u, int fa)
{
    sz[u] = 1;
    for (int i = 0; i < adj[u].size(); i++)
    {
        if (adj[u][i] == fa) continue;
        int temp = dfs(adj[u][i], u);
        asw = (asw % mod + (C(temp, k / 2) * C(n - temp, k / 2)) % mod) % mod;
        sz[u] += temp;
    }
    return sz[u];
}

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    init();
    cin >> n >> k;
    for (int i = 1; i <= n - 1; i++)
    {
        ll u, v;
        cin >> u >> v;
        adj[u].emplace_back(v);
        adj[v].emplace_back(u);
    }
    dfs(1, 0);
    if (k % 2 == 1)
    {
        cout << 1 << endl;
    }
    else
    {
        cout << ((asw + C(n, k)) * modinv(C(n, k), mod)) % mod << endl;
    }
    return 0;
}
```
