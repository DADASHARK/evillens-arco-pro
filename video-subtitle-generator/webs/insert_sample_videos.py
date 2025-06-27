import random
from datetime import datetime, timedelta
from app import create_app
from models.db import db
from models.video import Video

app = create_app()

def random_string(length=8):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choices(chars, k=length))

def random_province():
    provinces = [
        "北京市", "上海市", "广东省", "浙江省", "江苏省", "四川省", "山东省", "湖北省", "福建省", "湖南省"
    ]
    return random.choice(provinces)

def insert_sample_videos():
    with app.app_context():
        for i in range(10):
            vd_id = f"vd_{random_string(10)}"
            name = f"视频_{random_string(5)}"
            cover_url = f"https://example.com/cover_{random_string(6)}.jpg"
            province = random_province()
            publish_time = datetime.utcnow() - timedelta(days=random.randint(0, 365))
            likes = random.randint(0, 10000)
            shares = random.randint(0, 5000)
            comments = random.randint(0, 2000)
            reported = random.choice([True, False])
            removed = random.choice([True, False])

            video = Video(
                vd_id=vd_id,
                name=name,
                cover_url=cover_url,
                province=province,
                publish_time=publish_time,
                likes=likes,
                shares=shares,
                comments=comments,
                reported=reported,
                removed=removed
            )
            db.session.add(video)
        db.session.commit()
        print("已成功插入10条随机视频数据！")

if __name__ == "__main__":
    insert_sample_videos()