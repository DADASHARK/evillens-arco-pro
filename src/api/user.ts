import axios from 'axios';
import type { RouteRecordNormalized } from 'vue-router';
import { UserState } from '@/store/modules/user/types';

export interface LoginData {
  username: string;
  password: string;
}

export interface LoginRes {
  code: number;
  data: {
    token: string;
    user: {
      id: number;
      username: string;
    };
    message?: string;
  };
}

// 修改登录API路径，指向后端认证接口
export function login(data: LoginData) {
  return axios.post<LoginRes>('/api/auth/login', data);
}

// 其他函数保持不变
export function logout() {
  return axios.post<LoginRes>('/api/user/logout');
}

export function getUserInfo() {
  return axios.post<UserState>('/api/user/info');
}

export function getMenuList() {
  return axios.post<RouteRecordNormalized[]>('/api/user/menu');
}
