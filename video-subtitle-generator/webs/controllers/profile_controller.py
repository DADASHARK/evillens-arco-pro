# profile_controller.py - 用户画像控制器
from flask import Blueprint, jsonify, request

profile_bp = Blueprint('profile', __name__)

# 模拟用户画像数据
mock_user_profiles = {
    "6006": {
        "user_id": "6006",
        "user_name": "小明",
        "age": 25,
        "follow_count": 150,
        "fans_count": 3000,
        "like_count": 5000,
        "ip_location": "北京",
        "self_description": "热爱生活，分享日常",
        "ai_description": "积极向上的年轻人",
        "video_list": [
            {
                "vd_id": "vid001",
                "name": "我的旅行日记",
                "publish_time": "2025-04-04 08:37:00",
                "likes": 1979,
                "shares": 8,
                "collects": 761
            },
            {
                "vd_id": "vid002",
                "name": "美食探店分享",
                "publish_time": "2025-04-03 15:22:10",
                "likes": 1200,
                "shares": 5,
                "collects": 600
            }
        ],
        "total": 2
    },
    "6007": {
        "user_id": "6007",
        "user_name": "小红",
        "age": 22,
        "follow_count": 280,
        "fans_count": 5200,
        "like_count": 8500,
        "ip_location": "上海",
        "self_description": "美食探店博主",
        "ai_description": "热情开朗的美食爱好者，善于发现城市美食",
        "video_list": [
            {
                "vd_id": "vid003",
                "name": "上海必吃小吃",
                "publish_time": "2025-04-05 12:30:00",
                "likes": 3500,
                "shares": 120,
                "collects": 980
            },
            {
                "vd_id": "vid004",
                "name": "隐藏在弄堂里的美食",
                "publish_time": "2025-04-02 18:45:00",
                "likes": 2800,
                "shares": 95,
                "collects": 850
            },
            {
                "vd_id": "vid005",
                "name": "周末早午餐推荐",
                "publish_time": "2025-03-28 09:15:00",
                "likes": 1950,
                "shares": 65,
                "collects": 720
            }
        ],
        "total": 3
    },
    "6008": {
        "user_id": "6008",
        "user_name": "小刚",
        "age": 28,
        "follow_count": 120,
        "fans_count": 1800,
        "like_count": 3200,
        "ip_location": "广州",
        "self_description": "健身达人，分享运动知识",
        "ai_description": "专注健康生活方式的运动博主，内容积极向上",
        "video_list": [
            {
                "vd_id": "vid006",
                "name": "家庭徒手训练指南",
                "publish_time": "2025-04-06 07:20:00",
                "likes": 1650,
                "shares": 78,
                "collects": 520
            },
            {
                "vd_id": "vid007",
                "name": "科学减脂方法",
                "publish_time": "2025-04-01 16:10:00",
                "likes": 2100,
                "shares": 105,
                "collects": 630
            }
        ],
        "total": 2
    }
}

@profile_bp.route('/get_user_profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """
    获取指定用户的画像信息
    
    参数:
        user_id: 用户ID
        
    返回:
        用户画像数据或空对象
    """
    # 检查用户ID是否在模拟数据中
    if user_id in mock_user_profiles:
        return jsonify({
            "code": 20000,
            "message": "获取成功",
            "data": mock_user_profiles[user_id]
        })
    else:
        # 用户不存在，返回空数据
        return jsonify({
            "code": 20000,
            "message": "获取成功",
            "data": {}
        })