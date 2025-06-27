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
    align-items: center;
    width: 100%; // 确保容器占满父元素宽度
    height: 100%; // 确保卡片占满容器高度
    min-height: 420px;
    padding: 36px 24px 32px;
    background: rgb(10 25 47 / 85%); // 修改为与其他组件一致的深蓝色背景
    border-radius: 18px;
    box-shadow: 0 8px 30px rgb(0 0 0 / 30%); // 增强阴影效果
    backdrop-filter: blur(8px); // 添加模糊效果

    &.dark-mode {
      background: rgb(10 25 47 / 95%); // 稍微加深背景
      box-shadow: 0 8px 30px rgb(0 0 0 / 40%);
    }
  }

  .feature-list-title {
    margin-bottom: 32px;
    color: #64ffda; // 保持青绿色
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
    width: 100%;
    max-width: 600px;
    height: 56px;
    padding-left: 28px;
    color: #fff;
    font-weight: 500;
    font-size: 18px;
    background: linear-gradient(
      90deg,
      rgb(10 25 47 / 90%) 0%,
      rgb(15 40 70 / 90%) 100%
    ); // 修改为深蓝色渐变

    border: 2px solid #64ffda; // 添加青绿色边框
    border-radius: 16px;
    box-shadow: 0 4px 20px rgb(100 255 218 / 15%);
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(
        90deg,
        rgb(15 40 70 / 90%) 0%,
        rgb(10 25 47 / 90%) 100%
      ); // 反向渐变

      border-color: #64ffda;
      box-shadow: 0 6px 25px rgb(100 255 218 / 25%);
      transform: translateY(-2px);
    }
  }

  .feature-index {
    display: inline-block;
    width: 28px;
    height: 28px;
    margin-right: 18px;
    color: rgb(10 25 47 / 90%); // 深蓝色文字
    font-weight: bold;
    font-size: 16px;
    line-height: 28px;
    text-align: center;
    background: #64ffda; // 修改为青绿色
    border-radius: 50%;
    box-shadow: 0 2px 8px rgb(100 255 218 / 20%);
  }

  .dark-mode {
    .feature-list-title {
      color: #64ffda; // 保持青绿色
    }

    .feature-btn {
      color: #fff;
      background: linear-gradient(
        90deg,
        rgb(10 25 47 / 95%) 0%,
        rgb(15 40 70 / 95%) 100%
      );

      &:hover {
        background: linear-gradient(
          90deg,
          rgb(15 40 70 / 95%) 0%,
          rgb(10 25 47 / 95%) 100%
        );
      }
    }

    .feature-index {
      color: rgb(10 25 47 / 95%);
      background: #64ffda;
    }
  }
</style>
