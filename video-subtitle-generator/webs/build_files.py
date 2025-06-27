import os


def create_directory_structure():
    # 定义项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # 创建根目录
    # os.makedirs(root_dir, exist_ok=True)

    # 创建根目录文件
    root_files = [
        "app.py",
        "config.py",
        "run.py",
        "init_db.py",
        "requirements.txt",
        ".env",
    ]

    for file in root_files:
        open(os.path.join(root_dir, file), "w").close()

    # 创建models目录结构
    models_dir = os.path.join(root_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    models_files = [
        "__init__.py",
        "db.py",
        "video.py",
        "keyword.py",
        "video_keyword.py",
        "gang.py",
        "cross_platform_account.py",
    ]

    for file in models_files:
        open(os.path.join(models_dir, file), "w").close()

    # 创建controllers目录结构
    controllers_dir = os.path.join(root_dir, "controllers")
    os.makedirs(controllers_dir, exist_ok=True)

    controllers_files = [
        "__init__.py",
        "video_controller.py",
        "geography_controller.py",
        "trends_controller.py",
        "keywords_controller.py",
        "gangs_controller.py",
        "report_controller.py",
        "simple_api_controller.py",
    ]

    for file in controllers_files:
        open(os.path.join(controllers_dir, file), "w").close()

    print(f"项目目录结构已创建在: {os.path.abspath(root_dir)}")


if __name__ == "__main__":
    create_directory_structure()
