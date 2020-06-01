# 开发笔记

## MongoEngine 保存数据后立刻读取数据不会更新???
原因：MongoEngine 默认数据是做了缓存的，如果不特别指定，会使用缓存的数据，不会再次冲数据库中获取。为了更新数据，需要调用 `QuerySet` 的 `no_cache()` 函数关掉缓存，这样下次获取数据时，MongoEngine就会获取数据库最新数据，更新缓存。

## eval

## exec

