<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card class="general-card" :header-style="{ paddingBottom: '14px' }">
      <template #title>
        {{ $t('dataAnalysis.contentPublishRatio') }}
      </template>
      <template #extra>
        <a-link>{{ $t('workplace.viewMore') }}</a-link>
      </template>
      <Chart style="width: 100%; height: 347px" :option="chartOption" />
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import useLoading from '@/hooks/loading';
  import { TrendsWeekly, TrendsWeeklyItem } from '@/api/visualization'; // 你定义的接口方法
  import useChartOption from '@/hooks/chart-option';

  const { loading, setLoading } = useLoading(true);
  const xAxis = ref<string[]>([]);
  const countData = ref<number[]>([]);

  const tooltipItemsHtmlString = (items: any[]) => {
    return items
      .map(
        (el) => `<div class="content-panel">
      <p>
        <span style="background-color: ${
          el.color
        }" class="tooltip-item-icon"></span>
        <span>${el.seriesName}</span>
      </p>
      <span class="tooltip-value">${Number(el.value).toLocaleString()}</span>
    </div>`
      )
      .join('');
  };

  const { chartOption } = useChartOption((isDark) => {
    return {
      grid: {
        left: '4%',
        right: 0,
        top: '20',
        bottom: '60',
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
          formatter(value: number) {
            return value.toString(); // 显示纯数字
          },
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
        formatter(params) {
          const [firstElement] = params;
          return `<div>
            <p class="tooltip-title">${firstElement.axisValueLabel}</p>
            ${tooltipItemsHtmlString(params)}
          </div>`;
        },
        className: 'echarts-tooltip-diy',
      },
      series: [
        {
          name: '内容数量',
          data: countData.value,
          type: 'bar',
          color: isDark ? '#01349F' : '#81E2FF',
          itemStyle: {
            borderRadius: 2,
          },
        },
      ],
    };
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const { data } = await TrendsWeekly();
      console.log('', data);
      // 提取数据
      xAxis.value = data.map((item: TrendsWeeklyItem) => item.date);
      countData.value = data.map((item: TrendsWeeklyItem) => item.count);
    } catch (err) {
      console.error('数据获取失败', err);
    } finally {
      setLoading(false);
    }
  };

  fetchData();
</script>

<style scoped lang="less"></style>
