---
title: 2021年ICPC NAC J题
date: 2023-05-07
tags:
  - 2021年ICPC北美决赛
---
这个比赛的全称是ICPC North America Championship 2021

先贴个题目链接 [J-The Paladin](https://open.kattis.com/problems/thepaladin)

这道题目题意说得非常云里雾里,简而言之就是用输入的那几个以2为长度的字符串组合成一个长的回文.具体而言,这些小的字符串得两两在中间相连,而且每种小字符串都有所谓的费用,要求是使得费用最小.

~~容易看出,这道题得用DP~~

好 既然知道了要用DP,那么应该如何动态规划呢?要点就是找状态量和状态转移方程.

考虑到只要一个回文字符串左边出现了ab,则右边就必然出现ba,那么我们可以只研究这个字符串的一半:

![IMG_20230507_185021.jpg](../data/programming-contest/2021-icpc-north-america-championship-J/8d5809fec8f7404baeab04d2c7557bba~tplv-k3u1fbpfcp-watermark.image)

因此可以得到状态转移方程:
```c++
const int maxalpha = 26;
const int maxcost = 1e5;
const int maxk = 105;
```
设$dp[i][j]$中,$i$表示第i个字符,$j$表示在这第i个字符上选择$(j+'a')$这个字母.整体表示在这第i个字符上选择$(j+'a')$这个字母的最小的费用.

设$cost[i][j]$表示子字符串ij的费用,输入中没给出的一律当作`maxcost`

$dp[i][j] = min_{k=0->25}(dp[i-1][k]+cost[k][j]+cost[j][k])$

最后答案就是中间那个字符上选择任意一个字母的最小值.即

$min_{j=0->25}(dp[i_{last}][j])$

到这儿,其实这道题目的解法就已经大部分出来了.
<hr>

下面是一些小小的细节:

**1.**
对于k为奇数,那么根据我们只研究一半的字符串,只需要这个dp状态转移方程递推k/2次即可.

**2.**
对于k为偶数,~~根据多次的手操模拟~~发现只需要k/2-1次即可,前k/2-2次跟上面给出的那个状态转移方程完全一样,

最后一次略有不同,
为了更好地说明这种情况,可以想象abaaba中第3个字符----a,添加这个字母就会增加ba,ab,aa三个小字符串的费用.所以最后一次的状态转移方程应当是

$dp[i][j] = min_{k=0->25}(dp[i-1][k]+cost[k][j]+cost[j][k]+cost[j][j])$

**3.**
对于k==2,需要特判一下,也就是只能像aa,bb,cc这样的填进去.

最后得出答案的时候,如果最小值是maxcost,那么得输出-1才行.

<hr>

以下为AC代码,其中的ijk下标代表的意义可能与以上说明有所不同.但是道理是一样的.

时间复杂度大约为$O(\frac{k}{2}*26*26)$

```c++
#include <bits/stdc++.h>

using namespace std;

const int maxalpha = 26;
const int maxcost = 1e5;
const int maxk = 105;

int cost[maxalpha][maxalpha]{};
int dp[maxk][maxalpha]{};

int main()
{
    int n, k;
    cin >> n >> k;
    string temp;
    fill(*cost, *(cost + maxalpha), maxcost);
    for (int i = 1, c; i <= n; i++)
    {
        cin >> temp >> c;
        cost[temp[0] - 'a'][temp[1] - 'a'] = c;
    }
    if (k % 2 == 1)
    {
        for (int t = 1; t <= k / 2; t++)
        {
            for (int i = 0; i < maxalpha; i++)
            {
                int temp = maxcost;
                for (int j = 0; j < maxalpha; j++)
                {
                    temp = min(temp, dp[t - 1][j] + cost[j][i] + cost[i][j]);
                }
                dp[t][i] = temp;
            }
        }
    }
    else
    {
        if (k == 2)
        {
            for (int i = 0; i < maxalpha; i++)
            {
                dp[k / 2][i] = cost[i][i];
            }
        }
        else
        {
            for (int t = 1; t <= k / 2 - 2; t++)
            {
                for (int i = 0; i < maxalpha; i++)
                {
                    int temp = maxcost;
                    for (int j = 0; j < maxalpha; j++)
                    {
                        temp = min(temp, dp[t - 1][j] + cost[j][i] + cost[i][j]);
                    }
                    dp[t][i] = temp;
                }
            }
            for (int i = 0; i < maxalpha; i++)
            {
                int temp = maxcost;
                for (int j = 0; j < maxalpha; j++)
                {
                    temp = min(temp, dp[k / 2 - 2][j] + cost[j][i] + cost[i][j] + cost[i][i]);
                }
                dp[k / 2][i] = temp;
            }
        }
    }
    int asw = *min_element(*(dp + k / 2), *(dp + k / 2 + 1));
    if(asw == maxcost) cout << -1 << endl;
    else cout << asw << endl;
    return 0;
}
```