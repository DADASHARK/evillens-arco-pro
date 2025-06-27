# controllers/detect_controller.py
import threading
import time
import random
import datetime
import logging
import uuid
from flask import Blueprint, jsonify, request

detect_bp = Blueprint("detect", __name__)

# 添加日志记录
logger = logging.getLogger(__name__)

# 允许的演示视频链接
DEMO_VIDEO_LINKS = [
    "https://www.douyin.com/video/7476188844711349561",
    "https://www.douyin.com/video/7476188844711349562",
    "https://www.douyin.com/video/7476188844711349563",
]

# 存储所有模拟任务 - 改为全局变量，确保任务不会丢失
DEMO_TASKS = {}

# 初始化一些示例任务
def init_demo_tasks():
    """初始化一些示例任务，确保页面加载时有数据展示"""
    if not DEMO_TASKS:
        logger.info("创建初始示例任务...")
        for i in range(2):
            video_ids = [f"7476188844711349{i+1}"]
            task = generate_demo_task(video_ids)
            DEMO_TASKS[task["task_id"]] = task
            # 将示例任务标记为已完成
            complete_demo_task(task["task_id"])
        logger.info(f"已创建 {len(DEMO_TASKS)} 个示例任务")

def generate_demo_task(video_ids):
    """生成一个演示任务"""
    evil_video_ids = random.sample(video_ids, k=random.randint(0, len(video_ids)))
    now = datetime.datetime.now()
    task_id = str(uuid.uuid4())  # 使用UUID生成唯一任务ID
    task = {
        "task_id": task_id,
        "status": "processing",
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "completed_at": None,
        "evil_video_count": len(evil_video_ids),
        "all_video_count": len(video_ids),
        "video_ids": video_ids,
        "evil_video_ids": evil_video_ids,
        "rounds": [],
    }
    return task

def complete_demo_task(task_id):
    """完成一个演示任务，生成模拟数据"""
    task = DEMO_TASKS.get(task_id)
    if not task:
        logger.warning(f"任务 {task_id} 不存在，无法完成")
        return
    
    # 生成两轮拓展，每轮2-3个视频
    rounds = []
    for round_num in range(1, 3):
        videos = []
        for i in range(random.randint(2, 3)):
            vid = f"vid{round_num}{i+1:03d}"
            videos.append({
                "vd_id": vid,
                "vd_title": f"测试视频标题{vid}",
                "create_time": (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 100))).strftime("%Y-%m-%d %H:%M:%S"),
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
    task["completed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task["rounds"] = rounds
    
    # 确保更新后的任务被保存回字典
    DEMO_TASKS[task_id] = task
    logger.info(f"任务 {task_id} 已完成处理，状态更新为 completed")

def async_complete_task(task_id):
    """异步完成任务的线程函数"""
    logger.info(f"开始处理任务 {task_id}，将在5秒后完成")
    time.sleep(5)  # 模拟5秒的处理时间
    complete_demo_task(task_id)
    logger.info(f"任务 {task_id} 处理完成")

# 初始化示例任务
init_demo_tasks()

@detect_bp.route("/create_detect_task", methods=["POST"])
def create_detect_task():
    """创建检测任务API"""
    logger.info(f"收到创建任务请求: {request.data}")
    try:
        data = request.get_json()
        if not data or "video_url" not in data:
            return jsonify({"code": 400, "message": "缺少必要参数"}), 400
            
        video_url = data.get("video_url", "")
        logger.info(f"收到视频URL: {video_url}")
        
        # 提取视频ID
        video_ids = []
        import re
        matches = re.findall(r'douyin\.com/video/(\d+)', video_url)
        if matches:
            video_ids = matches
        
        # 如果没有匹配到视频ID，返回错误
        if not video_ids:
            logger.warning(f"不支持的链接: {video_url}")
            return jsonify({"code": 400, "message": "无效的视频链接"}), 400
        
        # 创建任务
        task = generate_demo_task(video_ids)
        DEMO_TASKS[task["task_id"]] = task
        logger.info(f"创建任务成功: {task['task_id']}")
        
        # 启动异步线程模拟检测
        threading.Thread(target=async_complete_task, args=(task["task_id"],), daemon=True).start()
        
        return jsonify({
            "code": 20000,
            "message": "任务创建成功",
            "data": {"task_id": task["task_id"]}
        })
    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

@detect_bp.route("/task_list", methods=["GET"])
def get_task_list():
    """获取任务列表API"""
    logger.info("获取任务列表")
    try:
        tasks = []
        for t in DEMO_TASKS.values():
            tasks.append({
                "task_id": t["task_id"],
                "status": t["status"],
                "created_at": t["created_at"],
                "completed_at": t["completed_at"],
                "evil_video_count": t["evil_video_count"],
                "all_video_count": t["all_video_count"],
            })
        
        # 按创建时间降序排序
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        logger.info(f"返回任务列表: {len(tasks)} 个任务")
        return jsonify({"code": 20000, "data": {"tasks": tasks}})
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

@detect_bp.route("/get_task/<task_id>", methods=["GET"])
def get_task(task_id):
    """获取任务详情API"""
    logger.info(f"获取任务详情: {task_id}")
    try:
        task = DEMO_TASKS.get(task_id)
        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404
            
        return jsonify({
            "code": 20000,
            "data": {
                "task_id": task["task_id"],
                "vd_id": task["video_ids"][0] if task["video_ids"] else "",
                "status": task["status"],
                "created_at": task["created_at"],
                "updated_at": task["completed_at"] or task["created_at"],
                "evil_video_ids": task["evil_video_ids"]
            }
        })
    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

@detect_bp.route("/get_task_report/<task_id>", methods=["GET"])
def get_task_report(task_id):
    """获取任务报告API"""
    logger.info(f"获取任务报告: {task_id}")
    try:
        task = DEMO_TASKS.get(task_id)
        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404
            
        return jsonify({
            "code": 20000,
            "data": {
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
        })
    except Exception as e:
        logger.error(f"获取任务报告失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

@detect_bp.route("/get_round_videos/<task_id>/<int:round_num>", methods=["GET"])
def get_round_videos(task_id, round_num):
    """获取指定轮次的视频详情API"""
    logger.info(f"获取任务 {task_id} 第 {round_num} 轮视频")
    try:
        task = DEMO_TASKS.get(task_id)
        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404
            
        # 查找指定轮次
        round_data = None
        for r in task.get("rounds", []):
            if r["round"] == round_num:
                round_data = r
                break
                
        if not round_data:
            return jsonify({"code": 404, "message": f"轮次 {round_num} 不存在"}), 404
            
        return jsonify({
            "code": 20000,
            "data": {
                "task_id": task["task_id"],
                "round": round_data["round"],
                "video_count": round_data["video_count"],
                "videos": round_data["videos"]
            }
        })
    except Exception as e:
        logger.error(f"获取轮次视频失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

@detect_bp.route("/get_all_round_videos/<task_id>", methods=["GET"])
def get_all_round_videos(task_id):
    """获取所有轮次的视频详情API"""
    logger.info(f"获取任务 {task_id} 所有轮次视频")
    try:
        task = DEMO_TASKS.get(task_id)
        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404
            
        return jsonify({
            "code": 20000,
            "data": {
                "task_id": task["task_id"],
                "total_rounds": len(task.get("rounds", [])),
                "rounds": task.get("rounds", [])
            }
        })
    except Exception as e:
        logger.error(f"获取所有轮次视频失败: {str(e)}", exc_info=True)
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

# 添加清空任务的API（仅用于测试）
@detect_bp.route("/clear_tasks", methods=["POST"])
def clear_tasks():
    """清空所有任务（仅用于测试）"""
    global DEMO_TASKS
    DEMO_TASKS = {}
    init_demo_tasks()  # 重新初始化示例任务
    logger.info("已清空所有任务并重新初始化示例任务")
    return jsonify({"code": 20000, "message": "已清空所有任务"})
