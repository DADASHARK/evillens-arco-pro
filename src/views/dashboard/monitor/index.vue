<template>
  <div class="container">
    <div class="content-wrapper">
      <a-row :gutter="16">
        <a-col :span="12">
          <studio-information />
        </a-col>
        <a-col :span="12">
          <chat-panel />
        </a-col>
      </a-row>
      
      <!-- 视频扩展网络可视化 -->
      <a-row :gutter="16" style="margin-top: 16px;">
        <a-col :span="24">
          <video-expansion-network />
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import StudioInformation from './components/studio-information.vue';
  import ChatPanel from './components/chat-panel.vue';
  import VideoExpansionNetwork from './components/video-expansion-network.vue';
</script>

<style lang="less" scoped>
  .container {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 16px;
    overflow: hidden;
    background-color: var(--color-fill-2);
  }
  
  .content-wrapper {
    flex: 1;
    padding-bottom: 24px; /* 确保底部有足够的空间 */
    overflow-y: auto;
  }
</style>
