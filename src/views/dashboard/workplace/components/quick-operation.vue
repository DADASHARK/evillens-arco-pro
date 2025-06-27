<template>
  <div class="feature-list-card" :class="{ 'dark-mode': isDark }">
    <div class="feature-list-title">平台核心功能</div>
    <div class="feature-list">
      <button class="feature-btn">
        <span class="feature-index">1</span>
        邪典视频展示
      </button>
      <button class="feature-btn">
        <span class="feature-index">2</span>
        地理信息溯源
      </button>
      <button class="feature-btn">
        <span class="feature-index">3</span>
        视频信息分析
      </button>
      <button class="feature-btn">
        <span class="feature-index">4</span>
        关键词云分析
      </button>
      <button class="feature-btn">
        <span class="feature-index">5</span>
        报告生成
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import useThemes from '@/hooks/themes';

  const { isDark } = useThemes();
</script>

<style scoped lang="less">
  .feature-list-card {
    display: flex;
    flex-direction: column;
    align-items: stretch; // 让内容撑满容器宽度
    width: 100%; // 新增，让容器等宽页面
    min-height: 420px;
    padding: 36px 24px 32px;
    background: #f6faff;
    border-radius: 18px;
    box-shadow: 0 4px 24px 0 rgb(24 144 255 / 10%);

    &.dark-mode {
      background: #16213a;
      box-shadow: 0 4px 24px 0 rgb(24 144 255 / 18%);
    }
  }

  .feature-list-title {
    margin-bottom: 32px;
    color: #1677ff;
    font-weight: bold;
    font-size: 22px;
    letter-spacing: 2px;
    text-align: center;
  }

  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 22px;
    align-items: center;
    width: 100%;
  }

  .feature-btn {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 260px;
    height: 56px;
    padding-left: 28px;
    color: #fff;
    font-weight: 500;
    font-size: 18px;
    background: linear-gradient(90deg, #1677ff 0%, #49b1f5 100%);
    border: none;
    border-radius: 16px;
    box-shadow: 0 2px 12px 0 rgb(22 119 255 / 10%);
    cursor: pointer;
    transition: background 0.2s, box-shadow 0.2s, transform 0.2s;

    &:hover {
      background: linear-gradient(90deg, #49b1f5 0%, #1677ff 100%);
      box-shadow: 0 4px 24px 0 rgb(22 119 255 / 18%);
      transform: translateY(-2px) scale(1.03);
    }
  }

  .feature-index {
    display: inline-block;
    width: 28px;
    height: 28px;
    margin-right: 18px;
    color: #1677ff;
    font-weight: bold;
    font-size: 16px;
    line-height: 28px;
    text-align: center;
    background: #fff;
    border-radius: 50%;
    box-shadow: 0 2px 8px 0 rgb(22 119 255 / 10%);
  }

  .dark-mode {
    .feature-list-title {
      color: #49b1f5;
    }

    .feature-btn {
      color: #fff;
      background: linear-gradient(90deg, #1a5be6 0%, #49b1f5 100%);

      &:hover {
        background: linear-gradient(90deg, #49b1f5 0%, #1a5be6 100%);
      }
    }

    .feature-index {
      color: #49b1f5;
      background: #22304a;
    }
  }
</style>
