---
title: 第15届吉林省赛 H题
date: 2023-04-01
tags:
  - 算法题解
---
先贴个题目链接[H-Visit the Park](https://codeforces.com/gym/103486/problem/H)

简而言之,这个题目先给你一个两点之间可能有多条路径的无向图,然后给你一组路线,每过一个路线就会记下一个字符,问你记下来的字符的一个数学期望.

拿样例1做例子,如图所示:

![IMG_20230401_173026.jpg](../data/programming-contest/15-jlcpc-H/e12d97a371a5468698c5a4bb6a5b42f2~tplv-k3u1fbpfcp-watermark.image)

注意到题目中给的数据有3e5那么大,所以拿个数字每经过一个点都去 * 10+新的数字固然是不可行的.因此我们需要去找一个更加科学的方法.

从样例1的例子中就可以看出来,从点1 ~ 点2的路线有且有就只能出现在十位,从点2 ~ 点3的路线有且只能出现在个位,因此我们可以把数字拆成k-1个数位....十位 * 10 + 个位 * 1.其中点1~点2的路线的权值就是 * 10,点2 ~ 点3的路线的权值就是 * 1.

那么对于点1 ~ 点2中的一种路线来说,他出现的概率是多少呢? 因为路线中包含点1和点2,因此他各个路线的概率和为1,而因为是完全随机,因此概率是点1~点2的路线总数分之1

综上所述,设要经过的点的数量总数为$k$,当前为第$i$段路,第$i$段路有$m$种走法,第i段路的走法权值和为$s_i$,则数学期望的公式为
$$
E=\sum^{k-1}_{i=1}{\frac{s_i*10^{k-i-1}}{m}}
$$

例如代入$i=1$,能得到求和运算内部就是点1 ~ 点2的权值和 * 10的幂再乘上概率1/m.


注意:
1. 题目要求对这个数学期望取模,由于这个公式中带有除法,需要我们求逆元.这里可以用扩展欧几里得公式来求.
2. 计算10的幂不应当每次分别去求,应当用预处理的方法,避免重复计算.
3. 用    ```map<pair<ll, ll>, pair<ll, ll>> g;
// u->v,有m条路径,路径和为s```来维护这个无向图.
1. 记得要开long long.

中途WA了两发,原因是求模运算中忘记了处处求模.

下面附上AC代码: 计算时间约468ms.
```c++
#include <bits/stdc++.h>

using namespace std;

using ll = long long;

const ll mod = 998244853;
const ll maxn = 3e5 + 5;

ll pow10[maxn];

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

ll modinv(ll a, ll p)
{
    ll x, y;
    ll gcd = exgcd(a, p, x, y);
    if (gcd != 1)
        return -1;
    else
        return (x % p + p) % p;
}

int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);
    map<pair<ll, ll>, pair<ll, ll>> g;
    // u->v,有m条路径,路径和为s
    ll n, m, k;
    cin >> n >> m >> k;
    for (ll i = 1, u, v, w; i <= m; i++)
    {
        cin >> u >> v >> w;
        g[{min(u, v), max(u, v)}].first++;
        g[{min(u, v), max(u, v)}].second += (ll)w;
    }
    pow10[0] = 1;
    for (int i = 1; i < maxn; i++)
    {
        pow10[i] = pow10[i - 1] * 10 % mod;
    }
    ll asw = 0, temp;
    ll p1, p2;
    cin >> p2;
    for (int i = 1; i < k; i++)
    {
        p1 = p2;
        cin >> p2;
        if (g[{min(p1, p2), max(p1, p2)}].first == 0)
        {
            cout << "Stupid Msacywy!\n";
            return 0;
        }
        temp = g[{min(p1, p2), max(p1, p2)}].second % mod;
        temp = (temp % mod) * (pow10[k - i - 1] % mod) % mod;
        temp = (temp % mod) * modinv(g[{min(p1, p2), max(p1, p2)}].first, mod) % mod;
        asw = (asw % mod + temp % mod) % mod;
    }
    cout << asw << '\n';
    return 0;
}
```