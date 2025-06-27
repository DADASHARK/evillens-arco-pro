<template>
  <a-col class="banner">
    <a-col :span="8">
      <a-typography-title
        :heading="5"
        :style="{
          marginTop: 0,
          fontSize: '14px',
          fontFamily: `'Orbitron', 'Roboto Mono', 'Consolas', 'monospace', sans-serif'`,
          // fontWeight: 'bold',
          fontStyle: 'italic',
          letterSpacing: '1px',
        }"
      >
        {{ $t('workplace.welcome') }}
        <!-- {{ userInfo.name }} -->
      </a-typography-title>
    </a-col>
    <a-divider class="panel-border" />
  </a-col>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useUserStore } from '@/store';

  const userStore = useUserStore();
  const userInfo = computed(() => {
    return {
      name: userStore.name,
    };
  });
</script>

<style scoped lang="less">
  .banner {
    width: 100%;
    padding: 20px 20px 0;
    background-color: var(--color-bg-2);
    border-radius: 4px 4px 0 0;
  }

  :deep(.arco-icon-home) {
    margin-right: 6px;
  }
</style>
