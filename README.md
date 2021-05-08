
# Get Started with quantz_repo

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d80278dcbcac47bf9cb2dcbc18857792)](https://app.codacy.com/gh/zhangyuz/quantz_repo?utm_source=github.com&utm_medium=referral&utm_content=zhangyuz/quantz_repo&utm_campaign=Badge_Grade)
[![CodeFactor](https://www.codefactor.io/repository/github/zhangyuz/quantz_repo/badge)](https://www.codefactor.io/repository/github/zhangyuz/quantz_repo)

## System Requirements
1. MongoDB: quantz-repo 使用 MongoDB 作为数据存储的数据库，使用本代码之前，你必须有一个可用的 MongoDB 数据库`docker run --name quantz_mongo -d -p 27017:27017 -v you/data/path:/dadta/db mongo:4.4.2`
2. Anaconda: 一个开箱即用的 Python 环境，笔者使用的就是Anaconda，建议使用
3. tushare：本代码依赖tushare，你必须提前配置好 tushare 的 token（`ts.set_token('your token here')`），由于 tushare 的部分接口要求会员积分，你的 tushare 账号至少要有2000以上的积分, 参考 [https://www.waditu.com/document/1?doc_id=40](https://www.waditu.com/document/1?doc_id=40)
4. https://fred.stlouisfed.org/docs/api/fred/, FRED 开发者 api key

## Installation
```bash
git clone git@github.com:zhangyuz/quantz_repo.git
cd quantz_repo
pip install .
```
## Usage
安装完成后，你需要调用各种初始化函数来初始化各种数据，参考下边代码，各种initialize_xxx和get_xxx。

### Show Me the Code
```python
import quantz_repo
quantz_repo.initialize_db(db='db_name', host='mongo_host', port=27017)
quantz_repo.get_us_initial_jobless()
quantz_repo.initialize_industrial_classification()
quantz_repo.get_industrial_classifications(level='L2')
quantz_repo.get_industrial_classfication_members('801710.SI')
quantz_repo.get_industrial_classification_for(ts_code='300496.SZ')
quantz_repo.deinitialize_db()
```
API 文档待完善，其他实例可以参考源码中的单元测试代码和sample.ipynb。所有公开api都可查看quantz_repo/__init__.py,代码中有相关注释。

### quantzrepoi
用作初始化数据，安装完成后，要运行此命令并保证运行成功
```shell
quantzrepoi
```

### quantzrepou
用作手动更新数据库数据到最新
```shell
quantzrepou
```

### quantzrepod
这是日常更新数据库的守护进程，安装quantz_repo 完成后可以直接在命令行使用。
```shell
quantzrepod
```