---
title: "P1: Buffer Pool Manager"
tags:
  - CPP
  - 并发
  - RAII
date: 2025-09-11
---
严格来说，这才是CMU 15-445的第一个项目，还是挺简单的，但是因为这是第一次写这种需要保证线程安全的程序，所以还是出现了不少小意外。

## Task1 LRU-K 置换策略

LRU-K和LRU相似，但是显然是不一样的。LRU是在现有的`Frame`中找到自上次访问以来所经历的时间最长的那个`Frame`然后把它给淘汰掉；而LRU-K是在现有的`Frame`中找到倒数第$k$次访问以来所经历的时间最长的那个`Frame`然后把它淘汰掉，如果不足$k$次访问当作经历的时间无限长，在无限长中则去找最“旧”的那一个。于是你就会发现，LRU-1是和LRU完全一致的，而当$k > 1$之后，有很重要的一点就是不足`k`次访问的`Frame`一定会被优先淘汰掉，这就会让原本的LRU更能不被偶尔的那种出现1次的`Frame`所干扰。

其实上面说这么多只是对于LRU-K算法的一点理解，对通过这个任务其实并没有太大的作用。根据框架代码，我们很容易想到在`RecordAccess()`的时候就把访问的时候的时间戳压入到`node_store_`里所对应的`LRUKNode`里的`history_`这个链表里，确保这个链表的长度不超过`k`即可。在调用`Evict()`淘汰的时候就遍历这个`node_store_`，排除掉不可淘汰的页之后根据上面的规则找到最应该被淘汰掉的页即可。

这样的实现，想必在`Frame`数量很多的时候肯定会比较缓慢吧，毕竟这必须要遍历所有的`Frame`。因此我想着能不能模仿LRU算法的实现（双向链表），事实证明，这是完全可行的。

首先我们考虑在`LRUKReplacer`中放一个链表`std::list<frame_id_t> access_log_`，维护的就是按时间顺序被访问到的各个`Frame`，因此`RecordAccess()`的实现就可以是在`history_`里记录下近$k$次访问在`access_log_`里的迭代器，当`history_`的元素数量等于$k$之后，就可以把之前最旧的一次访问弹出并从`access_log_`中删除，并压入一个新的访问。

如果你用双向链表实现过LRU算法，你将会觉得上面的这些策略非常熟悉且合理，然而，它并不能优先删除不足$k$次访问的`Frame`。所以，我们要专门为不足$k$次访问的`Frame`单独安排一个`std::list<frame_id_t> non_k_access_log_`，在`Evict()`的时候就应该优先看`non_k_access_log_`，其次再看`access_log_`，因此`RecordAccess()`将会在`history_`的元素数量小于$k$的时候往`access_log_`和`non_k_access_log_`都压入这个`Frame`，当元素数量一旦等于$k$，则将对应`Frame`在`non_k_access_log_`中的访问尽数删除即可。

最后记得加锁，实际上一把大锁从头锁到尾没啥问题。

下面是两个关键函数`Evict()`和`RecordAccess()`的实现：

```c++ title="src/buffer/lru_k_replacer.cpp"
auto LRUKReplacer::Evict() -> std::optional<frame_id_t> {
  std::scoped_lock slk(latch_);
  std::optional<frame_id_t> ret = std::nullopt;
  for (auto fid : non_k_access_log_) {
    if (!node_store_[fid].is_evictable_) {
      continue;
    }
    ret = fid;
    break;
  }
  if (ret != std::nullopt) {
    goto RETURN;
  }
  for (auto fid : access_log_) {
    if (!node_store_[fid].is_evictable_) {
      continue;
    }
    ret = fid;
    break;
  }
RETURN:
  if (ret != std::nullopt) {
    RemoveNoLock(ret.value());
  }
  return ret;
}

void LRUKReplacer::RecordAccess(frame_id_t frame_id, [[maybe_unused]] AccessType access_type) {
  BUSTUB_ASSERT(static_cast<size_t>(frame_id) < replacer_size_, "Invalid frame_id");
  std::scoped_lock slk(latch_);
  if (node_store_.count(frame_id) == 0) {
    node_store_[frame_id] = LRUKNode(k_, frame_id);
  }
  auto &node = node_store_[frame_id];
  access_log_.emplace_back(frame_id);
  node.history_.emplace_back(prev(access_log_.end()));
  if (node.history_.size() > node.k_) {
    access_log_.erase(node.history_.front());
    node.history_.pop_front();
  } else if (node.history_.size() == node.k_) {
    for (auto iter : node.non_k_history_) {
      non_k_access_log_.erase(iter);
    }
    node.non_k_history_.clear();
  } else {
    non_k_access_log_.emplace_back(frame_id);
    node.non_k_history_.emplace_back(prev(non_k_access_log_.end()));
  }
}
```

本地的LRU-K置换策略的测试太水了，好像也测不出来啥，基本上都能过。

## Task2 磁盘调度器

这个任务感觉也是相对简单的。简而言之，磁盘调度器会接受一系列的磁盘IO读写操作，然后用另一个线程以不阻塞主线程的方式进行IO读写并通知IO读写是否完成。感觉难点可能在于认识`std::promise`和`std::future`。这俩是用来线程间交流的，其中`std::promise`可以把结果存起来，而与之对应的`std::future`则可以把结果取出来。其余没啥难度了：

```c++ title="src/storage/disk/disk_scheduler.cpp"
DiskScheduler::~DiskScheduler() {
  // Put a `std::nullopt` in the queue to signal to exit the loop
  request_queue_.Put(std::nullopt);
  if (background_thread_.has_value()) {
    background_thread_->join();
  }
}

void DiskScheduler::Schedule(DiskRequest r) { request_queue_.Put(std::move(r)); }

void DiskScheduler::StartWorkerThread() {
  std::optional<DiskRequest> opt;
  while (opt = request_queue_.Get(), opt.has_value()) {
    DiskRequest req = std::move(opt.value());
    if (req.is_write_) {
      disk_manager_->WritePage(req.page_id_, req.data_);
    } else {
      disk_manager_->ReadPage(req.page_id_, req.data_);
    }
    req.callback_.set_value(true);
  }
}
```

## Task3 缓冲池管理器

缓冲池，就是用有限的内存上的空间缓冲磁盘上的页，所以缓冲池管理器就要负责管理如何在需要IO操作的时候把磁盘中的页调换到内存中来，并在内存不够用的时候把内存中的`Frame`给调换回磁盘去。其中管理磁盘读写的工作就是上面的[[p1 buffer pool manager#Task2 磁盘调度器|磁盘调度器]]做的事情，而有关淘汰内存中的`Frame`所用的策略便是上述的[[p1 buffer pool manager#Task1 LRU-K 置换策略|LRU-K置换策略]]。

### 实现缓冲池

为了更好地对内存中的`Frame`进行IO操作，框架的代码中引入了一个`FrameHeader`来提供了一个`Frame`相关的元信息及其数据内容。考虑到如果让用户直接使用`Frame`，很可能会导致一些并发问题（教程中所提及），也需要用户在认为自己用完`Frame`之后将其放到空闲区，写回一些内容。这样的诸多事情会让用户很难用且很容易出错，所以框架代码建议我们不妨直接引入两个RAII的类（`ReadPageGuard`和`WritePageGuard`），这些类可以为用户提供线程安全的对`Frame`的读写操作。

框架代码的注释告诉我们应该先行实现函数`BufferPoolManager::CheckedWritePage()`，显然，这个函数的意思就是让我们找`page_id`对应的一个`Frame`，并用这个`Frame`去构造一个`WritePageGuard`。自然，如果之前已经有一个`Frame`对应的这个`page_id`，那就 依旧照样用它，如果没有的话，就需要我们去找一个空闲的`Frame`了。如果`free_frames_`非空，那么就可以从里面取一个出来当作空闲`Frame`，否则就要用LRU-K算法淘汰掉一个`Frame`。注意淘汰出来的`Frame`应当根据其脏位决定是否需要进行一个写回的操作，在此之后应该把磁盘中的内容又写到这个`Frame`里面来，方便之后的读写工作。大致代码如下：

```c++ title="src/buffer/buffer_pool_manager.cpp"
auto BufferPoolManager::CheckedWritePage(page_id_t page_id, AccessType access_type) -> std::optional<WritePageGuard> {
  bpm_latch_->lock();
  size_t cnt = page_table_.count(page_id);
  if (cnt != 0) {
    frame_id_t fid = page_table_[page_id];
    auto frame = frames_[fid];
    return WritePageGuard(page_id, frame, replacer_, bpm_latch_);
  }
  auto fid_opt = GetFreeFrame();
  if (!fid_opt.has_value()) {
    bpm_latch_->unlock();
    return std::nullopt;
  }
  auto fid = fid_opt.value();
  auto frame = InitFreeFrame(fid, page_id);
  return WritePageGuard(page_id, frame, replacer_, bpm_latch_);
}

auto BufferPoolManager::GetFreeFrame() -> std::optional<frame_id_t> {
  if (!free_frames_.empty()) {
    frame_id_t fid = free_frames_.front();
    free_frames_.pop_front();
    return fid;
  }
  auto fid_opt = replacer_->Evict();
  if (!fid_opt.has_value()) {
    return std::nullopt;
  }
  frame_id_t fid = fid_opt.value();
  auto frame = frames_[fid];
  FlushPageNoLock(frame->page_id_.value());
  page_table_.erase(frame->page_id_.value());
  frame->page_id_ = std::nullopt;
  return fid;
}

auto BufferPoolManager::InitFreeFrame(frame_id_t frame_id, page_id_t page_id) -> std::shared_ptr<FrameHeader> {
  auto frame = frames_[frame_id];
  page_table_[page_id] = frame_id;
  frame->page_id_ = page_id;
  if (frame->pin_count_ == 0) {
    frame->Reset(page_id);
    auto promise = disk_scheduler_->CreatePromise();
    auto future = promise.get_future();
    disk_scheduler_->Schedule({false, frame->GetDataMut(), frame->page_id_.value(), std::move(promise)});
    replacer_->RecordAccess(frame_id);
    future.get();
  }
  return frame;
}

auto BufferPoolManager::FlushPageNoLock(page_id_t page_id) -> bool {
  if (page_table_.count(page_id) == 0) {
    return false;
  }
  frame_id_t fid = page_table_[page_id];
  auto frame = frames_[fid];
  if (frame->is_dirty_) {
    auto promise = disk_scheduler_->CreatePromise();
    auto future = promise.get_future();
    disk_scheduler_->Schedule({true, frame->GetDataMut(), frame->page_id_.value(), std::move(promise)});
    frame->is_dirty_ = false;
    return future.get();
  }
  return true;
}
```

这样，`BufferPoolManager`中的剩下的那些函数该怎么实现其实也差不多七七八八了，虽然在具体的实现过程中确实还是有点复杂的，不过至少知道要干什么了，对吧？

### 实现PageGuard

由于`ReadPageGuard`和`WritePageGuard`实际上差不太多，所以在这里只考虑`WritePageGuard`该怎么实现。总体来说，这个`PageGuard`干的事情就是在构造、析构的时候管理它所需要的资源，其他时候就提供一些API接口可供读写。

#### 构造函数

```c++ title="src/storage/page/page_guard.cpp"
WritePageGuard::WritePageGuard(page_id_t page_id, std::shared_ptr<FrameHeader> frame,
                               std::shared_ptr<LRUKReplacer> replacer, std::shared_ptr<std::mutex> bpm_latch)
    : page_id_(page_id),
      frame_(std::move(frame)),
      replacer_(std::move(replacer)),
      bpm_latch_(std::move(bpm_latch)),
      is_valid_(true) {
  frame_->pin_count_++;
  replacer_->SetEvictable(frame_->frame_id_, false);
  bpm_latch_->unlock();
  frame_->rwlatch_.lock();
}
```

这里的`bpm_latch_.unlock()`是有说法的，它正好是和`BufferPoolManager::CheckedWritePage()`的`bpm_latch.lock()`是对应的。那为什么不能直接在`BufferPoolManager::CheckedWritePage()`里面一把大锁从早锁到晚呢？可以参考一下`BufferPollManagerTest`中`DeadlockTest`的代码：如果有两个`CheckedWritePage`发生，那么第二个一定会因为拿不到`Frame`的`rwlatch_.lock()`而卡住，这就会导致一直锁住了`BufferPoolManager`的`bpm_latch_`，进而使得其他的关于`BufferPoolManager`的操作都无法进行。

所以我们要在这里开一下手动挡，手动控制`bpm_latch_`的开关。

此外，还有一个重点就是确保`WritePageGuard`的构造函数的`frame`的有效性，具体就是一定要从拿到空闲的`Frame`开始一直到更新`Frame`的`pin_count`和`SetEvictable`为止，中间绝不可以解锁。如果中间解锁，由于是多线程的，很有可能会把你这个`Frame`拿去淘汰掉了，进而导致这个`Frame`直接失效，产生一系列莫名其妙无法理解的并发Bug（我调试了1天）。

#### 析构函数

```c++ title="src/storage/page/page_guard.cpp"
void WritePageGuard::Drop() {
  if (!is_valid_) {
    return;
  }
  std::scoped_lock slk(*bpm_latch_);

  if (--(frame_->pin_count_) == 0) {
    replacer_->SetEvictable(frame_->frame_id_, true);
  }
  frame_->rwlatch_.unlock();
  frame_.reset();

  replacer_.reset();
  bpm_latch_.reset();

  is_valid_ = false;
}

WritePageGuard::~WritePageGuard() { Drop(); }
```

析构函数差不多就是把构造函数时候的东西反过来一下就可以了。注意`WritePageGuard::Drop()`是用来手动析构的，所以要把那些智能指针也给释放了。

#### 移动语义

很显然这种管理资源的RAII对象是不可以拷贝的，不然容易导致多次释放、释放后使用的问题，因而只能移动。 框架代码中开放了两个函数，一个用于移动赋值，一个用于移动构造，它俩有区别但是在这里都基于同样的原则，这里就只说移动赋值函数。它相当于让一个`WritePageGuard`接管另一个`WritePageGuard`的资源，所以应该先把自己这个`WritePageGuard`管理的资源先释放掉，然后把另一个的资源用`std::move()`接管过来，然后再设置另一个的失效位。需要注意的是应当在最开始判断这两个`WritePageGuard`是不是同一个，如果是那就直接返回即可，否则会出事！

```c++ title="src/storage/page/page_guard.cpp"
auto WritePageGuard::operator=(WritePageGuard &&that) noexcept -> WritePageGuard & {
  if (&that == this) {
    return *this;
  }
  this->Drop();

  this->page_id_ = that.page_id_;
  this->frame_ = std::move(that.frame_);
  this->replacer_ = std::move(that.replacer_);
  this->bpm_latch_ = std::move(that.bpm_latch_);
  this->is_valid_ = that.is_valid_;

  that.is_valid_ = false;

  return *this;
}
```

实现了以上的这些内容，再补上其他的一些API，不出意外就可以通过所有测试了~需要注意的是如果要上排行榜的话，应该先在仓库的根目录下`python3 gradescope_sign.py`生成GRADESCOPE.md，然后再`make submit-p1`生成project1-submission.zip。

我在Leaderboard Task中测得我的实现的QPS为4699.16923，我的LRU-K算法的优化版实现应该起了不小作用。