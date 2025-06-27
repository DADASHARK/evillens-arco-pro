# controllers/geography_controller.py - 地域分析相关接口
from flask import Blueprint, jsonify, current_app
from sqlalchemy import func
from models.db import db
from models.video import Video
import time
from models.database import (
    session, AccountStat, TopVideo, HourlyDistribution,
    DailyDistribution, InteractionCorrelation, SimilarUser,session, TagVideoMapping
)  # 确保包含AccountStat导入

geography_bp = Blueprint("geography", __name__)

# 缓存数据和时间戳
_cache_data = None
_cache_timestamp = 0
_cache_timeout = 300  # 5分钟缓存

@geography_bp.route("/distribution", methods=["GET"])
def get_geography_distribution():
    """获取地域分布数据"""
    global _cache_data, _cache_timestamp
    
    try:
        # 检查内存缓存是否有效
        current_time = time.time()
        if _cache_data and (current_time - _cache_timestamp < _cache_timeout):
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 返回缓存的地域分布数据")
            return jsonify({"code": 20000, "data": _cache_data})
        
        # 记录请求时间
        request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{request_time}] 请求地域分布数据，缓存未命中或已过期，查询数据库")
        
        # 从account_stats表按location字段统计
        query_result = (
            db.session.query(
                AccountStat.location,
                func.sum(AccountStat.video_count).label("total_videos")
            )
            .group_by(AccountStat.location)
            .all()
        )
        
        # 添加调试输出验证查询结果
        print(f"数据库查询结果: {query_result}")
        
        # 统计各省份视频数量
        province_counter = {}
        total = 0
        for location, count in query_result:
            # 添加空值过滤和调试日志
            if location and location.strip() != '' and location != '无':
                print(f"处理地域数据: {location} => {count}")
                province_counter[location] = province_counter.get(location, 0) + count
                total += count
            else:
                print(f"忽略无效地域数据: {location}")
        
        # 计算百分比
        result = []
        for province, count in province_counter.items():
            percentage = count / total if total > 0 else 0
            result.append({
                "province": province,
                "percentage": round(percentage, 5)
            })

        # 按百分比降序排序
        result = sorted(result, key=lambda x: x['percentage'], reverse=True)
        
        # 更新内存缓存
        _cache_data = result
        _cache_timestamp = current_time
        
        # 调试输出
        print(f"地域分布数据: {result}")
        print(f"[{request_time}] 数据库查询完成，数据已缓存5分钟")
        
        return jsonify({"code": 20000, "data": result})
    except Exception as e:
        print(f"获取地域分布数据错误: {str(e)}")
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
