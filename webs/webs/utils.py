# 工具函数
from datetime import datetime
import requests
import pandas as pd
import numpy as np
import os

def parse_date(date_str):
    """日期解析器"""
    formats = ['%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y/%m/%d %H:%M', '%Y年%m月%d日']
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    return pd.NaT

def download_image(url, save_path):
    """图片下载器"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"下载失败: {url} - {str(e)}")
    return False