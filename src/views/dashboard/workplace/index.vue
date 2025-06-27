<template>
  <div class="container">
    <!-- 直接放在最上方 -->
    <Breadcrumb :items="['menu.dashboard', '功能展示页']" />
    <div class="layout">
      <div class="left-side">
        <QuickOperation />
      </div>
      <div class="right-side">
        <Announcement />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import QuickOperation from './components/quick-operation.vue';
  import Announcement from './components/announcement.vue';
</script>

<script lang="ts">
  export default {
    name: 'Dashboard',
  };
</script>

<style lang="less" scoped>
  .container {
    display: flex;
    flex-direction: column; // 新增，使内容垂直排列
    width: 100%;
    min-height: 100vh;
    background-color: var(--color-fill-2);
    // position: relative; // 可以去掉
  }

  // 删除 .breadcrumb-fixed 样式
  .layout {
    display: flex;
    width: 100%;
  }

  .left-side {
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    width: 400px;
    min-height: 100vh;
    padding: 32px 0 0 32px;
    background: transparent;
  }

  .right-side {
    display: flex;
    flex: 1;
    align-items: flex-start;
    justify-content: flex-start;
    min-height: 100vh;
    padding: 32px 32px 0;
    background: transparent;
  }
</style>
