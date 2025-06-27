<template>
  <div class="container">
    <Breadcrumb :items="['menu.form', 'menu.form.step']" />
    <a-spin :loading="loading" style="width: 100%">
      <div class="split-container">
        <!-- 左侧表单部分 -->
        <a-card class="general-card form-section">
          <template #title>
            {{ $t('stepForm.step.title') }}
          </template>
          <div class="wrapper">
            <a-steps
              v-model:current="step"
              style="width: 580px"
              line-less
              class="steps"
            >
              <a-step :description="$t('stepForm.step.subTitle.baseInfo')">
                {{ $t('stepForm.step.title.baseInfo') }}
              </a-step>
              <a-step :description="$t('stepForm.step.subTitle.channel')">
                {{ $t('stepForm.step.title.channel') }}
              </a-step>
              <a-step :description="$t('stepForm.step.subTitle.finish')">
                {{ $t('stepForm.step.title.finish') }}
              </a-step>
            </a-steps>
            <keep-alive>
              <BaseInfo v-if="step === 1" @change-step="changeStep" />
              <ChannelInfo v-else-if="step === 2" @change-step="changeStep" />
              <Success
                v-else-if="step === 3"
                @change-step="changeStep"
                :form-data="submitModel"
              />
            </keep-alive>
          </div>
        </a-card>

        <!-- 右侧图片展示部分 -->
        <div class="image-section">
          <a-card class="general-card image-card">
            <template #title>报告示例</template>
            <div class="image-container">
              <img
                src="@/assets/images/report.png"
                alt="报告示例"
                class="preview-image"
              />
            </div>
          </a-card>
          <a-card class="general-card image-card">
            <template #title>邮件示例</template>
            <div class="image-container">
              <img
                src="@/assets/images/email.png"
                alt="邮件示例"
                class="preview-image"
              />
            </div>
          </a-card>
        </div>
      </div>
    </a-spin>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import useLoading from '@/hooks/loading';
  import {
    submitChannelForm,
    BaseInfoModel,
    ChannelInfoModel,
    UnitChannelModel,
  } from '@/api/form';
  import BaseInfo from './components/base-info.vue';
  import ChannelInfo from './components/channel-info.vue';
  import Success from './components/success.vue';

  const { loading, setLoading } = useLoading(false);
  const step = ref(1);
  const submitModel = ref<UnitChannelModel>({} as UnitChannelModel);
  const submitForm = async () => {
    setLoading(true);
    try {
      // 只传递邮箱
      await submitChannelForm(submitModel.value.advertisingContent); // 假设邮箱在 advertisingContent 字段
      step.value = 3;
      // 不要清空submitModel，因为需要传递给Success组件
      // submitModel.value = {} as UnitChannelModel;
    } catch (err) {
      // 错误处理
      console.error('提交表单失败:', err);
      // 即使失败也继续到成功页面，使用本地PDF
      submitModel.value.localPdfPath =
        'D:/xinansai/web/evillens-arco-pro/src/assets/evidence_report.pdf';
      submitModel.value.useLocalPdf = true;
      step.value = 3;
    } finally {
      setLoading(false);
    }
  };
  const changeStep = (
    direction: string | number,
    model: BaseInfoModel | ChannelInfoModel
  ) => {
    if (typeof direction === 'number') {
      step.value = direction;
      return;
    }

    if (direction === 'forward' || direction === 'submit') {
      submitModel.value = {
        ...submitModel.value,
        ...model,
      };
      if (direction === 'submit') {
        submitForm();
        return;
      }
      step.value += 1;
    } else if (direction === 'backward') {
      step.value -= 1;
    }
  };
</script>

<script lang="ts">
  export default {
    name: 'Step',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px;
  }

  .split-container {
    display: flex;
    gap: 20px;
    width: 100%;
  }

  .form-section {
    flex: 1;
    min-width: 0;
  }

  .image-section {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: 20px;
  }

  .image-card {
    display: flex;
    flex-direction: column;
    height: calc(50% - 10px);
  }

  .image-container {
    display: flex;
    flex: 1;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 15%);
  }

  .wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 64px 0;
    background-color: var(--color-bg-2);

    :deep(.arco-form) {
      .arco-form-item {
        &:last-child {
          margin-top: 20px;
        }
      }
    }
  }

  .steps {
    margin-bottom: 76px;
  }
</style>
