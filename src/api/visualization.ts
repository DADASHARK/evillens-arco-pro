import axios from 'axios';
import { GeneralChart } from '@/types/global';

export interface ChartDataRecord {
  x: string;
  y: number;
  name: string;
}
export interface DataChainGrowth {
  quota: string;
}

export interface DataChainGrowthRes {
  count: number;
  growth: number;
  chartData: {
    xAxis: string[];
    data: { name: string; value: number[] };
  };
}
export function queryDataChainGrowth(data: DataChainGrowth) {
  return axios.post<DataChainGrowthRes>('/api/data-chain-growth', data);
}

export interface PopularAuthorRes {
  list: {
    ranking: number;
    author: string;
    contentCount: number;
    clickCount: number;
  }[];
}

export function queryPopularAuthor() {
  return axios.get<PopularAuthorRes>('/api/popular-author/list');
}

export interface ContentPublishRecord {
  x: string[];
  y: number[];
  name: string;
}

export function queryContentPublish() {
  return axios.get<ContentPublishRecord[]>('/api/content-publish');
}

export function queryContentPeriodAnalysis() {
  return axios.post<GeneralChart>('/api/content-period-analysis');
}

export interface PublicOpinionAnalysis {
  quota: string;
}
export interface PublicOpinionAnalysisRes {
  count: number;
  growth: number;
  chartData: ChartDataRecord[];
}
export function queryPublicOpinionAnalysis(data: DataChainGrowth) {
  return axios.post<PublicOpinionAnalysisRes>(
    '/api/public-opinion-analysis',
    data
  );
}
export interface DataOverviewRes {
  xAxis: string[];
  data: Array<{ name: string; value: number[]; count: number }>;
}

export function queryDataOverview() {
  return axios.post<DataOverviewRes>('/api/data-overview');
}

// 新增地域分布数据接口
export interface GeographyDistributionItem {
  province: string;
  percentage: string | number; // 百分比
}

export interface GeographyDistributionRes {
  code: number;
  data: GeographyDistributionItem[];
}

export function queryGeographyDistribution() {
  return axios.get<GeographyDistributionRes>('/api/geography/distribution');
}

// 一天内
export interface TimeDistributionItem {
  count: number;
  hour: number;
}
export interface TimeDistributionRes {
  code: number;
  data: TimeDistributionItem[];
}
export function TimeDistribution() {
  return axios.get<GeographyDistributionRes>('/api/trends/hourly');
}
// 仅七天

export interface TrendsWeeklyItem {
  count: number;
  date: string;
}
export interface TrendsWeeklyRes {
  code: number;
  data: TrendsWeeklyItem[];
}
export function TrendsWeekly() {
  return axios.get<TrendsWeeklyRes>('/api/trends/recent');
}

export interface TrendsDetailItem {
  total_shares: number;
  total_likes: number;
  recent_seven_days_videos: number;
}

export interface TrendsDetailRes {
  code: number;
  data: TrendsDetailItem;
}
export function TrendsDetail() {
  return axios.get<TrendsDetailRes>('/api/trends/detail');
}

// 用户画像接口
export interface VideoItem {
  vd_id: string;
  name: string;
  publish_time: string;
  likes: number;
  shares: number;
  collects: number;
}

export interface UserProfileData {
  user_id: string;
  user_name: string;
  age: number;
  follow_count: number;
  fans_count: number;
  like_count: number;
  ip_location: string;
  self_description: string;
  ai_description: string;
  video_list: VideoItem[];
  total: number;
}

export interface UserProfileResponse {
  code: number;
  message: string;
  data: UserProfileData;
}

export function getUserProfile(userId: string) {
  return axios.get<UserProfileResponse>(
    `/api/profile/get_user_profile/${userId}`
  );
}

// 添加关键词云数据接口
export interface KeywordItem {
  keyword: string;
  frequency: number;
}

export interface KeywordsResponse {
  data: KeywordItem[];
  code: number;
}

export function getKeywords() {
  return axios.get<KeywordsResponse>('/api/keywords');
}
