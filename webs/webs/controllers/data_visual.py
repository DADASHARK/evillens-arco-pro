# 可视化模块
import matplotlib.pyplot as plt
import seaborn as sns
import os
from config import OUTPUT_DIR


def generate_interaction_plot(data):
    """生成互动数据分布图"""
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(10, 6))
    data[['likes', 'shares', 'collects']].plot.box(
        showfliers=False,
        grid=True,
        logy=True,
        color=dict(boxes='skyblue', whiskers='gray')
    )
    plt.title('互动数据分布（对数坐标）', fontsize=14)
    plt.ylabel('数值（对数刻度）')
    plt.xlabel('互动类型')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'interaction_plot.png'), dpi=300)
    plt.close()


def generate_trend_plot(data):
    """生成发布时间趋势图"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'FangSong', 'KaiTi']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(12, 7))
    time_series = data.set_index('create_time').resample('D')['vd_id'].count()
    time_series.plot(kind='line', marker='o', linestyle='--',
                     color='#2E86AB', markersize=6, linewidth=2)
    plt.title('视频发布时间趋势（按天）', fontsize=16)
    plt.xlabel('日期')
    plt.ylabel('视频数量')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'trend_plot.png'), dpi=300)
    plt.close()


# 在文件开头添加字体配置（建议在import之后）
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def generate_hourly_distribution_plot(data):
    plt.rc('font', family='SimHei', size=12)  # 确保中文显示
    sns.set(style="whitegrid", palette="Blues")
    hourly_counts = data['hour_of_day'].value_counts().sort_index()

    plt.figure(figsize=(12, 6))
    sns.barplot(x=hourly_counts.index, y=hourly_counts.values, errorbar=None)  # 替换ci=None为errorbar=None
    plt.title('24小时视频发布分布', fontsize=16)
    plt.xlabel('小时 (0-23)', fontsize=12)
    plt.ylabel('视频数量', fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'hourly_distribution_plot.png'), dpi=300)
    plt.close()