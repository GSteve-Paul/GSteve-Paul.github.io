---
title: "P0: C++ Primer"
tags:
  - CPP
date: 2025-09-07
---
一上来感觉很有压力啊！首先就摆明了：如果无法完美地完成Project #0 ，那么这个课就可以直接不用来上啦！我之前并没有学过太多现代C++的内容，如果你和我一样，那么就先看看这个[Bootcamp](https://github.com/cmu-db/15445-bootcamp)吧，会有很大帮助的！

## 配置环境

首先是克隆一份仓库，并创建一个分支指向 v20241207-2024fall这个tag。然后就是设置自己的开发环境——由于我用的是Ubuntu 24.04 LTS，所以需要修改一下Makefile的代码，不然可能会报错。另外是clang-tidy的配置也需要改动（OJ上的配置和仓库里的不同，可能会导致OJ上通不过），建议随便交一发看OJ上的输出，并改成和OJ一样的。

## 了解概念

这个小项目其实就是让你实现一个用来估计基数的算法HyperLogLog。我们并不用了解算法的原理，用C++写出来就好了。教程中也把算法的流程讲解得很详细——在大致读完两个任务后就会知道两个任务的大致区别就在于一个是找第一个高位1的位置，另一个是找第一个低位1的位置。

## 实现

### Task1

这个实现起来很简单的。在构造`HyperLogLog`实例的时候就可以计算出`b`和`m`，并开一个含有`m`个元素的`vector`当作寄存器。其他的几个函数目的都很明确，也就只有`HyperLogLog::AddElem()`稍微有点复杂而已：

```c++ title="src/primer/hyperloglog.cpp"
template <typename KeyType>
auto HyperLogLog<KeyType>::AddElem(KeyType val) -> void {
  hash_t hash = CalculateHash(val);
  std::bitset<BITSET_CAPACITY> bset = ComputeBinary(hash);
  uint64_t index = RegisterIndex(bset);
  uint64_t value = PositionOfLeftmostOne(bset);
  sum_ -= 1.0 / std::pow(2.0, bucket_[index]);
  bucket_[index] = std::max(bucket_[index], value);
  sum_ += 1.0 / std::pow(2.0, bucket_[index]);
}
```

上面代码的`sum_`就是教程中所建议进行维护的$Sum$。

如果你的实现较好，那么应该可以顺利通过BasicTest1、BasicTest2和EdgeTest1。对于EdgeTest2，你应该确保能够正确处理`n_bits`为0的情况。对于BasicParallelTest和ParallelTest1，要注意`sum_`和`bucket_`是临界的，且是在`HyperLogLog::AddElem()`中写入，在`HyperLogLog::ComputeCardinality()`中读出，所以可以参考Bootcamp的rwlock.cpp，给它们分别加读写锁。

```c++ title="src/primer/hyperloglog.cpp"
template <typename KeyType>
auto HyperLogLog<KeyType>::AddElem(KeyType val) -> void {
  hash_t hash = CalculateHash(val);
  std::bitset<BITSET_CAPACITY> bset = ComputeBinary(hash);
  uint64_t index = RegisterIndex(bset);
  uint64_t value = PositionOfLeftmostOne(bset);
  std::unique_lock lk(m_);
  sum_ -= 1.0 / std::pow(2.0, bucket_[index]);
  bucket_[index] = std::max(bucket_[index], value);
  sum_ += 1.0 / std::pow(2.0, bucket_[index]);
}

template <typename KeyType>
auto HyperLogLog<KeyType>::ComputeCardinality() -> void {
  std::shared_lock lk(m_);
  cardinality_ = std::floor(CONSTANT * num_register_ * num_register_ / sum_);
}
```

上面的`m_`就是一个`std::shared_mutex`。

这样任务1的测试应该都可以顺利通过了。

### Task2

任务2的算法流程没有任务1中说得那么详细，这里建议阅读一下教程中提到的[这篇文章](https://engineering.fb.com/2018/12/13/data-infrastructure/hyperloglog/)。这样你应该可以了解到`dense_bucket_`和`overflow_bucket_`的区别：前一个放的是`p`的低$4$位，后一个放的是`p`的高位。因为我们这个小项目里都是处理的64位的哈希数据，当`b`不为$0$时，`p`的值域在$[0, 63]$，也就是说$7$个二进制位就够表示了，所以框架代码中高位的`bitset`的位数为$7 - 4 = 3$。

上面了解的是如何计算寄存器的新值。对于更新寄存器的逻辑，没有什么变化，需要注意的是比较`R`的时候应当把对应的`dense_bucket_`和`overflow_bucket_`又结合成一个数字再比较，不可以单独只看其中一个。

还有更重要的就是精度问题。在[[p0 c++ primer#任务1|任务1]]中我们是动态维护的`sum_`，在任务2中这会导致严重的精度问题（$1 + 2^{-63}$会表示不出来，进而一直丢失精度），致使PrestoCase1即使改成`long double`也无法通过。所以在这里我不再动态维护`sum_`，而是每次调用`HyperLogLogPresto::ComputeCardinality()`就遍历所有寄存器并计算`sum_`：

```c++ title="src/primer/hyperloglog_presto.cpp"
template <typename T>
auto HyperLogLogPresto<T>::ComputeCardinality() -> void {
  std::shared_lock lk(m_);
  sum_ = 0;
  for (int i = 0; i < static_cast<int>(num_register_); i++) {
    uint64_t pos = (overflow_bucket_[i].to_ullong() << DENSE_BUCKET_SIZE) + dense_bucket_[i].to_ullong();
    sum_ += 1.0 / std::pow(2, pos);
  }
  cardinality_ = std::floor(CONSTANT * (num_register_ * num_register_ / sum_));
}
```

这虽然很笨，但是确实有效……因为这样在处理很小的数字时能够更好地保留精度，具体原因可以看CS:APP中关于非规格化数的章节。不管怎么样，这样的实现至少能让我通过测试，不至于被“逐出”课堂。