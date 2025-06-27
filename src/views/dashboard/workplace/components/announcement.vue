<template>
  <a-card class="innovation-card" :class="{ 'dark-mode': isDark }">
    <div class="header">
      <div class="title">🚀 创新点展示</div>
      <div class="subtitle">本项目的创新性主要体现在以下几个方面：</div>
    </div>

    <div class="timeline">
      <div v-for="point in points" :key="point.id" class="item">
        <div class="icon">{{ point.icon }}</div>
        <div class="content">
          <div class="item-title">{{ point.title }}</div>
          <div class="item-desc">{{ point.content }}</div>
        </div>
      </div>
    </div>

    <div class="footer-warning">
      ⚠️ 本项目所有创新点均已在实际系统中落地应用，持续提升检测与防护能力！
    </div>
  </a-card>
</template>

<script setup lang="ts">
  import useThemes from '@/hooks/themes';

  const { isDark } = useThemes();

  const points = [
    {
      id: 1,
      title: '首个面向儿童邪典视频的挖掘治理平台',
      icon: '🛡️',
      content:
        '面向"网络空间未成年人保护"的国家重大战略需求，构建首个儿童邪典视频挖掘治理平台，实现主动挖掘、快速检测与治理分析，弥补现有内容审核机制在儿童专属有害内容识别上的空白。',
    },
    {
      id: 2,
      title: '基于二分图网络与推荐算法的视频拓展策略',
      icon: '🔍',
      content:
        '创新性地提出二分图网络+推荐算法的视频扩展策略，构建关键词-视频二分图，结合BiRank排序与Jaccard相似度进行评分，引入用户行为信号，显著提升挖掘覆盖率与准确率。',
    },
    {
      id: 3,
      title: '多模态融合的视频内容快速检测',
      icon: '🎛️',
      content:
        '集成视频画面与音频文本结合的多模态检测框架，采用领域成熟预训练模型提取特征，结合注意力机制进行特征融合，实现跨模态的语义关联与综合判定，快速准确检测邪典视频。',
    },
    {
      id: 4,
      title: '基于多维特征的邪典视频治理分析',
      icon: '📊',
      content:
        '迭代汇总邪典视频特征，实现整体时空趋势分析与风险评估，定位高风险发布者并生成精准用户画像，通过系统性分析与详细报告生成，为监管者和平台运营方提供邪典视频治理依据。',
    },
  ];
</script>

<style scoped lang="less">
  .innovation-card {
    padding: 24px;
    background: linear-gradient(135deg, #f6f9ff, #eaf2ff);
    border-radius: 16px;
    box-shadow: 0 4px 16px rgb(22 119 255 / 10%);

    .header {
      .title {
        margin-bottom: 8px;
        color: #1677ff;
        font-weight: 700;
        font-size: 24px;
      }

      .subtitle {
        margin-bottom: 24px;
        color: #555;
        font-size: 14px;
      }
    }

    .timeline {
      display: flex;
      flex-direction: column;
      gap: 20px;

      .item {
        display: flex;
        align-items: flex-start;
        padding: 16px 20px;
        background: #fff;
        border-left: 4px solid #1677ff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgb(0 0 0 / 4%);

        .icon {
          margin-right: 16px;
          color: #1677ff;
          font-size: 24px;
        }

        .content {
          .item-title {
            margin-bottom: 6px;
            color: #333;
            font-weight: 600;
            font-size: 16px;
          }

          .item-desc {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
          }
        }
      }
    }

    .footer-warning {
      margin-top: 32px;
      padding: 12px 16px;
      color: #0a66c2;
      font-weight: 500;
      font-size: 14px;
      background: #e8f3ff;
      border-left: 4px solid #0a66c2;
      border-radius: 6px;
    }
  }

  // 暗夜模式
  .dark-mode.innovation-card {
    background: linear-gradient(135deg, #16213a, #22304a);
    box-shadow: 0 4px 16px rgb(73 177 245 / 12%);

    .header {
      .title {
        color: #49b1f5;
      }

      .subtitle {
        color: #b3c6e0;
      }
    }

    .timeline {
      .item {
        background: #22304a;
        border-left: 4px solid #49b1f5;
        box-shadow: 0 2px 8px rgb(73 177 245 / 8%);

        .icon {
          color: #49b1f5;
        }

        .content {
          .item-title {
            color: #eaf6ff;
          }

          .item-desc {
            color: #b3c6e0;
          }
        }
      }
    }

    .footer-warning {
      color: #49b1f5;
      background: #22304a;
      border-left: 4px solid #49b1f5;
    }
  }
</style>
