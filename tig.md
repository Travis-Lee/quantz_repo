docker 网络设置
创建一个network，每个容器分配固定ip地址，配置好每个容器互相访问的ip地址

docker run --name some-mongo -v /my/custom:/etc/mongo -d mongo --config /etc/mongo/mongod.conf

docker run --name quantz_mongo --network host -v /Users/yuz/proj/quant/mongo_db:/data/db -d mongo:4.4.2


## 创建网络 telegraf、influxdb、monogoDB、grafana
docker network create --subnet 172.19.0.0/16 timg


## Docker 安装 influxdb

```bash
docker run -d --name influxdb --net=timg --ip=172.19.0.222 -p 8086:8086 quay.io/influxdb/influxdb:v2.0.2

docker run --name influxdb --net=influxdb -p 8086:8086 quay.io/influxdb/influxdb:v2.0.2
docker run --name influxdb --network host quay.io/influxdb/influxdb:v2.0.2


-v /etc/influxdb/influxdb.conf:/etc/influxdb/influxdb.conf \ 
-v /var/lib/influxdb:/var/lib/influxdb

docker exec -it influxdb /bin/bash
localhost:8086
```

### influxdb 配置
```bash
export INFLUXD_CONFIG_PATH=/path/to/custom/config/directory
https://docs.influxdata.com/influxdb/v2.0/reference/config-options/
export INFLUX_TOKEN=2ImAuTCxqi3vJyVt-q9Ubsip40bc68C5yiOpI60MRwMagqj7fPHCkCKE71xKoQFBYp7BX7roVwTGYNBx77V7Tw==
```

## Docker 安装telegraf

docker run --name telegraf -e INFLUX_TOKEN=2ImAuTCxqi3vJyVt-q9Ubsip40bc68C5yiOpI60MRwMagqj7fPHCkCKE71xKoQFBYp7BX7roVwTGYNBx77V7Tw== --net=influxdb telegraf


docker run --name telegraf --net=container:influxdb telegraf
docker run --name telegraf --network host telegraf:1.16.3
docker run --net=container:influxdb telegraf


docker run -d --name=telegraf --network host -v $PWD/telegraf.conf:/etc/telegraf/telegraf.conf:ro telegraf:1.16.3

telegraf --config http://localhost:8086/api/v2/telegrafs/06c1610a88585000

## Docker 安装 grafana

docker pull 

docker run -d -p 3000:3000 --name grafana grafana/grafana:7.3.5

-v $PWD/etcgrafana:/etc/grafana -v $PWD/usrsharegrafana:/usr/share/grafana -v $PWD/varloggrafana:/var/log/grafana 

mkdir varlibgrafana etcgrafana usrsharegrafana  varloggrafana etcmongo mongo_db

docker run -d -p 3000:3000 --name grafana_quant -v $PWD/varlibgrafana:/var/lib/grafana/ -e "GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource 1.4.1" grafana/grafana:7.3.5

docker run -d -p 27017:27017 --name mongo_quant -v $PWD/etcmongo:/etc/mongo -v $PWD/mongo_db:/data/db -d mongo:4.4.2 

--config /etc/mongo/mongod.conf

docker run -d --name influxdb -p 8086:8086 IMAGE [COMMAND] [ARG...]


Mac 不支持docker 网络设置为 host，因此必须想其他办法
http://host.docker.internal:27017 访问 host的主机地址