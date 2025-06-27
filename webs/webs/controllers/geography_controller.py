# controllers/geography_controller.py - 地域分析相关接口
from flask import Blueprint, jsonify, current_app
from sqlalchemy import func
from webs.models.db import db
from webs.models.video import Video
import time
from webs.models.database import (
    session,
    AccountStat,
    TopVideo,
    HourlyDistribution,
    DailyDistribution,
    InteractionCorrelation,
    SimilarUser,
    session,
    TagVideoMapping,
    MaliciousUser,
)  # 确保包含AccountStat导入
import traceback

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

        # 查询并统计各 IP 所在地的恶意用户数量
        query_result = (
            db.session.query(
                MaliciousUser.ip_location,
                func.count(MaliciousUser.id).label("user_count"),  # 添加 COUNT 聚合函数
            )
            .filter(MaliciousUser.ip_location.isnot(None))  # 可选：提前过滤掉空值
            .group_by(MaliciousUser.ip_location)
            .all()
        )

        # 添加调试输出验证查询结果
        # print(f"数据库查询结果: {query_result}")

        # 统计各省份视频数量
        province_counter = {}
        total = 0
        for location, count in query_result:
            # 添加空值过滤和调试日志
            if location and location.strip() != "" and location != "无":
                stripped_loc = location.strip()
                standardized = province_mapping.get(stripped_loc, None)
                # print(f"处理地域数据: {location} => {count}")
                province_counter[standardized] = (
                    province_counter.get(location, 0) + count
                )
                total += count
            # else:
            #     print(f"忽略无效地域数据: {location}")

        # 计算百分比
        result = []
        for province, count in province_counter.items():
            percentage = count / total if total > 0 else 0
            result.append({"province": province, "percentage": round(percentage, 5)})

        # 按百分比降序排序
        result = sorted(result, key=lambda x: x["percentage"], reverse=True)

        # 更新内存缓存
        _cache_data = result
        _cache_timestamp = current_time

        # 调试输出
        print(f"地域分布数据: {result}")
        print(f"[{request_time}] 数据库查询完成，数据已缓存5分钟")

        return jsonify({"code": 20000, "data": result})
    except Exception as e:
        print(f"获取地域分布数据错误: {str(e)}")
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


province_mapping = {
    # 直辖市
    "北京市": "北京市",
    "北京": "北京市",
    "上海市": "上海市",
    "上海": "上海市",
    "天津市": "天津市",
    "天津": "天津市",
    "重庆市": "重庆市",
    "重庆": "重庆市",
    # 省份
    "河北省": "河北省",
    "河北": "河北省",
    "山西省": "山西省",
    "山西": "山西省",
    "辽宁省": "辽宁省",
    "辽宁": "辽宁省",
    "吉林省": "吉林省",
    "吉林": "吉林省",
    "黑龙江省": "黑龙江省",
    "黑龙江": "黑龙江省",
    "江苏省": "江苏省",
    "江苏": "江苏省",
    "浙江省": "浙江省",
    "浙江": "浙江省",
    "安徽省": "安徽省",
    "安徽": "安徽省",
    "福建省": "福建省",
    "福建": "福建省",
    "江西省": "江西省",
    "江西": "江西省",
    "山东省": "山东省",
    "山东": "山东省",
    "河南省": "河南省",
    "河南": "河南省",
    "湖北省": "湖北省",
    "湖北": "湖北省",
    "湖南省": "湖南省",
    "湖南": "湖南省",
    "广东省": "广东省",
    "广东": "广东省",
    "海南省": "海南省",
    "海南": "海南省",
    "四川省": "四川省",
    "四川": "四川省",
    "贵州省": "贵州省",
    "贵州": "贵州省",
    "云南省": "云南省",
    "云南": "云南省",
    "陕西省": "陕西省",
    "陕西": "陕西省",
    "甘肃省": "甘肃省",
    "甘肃": "甘肃省",
    "青海省": "青海省",
    "青海": "青海省",
    "台湾省": "台湾省",
    "台湾": "台湾省",
    # 自治区
    "内蒙古自治区": "内蒙古自治区",
    "内蒙古": "内蒙古自治区",
    "广西壮族自治区": "广西壮族自治区",
    "广西": "广西壮族自治区",
    "西藏自治区": "西藏自治区",
    "西藏": "西藏自治区",
    "宁夏回族自治区": "宁夏回族自治区",
    "宁夏": "宁夏回族自治区",
    "新疆维吾尔自治区": "新疆维吾尔自治区",
    "新疆": "新疆维吾尔自治区",
    # 特别行政区
    "香港特别行政区": "香港特别行政区",
    "香港": "香港特别行政区",
    "澳门特别行政区": "澳门特别行政区",
    "澳门": "澳门特别行政区",
}
