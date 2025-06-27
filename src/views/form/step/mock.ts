import Mock from 'mockjs';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';

setupMock({
  setup() {
    // submit
    Mock.mock(new RegExp('/api/channel-form/submit'), () => {
      return successResponseWrap('ok');
    });

    // 添加获取报告统计数据的模拟接口
    Mock.mock(new RegExp('/api/report/stats'), () => {
      return successResponseWrap({
        status: 'success',
        reportUrl: '/src/assets/evidence_report.pdf',
        createdTime: new Date().toISOString(),
        downloadCount: 0,
      });
    });
  },
});
