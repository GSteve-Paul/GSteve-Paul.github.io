---
title: Codeforces Round 872(Div.2) D1题
date: 2023-05-09
tags:
  - Codeforces
---
先贴个题目链接[D1-LuoTianyi and the Floating Islands](https://codeforces.com/contest/1825/problem/D1)

这个题目的简单版本虽然是简单版本 但是我这个菜菜还是不会. 困难版本请看[D2](cf-872-div2-d2.md)

<hr>

看完题目之后能知道这道题简就简单在k只会是1,2,3.

- 假如是1,肯定只有那唯一一个人所在的那个点是good,所以每一种方案都只有1个good点,因此期望肯定是1.
- 假如是3,期望也是1.(其实可以直接推广到奇数个)

证明如下:
> 证明：称每个点到选定的 $k$ 个特殊点的距离之和称为距离和。假设目前 $x$ 和 $y$ 两个点都是“好点”，设定 $x$ 为这棵树的根，来考虑 $x$ 移动到 $y$ 过程中距离和的变化。设当前的距离和为 $dis$，当前点子树内共有 $s$ 个特殊点，那么从 $x$ 移动到其某一个儿子后，因为与子树内的特殊点的距离均 $−1$，与子树外的特殊点距离均 $+1$，距离和改变为 
> 
> $
> dis−s+(k−s)=dis+(k−2s)
> $。
> 
> 又由于 $x$ 为“好点”，则此时 $k−2s≥0$。而 $k$ 是奇数，所以 $k−2s>0$。又由于这个变化量是所有的变化量中最小的，故移动到点 $y$ 时，距离和一定会比 $dis$ 大，与题设矛盾，所以猜想成立。

- 假如是2,那么就有两个特殊点,这两个特殊点的直接路径上的所有的点都可以成为好点.也就是说,对于每一种选特殊点的方案,好点的个数总是两个特殊点间的边的数量+1.又因为选这两个点是任意的,那么总的好点数$=$树上任意两点间的距离之和$+C(k,2)$.

那么问题就变成了树上任意两点间的距离之和.如果强行遍历树的顶点,那么必然会超时($O(n^2log(n))$).

因此需要换个方向考虑----考虑边的贡献.把一条边看成是一个分割器,那么一棵树就会被分成两个互不相连的连通块.于是根据乘法原理,

这个边被通过的方案数$=$一个连通块的顶点数$×$另一个连通块的顶点数.

要求一个连通块的顶点数,本质上是求以某个顶点为树根的子树的大小.这个事情可以用递归来做.以下贴一个代码段:

![IMG_20230509_213417.jpg](../data/programming-contest/cf-872-div2-d1/a197d1aeccda4c2b8759ec8cc0ebdedd~tplv-k3u1fbpfcp-watermark.image)

```c++
const ll maxn=2e5+5;

vector<ll> adj[maxn]{};//邻接表维护树,adj[i]表示i节点所连接的所有节点
ll sz[maxn]{};//sz[i]表示以i为树根的子树的大小

int dfs(int u,int fa)  
{  
    sz[u]=1;  
    for(int i=0;i<adj[u].size();i++)  
    {  
        if(adj[u][i]==fa) continue;//防止往回找  
        int temp=dfs(adj[u][i],u);  
        asw=(asw+temp*(n-temp))%mod;  
        sz[u]+=temp;  
    }  
    return sz[u];  
}
```
其中这个asw的最终之和即为树上任意两点的距离之和.

最后运用逆元,即可得到答案.

以下为AC代码,时间复杂度是$O(n)$的,用时约124ms

```c++
#include <bits/stdc++.h>

using namespace std;
using ll = long long;

const ll maxn=2e5+5;
const ll mod=1e9+7;

vector<ll> adj[maxn]{};
ll sz[maxn]{};

ll asw=0;
ll n,k;

ll Cx2(ll n)
{
    return (n*(n-1)/2)%mod;
}

int dfs(int u,int fa)
{
    sz[u]=1;
    for(int i=0;i<adj[u].size();i++)
    {
        if(adj[u][i]==fa) continue;
        int temp=dfs(adj[u][i],u);
        asw=(asw+temp*(n-temp))%mod;
        sz[u]+=temp;
    }
    return sz[u];
}

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

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    cin >> n >> k;
    for(int i=1;i<=n-1;i++)
    {
        ll u,v;
        cin >> u >> v;
        adj[u].emplace_back(v);
        adj[v].emplace_back(u);
    }
    dfs(1,0);
    if(k==1 || k==3)
    {
        cout << 1 << endl;
    }
    else
    {
        cout << ((asw+Cx2(n))* modinv(Cx2(n),mod))%mod << endl;
    }
    return 0;
}
```