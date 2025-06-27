<template>
  <div class="container">
    <!-- Logo区块，和登录页一致 -->
    <div class="logo">
      <img alt="logo" src="../../assets/logo.svg" />
      <div class="logo-text">EvilLens:儿童邪典视频挖掘与治理平台</div>
    </div>
    <!-- 登录入口按钮 -->
    <div class="login-entry">
      <a-button type="outline" @click="goToLogin">
        <template #icon>
          <icon-user />
        </template>
        登录治理系统
      </a-button>
    </div>

    <!-- 内容容器 -->
    <div class="content-container">
      <!-- 上部分 - 内容图表 -->
      <div class="panel">
        <ContentChart />
      </div>

      <!-- 中间部分 - 核心功能和创新点并列 -->
      <div class="panel dual-panel">
        <div class="panel-half">
          <QuickOperation />
        </div>
        <div class="panel-half">
          <Chuangxin />
        </div>
      </div>

      <!-- 下部分 - 公告 -->
      <div class="panel">
        <Announcement />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { useRouter } from 'vue-router';
  import ContentChart from './components/content-chart.vue';
  import Announcement from './components/announcement.vue';
  import QuickOperation from './components/quick-operation.vue';
  import Chuangxin from './components/chuangxin.vue'; // 确保导入创新点组件

  const router = useRouter();

  const goToLogin = () => {
    router.push('/login');
  };
</script>

<script lang="ts">
  export default {
    name: 'introduce',
  };
</script>

<style lang="less" scoped>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    min-height: 100vh; // 确保至少占满整个视口高度
    padding: 16px 20px;
    padding-top: 80px;
    padding-bottom: 0;
    // 使用背景图片，纵向平铺循环
    background-image: url('@/assets/images/background.png');
    background-repeat: repeat-y; // 纵向循环
    background-position: top center;
    background-size: 100% auto; // 图片宽度撑满容器，高度自适应
  }

  .logo {
    position: absolute;
    top: 20px;
    left: 20px; // 由 right: 20px; 改为 left: 20px;
    z-index: 2;
    display: inline-flex;
    align-items: center;

    img {
      width: 80px;
      height: auto;
    }

    &-text {
      margin-right: 4px;
      margin-left: 4px;
      color: var(--color-fill-1);
      font-size: 20px;
    }
  }

  .login-entry {
    position: absolute;
    top: 20px;
    right: 20px;

    // 修改登录按钮样式为白底黑字
    :deep(.arco-btn) {
      color: #0a192f;
      font-weight: 500;
      background-color: white;
      border: none;
      box-shadow: 0 2px 8px rgb(0 0 0 / 15%);

      &:hover {
        color: #0a192f;
        background-color: #f5f5f5;
      }

      .arco-icon {
        color: #0a192f;
      }
    }
  }

  .content-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    max-width: 1200px;
  }

  .panel {
    margin-bottom: 16px;
    padding: 20px;
    overflow: auto;
    background-color: transparent;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgb(0 0 0 / 20%);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 6px 16px rgb(0 0 0 / 30%);
      transform: translateY(-2px);
    }
  }

  /* 响应式布局 */
  @media (max-width: 768px) {
    .content-container {
      width: 100%;
    }
  }

  .dual-panel {
    display: flex;
    flex-direction: row;
    gap: 20px;
    padding: 0; // 移除内边距，让子元素自己控制内边距

    @media (max-width: 768px) {
      flex-direction: column; // 在移动设备上改为垂直排列
    }
  }

  .panel-half {
    flex: 1;
    min-width: 0; // 防止内容溢出
    padding: 0; // 移除内边距

    @media (max-width: 768px) {
      width: 100%;
    }
  }
</style>
