import axios from 'axios';
import type { TableData } from '@arco-design/web-vue/es/table/interface';

// 视频检测任务相关接口
export interface DetectTaskParams {
  video_url: string;
}

export interface DetectTaskResult {
  task_id: string;
  message: string;
}

// 创建检测任务
export function createDetectTask(params: DetectTaskParams) {
  return axios
    .post<any>('/api/detect/create_detect_task', params)
    .then((response) => {
      // 检查响应格式是否符合预期 - 更宽松的检查
      if (response.data) {
        // 情况1: 标准格式 {code: 20000, data: {task_id: ...}}
        if (
          response.data.code === 20000 &&
          response.data.data &&
          response.data.data.task_id
        ) {
          return {
            data: response.data.data,
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            config: response.config,
          };
        }

        // 情况2: 直接返回 {task_id: ...}
        if (response.data.task_id) {
          return {
            data: { task_id: response.data.task_id },
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            config: response.config,
          };
        }
      }

      // 如果格式不符合预期但有错误信息，抛出具体错误
      if (response.data && response.data.message) {
        throw new Error(response.data.message);
      }

      // 默认错误信息 - 包含更多信息
      throw new Error(`API返回格式不正确: ${JSON.stringify(response.data)}`);
    })
    .catch((error) => {
      throw error;
    });
}

export interface TaskItem {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at: string | null;
  evil_video_count: number;
  all_video_count: number;
}

// 获取任务列表 - 合并两个重复的函数
// 获取任务列表
export function getTaskList() {
  return axios
    .get<{ code: number; data: { tasks: TaskItem[] }; message: string }>(
      '/api/detect/task_list'
    )
    .then((response) => {
      // 增强错误处理和数据格式兼容性
      if (response.data) {
        // 检查是否有标准格式的响应 {code: 20000, data: {tasks: [...]}}
        if (
          response.data.code === 20000 &&
          response.data.data &&
          Array.isArray(response.data.data.tasks)
        ) {
          return {
            data: response.data.data,
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            config: response.config,
          };
        }

        // 检查是否直接返回了任务数组 [{task_id: ..., status: ...}, ...]
        if (Array.isArray(response.data)) {
          return {
            data: { tasks: response.data },
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            config: response.config,
          };
        }

        // 检查是否有另一种格式 {tasks: [...]}
        if (response.data.tasks && Array.isArray(response.data.tasks)) {
          return {
            data: { tasks: response.data.tasks },
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            config: response.config,
          };
        }

        console.error('任务列表响应格式不符合预期:', response.data);
      }

      // 如果没有匹配任何已知格式，返回空数组避免前端报错
      return {
        data: { tasks: [] },
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        config: response.config,
      };
    });
}

// 获取任务详情
export interface TaskDetail {
  task_id: string;
  vd_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  evil_video_ids: string[];
}

// 获取任务检测报告
export interface TaskReport {
  task_info: {
    task_id: string;
    status: string;
    created_at: string;
    completed_at: string | null;
    evil_video_ids: string[];
  };
  summary: {
    total_videos: number;
    evil_videos: number;
    normal_videos: number;
  };
  evil_video_ids: string[];
}

// 获取任务检测报告
export function getTaskReport(taskId: string) {
  // 修改类型定义，匹配后端返回的格式
  return axios
    .get<{ code: number; data: any; message: string }>(
      `/api/detect/get_task_result/${taskId}`
    )
    .then((response) => {
      // 检查响应格式
      if (response.data && response.data.code === 20000 && response.data.data) {
        // 适配后端返回的数据格式
        const { data } = response.data;

        // 构建前端期望的格式
        const taskReport: TaskReport = {
          task_info: {
            task_id: data.task_info.task_id,
            status: data.task_info.status,
            created_at: data.task_info.created_at,
            completed_at: data.task_info.completed_at,
            evil_video_ids: data.evil_video_ids || [],
          },
          summary: {
            total_videos: data.summary.total_videos,
            evil_videos: data.summary.evil_videos,
            normal_videos: data.summary.normal_videos,
          },
          evil_video_ids: data.evil_video_ids || [],
        };

        return {
          data: taskReport,
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
          config: response.config,
        };
      }

      // 如果格式不符合预期，抛出错误
      throw new Error(
        `任务报告API返回格式不正确: ${JSON.stringify(response.data)}`
      );
    })
    .catch((error) => {
      // 针对404错误提供更友好的错误信息
      if (error.response) {
        if (error.response.status === 404) {
          throw new Error(
            `任务报告不存在，任务ID: ${taskId} 可能尚未完成或不存在`
          );
        }

        // 针对400错误提供更友好的错误信息
        if (error.response.status === 400) {
          const message = error.response.data?.message || '任务尚未完成';
          throw new Error(message);
        }
      } else if (error.request) {
        throw new Error('服务器未响应，请检查网络连接或服务器状态');
      }

      throw error;
    });
}

// 获取任务详情
// 获取任务详情
export function getTaskDetail(taskId: string) {
  return axios
    .get<{ code: number; data: TaskDetail; message: string } | TaskDetail>(
      `/api/detect/get_task/${taskId}`
    )
    .then((response) => {
      // 检查响应格式 - 处理两种可能的格式
      // 情况1: {code: 20000, data: {...}}
      if (
        response.data &&
        typeof response.data === 'object' &&
        'code' in response.data &&
        response.data.code === 20000 &&
        'data' in response.data &&
        response.data.data
      ) {
        return {
          data: response.data.data,
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
          config: response.config,
        };
      }

      // 情况2: 直接返回数据对象 {task_id: ..., status: ..., ...}
      if (
        response.data &&
        typeof response.data === 'object' &&
        'task_id' in response.data &&
        'status' in response.data
      ) {
        return {
          data: response.data as TaskDetail,
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
          config: response.config,
        };
      }

      // 如果格式不符合预期，抛出错误
      throw new Error(
        `任务详情API返回格式不正确: ${JSON.stringify(response.data)}`
      );
    })
    .catch((error) => {
      // 针对404错误提供更友好的错误信息
      if (error.response) {
        if (error.response.status === 404) {
          throw new Error(`任务不存在，任务ID: ${taskId}`);
        }
      } else if (error.request) {
        throw new Error('服务器未响应，请检查网络连接或服务器状态');
      }

      throw error;
    });
}

// 获取指定轮次的视频详情
export interface RoundVideo {
  vd_id: string;
  vd_title: string;
  create_time: string;
  author: string;
  likes: string;
  shares: string;
  collects: string;
  img_url: string;
  tags: string[];
}

export interface RoundVideosResult {
  task_id: string;
  round: number;
  video_count: number;
  videos: RoundVideo[];
}

export function getRoundVideos(taskId: string, roundNum: number) {
  return axios.get<RoundVideosResult>(
    `/api/detect/get_round_videos/${taskId}/${roundNum}`
  );
}

// 获取所有轮次的视频详情
export interface AllRoundsResult {
  task_id: string;
  total_rounds: number;
  rounds: {
    round: number;
    video_count: number;
    videos: RoundVideo[];
  }[];
}

export function getAllRoundVideos(taskId: string) {
  return axios.get<AllRoundsResult>(
    `/api/detect/get_all_round_videos/${taskId}`
  );
}

export interface ContentDataRecord {
  x: string;
  y: number;
}

export function queryContentData() {
  return axios.get<ContentDataRecord[]>('/api/content-data');
}

export interface PopularRecord {
  key: number;
  clickNumber: string;
  title: string;
  increases: number;
}

export function queryPopularList(params: { type: string }) {
  return axios.get<TableData[]>('/api/popular/list', { params });
}
