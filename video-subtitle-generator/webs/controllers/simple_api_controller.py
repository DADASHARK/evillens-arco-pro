from flask import Blueprint, jsonify

simple_api_bp = Blueprint('simple_api', __name__)

@simple_api_bp.route('/risk-value')
def risk_value():
    risk = 83
    return jsonify({"code": 20000, "data": risk})

# @simple_api_bp.route('/evil-videos')
# def evil_videos():
#     videos = [
#         {
#             "video_id": 7478899729624010041,
#             "title": "变异南瓜人#动画 #搞笑 #儿童动画 #即梦ai",
#             "coverimg_url":"https://p3-pc-sign.douyinpic.com/image-cut-tos-priv/77b02b2462194eb0ced07b4cd9a546cd~tplv-dy-resize-origshort-autoq-75:330.jpeg?biz_tag=pcweb_cover&from=327834062&lk3s=138a59ce&s=PackSourceEnum_AWEME_DETAIL&sc=cover&se=false&x-expires=2061201600&x-signature=fpaa4NTuGh6C6%2BU3W3Js%2Bu6hU50%3D"
#         },
#         {
#             "video_id": 7466382479549582619,
#             "title": "史莱姆把少女吞噬了#二次元少女 #二次元动漫 #动漫解说 #游戏解说 #动漫",
#             "coverimg_url": "https://p3-pc-sign.douyinpic.com/image-cut-tos-priv/5d7b7974fd547383fc66cbc67b314c48~tplv-dy-resize-origshort-autoq-75:330.jpeg?biz_tag=pcweb_cover&from=327834062&lk3s=138a59ce&s=PackSourceEnum_AWEME_DETAIL&sc=cover&se=false&x-expires=2061201600&x-signature=6RzzRTVEwTYGkzppSZqz%2FZYrVtM%3D"
#         },
#         {
#             "video_id": 7466382479549582619,
#             "title": "史莱姆把少女吞噬了#二次元少女 #二次元动漫 #动漫解说 #游戏解说 #动漫",
#             "coverimg_url": "https://p3-pc-sign.douyinpic.com/image-cut-tos-priv/5d7b7974fd547383fc66cbc67b314c48~tplv-dy-resize-origshort-autoq-75:330.jpeg?biz_tag=pcweb_cover&from=327834062&lk3s=138a59ce&s=PackSourceEnum_AWEME_DETAIL&sc=cover&se=false&x-expires=2061201600&x-signature=6RzzRTVEwTYGkzppSZqz%2FZYrVtM%3D"
#         },
#     ]
#     return jsonify({"code": 20000, "data": videos})