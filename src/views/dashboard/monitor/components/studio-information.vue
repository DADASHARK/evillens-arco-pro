<template>
  <a-card class="general-card" :title="$t('monitor.title.studioInfo')">
    <a-form :model="formData" layout="vertical">
      <a-form-item :label="$t('monitor.studioInfo.label.studioTitle')" required>
        <a-textarea
          v-model="formData.video_url"
          :placeholder="$t('monitor.studioInfo.placeholder.studioTitle')"
          :auto-size="{ minRows: 3, maxRows: 5 }"
        />
        <div class="link-tips">
          支持的链接类型：（支持同时输入多个链接，以空格或回车分开）
          <ul>
            <li
              >视频详情页面"video/"型
              https://www.douyin.com/video/7476188844711349561</li
            >
            <li>带modal_id的搜索结果链接</li>
            <li>分享链接"v.douyin.com"型</li>
          </ul>
        </div>
      </a-form-item>
    </a-form>
    <div class="action-buttons">
      <a-button :loading="loading" type="primary" @click="submitDetectTask">
        {{ $t('monitor.studioInfo.btn.fresh') }}
      </a-button>
      <a-button :disabled="loading" @click="clearForm">
        {{ $t('monitor.action.clear') }}
      </a-button>
    </div>

    <div v-if="validationResult.length > 0" class="validation-results">
      <div class="validation-title">链接验证结果：</div>
      <div
        v-for="(result, index) in validationResult"
        :key="index"
        class="validation-item"
        :class="{ valid: result.isValid, invalid: !result.isValid }"
      >
        <icon-check-circle-fill v-if="result.isValid" class="valid-icon" />
        <icon-close-circle-fill v-else class="invalid-icon" />
        <span class="link-text">{{ result.link }}</span>
      </div>
    </div>

    <!-- 添加结果提示组件 -->
    <a-result
      v-if="submitResult.show"
      :status="submitResult.status"
      :title="submitResult.title"
      :subtitle="submitResult.subtitle"
    >
      <template #extra>
        <a-button type="primary" @click="submitResult.show = false">
          {{ $t('monitor.action.confirm') }}
        </a-button>
      </template>
    </a-result>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import useLoading from '@/hooks/loading';
  import { createDetectTask } from '@/api/dashboard';
  import { useI18n } from 'vue-i18n';

  // 定义 ResultStatus 类型
  type ResultStatus =
    | 'error'
    | 'success'
    | 'warning'
    | 'info'
    | '403'
    | '404'
    | '500'
    | null;

  const { t } = useI18n();

  const { loading, setLoading } = useLoading(false);
  const formData = reactive({
    video_url: '',
  });

  // 修改 submitResult 的类型
  const submitResult = reactive<{
    show: boolean;
    status: ResultStatus;
    title: string;
    subtitle: string;
  }>({
    show: false,
    status: null,
    title: '',
    subtitle: '',
  });

  interface ValidationResult {
    link: string;
    isValid: boolean;
  }

  const validationResult = ref<ValidationResult[]>([]);

  // 提取链接
  const extractLinks = (text: string): string[] => {
    if (!text) return [];

    // 分割文本，支持空格、换行、逗号等分隔符
    const parts = text.split(/[\s,，;；]+/);

    // 过滤出包含douyin.com的链接
    return parts.filter((part) => part.includes('douyin.com'));
  };

  // 验证链接
  const validateLinks = (links: string[]): boolean => {
    validationResult.value = [];

    if (links.length === 0) {
      Message.error(t('monitor.message.noValidLinks'));
      return false;
    }

    // 验证每个链接
    validationResult.value = links.map((link) => {
      let isValid = false;

      if (link.includes('douyin.com/video/')) {
        isValid = /douyin\.com\/video\/\d+/.test(link);
      } else if (link.includes('modal_id=')) {
        isValid = /modal_id=\d+/.test(link);
      } else if (link.includes('v.douyin.com/')) {
        isValid = /v\.douyin\.com\/[a-zA-Z0-9]+/.test(link);
      }

      return {
        link,
        isValid,
      };
    });

    // 检查是否所有链接都有效
    return validationResult.value.every((result) => result.isValid);
  };

  // 清空表单
  const clearForm = () => {
    formData.video_url = '';
    validationResult.value = [];
  };

  // 提交检测任务
  const submitDetectTask = async () => {
    try {
      // 提取链接
      const links = extractLinks(formData.video_url);

      // 验证链接
      if (!validateLinks(links)) {
        return;
      }

      setLoading(true);

      console.log('准备发送检测任务请求，链接:', formData.video_url);
      
      // 调用API创建检测任务
      const response = await createDetectTask({
        video_url: formData.video_url,
      });

      console.log('检测任务创建成功，响应:', response);

      // 处理响应
      submitResult.show = true;
      submitResult.status = 'success';
      submitResult.title = t('monitor.message.taskCreated');
      submitResult.subtitle = `${t('monitor.result.taskId')}: ${response.data.task_id}`;

      // 触发一个自定义事件，将任务信息传递给 chat-panel 组件
      const event = new CustomEvent('detect-task-created', {
        detail: {
          taskId: response.data.task_id,
        },
      });
      window.dispatchEvent(event);
      console.log('已触发detect-task-created事件，任务ID:', response.data.task_id);

      // 清空表单
      clearForm();
    } catch (error) {
      const err = error as any;
      console.error('创建检测任务失败:', error);
      
      // 更详细的错误日志
      if (err.response) {
        console.error('HTTP状态码:', err.response.status);
        console.error('响应头:', err.response.headers);
        console.error('响应数据:', err.response.data);
      } else if (err.request) {
        console.error('请求已发送但未收到响应:', err.request);
      } else {
        console.error('请求配置错误:', err.config);
      }
      
      submitResult.show = true;
      submitResult.status = 'error';
      submitResult.title = t('monitor.message.taskCreateFailed');
      submitResult.subtitle = err.response?.data?.message || err.message || t('monitor.message.unknownError');
    } finally {
      setLoading(false);
    }
  };

  // 监听页面加载
  onMounted(() => {
    console.log('studio-information 组件已加载');
  });
</script>

<style lang="less" scoped>
  .link-tips {
    margin-top: 8px;
    color: var(--color-text-3);
    font-size: 12px;

    ul {
      margin-top: 4px;
      padding-left: 20px;
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 16px;
  }

  .validation-results {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--color-border-2);

    .validation-title {
      margin-bottom: 8px;
      font-weight: bold;
    }

    .validation-item {
      display: flex;
      align-items: center;
      margin-bottom: 6px;

      &.valid {
        color: rgb(var(--success-6));
      }

      &.invalid {
        color: rgb(var(--danger-6));
      }

      .valid-icon,
      .invalid-icon {
        margin-right: 8px;
      }

      .link-text {
        word-break: break-all;
      }
    }
  }
</style>
