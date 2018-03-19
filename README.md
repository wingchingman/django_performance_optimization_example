[Python Django性能测试与优化指南](http://blog.csdn.net/dev_csdn/article/details/78782570)
源码运行起来有问题，最后把 BashHash 相关的部分给去掉

===

看了看 Django 性能优化方面的东西。

# 一：了解瓶颈的指标
第一步也是最重要的地方，用工具找到需要优化的地方，根据指标来判断需不需要优化。
瓶颈的指标：执行时间、响应时间、内存占用、函数调用次数
Web项目中，响应时间（服务器接收由某个用户的操作产生的请求，处理该请求并返回结果所需的总的时间）通常是最重要的指标。

# 二：用工具测量指标 - 确定瓶颈
最常见的 cProfile、line_profiler，其余见参考列表

###### Django 相关的工具
- `django-silk`：记录请求的响应时间，数据库查询的时间和次数  
- `snakeviz`：把 `silk` 的分析文件进行可视化展示，显示调用堆栈，文件名、函数名及其行号，以及该方法花费的时间  
- `django-debug-toolbar`：跟 `django-silk` 类似  

# 三：优化手段、技巧
见参考列表（待整理和实践）
常见方法：算法，选择合适的数据结构、循环优化、使用列表解释和生成式表达式

###### Django 相关
1. 了解执行的 level
    - `queryset.count()` #最低的数据库 level
    - `len(queryset)` #统计 Python objects
    - `\{\{ my_bicycles|length \}\}` #Template filter
2. 常使用 filter()，exclude()，order_by() 的字段加索引
3. 理解 `queryset`
    - lazy 特性：只有 queryset 被 evalute 时才会被执行，比如进行的 filter/exclude 是不触发查询的
    - 生成 cache 的情况：生成 cache 后会保存在 queryset 对象中，不用每次都去数据库查。`Entry.objects.all()` 不会生成 cache
    - 跟 `ForeignKey`、`Many2Many` 、`Many2One` 字段相关的，ForeignKey Field 默认是不提取的，用时才会到数据库查询。`select_related()` 是对 `ForeignKey` 的优化， `Many2Many` 或 `Many2One `用 `prefetch_related()`
    - 如果 `queryset` 只用一次, 使用 `iterator()` 防止占用太多内存，`for star in queryset.iterator(): print(star.name)`
    - 尽可能把数据库层级的工作放到数据库，例如使用 `filter/exclude`，`annotate`，`aggregate`。(getting the database, rather than Python, to do work)

# 四：一个实例实践
一个实例：[Python Django性能测试与优化指南](http://blog.csdn.net/dev_csdn/article/details/78782570)
源码运行起来有问题，最后把 BashHash 相关的部分给去掉

总结一下思路
1. 整个 app 有两个模型，Country，House，用 factory-boy 生成十万条假数据，用 django-rest-framework 提供 api
2. 优化目标：api 的访问
3. 安装 django-silk 分析项目性能：每次请求的用时，数据库查询的次数和时间
    - 一：数据库查询用了 15s，五万多次
        - 第一次优化
            - 优化方法：对 Django ORM 的理解，queryset 的延迟计算
            - 在这个案例中，ForeignKey Field 默认是不提取的，用时才会到数据库查询。所以造成了五万多次的查询。
            - select_related() 是对 ForeignKey 的优化，而 many2many 或 many2one 用 prefetch_related()
        - 第二次优化
            - 只提取需要的值，使用 only 限制查询只需要的字段
    - 二：业务逻辑
        - 使用自定义序列化器。
        - （不清楚是通过哪个指标定位到这里的）
    - 三：使用 `snakeviz` 把前面 silk 的分析文件进行可视化分析
        - 调用堆栈，文件名、函数名及其行号，以及该方法花费的时间
        - 定位到 `basehash/__init__.py`，
    - 告一段落。由最开始的 77s 到最后的 3s

## 实践后的想法
    1. 最重要的地方在于，熟练利用工具来测量性能的指标（运行时间、内存占用），也就是定位到哪里需要优化。所以掌握工具栈很重要。
    2. 熟悉常见的优化技巧。
    3. 按着作者的思路走下来，没得到想要的结果

# 参考
- [Database access optimization¶](https://docs.djangoproject.com/en/2.0/topics/db/optimization/)
- [Performance and optimization¶](https://docs.djangoproject.com/en/2.0/topics/performance/)
- [Python 中有哪些性能优化方法？ - 赖勇浩的回答 - 知乎](https://www.zhihu.com/question/30848372/answer/51531696)
- [代码优化指南：人生苦短，我用Python](https://www.jiqizhixin.com/articles/2017-11-20-5)
- [Python 代码性能优化技巧](https://www.ibm.com/developerworks/cn/linux/l-cn-python-optim/index.html)
- [Django 性能优化官方文档笔记(主要针对ORM)](https://changchen.me/blog/20170503/django-performance-and-optimisation/)

