# services/analysis_service.py
import json
import logging
from datetime import datetime
from models.db_models import db, Video, AnalysisResult

logger = logging.getLogger(__name__)


class AnalysisService:
    """视频分析服务类"""

    def get_analysis_by_video_id(self, video_id):
        """获取视频分析结果"""
        analysis = AnalysisResult.query.filter_by(video_id=video_id).first()
        if not analysis:
            return None
        return analysis.to_dict()

    def request_video_detection(self, video_id):
        """
        请求视频检测

        Args:
            video_id: 视频ID
        """
        # 检查视频是否存在
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"Video not found with ID: {video_id}")

        # 创建或更新分析记录
        analysis = AnalysisResult.query.filter_by(video_id=video_id).first()
        if not analysis:
            analysis = AnalysisResult(video_id=video_id)
            db.session.add(analysis)

        db.session.commit()

        # 这里应该调用您已有的检测模型
        # detector.detect_video.delay(video_id)  # 假设您使用Celery等任务队列

        # 模拟调用检测模型的代码
        logger.info(f"Requested video detection for ID: {video_id}")

    def update_detection_results(self, video_id, is_dangerous, detection_results):
        """
        更新检测结果

        Args:
            video_id: 视频ID
            is_dangerous: 是否为危险视频
            detection_results: 检测结果详情
        """
        # 更新视频危险标志
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"Video not found with ID: {video_id}")

        video.is_dangerous = is_dangerous

        # 更新分析结果
        analysis = AnalysisResult.query.filter_by(video_id=video_id).first()
        if not analysis:
            analysis = AnalysisResult(video_id=video_id)
            db.session.add(analysis)

        analysis.detection_date = datetime.utcnow()
        analysis.detection_score = detection_results.get("score", 0.0)
        analysis.detection_features = json.dumps(detection_results)

        db.session.commit()
        logger.info(
            f"Updated detection results for video ID: {video_id}, is_dangerous: {is_dangerous}"
        )

    def request_trace_analysis(self, video_id):
        """
        请求溯源分析

        Args:
            video_id: 视频ID
        """
        # 检查视频是否存在
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"Video not found with ID: {video_id}")

        # 这里应该调用您已有的溯源分析模块
        # analyzer.trace_video.delay(video_id)  # 假设您使用Celery等任务队列

        # 模拟调用溯源分析模块的代码
        logger.info(f"Requested trace analysis for video ID: {video_id}")

    def update_analysis_results(self, video_id, analysis_results):
        """
        更新溯源分析结果

        Args:
            video_id: 视频ID
            analysis_results: 分析结果详情
        """
        analysis = AnalysisResult.query.filter_by(video_id=video_id).first()
        if not analysis:
            analysis = AnalysisResult(video_id=video_id)
            db.session.add(analysis)

        analysis.analysis_date = datetime.utcnow()
        analysis.trace_results = json.dumps(analysis_results)

        db.session.commit()
        logger.info(f"Updated trace analysis results for video ID: {video_id}")

    def get_trace_analysis(self, video_id):
        """获取溯源分析结果"""
        analysis = AnalysisResult.query.filter_by(video_id=video_id).first()
        if not analysis or not analysis.trace_results:
            return None

        return json.loads(analysis.trace_results)

    def get_analysis_statistics(self):
        """获取分析统计数据"""
        total_analyzed = AnalysisResult.query.filter(
            AnalysisResult.detection_date.isnot(None)
        ).count()
        total_traced = AnalysisResult.query.filter(
            AnalysisResult.analysis_date.isnot(None)
        ).count()

        # 检测评分分布统计
        score_ranges = {
            "0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0,
        }

        for result in AnalysisResult.query.filter(
            AnalysisResult.detection_score.isnot(None)
        ).all():
            score = result.detection_score
            if score < 0.2:
                score_ranges["0-0.2"] += 1
            elif score < 0.4:
                score_ranges["0.2-0.4"] += 1
            elif score < 0.6:
                score_ranges["0.4-0.6"] += 1
            elif score < 0.8:
                score_ranges["0.6-0.8"] += 1
            else:
                score_ranges["0.8-1.0"] += 1

        return {
            "total_analyzed": total_analyzed,
            "total_traced": total_traced,
            "score_distribution": score_ranges,
        }
