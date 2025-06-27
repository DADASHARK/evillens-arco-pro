import axios from 'axios';

export interface MessageRecord {
  id: number;
  type: string;
  title: string;
  subTitle: string;
  avatar?: string;
  content: string;
  time: string;
  status: 0 | 1;
  messageType?: number;
}
export type MessageListType = MessageRecord[];

export function queryMessageList() {
  return axios.post<MessageListType>('/api/message/list');
}

interface MessageStatus {
  ids: number[];
}

export function setMessageStatus(data: MessageStatus) {
  return axios.post<MessageListType>('/api/message/read', data);
}

// 在 ChatRecord 接口中添加 status 属性
export interface ChatRecord {
  id: number;
  username: string;
  content: string;
  time: string;
  isCollect: boolean;
  status?: 'detecting' | 'completed'; // 添加状态属性
}

export function queryChatList() {
  return axios.post<ChatRecord[]>('/api/chat/list');
}
