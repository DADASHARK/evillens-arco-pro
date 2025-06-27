import axios from 'axios';
import qs from 'query-string';
import type { DescData } from '@arco-design/web-vue/es/descriptions/interface';

export interface PolicyRecord {
  id: string;
  number: number;
  name: string;
  author: string;
  engagement: number;
  count: number;
  status: boolean;
  createdTime: string;
}

export interface PolicyParams extends Partial<PolicyRecord> {
  current: number;
  pageSize: number;
}

export interface PolicyListRes {
  list: PolicyRecord[];
  total: number;
}

// 修改接口地址为 /api/video
export function queryPolicyList(params: PolicyParams) {
  return axios.get<PolicyListRes>('/api/video/', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

// // @/types/list.ts 或类似路径
// export interface VideoSearchItem {
//   id: string;
//   number: number;
//   name: string;
//   contentType: string; // 原始值如“短视频”、“图文”
//   filterType: string; // 原始值如“规则筛选”
//   count: number;
//   createdTime: string;
//   status: number; // 1 表示在线，其他表示离线
// }
// export interface VideoSearchItem {
//   id: string;
//   number: number;
//   name: string;
//   contentType: string; // 原始值如"短视频"、"图文"
//   filterType: string; // 原始值如"规则筛选"
//   count: number;
//   createdTime: string;
//   status: number; // 1 表示在线，其他表示离线
// }

// export interface VideoSearchRes {
//   code: number;
//   data: {
//     list: VideoSearchItem[];
//     total: number;
//   };
// }

// export function queryVideoSearch(params?: PolicyParams) {
//   return axios.get<VideoSearchRes>('/api/searchVideo', {
//     params,
//     paramsSerializer: (obj) => {
//       return qs.stringify(obj);
//     },
//   });
// }
export interface ServiceRecord {
  id: number;
  title: string;
  description: string;
  name?: string;
  actionType?: string;
  icon?: string;
  data?: DescData[];
  enable?: boolean;
  expires?: boolean;
}
export function queryInspectionList() {
  return axios.get('/api/list/quality-inspection');
}

export function queryTheServiceList() {
  return axios.get('/api/list/the-service');
}

export function queryRulesPresetList() {
  return axios.get('/api/list/rules-preset');
}
