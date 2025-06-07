---
title: Codeforces Round 882(Div.2) D题
date: 2023-07-14
---
先贴一个题目链接[D. Row Major](https://codeforces.com/contest/1844/problem/D)
<hr>
题意：构造长度为$n$的字符串，要求这个字符串在转换成任意形式矩阵后不会出现相邻的块字符一样的情况。
<hr>

对于不会出现相邻相同的情况，意思就是

${\forall i∈n},s[i] \neq s[i+a]$ , $a$为$n$的任意因子,$a$不包括$n$自身。

这一点很好理解，因为反映到矩阵上$a$就是矩阵可能的列数，相当于上下不同。而左右不同就是相当于$a = 1$的情况。

关键问题是：如何构造这样的一个字符串。

假设有一个没有重复字符的字符串$s$，如果$s$的长度$m$不会被任何的$n$的因子整除,那么就不会发生相邻相同的情况。而这一句话又可以转换为$m$不可以被$n$整除，通过打表发现，$m$最大也只有$17$，该问题便迎刃而解了。

<hr>

AC代码：
```c++
#include <bits/stdc++.h>

using namespace std;

const int maxn = 1e6 + 5;

int cycle[maxn];

string s = "abcdefghijklmnopq";

void solve()
{
    int n;
    cin >> n;
    string tmp = s.substr(0, cycle[n]);
    for (int i = 1; i <= n / cycle[n]; i++)
    {
        cout << tmp;
    }
    if (n % cycle[n])
    {
        cout << tmp.substr(0, n % cycle[n]);
    }
    cout << "\n";
}

int main()
{
    for (int i = 1; i <= 1e6; i++)
    {
        for (int j = 1;; j++)
        {
            if (i % j)
            {
                cycle[i] = j;
                break;
            }
        }
    }
    ios::sync_with_stdio(0);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) solve();
    return 0;
}
```