<template>
  <div class="login-form-wrapper">
    <div class="login-form-title">{{ $t('login.form.title') }}</div>
    <div class="login-form-sub-title">{{ $t('login.form.title') }}</div>
    <div class="login-form-error-msg">{{ errorMessage }}</div>
    <a-form
      ref="loginForm"
      :model="userInfo"
      class="login-form"
      layout="vertical"
      @submit="handleSubmit"
    >
      <a-form-item
        field="username"
        :rules="[{ required: true, message: $t('login.form.userName.errMsg') }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input
          v-model="userInfo.username"
          :placeholder="$t('login.form.userName.placeholder')"
        >
          <template #prefix>
            <icon-user />
          </template>
        </a-input>
      </a-form-item>
      <a-form-item
        field="password"
        :rules="[{ required: true, message: $t('login.form.password.errMsg') }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input-password
          v-model="userInfo.password"
          :placeholder="$t('login.form.password.placeholder')"
          allow-clear
        >
          <template #prefix>
            <icon-lock />
          </template>
        </a-input-password>
      </a-form-item>
      <a-space :size="16" direction="vertical">
        <div class="login-form-password-actions">
          <a-checkbox
            checked="rememberPassword"
            :model-value="loginConfig.rememberPassword"
            @change="setRememberPassword as any"
          >
            {{ $t('login.form.rememberPassword') }}
          </a-checkbox>
          <a-link>{{ $t('login.form.forgetPassword') }}</a-link>
        </div>
        <a-button type="primary" html-type="submit" long :loading="loading">
          {{ $t('login.form.login') }}
        </a-button>
        <a-button type="text" long class="login-form-register-btn">
          {{ $t('login.form.register') }}
        </a-button>
      </a-space>
    </a-form>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import { Message } from '@arco-design/web-vue';
  import { ValidatedError } from '@arco-design/web-vue/es/form/interface';
  import { useI18n } from 'vue-i18n';
  import { useStorage } from '@vueuse/core';
  import { useUserStore } from '@/store';
  import useLoading from '@/hooks/loading';
  import type { LoginData } from '@/api/user';
  import { login } from '@/api/user';

  const router = useRouter();
  const { t } = useI18n();
  const errorMessage = ref('');
  const { loading, setLoading } = useLoading();
  const userStore = useUserStore();

  interface LoginConfig {
    rememberPassword: boolean;
    username: string;
    password: string;
  }
  const loginConfig = useStorage<LoginConfig>('login-config', {
    rememberPassword: true,
    username: '', // 移除默认值
    password: '', // 移除默认值
  });
  const userInfo = reactive({
    username: loginConfig.value.username,
    password: loginConfig.value.password,
  });

  const handleSubmit = async ({
    errors,
    values,
  }: {
    errors: Record<string, ValidatedError> | undefined;
    values: Record<string, any>;
  }) => {
    if (loading.value) return;
    if (!errors) {
      setLoading(true);
      errorMessage.value = ''; // 清除之前的错误信息

      try {
        // 直接调用登录API
        const res = await login(values as LoginData);

        // 检查响应结构，确定正确的访问路径
        // console.log('登录响应:', res); // 调试用，了解实际响应结构

        // 根据实际响应结构调整条件判断和数据访问
        if (res.code === 20000) {
          // 登录成功，保存token
          userStore.setToken(res.data.token);

          // 设置用户信息
          userStore.setUserInfo({
            userId: res.data.user.id,
            username: res.data.user.username,
          });

          const { redirect, ...othersQuery } = router.currentRoute.value.query;
          router.push({
            name: (redirect as string) || 'DataAnalysis',
            query: {
              ...othersQuery,
            },
          });

          Message.success(t('login.form.login.success'));

          // 保存用户名，但出于安全考虑不保存密码
          const { rememberPassword } = loginConfig.value;
          loginConfig.value.username = rememberPassword ? values.username : '';
          loginConfig.value.password = ''; // 不保存密码
        } else {
          // 登录失败但有响应
          errorMessage.value = res.data.data?.message || '登录失败，请稍后重试';
        }
      } catch (err: any) {
        // 显示友好的错误信息
        console.error('登录错误:', err);
        errorMessage.value = err.message || '用户名或密码错误';

        // 可以根据错误类型显示不同的错误信息
        if (err.message.includes('用户名或密码错误')) {
          Message.error({
            content: '用户名或密码错误，请重新输入',
            duration: 3000,
          });
        }
      } finally {
        setLoading(false);
      }
    }
  };

  const setRememberPassword = (value: boolean) => {
    loginConfig.value.rememberPassword = value;
  };
</script>

<style lang="less" scoped>
  .login-form {
    &-wrapper {
      width: 320px;
    }

    &-title {
      color: var(--color-text-1);
      font-weight: 500;
      font-size: 22px;
      line-height: 32px;
    }

    &-sub-title {
      color: var(--color-text-3);
      font-size: 14px;
      line-height: 24px;
    }

    &-error-msg {
      height: 32px;
      color: rgb(var(--red-6));
      line-height: 32px;
    }

    &-password-actions {
      display: flex;
      justify-content: space-between;
    }

    &-register-btn {
      color: var(--color-text-3) !important;
    }
  }
</style>
