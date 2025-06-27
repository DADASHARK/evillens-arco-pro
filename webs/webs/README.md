所有的示例数据都写在了init_db.py中
生成在instance/app.db中
运行run.



# 6.10 新增
1. 增加了用户登录后端哈希表
具体代码增加：
controllers/auth_controller.py
models/database.py L15 L115-129 L135-146
app.py L23-24 L53