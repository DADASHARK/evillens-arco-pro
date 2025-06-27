# controllers/__init__.py
from .video_controller import video_bp
from .geography_controller import geography_bp
from .trends_controller import trends_bp
from .keywords_controller import keywords_bp
from .gangs_controller import gangs_bp
from .report_controller import report_bp
from .simple_api_controller import simple_api_bp
# 导出所有蓝图，方便在主应用中注册
__all__ = [
    "video_bp",
    "geography_bp",
    "trends_bp",
    "keywords_bp",
    "gangs_bp",
    "report_bp",
    "simple_api_bp",
]
