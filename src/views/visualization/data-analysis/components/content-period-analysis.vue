<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card class="general-card" :header-style="{ paddingBottom: '16px' }">
      <template #title>
        {{ $t('dataAnalysis.contentPeriodAnalysis') }}
      </template>
      <Chart style="width: 100%; height: 370px" :option="chartOption" />
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import useLoading from '@/hooks/loading';
  import { TimeDistribution, TimeDistributionItem } from '@/api/visualization'; // 👈 请将路径替换为实际路径
  // import { TimeDistributionItem } from '@/types/your-types'; // 👈 替换为实际路径
  import useChartOption from '@/hooks/chart-option';

  // 初始化数据
  const xAxis = ref<string[]>([]); // 横坐标时间字符串 "00:00", "01:00" ...
  const countData = ref<number[]>([]); // 每小时 count

  // 自定义 loading hook
  const { loading, setLoading } = useLoading(true);

  // 构建图表配置
  const { chartOption } = useChartOption((isDark) => {
    return {
      grid: {
        left: '40',
        right: 0,
        top: '20',
        bottom: '100',
      },
      legend: {
        bottom: 0,
        icon: 'circle',
        textStyle: {
          color: '#4E5969',
        },
      },
      xAxis: {
        type: 'category',
        data: xAxis.value,
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: isDark ? '#3f3f3f' : '#A9AEB8',
          },
        },
        axisTick: {
          show: true,
          alignWithLabel: true,
          lineStyle: {
            color: '#86909C',
          },
        },
        axisLabel: {
          color: '#86909C',
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#86909C',
          formatter: '{value}', // 不加百分号
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#3F3F3F' : '#E5E6EB',
          },
        },
      },
      tooltip: {
        show: true,
        trigger: 'axis',
        formatter(params: any) {
          const [first] = params;
          return `
          <div>
            <p class="tooltip-title">${first.axisValueLabel}</p>
            <div class="content-panel">
              <p>
                <span style="background-color: ${first.color}" class="tooltip-item-icon"></span>
                <span>${first.seriesName}</span>
              </p>
              <span class="tooltip-value">${first.value}</span>
            </div>
          </div>`;
        },
        className: 'echarts-tooltip-diy',
      },
      series: [
        {
          name: '视频数量',
          data: countData.value,
          type: 'line',
          smooth: true,
          showSymbol: false,
          color: isDark ? '#6CAAF5' : '#81E2FF',
          symbol: 'circle',
          symbolSize: 10,
          emphasis: {
            focus: 'series',
            itemStyle: {
              borderWidth: 2,
              borderColor: '#D9F6FF',
            },
          },
        },
      ],
      dataZoom: [
        {
          bottom: 40,
          type: 'slider',
          left: 40,
          right: 14,
          height: 14,
          borderColor: 'transparent',
          handleIcon:
            'image://http://p3-armor.byteimg.com/tos-cn-i-49unhts6dw/1ee5a8c6142b2bcf47d2a9f084096447.svg~tplv-49unhts6dw-image.image',
          handleSize: '20',
          handleStyle: {
            shadowColor: 'rgba(0, 0, 0, 0.2)',
            shadowBlur: 4,
          },
          brushSelect: false,
          backgroundColor: isDark ? '#313132' : '#F2F3F5',
        },
        {
          type: 'inside',
          start: 0,
          end: 100,
          zoomOnMouseWheel: false,
        },
      ],
    };
  });

  // 拉取数据
  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await TimeDistribution();
      const list: TimeDistributionItem[] = res.data;
      xAxis.value = list.map(
        (item) => `${item.hour.toString().padStart(2, '0')}:00`
      );
      countData.value = list.map((item) => item.count);
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 页面加载时请求数据
  fetchData();
</script>

<style scoped lang="less">
  .chart-box {
    width: 100%;
    height: 230px;
  }

  .tooltip-item-icon {
    display: inline-block;
    width: 8px;
    height: 8px;
    margin-right: 4px;
    border-radius: 50%;
  }

  .tooltip-title {
    margin-bottom: 4px;
    font-weight: bold;
  }

  .tooltip-value {
    float: right;
  }
</style>
