// import Mock from 'mockjs';

// import setupMock, {
//   successResponseWrap,
//   // failResponseWrap,
// } from '@/utils/setup-mock';

// setupMock({
//   setup() {
//     // 修改为返回固定的模拟数据
//     Mock.mock(new RegExp('/api/chat/list'), () => {
//       // 从 localStorage 获取任务数据，如果没有则返回空数组
//       const storedTasks = localStorage.getItem('detect-tasks');
//       let tasks = [];

//       if (storedTasks) {
//         tasks = JSON.parse(storedTasks);
//       }
//       // 移除了默认的模拟数据，初始状态下不显示任何任务

//       return successResponseWrap(tasks);
//     });

//     // 添加创建任务的模拟接口
//     Mock.mock(
//       new RegExp('/api/detect/create_detect_task'),
//       'post',
//       (options) => {
//         const body = JSON.parse(options.body);
//         const videoUrls = body.video_url.split(',');

//         // 使用固定的任务ID
//         const taskId = '44368c7c-4812-4c1a-bfe4-22c288d8eeb9';

//         return {
//           code: 20000,
//           data: {
//             task_id: taskId,
//             video_ids: videoUrls,
//           },
//           message: '任务创建成功',
//         };
//       }
//     );
//   },
// });
