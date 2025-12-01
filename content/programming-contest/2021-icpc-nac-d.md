---
title: 2021年ICPC NAC D题
date: 2023-05-09
tags:
  - 算法题解
---
先贴一个题目链接[D-Contest Construction](https://open.kattis.com/problems/contestconstruction)

这个题是与J题相似的一个DP题目

这道题就是要你用给出的n个数字来构成一个k长度的数列a,使得这个数列a是递增序的时候,对于任意的$i,(i+2<=k)$有

$a[n+2]<=a[n+1]+a[n]$ 且 $a[n+2]>a[n+1]>a[n]$

然后问你满足条件的方案有多少个.
<hr>

为了解决这个问题,我们需要先把这n个数字进行排序,然后就顺序地往后面取数字,这样一来,就可以保证取到的数字只会越来越大,并且不会出现重复的方案.

因为要取第$n+2$个数字必须要知道第$n$和第$n+1$个数字,所以状态量中必然会出现两个连续数位上的取到的数字.

因此得到如下dp方程

```c++
int dp[maxk][maxn][maxn]{};//dp[t][j][k] 第t个题目,选择题目为i,上一个是j的方案数量
```

$$dp[t][i][j]=sum(dp[t-1][j][k]),k<j<i $且$ d[i]≤d[j]+d[k]$$

最终答案就是$sum(dp[k][i][j])$

当然了,要提前设定好$dp[2][i][j]$的值,也就是说,只要$i<j$,就设定为1.

<hr>

以下为AC代码,时间复杂度$O(kn^3)$

一开始WA了一发,发现是没有开long long.

```c++
#include <bits/stdc++.h>

using namespace std;
#define int long long

const int maxn=55;
const int maxk=25;

int d[maxn];
int dp[maxk][maxn][maxn]{};//[t][j][k] 第 t 个题目,选择题目为 i ,上一个是 j .   的方案数量

signed main()
{
    int n,k;
    cin >> n >> k;
    for(int i=1;i<=n;i++)
        cin >> d[i];
    sort(d+1,d+n+1);
    for(int i=1;i<=n;i++)
    {
        for(int j=1;j<i;j++)
        {
            dp[2][i][j]=1;
        }
    }
    for(int t=3;t<=k;t++)
    {
        for(int i=1;i<=n;i++)
        {
            for(int j=1;j<i;j++)
            {
                int sum = 0;
                for(int k=1;k<j;k++)
                {
                    if(d[i]<=d[j]+d[k])
                    {
                        sum+=dp[t-1][j][k];
                    }
                }
                dp[t][i][j]=sum;
            }
        }
    }
    int asw = 0;
    for(int i=1;i<=n;i++)
    {
        for(int j=1;j<i;j++)
        {
            asw+=dp[k][i][j];
        }
    }
    cout << asw << endl;
    return 0;
}
```