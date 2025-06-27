import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import { Message, Modal } from '@arco-design/web-vue';
import { useUserStore } from '@/store';
import { getToken } from '@/utils/auth';

export interface HttpResponse<T = unknown> {
  status: number;
  msg: string;
  code: number;
  data: T;
}

if (import.meta.env.VITE_API_BASE_URL) {
  axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL;
}

axios.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // let each request carry token
    // this example using the JWT token
    // Authorization is a custom headers key
    // please modify it according to the actual situation
    const token = getToken();
    if (token) {
      if (!config.headers) {
        config.headers = {};
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // do something
    return Promise.reject(error);
  }
);
// add response interceptors
axios.interceptors.response.use(
  (response: AxiosResponse<HttpResponse>) => {
    const res = response.data;
    // if the custom code is not 20000, it is judged as an error.
    if (res.code !== 20000) {
      // 获取错误信息
      const errorMsg =
        res.data && typeof res.data === 'object' && 'message' in res.data
          ? res.data.message
          : res.msg || 'Error';

      // 不要对登录接口的错误显示全局消息提示
      if (!response.config.url?.includes('/api/auth/login')) {
        Message.error({
          content: String(errorMsg), // 使用 String() 确保转换为字符串类型
          duration: 5 * 1000,
        });
      }

      // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
      if (
        [50008, 50012, 50014].includes(res.code) &&
        response.config.url !== '/api/user/info'
      ) {
        Modal.error({
          title: 'Confirm logout',
          content:
            'You have been logged out, you can cancel to stay on this page, or log in again',
          okText: 'Re-Login',
          async onOk() {
            const userStore = useUserStore();

            await userStore.logout();
            window.location.reload();
          },
        });
      }
      return Promise.reject(new Error(String(errorMsg)));
    }
    return res;
  },
  (error) => {
    // 处理登录接口的特殊错误
    if (
      error.config &&
      error.config.url &&
      error.config.url.includes('/api/auth/login')
    ) {
      // 对于登录接口，我们不显示全局错误消息，而是返回特定错误供登录表单处理
      if (error.response && error.response.status === 401) {
        return Promise.reject(new Error('用户名或密码错误'));
      }
    } else {
      // 其他接口的错误处理保持不变
      // Message.error({
      //   content: '请求错误，请稍后重试',
      //   duration: 5 * 1000,
      // });
    }
    return Promise.reject(error);
  }
);
