# controllers/tasks_controller.py - 任务相关接口
import os
import csv
import re
import requests
import threading
import datetime
import uuid
import json
import pandas as pd
from flask import Blueprint, jsonify, request, current_app
from urllib.parse import urlparse, parse_qs
from webs.models.db import db
from webs.models.task import Task, DetectionResult
from utils.detect import crawler_and_detect
from crawler.explore.new_pipline1 import (
    main_explore,
    load_selected_video_records,
    write_to_csv,
)
from webs.controllers.analysis import store_file_to_database
from multiprocessing import Process
import traceback
from webs.config import basedir


tasks_bp = Blueprint("detect", __name__)


def run_in_context(app, func, *args, **kwargs):
    with app.app_context():
        func(*args, **kwargs)


# 新的进程调用方式
def start_background_process(app, task_func, task_id, video_ids, active_time):
    # 获取当前 Flask 应用的配置信息
    app_config = app.config.copy()

    # 启动进程，传递配置和任务参数
    process = Process(
        target=process_task,
        args=(app_config, task_func, task_id, video_ids, active_time),
        daemon=True,
    )
    process.start()


def extract_video_id(text):
    """
    从任意文本中提取抖音视频的 video_id。
    支持标准视频链接、含 modal_id 的搜索链接、v.douyin.com 短链接。

    参数:
        text (str): 包含抖音链接的任意文本。

    返回:
        List[str]: 所有成功提取的 video_id 列表。
    """
    # 正则提取所有抖音链接
    urls = re.findall(r'https?://[^\s"]*douyin\.com[^\s"]*', text)
    video_ids = []

    for url in urls:
        # 处理短链接
        if "v.douyin.com" in url:
            try:
                real_url = get_real_url(url)
                if not real_url:
                    continue
                url = real_url
            except Exception:
                continue  # 短链解析失败，跳过

        # 从路径提取 video_id
        video_match = re.search(r"/video/(\d+)", url)
        if video_match:
            video_ids.append(video_match.group(1))
            continue

        # 从查询参数提取 modal_id
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        modal_id = query_params.get("modal_id", [None])[0]
        if modal_id:
            video_ids.append(modal_id)

    return video_ids


def get_real_url(short_url, timeout=10):
    """
    获取短链接跳转后的最终 URL。
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # 尝试 HEAD 请求获取跳转
        response = requests.head(
            short_url, allow_redirects=True, headers=headers, timeout=timeout
        )
        # 如果 HEAD 不支持，尝试 GET
        if response.status_code in [405, 501]:
            response = requests.get(
                short_url, allow_redirects=True, headers=headers, timeout=timeout
            )
        return response.url
    except requests.exceptions.RequestException:
        # 如果 HEAD 或 GET 出错，尝试无重定向获取
        try:
            response = requests.get(
                short_url, allow_redirects=True, headers=headers, timeout=timeout
            )
            return response.url
        except requests.exceptions.RequestException:
            return None


def generate_task_id():
    """生成唯一任务ID"""
    return str(uuid.uuid4())


def prepare_csv_file(task_id, video_ids):
    """准备CSV文件"""
    # csv_dir = os.path.join(basedir, "static", "tasks", task_id)
    test_path = r"D:\Documents\VSCode\minor_protection\to_use\test"
    csv_dir = os.path.join(test_path, task_id)
    os.makedirs(csv_dir, exist_ok=True)

    csv_file_path = os.path.join(csv_dir, "input.csv")

    with open(csv_file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vd_id", "label"])
        for video_id in video_ids:
            writer.writerow([video_id, ""])

    return csv_file_path


# 测试中函数，还要bug，如要测试直接返回自定义的json
def process_task(task_id, video_ids, active_time):
    # def process_task(app_config, task_func, task_id, video_ids, active_time):
    """处理检测任务的后台线程"""
    # 重新创建 Flask 应用实例
    # app = create_app(app_config)
    try:
        # 更新任务状态为处理中
        task = Task.query.filter_by(task_id=task_id).first()
        task.status = "processing"
        db.session.commit()

        # 准备CSV文件
        csv_file_path = prepare_csv_file(task_id, video_ids)

        # 调用检测函数
        # evil_video_ids = crawler_and_detect(csv_file_path, active_time)
        # evil_video_ids = crawler_and_detect(csv_file_path, task_id)
        evil_video_ids = ["7460657806849445120"]

        # 保存检测结果
        print("检测结果：", evil_video_ids)
        all_csv = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\all.csv"
        new_csv_folder = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\results"
        new_csv_path = os.path.join(new_csv_folder, f"evil_{task_id}.csv")
        new_evil = load_selected_video_records(evil_video_ids, all_csv)
        print(new_evil)
        write_to_csv(new_csv_path, new_evil, all_csv)
        store_file_to_database(new_csv_path, task_id=task_id)  # 保存后csv文件位置有变动
        # new_csv_path = os.path.join(new_csv_folder, f"evil_{task_id}.csv")
        # csv_content = load_selected_video_records(evil_video_ids, all_csv)
        # write_to_csv(new_csv_path, csv_content, all_csv)
        # store_file_to_database(new_csv_path, task_id=task_id)
        # not_evil_video_ids = list(set(video_ids) - set(evil_video_ids))

        # 调用视频拓展函数
        main_explore(task_id)

        # 保存拓展视频信息
        json_folder = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\round_results"
        json_paths = [
            os.path.join(json_folder, f)
            for f in os.listdir(json_folder)
            if f.endswith(".json") and f.startswith(task_id)
        ]
        for json_path in json_paths:
            store_file_to_database(json_path)

        # 更新任务状态
        task.status = "completed"
        task.completed_at = datetime.datetime.now()
        db.session.commit()

        # 保存检测结果
        for vd_id in video_ids:
            result = DetectionResult(
                task_id=task_id,
                vd_id=vd_id,
                is_evil=(vd_id in evil_video_ids),
                # confidence=confidence,
            )
            db.session.add(result)
        db.session.commit()

    except Exception as e:
        # current_app.logger.error(f"Task processing error: {str(e)}")
        print(f"Task processing error: {str(e)}")
        traceback.print_exc()
        task = Task.query.filter_by(task_id=task_id).first()
        if task:
            task.status = "failed"
            task.completed_at = datetime.datetime.now()
            db.session.commit()


@tasks_bp.route("/create_detect_task", methods=["POST"])
def create_task():
    """创建检测任务"""
    try:
        data = request.get_json()

        if not data or "video_url" not in data:
            return jsonify({"code": 400, "message": "缺少必要参数"}), 400

        video_url = data["video_url"]

        # 提取视频ID
        video_ids = extract_video_id(video_url)

        task_id = generate_task_id()
        task = Task(task_id=task_id, status="pending")
        db.session.add(task)
        db.session.commit()

        if not video_ids:
            task.status = "failed"
            task.completed_at = datetime.datetime.now()
            db.session.commit()
            return jsonify({"code": 400, "message": "无效的视频ID"})

        active_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # 启动后台线程处理任务
        # threading.Thread(
        #     target=process_task, args=(task_id, video_ids, active_time), daemon=True
        # ).start()
        threading.Thread(
            target=run_in_context,
            args=(
                current_app._get_current_object(),
                process_task,
                task_id,
                video_ids,
                active_time,
            ),
            daemon=True,
        ).start()
        # start_background_process(
        #     current_app._get_current_object(),
        #     process_task,
        #     task_id,
        #     video_ids,
        #     active_time,
        # )

        return jsonify(
            {"code": 20000, "message": "任务创建成功", "data": {"task_id": task_id}}
        )

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@tasks_bp.route("/task_list", methods=["GET"])
def get_tasks():
    """获取任务列表"""
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()

        result = []
        for task in tasks:
            task_dict = task.to_dict()
            # 添加此任务中检测到的邪典视频数量
            evil_videos = task.get_evil_video_ids()
            task_dict["evil_video_count"] = len(evil_videos)
            all_videos = task.get_all_video_ids()
            task_dict["all_video_count"] = len(all_videos)
            result.append(task_dict)

        return jsonify({"code": 20000, "data": {"tasks": result}})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@tasks_bp.route("/get_task/<string:task_id>", methods=["GET"])
def get_task_detail(task_id):
    """获取任务详情"""
    try:
        task = Task.query.filter_by(task_id=task_id).first()

        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404

        task_dict = task.to_dict()
        # 添加此任务中检测到的邪典视频ID列表
        task_dict["evil_video_ids"] = task.get_evil_video_ids()

        return jsonify({"code": 20000, "data": task_dict})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@tasks_bp.route("/task_result/<string:task_id>", methods=["GET"])
def get_task_report(task_id):
    """获取任务检测报告"""
    try:
        task = Task.query.filter_by(task_id=task_id).first()

        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404

        if task.status != "completed":
            return (
                jsonify(
                    {"code": 400, "message": f"任务尚未完成，当前状态: {task.status}"}
                ),
                400,
            )

        # 获取检测结果
        # results = DetectionResult.query.filter_by(task_id=task_id).all()
        results = (
            DetectionResult.query.with_entities(DetectionResult.vd_id)
            .filter_by(task_id=task_id)
            .distinct(DetectionResult.vd_id)
            .all()
        )
        results = [r.vd_id for r in results]
        evil_video_ids = task.get_evil_video_ids()

        # 组装报告数据
        report_data = {
            "task_info": task.to_dict(),
            "detection_results": [result for result in results],
            "evil_video_ids": evil_video_ids,
            "summary": {
                "total_videos": len(results),
                "evil_videos": len(evil_video_ids),
                "normal_videos": len(results) - len(evil_video_ids),
            },
        }

        return jsonify({"code": 20000, "data": report_data})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@tasks_bp.route("/get_round_videos/<string:task_id>/<int:round_num>", methods=["GET"])
def get_round_videos(task_id, round_num):
    """获取指定任务和轮次的视频拓展信息"""
    try:
        # 检查任务是否存在
        task = Task.query.filter_by(task_id=task_id).first()
        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404

        # 构建JSON文件路径
        json_folder = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\round_results"
        json_filename = f"{task_id}_round_{round_num}.json"
        json_path = os.path.join(json_folder, json_filename)

        # 检查文件是否存在
        if not os.path.exists(json_path):
            return (
                jsonify(
                    {
                        "code": 404,
                        "message": f"未找到任务 {task_id} 第 {round_num} 轮的视频拓展数据",
                    }
                ),
                404,
            )

        # 读取JSON文件
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                video_data = json.load(f)
        except json.JSONDecodeError:
            return jsonify({"code": 500, "message": "视频数据文件格式错误"}), 500
        except Exception as e:
            return (
                jsonify({"code": 500, "message": f"读取视频数据文件失败: {str(e)}"}),
                500,
            )

        # 返回视频数据
        response_data = {
            "task_id": task_id,
            "round": round_num,
            "video_count": len(video_data.get("videos", [])),
            "videos": video_data.get("videos", []),
        }

        return jsonify({"code": 20000, "message": "获取成功", "data": response_data})

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@tasks_bp.route("/get_all_round_videos/<string:task_id>", methods=["GET"])
def get_all_round_videos(task_id):
    """获取指定任务所有轮次的视频拓展信息"""
    try:
        # 检查任务是否存在
        task = Task.query.filter_by(task_id=task_id).first()
        if not task:
            return jsonify({"code": 404, "message": "任务不存在"}), 404

        json_folder = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\round_results"

        # 查找所有相关的JSON文件
        all_rounds_data = []

        if not os.path.exists(json_folder):
            return jsonify({"code": 404, "message": "视频拓展数据目录不存在"}), 404

        # 遍历目录查找匹配的文件
        for filename in os.listdir(json_folder):
            if filename.startswith(f"{task_id}_round_") and filename.endswith(".json"):
                # 提取轮次号
                try:
                    round_part = filename.replace(f"{task_id}_round_", "").replace(
                        ".json", ""
                    )
                    round_num = int(round_part)

                    json_path = os.path.join(json_folder, filename)
                    with open(json_path, "r", encoding="utf-8") as f:
                        video_data = json.load(f)

                    round_info = {
                        "round": round_num,
                        "video_count": len(video_data.get("videos", [])),
                        "videos": video_data.get("videos", []),
                    }
                    all_rounds_data.append(round_info)

                except (ValueError, json.JSONDecodeError) as e:
                    # 跳过无效文件
                    continue

        # 按轮次排序
        all_rounds_data.sort(key=lambda x: x["round"])

        response_data = {
            "task_id": task_id,
            "total_rounds": len(all_rounds_data),
            "rounds": all_rounds_data,
        }

        return jsonify({"code": 20000, "message": "获取成功", "data": response_data})

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
