# Get Started with quantz_repo

## System Requirements
1. MongoDB: quantz-repo 使用 MongoDB 作为数据存储的数据库，使用本代码之前，你必须有一个可用的 MongoDB 数据库
2. Anaconda: 一个开箱即用的 Python 环境，笔者使用的就是Anaconda，建议使用
3. tushare：本代码依赖tushare，你必须提前配置好 tushare 的 token（`ts.set_token('your token here')`），由于 tushare 的部分接口要求会员积分，你的 tushare 账号至少要有2000以上的积分, 参考 [https://www.waditu.com/document/1?doc_id=40](https://www.waditu.com/document/1?doc_id=40)

## Installation
```bash
git clone git@github.com:zhangyuz/quantz_repo.git
cd quantz_repo
pip install .
```

## Show Me the Code
```python
import quantz_repo
quantz_repo.initialize_db(db='quntz_repo', host='127.0.0.1', port=27017)
quantz_repo.get_us_initial_jobless()
quantz_repo.initialize_industrial_classification()
quantz_repo.get_industrial_classifications(level='L2')
quantz_repo.get_industrial_classfication_members('801710.SI')
quantz_repo.get_industrial_classification_for(ts_code='300496.SZ')
quantz_repo.deinitialize_db()
```
其他实例可以参考源码中的单元测试代码。