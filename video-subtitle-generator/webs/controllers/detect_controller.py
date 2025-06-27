# detect_controller.py - 视频检测任务相关API
from flask import Blueprint, jsonify, request
import os
import json
import random
import datetime
import time
import threading
from models.db import db
from flask_cors import CORS  # 添加这一行

# 创建蓝图
detect_bp = Blueprint("detect", __name__)
CORS(detect_bp)  # 添加这一行，为蓝图启用CORS支持

# 允许演示视频链接
DEMO_VIDEO_LINKS = [
    "https://www.douyin.com/video/7476188844711349561",
]

# 存储演示任务 - 使用全局变量存储，简化问题排查
DEMO_TASKS = {}

# 初始化一些示例任务
def init_demo_tasks():
    global DEMO_TASKS
    if not DEMO_TASKS:
        print("创建示例任务...")
        for i in range(2):
            video_ids = [f"sample_video_{j}" for j in range(1, random.randint(3, 6))]
            task = generate_demo_task(video_ids)
            DEMO_TASKS[task["task_id"]] = task
            # 将示例任务标记为已完成
            complete_demo_task(task["task_id"])
        print(f"已创建 {len(DEMO_TASKS)} 个示例任务")

# 修改 generate_demo_task 函数，使用与前端一致的UUID格式
def generate_demo_task(video_ids):
    # 随机生成evil
    evil_video_count = random.randint(0, len(video_ids))
    evil_video_ids = random.sample(video_ids, k=evil_video_count)
    now = datetime.datetime.now()
    
    # 使用与前端一致的UUID格式
    import uuid
    task_id = str(uuid.uuid4())
    
    task = {
        "task_id": task_id,
        "status": "processing",
        "created_at": now.isoformat(),
        "completed_at": None,
        "evil_video_count": evil_video_count,
        "all_video_count": len(video_ids),
        "video_ids": video_ids,
        "evil_video_ids": evil_video_ids,
        "rounds": [],
    }
    return task

# 修改 create_detect_task 函数，添加特殊链接处理
@detect_bp.route("/create_detect_task", methods=["POST", "OPTIONS"])
def create_detect_task():
    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        response = jsonify({"code": 20000, "message": "OK"})
        return add_cors_headers(response)
    
    try:
        data = request.json
        video_url = data.get("video_url", "")
        
        print(f"收到创建任务请求，视频链接: {video_url}")
        
        # 提取链接
        links = [link.strip() for link in video_url.split() if link.strip()]
        if not links:
            response = jsonify({"code": 40000, "message": "无效的视频链接"})
            return add_cors_headers(response), 400
        
        # 特殊链接处理 - 创建指定ID的任务
        if "https://www.douyin.com/video/7476188844711349561" in links:
            print("检测到特殊链接，创建指定ID的任务")
            special_task_id = "44368c7c-4812-4c1a-bfe4-22c288d8eeb9"
            
            # 检查任务是否已存在
            if special_task_id in DEMO_TASKS:
                print(f"特殊任务 {special_task_id} 已存在，直接返回")
                response = jsonify({
                    "code": 20000,
                    "data": {"task_id": special_task_id}
                })
                return add_cors_headers(response)
            
            # 创建特殊任务
            now = datetime.datetime.now()
            special_task = {
                "task_id": special_task_id,
                "status": "processing",
                "created_at": now.isoformat(),
                "completed_at": None,
                "evil_video_count": 1,
                "all_video_count": 1,
                "video_ids": ["douyin_7476188844711349561"],
                "evil_video_ids": ["douyin_7476188844711349561"],
                "rounds": [],
            }
            DEMO_TASKS[special_task_id] = special_task
            
            # 异步处理特殊任务，添加更多轮次
            threading.Thread(target=async_complete_special_task, args=(special_task_id,)).start()
            
            response = jsonify({
                "code": 20000,
                "data": {"task_id": special_task_id}
            })
            return add_cors_headers(response)
        
        # 常规任务处理
        video_ids = [f"video_{int(time.time())}_{i}" for i in range(len(links))]
        task = generate_demo_task(video_ids)
        DEMO_TASKS[task["task_id"]] = task
        
        print(f"创建任务成功: {task['task_id']}")
        
        # 异步处理任务
        threading.Thread(target=async_complete_task, args=(task["task_id"],)).start()
        
        # 返回任务ID
        response = jsonify({
            "code": 20000,
            "data": {"task_id": task["task_id"]}
        })
        return add_cors_headers(response)
    except Exception as e:
        print(f"创建任务失败: {str(e)}")
        response = jsonify({"code": 50000, "message": f"服务器内部错误: {str(e)}"})
        return add_cors_headers(response), 500

# 添加特殊任务的完成函数
def async_complete_special_task(task_id):
    print(f"开始处理特殊任务 {task_id}，将在5秒后完成")
    time.sleep(5)  # 等待5秒
    
    task = DEMO_TASKS.get(task_id)
    if not task:
        print(f"特殊任务 {task_id} 不存在，无法完成")
        return
    
    # 生成两轮扩展，第二轮3个视频，第三轮5个视频
    rounds = []
    
    # 第一轮 - 原始视频
    videos = [{
        "vd_id": "douyin_7476188844711349561",
        "vd_title": "可疑邪典视频示例",
        "create_time": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
        "author": "邪典视频创作者",
        "likes": "8721",
        "shares": "1243",
        "collects": "3567",
        "img_url": "http://example.com/cover_special.jpg",
        "tags": ["儿童", "动画", "可疑内容"]
    }]
    
    rounds.append({
        "round": 1,
        "video_count": 1,
        "videos": videos
    })
    
    # 第二轮 - 3个视频
    videos = []
    for i in range(3):
        vid = f"related_vid_{i+1}"
        videos.append({
            "vd_id": vid,
            "vd_title": f"相关视频 {i+1}",
            "create_time": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 10))).isoformat(),
            "author": random.choice(["小静启蒙早教", "童趣乐园", "故事大王"]),
            "likes": str(random.randint(1000, 10000)),
            "shares": str(random.randint(100, 500)),
            "collects": str(random.randint(500, 2000)),
            "img_url": f"http://example.com/cover_{vid}.jpg",
            "tags": [random.choice(["儿童", "动画", "早教", "益智"]), random.choice(["故事", "游戏", "音乐"])]
        })
    
    rounds.append({
        "round": 2,
        "video_count": 3,
        "videos": videos
    })
    
    # 第三轮 - 5个视频
    videos = []
    for i in range(5):
        vid = f"extended_vid_{i+1}"
        is_evil = random.random() < 0.2  # 20%概率是邪典视频
        
        video_data = {
            "vd_id": vid,
            "vd_title": f"扩展视频 {i+1}" + (" (可疑)" if is_evil else ""),
            "create_time": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 20))).isoformat(),
            "author": random.choice(["趣味动画", "儿童乐园", "益智小天地", "奇妙故事会", "童趣世界"]),
            "likes": str(random.randint(500, 8000)),
            "shares": str(random.randint(50, 300)),
            "collects": str(random.randint(200, 1500)),
            "img_url": f"http://example.com/cover_{vid}.jpg",
            "tags": [random.choice(["儿童", "动画", "早教"]), random.choice(["故事", "游戏", "音乐"])]
        }
        
        videos.append(video_data)
        
        # 如果是邪典视频，添加到evil_video_ids
        if is_evil:
            task["evil_video_ids"].append(vid)
            task["evil_video_count"] += 1
            task["all_video_count"] += 1
    
    rounds.append({
        "round": 3,
        "video_count": 5,
        "videos": videos
    })
    
    # 更新任务状态
    task["status"] = "completed"
    task["completed_at"] = datetime.datetime.now().isoformat()
    task["rounds"] = rounds
    task["all_video_count"] = 1 + 3 + 5  # 总共9个视频
    
    # 更新任务
    DEMO_TASKS[task_id] = task
    
    print(f"特殊任务 {task_id} 已完成，状态更新为: {task['status']}")
    print(f"- 总视频数: {task['all_video_count']}")
    print(f"- 邪典视频数: {task['evil_video_count']}")
    print(f"- 轮次数: {len(task['rounds'])}")

def complete_demo_task(task_id):
    global DEMO_TASKS
    task = DEMO_TASKS.get(task_id)
    if not task:
        print(f"任务 {task_id} 不存在，无法完成")
        return
    
    # 生成两轮扩展，每轮2-3个视频
    rounds = []
    for round_num in range(1, 3):
        videos = []
        for i in range(random.randint(2, 3)):
            vid = f"vid{round_num}{i+1:03d}"
            videos.append({
                "vd_id": vid,
                "vd_title": f"测试视频标题{vid}",
                "create_time": (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 100))).isoformat(),
                "author": random.choice(["小静启蒙早教", "童趣乐园", "故事大王"]),
                "likes": str(random.randint(1000, 3000)),
                "shares": str(random.randint(1, 20)),
                "collects": str(random.randint(500, 1500)),
                "img_url": f"http://example.com/cover{vid}.jpg",
                "tags": [f"标签{random.randint(1, 5)}", f"标签{random.randint(6, 10)}"]
            })
        rounds.append({
            "round": round_num,
            "video_count": len(videos),
            "videos": videos
        })
    
    task["status"] = "completed"
    task["completed_at"] = datetime.datetime.now().isoformat()
    task["rounds"] = rounds
    
    # 更新任务
    DEMO_TASKS[task_id] = task
    
    print(f"任务 {task_id} 已完成，状态更新为: {task['status']}")

def async_complete_task(task_id):
    print(f"开始处理任务 {task_id}，将在5秒后完成")
    time.sleep(5)  # 等待5秒
    complete_demo_task(task_id)
    print(f"任务 {task_id} 处理完成，状态已更新为 completed")

# 初始化示例任务
init_demo_tasks()

# 通用的 CORS 处理函数
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 创建检测任务
# @detect_bp.route("/create_detect_task", methods=["POST", "OPTIONS"])
# def create_detect_task():
#     # 处理 OPTIONS 请求
#     if request.method == "OPTIONS":
#         response = jsonify({"code": 20000, "message": "OK"})
#         return add_cors_headers(response)
    
#     try:
#         data = request.json
#         video_url = data.get("video_url", "")
        
#         print(f"收到创建任务请求，视频链接: {video_url}")
        
#         # 提取链接
#         links = [link.strip() for link in video_url.split() if link.strip()]
#         if not links:
#             response = jsonify({"code": 40000, "message": "无效的视频链接"})
#             return add_cors_headers(response), 400
        
#         # 创建任务
#         video_ids = [f"video_{int(time.time())}_{i}" for i in range(len(links))]
#         task = generate_demo_task(video_ids)
#         DEMO_TASKS[task["task_id"]] = task
        
#         print(f"创建任务成功: {task['task_id']}")
        
#         # 异步处理任务
#         threading.Thread(target=async_complete_task, args=(task["task_id"],)).start()
        
#         # 返回任务ID
#         response = jsonify({
#             "code": 20000,
#             "data": {"task_id": task["task_id"]}
#         })
#         return add_cors_headers(response)
#     except Exception as e:
#         print(f"创建任务失败: {str(e)}")
#         response = jsonify({"code": 50000, "message": f"服务器内部错误: {str(e)}"})
#         return add_cors_headers(response), 500

# 获取任务列表
@detect_bp.route("/task_list", methods=["GET", "OPTIONS"])
def get_task_list():
    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        response = jsonify({"code": 20000, "message": "OK"})
        return add_cors_headers(response)
    
    try:
        # 将任务转换为前端期望的格式
        tasks = []
        print(f"获取任务列表: {len(DEMO_TASKS)} 个任务")
        for task_id, task in DEMO_TASKS.items():
            tasks.append({
                "task_id": task["task_id"],
                "status": task["status"],
                "created_at": task["created_at"],
                "completed_at": task["completed_at"],
                "evil_video_count": task["evil_video_count"],
                "all_video_count": task["all_video_count"]
            })
            print(f"  - 任务 {task_id}: 状态={task['status']}")
        
        # 按创建时间倒序排序，最新的任务在前面
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        response = jsonify({
            "code": 20000,
            "data": {"tasks": tasks}
        })
        return add_cors_headers(response)
    except Exception as e:
        print(f"获取任务列表失败: {str(e)}")
        response = jsonify({"code": 50000, "message": f"服务器内部错误: {str(e)}"})
        return add_cors_headers(response), 500

# 获取任务详情
@detect_bp.route("/get_task/<string:task_id>", methods=["GET", "OPTIONS"])
def get_task(task_id):
    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        response = jsonify({"code": 20000, "message": "OK"})
        return add_cors_headers(response)
    
    task = DEMO_TASKS.get(task_id)
    if not task:
        print(f"任务不存在: {task_id}")
        response = jsonify({"code": 404, "message": "任务不存在"})
        return add_cors_headers(response), 404
    
    print(f"获取任务详情: {task_id}")
    
    # 构建任务详情
    task_detail = {
        "task_id": task["task_id"],
        "vd_id": task["video_ids"][0] if task["video_ids"] else "",
        "status": task["status"],
        "created_at": task["created_at"],
        "updated_at": task["completed_at"] or task["created_at"],
        "evil_video_ids": task["evil_video_ids"]
    }
    
    response = jsonify({"code": 20000, "data": task_detail})
    return add_cors_headers(response)

# 获取任务报告
@detect_bp.route("/get_task_result/<string:task_id>", methods=["GET", "OPTIONS"])
def get_task_result(task_id):
    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        response = jsonify({"code": 20000, "message": "OK"})
        return add_cors_headers(response)
    
    task = DEMO_TASKS.get(task_id)
    if not task:
        print(f"任务不存在: {task_id}")
        response = jsonify({"code": 404, "message": "任务不存在"})
        return add_cors_headers(response), 404
    
    if task["status"] != "completed":
        print(f"任务未完成: {task_id}")
        response = jsonify({"code": 400, "message": "任务尚未完成"})
        return add_cors_headers(response), 400
    
    print(f"获取任务报告: {task_id}, 状态: {task['status']}")
    
    # 构建任务报告
    report = {
        "task_info": {
            "task_id": task["task_id"],
            "status": task["status"],
            "created_at": task["created_at"],
            "completed_at": task["completed_at"],
            "evil_video_ids": task["evil_video_ids"]
        },
        "summary": {
            "total_videos": task["all_video_count"],
            "evil_videos": task["evil_video_count"],
            "normal_videos": task["all_video_count"] - task["evil_video_count"]
        },
        "evil_video_ids": task["evil_video_ids"]
    }
    
    response = jsonify({"code": 20000, "data": report})
    return add_cors_headers(response)

# 获取所有轮次视频
@detect_bp.route("/get_all_round_videos/<string:task_id>", methods=["GET", "OPTIONS"])
def get_all_round_videos(task_id):
    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        response = jsonify({"code": 20000, "message": "OK"})
        return add_cors_headers(response)
    
    task = DEMO_TASKS.get(task_id)
    if not task:
        print(f"任务不存在: {task_id}")
        response = jsonify({"code": 404, "message": "任务不存在"})
        return add_cors_headers(response), 404
    
    if task["status"] != "completed":
        print(f"任务未完成: {task_id}")
        response = jsonify({"code": 400, "message": "任务尚未完成"})
        return add_cors_headers(response), 400
    
    print(f"获取所有轮次视频: {task_id}, 轮次数: {len(task['rounds'])}")
    
    result = {
        "task_id": task["task_id"],
        "total_rounds": len(task["rounds"]),
        "rounds": task["rounds"]
    }
    
    response = jsonify({"code": 20000, "data": result})
    return add_cors_headers(response)

# 获取指定轮次视频
@detect_bp.route("/get_round_videos/<string:task_id>/<int:round_num>", methods=["GET", "OPTIONS"])
def get_round_videos(task_id, round_num):
    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        response = jsonify({"code": 20000, "message": "OK"})
        return add_cors_headers(response)
    
    task = DEMO_TASKS.get(task_id)
    if not task:
        print(f"任务不存在: {task_id}")
        response = jsonify({"code": 404, "message": "任务不存在"})
        return add_cors_headers(response), 404
    
    if task["status"] != "completed":
        print(f"任务未完成: {task_id}")
        response = jsonify({"code": 400, "message": "任务尚未完成"})
        return add_cors_headers(response), 400
    
    # 查找指定轮次
    round_data = None
    for r in task["rounds"]:
        if r["round"] == round_num:
            round_data = r
            break
    
    if not round_data:
        print(f"轮次不存在: {task_id}, 轮次: {round_num}")
        response = jsonify({"code": 404, "message": f"轮次 {round_num} 不存在"})
        return add_cors_headers(response), 404
    
    print(f"获取轮次视频: {task_id}, 轮次: {round_num}, 视频数: {round_data['video_count']}")
    
    result = {
        "task_id": task["task_id"],
        "round": round_num,
        "video_count": round_data["video_count"],
        "videos": round_data["videos"]
    }
    
    response = jsonify({"code": 20000, "data": result})
    return add_cors_headers(response)