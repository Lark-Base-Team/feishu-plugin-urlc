## 飞书 长链接转短链接插件

## 数据表设计
```python
class ShortLink(Base):
    __tablename__ = "short_link"
    id = Column(Integer, primary_key=True)
    short_key = Column(String(30), unique=True, nullable=False)  # 短连接KEY，数据库唯一
    source_url = Column(String(300), nullable=False)  # 原连接
    created_time = Column(DateTime, nullable=False)

```

## 部署相关

- 初始化数据库
```shell
python backend/init_db.py 
```

- 前端页面打包
```bash
bash build.sh
```


- 启动flask server
```shell
python backend/main.py 
```
