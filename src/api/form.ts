import axios from 'axios';

export interface BaseInfoModel {
  activityName: string;
  channelType: string;
  promotionTime: string[];
  promoteLink: string;
}
export interface ChannelInfoModel {
  advertisingSource: string;
  advertisingMedia: string;
  keyword: string[];
  pushNotify: boolean;
  advertisingContent: string;
}

export type UnitChannelModel = BaseInfoModel & ChannelInfoModel;

export function submitChannelForm(email: string) {
  return axios.post('/api/report/gen_report', { email });
}

// // 新增：发送邮件报告的API
// export function sendReportEmail(email: string) {
//   return axios.post('/api/report/gen_report', { email });
// }

// 新增：获取报告统计数据
export function getReportStats() {
  return axios.get('/api/report');
}
