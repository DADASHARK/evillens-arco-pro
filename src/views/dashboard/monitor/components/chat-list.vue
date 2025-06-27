<template>
  <div class="chat-list">
    <a-list :bordered="false">
      <a-list-item
        v-for="item in renderList"
        :key="item.id"
        class="chat-item"
        @click="handleItemClick(item)"
      >
        <a-list-item-meta>
          <template #avatar>
            <div class="avatar-wrapper">
              <a-avatar shape="square">
                <icon-file-video />
              </a-avatar>
            </div>
          </template>
          <template #title>
            <div class="title-wrapper">
              <span class="title-content">{{ item.username }}</span>
              <span class="title-time">{{ item.time }}</span>
            </div>
          </template>
          <template #description>
            <div class="description-wrapper">
              <span class="description-content">{{ item.content }}</span>
              <!-- 添加状态显示 -->
              <span
                class="description-status"
                :class="{ 'status-detecting': item.status === 'detecting' }"
              >
                {{ item.status === 'detecting' ? '正在检测中...' : '' }}
                <icon-loading v-if="item.status === 'detecting'" />
              </span>
            </div>
          </template>
        </a-list-item-meta>
      </a-list-item>
    </a-list>
  </div>
</template>

<script lang="ts" setup>
  import { PropType } from 'vue';
  import { ChatRecord } from '@/api/message';

  defineProps({
    renderList: {
      type: Array as PropType<ChatRecord[]>,
      default: () => [],
    },
  });

  const emit = defineEmits(['itemClick']);

  const handleItemClick = (item: ChatRecord) => {
    emit('itemClick', item);
  };
</script>

<style scoped lang="less">
  .chat-list {
    height: 100%;
    overflow-y: auto;
  }

  .chat-item {
    padding: 10px 0;
    border-bottom: 1px solid var(--color-border-2);
    cursor: pointer;

    &:hover {
      background-color: var(--color-fill-2);
    }
  }

  .avatar-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
  }

  .title-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title-content {
    flex: 1;
    color: var(--color-text-1);
    font-weight: 500;
    font-size: 14px;
  }

  .title-time {
    color: var(--color-text-3);
    font-size: 12px;
  }

  .description-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .description-content {
    flex: 1;
    color: var(--color-text-2);
    font-size: 12px;
    word-break: break-all;
  }

  .description-status {
    display: flex;
    align-items: center;
    color: var(--color-text-3);
    font-size: 12px;

    &.status-detecting {
      color: rgb(var(--primary-6));
    }

    .arco-icon {
      margin-left: 4px;
    }
  }
</style>
