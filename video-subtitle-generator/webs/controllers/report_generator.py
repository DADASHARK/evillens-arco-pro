from models.database import TopVideo as Video, session  # 导入模型和数据库会话
import pandas as pd
import os
from config import OUTPUT_DIR, IMAGE_DIR  # 新增导入图片存储目录配置（需在config.py中定义IMAGE_DIR，如"static/images"）

def generate_report():
    """内部处理数据库查询并生成报告（含图片和CSV）"""
    # 1. 查询未标记的视频数据
    videos = session.query(Video).filter_by(reported=False).all()
    if not videos:
        raise ValueError("无未标记视频，无需生成报告")  # 抛异常触发控制器的错误处理
    
    # 2. 转换数据为DataFrame
    data = pd.DataFrame([{
        "vd_id": video.vd_id,
        "vd_title": video.vd_title,
        "author": video.author,
        "create_time": video.create_time,
        "likes": video.likes,
        "shares": video.shares,
        "collects": video.collects,
        "reported": video.reported
    } for video in videos])
    
    # 3. 生成Markdown报告（含图片）
    report_path = os.path.join(OUTPUT_DIR, "evidence_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 邪典视频检测报告\n\n")
        f.write("## 未标记视频列表\n\n")
        for idx, row in data.iterrows():  # idx为当前行的索引（与videos列表顺序一致）
            # 拼接图片路径（假设图片存储在IMAGE_DIR目录下，文件名格式为{vd_id}.jpg）
            image_path = os.path.join(IMAGE_DIR, f"{row['vd_id']}.jpg")
            # 检查图片是否存在
            if os.path.exists(image_path):
                f.write(f"![{row['vd_id']}](/{image_path})\n")  # 前端访问路径需根据实际静态资源配置调整
            else:
                f.write(f"*视频ID {row['vd_id']} 视频已下架*\n")
                # 关键修改：标记视频为已下架（removed=True）
                video = videos[idx]  # 通过索引获取对应的Video对象（与data顺序一致）
                video.removed = True  # 设置removed字段为True（数据库中为1）
            
            f.write(f"- **视频ID**: {row['vd_id']}\n")
            f.write(f"  - 标题: {row['vd_title']}\n")
            f.write(f"  - 作者: {row['author']}\n")
            f.write(f"  - 点赞数: {row['likes']}\n")
            f.write(f"  - 分享数: {row['shares']}\n\n")
    
    # 4. 生成CSV文件
    csv_path = os.path.join(OUTPUT_DIR, "evidence_report.csv")
    data.to_csv(csv_path, index=False, encoding="utf-8")  # 导出为无索引的CSV文件
    
    # 5. 标记视频为已报告（可选，根据业务需求）
    for video in videos:
        video.reported = True
    session.commit()  # 提交数据库修改

    # 6. 删除已报告视频的图片（新增逻辑）
    for video in videos:
        image_path = os.path.join(IMAGE_DIR, f"{video.vd_id}.jpg")
        if os.path.exists(image_path):
            os.remove(image_path)  # 删除图片文件