---
title: Redis学习入门
date: 2023-09-06
tags:
  - 蓝旭2023秋季学习
---
# 概念
> Redis是一个key-value存储系统（键值存储系统），支持丰富的数据类型，如：String、list、set、zset、hash。

# 5种基本数据结构

## String字符串

String类型是一个键值对的结构，其中key必须是字符串，而value可以是任意的数据。

它的最基本的命令有三个，分别是设置，获取和删除：
``` redis
SET key value
GET key
DEL key 
```
除此之外，还有些特殊操作：

对于value为 integer 的String类型，可以使用`INCRBY key increment`和`DECRBY key decrement`来增加/减少，返回值是操作之后的整数。

还可以用`APPEND key value`，把一个字符串追加到后边，这个对于非字符串的value也是可以的。

### 设置过期时间

有时候希望我们的键值对会在一定时间后自动消失，那么我们可以设置一个过期时间：

`SETEX key seconds value` 创建键值对时带上过期时间

`EXPIRE key seconds` 键值对存在，设置其过期时间

`TTL key` 获取某个键值对的剩余过期时间

## List列表

Redis中的List其实就是一个双端链表。 所以用双端链表能实现的，它都能实现，比如栈，队列，双端队列之类的。

对于左边，有如下的基本操作：
这里的Key就不再是键值对的键，而是列表的名字。
```redis
LPUSH key value 
LPOP key
LINDEX key index //左边index下标下的key
LRANGE key start stop //左边下标[start,stop]的所有key
//如果要整个List，start = 0,stop = -1
LTRIM key start stop //删除两边的，只剩下[start,stop]的key
LSET kay index value //设置列表中下标index的value
```

### 设置阻塞

`BLPOP key[key...] timeout`

这是一种阻塞式的pop命令，他的不同点就在于，如果这些list全是空的，那么他就会阻塞当前的客户端timeout秒，直到有其他的客户端进行lpush，然后他才pop出去，返回的是key和value，如果一直都没有，就返回nil

同理，对列表右边的操作也是完全一样的。

## Set集合

Redis中的Set就是个HashSet，其中元素必须都是String

一些基本操作：
```redis
SADD key member
SREM key member 
SMEMBERS key //获取集合key中的所有成员
SISMEMBER key member //检查一个member是否在集合key中
SCARD key //获取集合中的元素数量
```

### SCAN 操作

对于一些大的Set,像SMEMBERS这样的命令就会阻塞服务器较长的时间。而SCAN可以解决这个问题，因为它是分批次，以增量来迭代数据集的元素的。

SCAN是基于游标的迭代器，当游标参数是0时，服务器将会进行一次新的迭代，所以当服务器返回来的游标是0时，说明迭代完了。

但是需要注意的是，如果一个数据在迭代过程中添加或者删除，他可能迭代不到。同一个数据可能会被迭代到多次

COUNT 参数可以用来作为每一次迭代中返回数据数量的一个提示，但是返回来的不一定正好就是这么多的数据。默认是10。

MATCH 参数可以用来筛选值。

![](https://file.stevepaul101.net/d000f614ef4f4ac6a1f417e0a2820554.png)

## Hash散列

散列就是正宗的HashMap了。但要注意的是，key是Hash映射表，field是键，value是值。同样，这个value可以是任意的。

一些基本操作：
```redis
HSET key field value
HGET key field
HDEL key field
HKEYS key //获取key表中所有的field
HVALS key //获取key表中所有的value
HGETALL key //获取指定键中的所有字段和值，两两在一块
HEXISTS key field
HINCRBY key field increment
```

同理，可以用HSCAN优化迭代

## Zset有序集合

与Set几乎一模一样，只是对于每个元素，都有一个分数与之对应，这样就可以让成员按照分数进行排序

基本操作：
```redis
ZADD key score member [score member ...] //添加
ZREM key member [member ...] //删除
ZSCORE key member //获取某成员的分数
ZCARD key
ZRANK key member //按分数升序展示某个成员的排名，降序变成ZREVRANK
ZRANGE key start stop [WITHSCORES] //按分数升序展示指定排名内的成员，添加个WITHSCORES 可以同时返回分数，降序改成ZREVRANGE
ZCOUNT key min max //数数，按照在指定的分数范围内
```

也有zscan优化迭代。
```redis
127.0.0.1:6379> zadd zl 0 paul 1 steve 2 lijn
(integer) 3
127.0.0.1:6379> zscore zl paul
"0"
127.0.0.1:6379> zcard zl
(integer) 3
127.0.0.1:6379> zrevrank zl lijn
(integer) 0
127.0.0.1:6379> zrevrank zl paul
(integer) 2
127.0.0.1:6379> zrange zl 0 -1 withscores
1) "paul"
2) "0"
3) "steve"
4) "1"
5) "lijn"
6) "2"
127.0.0.1:6379> zcount zl 0 1
(integer) 2
127.0.0.1:6379> zscan zl 0 match *l* count 5
1) "0"
2) 1) "paul"
   2) "0"
   3) "lijn"
   4) "2"
```

## HyperLogLogs基数统计

它可以用作基数统计，说人话就是所有元素的个数，重复的不算。

它的优势体现在它用的内存很少，但是也有缺陷就是估算出来的基数并不准确，所以只能用于可容错的场景。

其基本用法如下：
```redis
127.0.0.1:6379> pfadd pf1 a b c d e f g
(integer) 1
127.0.0.1:6379> pfcount pf1
(integer) 7
127.0.0.1:6379> pfadd pf2 a b c d t h j
(integer) 1
127.0.0.1:6379> pfcount pf2
(integer) 7
127.0.0.1:6379> pfmerge pf3 pf1 pf2
OK
127.0.0.1:6379> pfcount pf3
(integer) 9
```

## Bitmap位存储

类似于C++中的bitset，都是操作内存中的每一个bit.

```
SETBIT key offset value //设置
GETBIT key offset //查询
BITCOUNT key [start end] //查询指定范围内的1的数量
BITOP operation destkey key[key...] //进行位操作，将结果保存到destkey
```
