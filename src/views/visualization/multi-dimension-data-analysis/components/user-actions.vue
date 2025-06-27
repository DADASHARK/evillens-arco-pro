<template>
  <a-card
    class="general-card"
    :title="$t('multiDAnalysis.card.title.userActions')"
  >
    <Chart height="400px" :option="chartOption" />
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  import useChartOption from '@/hooks/chart-option';
  import { queryGeographyDistribution } from '@/api/visualization';

  // 省份数据
  const provinceData = ref<{ province: string; percentage: number }[]>([]);
  let refreshTimer: number | null = null;

  // 获取地域分布数据
  const fetchGeographyData = async () => {
    try {
      const response = await queryGeographyDistribution();
      const { data } = response;
      // 判断数据是否为空数组或无效
      if (!Array.isArray(data) || data.length === 0) {
        throw new Error('后端返回数据为空'); // 手动触发 catch
      }
      // 处理数据
      const processedData = data.map((item: any) => {
        let percentage = 0;
        if (typeof item.percentage === 'string') {
          percentage = parseFloat(item.percentage) || 0;
        } else if (typeof item.percentage === 'number') {
          percentage = item.percentage;
        }
        return {
          province: item.province.trim(),
          percentage,
        };
      });

      // 按百分比排序并获取前三名
      provinceData.value = processedData
        .sort(
          (a: { percentage: number }, b: { percentage: number }) =>
            b.percentage - a.percentage
        )
        .slice(0, 10);

      console.log('前十省份数据已更新:', provinceData.value);
    } catch (err) {
      console.error('获取地域分布数据失败:', err);
      // 使用模拟数据作为后备
      provinceData.value = [
        { province: '广东省', percentage: 0.12 },
        { province: '江苏省', percentage: 0.1 },
        { province: '浙江省', percentage: 0.085 },
        { province: '山东省', percentage: 0.08 },
        { province: '河南省', percentage: 0.075 },
        { province: '四川省', percentage: 0.07 },
        { province: '上海市', percentage: 0.06 },
        { province: '北京市', percentage: 0.055 },
        { province: '湖北省', percentage: 0.05 },
        { province: '湖南省', percentage: 0.045 },
      ];
    }
  };

  // 组件挂载时获取数据
  onMounted(async () => {
    await fetchGeographyData();
    // 设置定时器，每5分钟刷新一次数据
    refreshTimer = window.setInterval(fetchGeographyData, 5 * 60 * 1000);
  });

  // 组件卸载时清除定时器
  onUnmounted(() => {
    if (refreshTimer !== null) {
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
  });

  const { chartOption } = useChartOption((isDark) => {
    // 提取省份名称和百分比数据
    const provinces = provinceData.value.map((item) => {
      const province = item.province.trim();
      return province.length > 4 ? province.substring(0, 2) : province;
    });

    const percentages = provinceData.value.map((item) =>
      (item.percentage * 100).toFixed(2)
    );

    return {
      grid: {
        left: 44,
        right: 20,
        top: 0,
        bottom: 20,
      },
      xAxis: {
        type: 'value',
        axisLabel: {
          show: true,
          formatter(value: number) {
            return `${value}%`;
          },
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#484849' : '#E5E8EF',
          },
        },
        max: 15, // 设置最大值为20%
      },
      yAxis: {
        type: 'category',
        data: provinces.length
          ? provinces
          : ['暂无数据', '暂无数据', '暂无数据'],
        axisLabel: {
          show: true,
          color: '#4E5969',
          margin: 5,
        },
        axisTick: {
          show: true,
          length: 2,
          lineStyle: {
            color: '#A9AEB8',
          },
          alignWithLabel: true,
        },
        axisLine: {
          lineStyle: {
            color: isDark ? '#484849' : '#A9AEB8',
          },
        },
        inverse: true,
      },
      tooltip: {
        show: true,
        trigger: 'axis',
        formatter: '{b}: {c}%',
      },
      series: [
        {
          data: percentages.length ? percentages : [0, 0, 0],
          type: 'bar',
          barWidth: 10,
          barGap: '-100%',
          barCategoryGap: '10%',
          itemStyle: {
            color: '#0b7ff3',
            borderRadius: 0,
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{c}%',
            color: isDark ? '#ffffff' : '#333333',
          },
        },
      ],
    };
  });
</script>

<style scoped lang="less"></style>
