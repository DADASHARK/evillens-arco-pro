// import Mock from 'mockjs';
// import qs from 'query-string';
// import setupMock, { successResponseWrap } from '@/utils/setup-mock';
// import { GetParams } from '@/types/global';

// const { Random } = Mock;

// // CSV 数据转换为 mock 数据
// const videoData = [
//   {
//     id: '7462304269652282681',
//     number: '7462304269',
//     name: '爱莎公主儿童益智早教动画片',
//     author: '张三', // 修改
//     engagement: 123.5, // 修改
//     count: 167,
//     status: false, // online -> false
//     createdTime: '2025-01-21 17:52:09',
//   },
//   {
//     id: '7490071193530289447',
//     number: '7490071193',
//     name: '原创视频搞笑动画',
//     author: '李四',
//     engagement: 88.2,
//     count: 2522,
//     status: false,
//     createdTime: '2025-04-06 13:42:07',
//   },
//   {
//     id: '7479999480595631371',
//     number: '7479999480',
//     name: '益智动画卡通动漫',
//     author: '王五',
//     engagement: 99.9,
//     count: 1524,
//     status: false,
//     createdTime: '2025-03-10 10:18:44',
//   },
//   {
//     id: '7490381420196597028',
//     number: '7490381420',
//     name: '原创视频创作者扶持计划',
//     author: '赵六',
//     engagement: 12.3,
//     count: 42,
//     status: true, // offline -> true
//     createdTime: '2025-04-07 09:45:54',
//   },
// ];

// // 使用真实数据替代 mock 数据
// const data = {
//   list: videoData
// };

// setupMock({
//   setup() {
//     Mock.mock(new RegExp('/api/list/policy'), (params: GetParams) => {
//       const { current = 1, pageSize = 10, number, name, contentType, filterType, status } = qs.parseUrl(params.url).query;

//       // 筛选逻辑
//       let filteredList = [...data.list];

//       // 按视频ID完全匹配筛选
//       if (number) {
//         filteredList = filteredList.filter(item => item.number === number);
//       }

//       // 按关键词包含筛选
//       if (name) {
//         filteredList = filteredList.filter(item =>
//           item.name.toLowerCase().includes(String(name).toLowerCase())
//         );
//       }

//       // 按内容分类筛选
//       // if (contentType) {
//       //   filteredList = filteredList.filter(item => item.contentType === contentType);
//       // }

//       // // 按筛选方式筛选
//       // if (filterType) {
//       //   filteredList = filteredList.filter(item => item.filterType === filterType);
//       // }

//       // // 按状态筛选
//       // if (status) {
//       //   filteredList = filteredList.filter(item => item.status === status);
//       // }

//       const p = Number(current);
//       const ps = Number(pageSize);

//       return successResponseWrap({
//         list: filteredList.slice((p - 1) * ps, p * ps),
//         total: filteredList.length,
//       });
//     });
//   },
// });
