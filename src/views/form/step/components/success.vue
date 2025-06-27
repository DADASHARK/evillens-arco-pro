<template>
  <div class="success-wrap">
    <a-result
      status="success"
      :title="$t('stepForm.success.title')"
      :subtitle="$t('stepForm.success.subTitle')"
    />
    <a-space :size="16">
      <a-button key="view" type="primary" @click="viewReport">
        {{ $t('stepForm.button.view') }}
      </a-button>
      <a-button key="again" type="secondary" @click="oneMore">
        {{ $t('stepForm.button.again') }}
      </a-button>
    </a-space>
    <div class="details-wrapper">
      <a-typography-title :heading="6" style="margin-top: 0">
        {{ $t('stepForm.form.description.title') }}
      </a-typography-title>
      <a-typography-paragraph style="margin-bottom: 0">
        {{ $t('stepForm.form.description.text') }}
        <a-link href="javascript:void(0)" @click="viewReport">{{
          $t('stepForm.button.view')
        }}</a-link>
      </a-typography-paragraph>
    </div>

    <!-- PDF查看器对话框 -->
    <a-modal
      v-model:visible="pdfModalVisible"
      :title="$t('stepForm.button.view')"
      :footer="false"
      :mask-closable="true"
      :closable="true"
      :modal-class="'pdf-modal'"
      :width="1000"
    >
      <template #title>
        <div class="pdf-modal-header">
          <span>{{ $t('stepForm.button.view') }}</span>
          <a-button type="text" @click="downloadPdf">
            <icon-download />
            下载报告
          </a-button>
        </div>
      </template>
      <div class="pdf-container">
        <iframe :src="pdfUrl" width="100%" height="600"></iframe>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { getReportStats } from '@/api/form';
  import { Message } from '@arco-design/web-vue';

  const reportStats = ref(null);
  const emits = defineEmits(['changeStep']);
  const pdfModalVisible = ref(false);
  const pdfUrl = ref('');
  const localPdfPath = ref(
    'D:/xinansai/web/evillens-arco-pro/src/assets/evidence_report.pdf'
  );

  // 从父组件接收数据
  const props = defineProps({
    formData: {
      type: Object,
      default: () => ({}),
    },
  });

  const oneMore = () => {
    emits('changeStep', 1);
  };

  const viewReport = () => {
    // 使用相对路径，确保在浏览器中可以访问
    pdfUrl.value = '/src/assets/evidence_report.pdf';
    pdfModalVisible.value = true;
  };

  const downloadPdf = () => {
    // 创建一个链接元素
    const link = document.createElement('a');
    link.href = pdfUrl.value;
    link.download = 'evidence_report.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    Message.success('报告下载成功');
  };

  onMounted(async () => {
    try {
      const res = await getReportStats();
      if (res.data && res.data.code === 20000) {
        reportStats.value = res.data.data;
      }
    } catch (error) {
      console.error('获取报告统计数据失败:', error);
      // 使用本地数据
      reportStats.value = {
        status: 'success',
        reportUrl: '/src/assets/evidence_report.pdf',
      };
    }

    // 如果从父组件传递了本地PDF路径，则使用它
    if (props.formData && props.formData.localPdfPath) {
      localPdfPath.value = props.formData.localPdfPath;
    }
  });
</script>

<style scoped lang="less">
  .success-wrap {
    text-align: center;
  }

  :deep(.arco-result) {
    padding-top: 0;
  }

  .details-wrapper {
    width: 895px;
    margin-top: 54px;
    padding: 20px;
    text-align: left;
    background-color: var(--color-fill-2);
  }

  .pdf-container {
    width: 100%;
    height: 600px;
    overflow: hidden;
  }

  .pdf-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  :deep(.pdf-modal) {
    .arco-modal-body {
      padding: 0;
    }
  }
</style>
