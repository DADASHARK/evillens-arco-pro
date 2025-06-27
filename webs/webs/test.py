# import sys
# # 添加项目根目录到 Python 模块搜索路径
# sys.path.append("d:\\XAS\\video-subtitle-generator\\webs")
from webs.run import start_app

start_app(enable_file_watcher=True)
