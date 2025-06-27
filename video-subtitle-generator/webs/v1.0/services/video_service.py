# services/video_service.py
import json
import logging
from datetime import datetime, timedelta
from models.db_models import db, Video
import uuid

logger = logging.getLogger(__name__)


class VideoService:
    """视频数据服务类"""

    def get_videos(self, page=1, per_page=10, filter_type=None):
        """
        获取视频列表，支持分页和筛选

        Args:
            page: 页码
            per_page: 每页数量
            filter_type: 筛选类型 (all, dangerous, normal)

        Returns:
            tuple: (视频列表, 总数)
        """
        query = Video.query

        # 应用筛选条件
        if filter_type == "dangerous":
            query = query.filter(Video.is_dangerous == True)
        elif filter_type == "normal":
            query = query.filter(Video.is_dangerous == False)

        # 计算总数
        total = query.count()

        # 分页查询
        videos = query.order_by(Video.crawl_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # 转换为字典列表
        result = [video.to_dict() for video in videos.items]

        return result, total

    def get_video_by_id(self, video_id):
        """获取单个视频信息"""
        video = Video.query.get(video_id)
        if not video:
            return None
        return video.to_dict()

    def get_video_by_url(self, url):
        """根据URL获取视频信息"""
        video = Video.query.filter_by(url=url).first()
        if not video:
            return None
        return video.to_dict()

    def request_video_crawl(self, url):
        """
        请求爬取视频

        Args:
            url: 视频URL

        Returns:
            int: 视频ID
        """
        # 创建视频记录
        video = Video(
            url=url,
            status="pending",
            crawl_date=datetime.utcnow(),
            metadata=json.dumps({"request_id": str(uuid.uuid4())}),
        )

        db.session.add(video)
        db.session.commit()

        # 这里应该调用您已有的爬虫模块
        # crawler.crawl_video.delay(video.id, url)  # 假设您使用Celery等任务队列

        # 模拟调用爬虫模块的代码
        logger.info(f"Requested video crawl for URL: {url}, ID: {video.id}")

        return video.id

    def update_video_status(self, video_id, status, metadata=None):
        """更新视频状态"""
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"Video not found with ID: {video_id}")

        video.status = status

        if metadata:
            # 合并新旧元数据
            current_metadata = json.loads(video.metadata) if video.metadata else {}
            current_metadata.update(metadata)
            video.metadata = json.dumps(current_metadata)

            # 更新视频信息
            if "title" in metadata:
                video.title = metadata["title"]
            if "source" in metadata:
                video.source = metadata["source"]
            if "upload_date" in metadata:
                try:
                    video.upload_date = datetime.fromisoformat(metadata["upload_date"])
                except (ValueError, TypeError):
                    pass

        db.session.commit()
        logger.info(f"Updated video status to {status} for ID: {video_id}")

    def get_total_videos(self):
        """获取视频总数"""
        return Video.query.count()

    def get_dangerous_videos_count(self):
        """获取危险视频数量"""
        return Video.query.filter_by(is_dangerous=True).count()

    def get_recent_additions(self, days=7):
        """获取最近添加的视频数量"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return Video.query.filter(Video.crawl_date >= cutoff_date).count()

    def search_videos(self, query, page=1, per_page=10):
        """
        搜索视频

        Args:
            query: 搜索关键词
            page: 页码
            per_page: 每页数量

        Returns:
            tuple: (视频列表, 总数)
        """
        # 简单的模糊匹配
        search = f"%{query}%"

        result = Video.query.filter(
            (Video.title.like(search))
            | (Video.url.like(search))
            | (Video.source.like(search))
        ).order_by(Video.crawl_date.desc())

        total = result.count()

        videos = result.paginate(page=page, per_page=per_page, error_out=False)

        return [video.to_dict() for video in videos.items], total
