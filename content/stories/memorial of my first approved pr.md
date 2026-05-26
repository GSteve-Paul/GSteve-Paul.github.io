---
title: 记第一次发布成功的PR
date: 2025-06-08
---
破事水🌊~ 但这是我[第一次发出并迅速被批准的一个PR](https://github.com/jackyzha0/quartz/pull/2012)。

## 摘要

这个PR解决了[Quartz 4](https://github.com/jackyzha0/quartz)中的评论模块无法自定义[giscus](https://giscus.app/)语言的问题。其实就是原作者没给选项里添上这个语言字段而已，连我一个基本不会前端，完全不会TypeScript的人本着连猜带蒙的原则都会改。

## 修改内容

这是giscus给出的一段代码，放在网页里就可以做评论模块，注意到`data-lang`字段表示语言。
而Quartz 4也就是对这个代码进行了一些复杂的包装而已。
```js
<script src="https://giscus.app/client.js"
        data-repo="[ENTER REPO HERE]"
        data-repo-id="[ENTER REPO ID HERE]"
        data-category="[ENTER CATEGORY NAME HERE]"
        data-category-id="[ENTER CATEGORY ID HERE]"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="en"
        crossorigin="anonymous"
        async>
</script>
```
于是就可以在Quartz 4中的包装这些参数的地方填上`data-lang`参数即可，顺便要设定一个默认值`en`比较好。

在这样的改动后，我只需要在`quartz.layout.ts`添加这些代码就能配置成中文的giscus了。

```diff
afterBody: [
    Component.Comments({
        provider: 'giscus',
        options: {
            // from data-repo
            repo: 'XXXXXXXXXXX',
            // from data-repo-id
            repoId: 'XXXXXXXXXXX',
            // from data-category
            category: 'XXXXXXXXXXX',
            // from data-category-id
            categoryId: 'XXXXXXXXXXX',
+           // from data-lang
+           lang: 'zh-CN',
        }
    }),
],
```

## 题外

没想到我发表PR后很快就有合作者来审核，告诉我添了这个新功能还要在文档里面写好。确实像这样的大项目就需要更加细致准确的文档管理，以前我从未写过像样的文档。