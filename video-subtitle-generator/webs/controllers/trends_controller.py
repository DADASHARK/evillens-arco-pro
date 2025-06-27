from flask import Blueprint, jsonify
import sys
import os
# Add the parent directory (webs) to Python's module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.daily_distribution import DailyDistribution
from models.hourly_distribution import HourlyDistribution  # Fixed import path
from datetime import datetime, timedelta
from config import Config  # Updated import: use top-level config module

trends_bp = Blueprint('trends', __name__, url_prefix='/api/trends')

@trends_bp.route('/recent', methods=['GET'])
def get_daily_trends():
    try:
        start_date = datetime.now() - timedelta(Config.DEFAULT_STATS_DAYS)  # Use Config class
        daily_data = DailyDistribution.query.filter(DailyDistribution.date >= start_date).all()
        result = [item.to_dict() for item in daily_data]
        
        return jsonify({
            "code": 20000,
            "data": result,
            "message": "success"
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@trends_bp.route('/hourly', methods=['GET'])
def get_hourly_trends():
    """获取每小时分布数据"""
    try:
        hourly_data = HourlyDistribution.query.all()
        result = [item.to_dict() for item in hourly_data]
        
        return jsonify({
            "code": 20000,
            "data": result,
            "message": "success"
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500