import axios from 'axios';
import type { TableData } from '@arco-design/web-vue/es/table/interface';

// // 介绍页面数据接口
// export interface IntroduceDataItem {
//   id: string;
//   title: string;
//   description: string;
//   imageUrl: string;
//   tags: string[];
// }

// export interface IntroduceDataRes {
//   code: number;
//   data: {
//     welcomeTitle: string;
//     welcomeDescription: string;
//     features: string[];
//     sampleVideos: IntroduceDataItem[];
//   };
// }

// // 获取介绍页面数据
// export function queryIntroduceData() {
//   return axios.get<IntroduceDataRes>('/api/introduce/data');
// }

// // 系统功能介绍数据
// export interface SystemFeatureItem {
//   title: string;
//   description: string;
//   icon: string;
// }

// export interface SystemFeaturesRes {
//   code: number;
//   data: SystemFeatureItem[];
// }

// // 获取系统功能介绍数据
// export function querySystemFeatures() {
//   return axios.get<SystemFeaturesRes>('/api/introduce/features');
// }

// // 快速入门指南数据
// export interface QuickStartGuideItem {
//   title: string;
//   link: string;
//   type: 'document' | 'video' | 'tutorial';
// }

// export interface QuickStartGuideRes {
//   code: number;
//   data: QuickStartGuideItem[];
// }

// // 获取快速入门指南数据
// export function queryQuickStartGuide() {
//   return axios.get<QuickStartGuideRes>('/api/introduce/quick-start');
// }
