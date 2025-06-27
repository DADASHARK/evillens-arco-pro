<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card class="general-card" :header-style="{ paddingBottom: '14px' }">
      <template #title>
        {{ $t('dataAnalysis.popularAuthor') }}
      </template>
      <template #extra>
        <a-link>{{ $t('workplace.viewMore') }}</a-link>
      </template>
      <div ref="chartRef" class="wordcloud-container"></div>
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, onMounted, onBeforeUnmount } from 'vue';
  import useLoading from '@/hooks/loading';
  import { getKeywords, KeywordItem } from '@/api/visualization';
  import * as echarts from 'echarts';  // 修改为导入完整的echarts
  import 'echarts-wordcloud';

  const { loading, setLoading } = useLoading();
  const chartRef = ref<HTMLElement | null>(null);
  let chart: echarts.ECharts | null = null;

  // 解码Unicode编码的字符串
  function decodeUnicode(str: string) {
    try {
      // 如果已经是正常显示的中文，则直接返回
      if (/[\u4e00-\u9fa5]/.test(str)) {
        return str;
      }
      // 尝试解码Unicode
      return JSON.parse(`"${str}"`);
    } catch (e) {
      // 如果解码失败，返回原字符串
      return str;
    }
  }

  // 处理窗口大小变化
  const handleResize = () => {
    if (chart) {
      chart.resize();
    }
  };

  // 渲染词云图
  const renderWordCloud = (keywords: KeywordItem[]) => {
    if (!chartRef.value) {
      console.error('图表容器不存在');
      return;
    }
    
    // 确保有数据
    if (!keywords || keywords.length === 0) {
      console.error('关键词数据为空');
      return;
    }

    console.log('开始渲染词云图，关键词数量:', keywords.length);

    // 初始化图表
    if (!chart) {
      console.log('初始化echarts实例');
      chart = echarts.init(chartRef.value);
    }

    // 处理数据，转换为词云图所需格式
    const data = keywords.map((item) => {
      const decodedKeyword = decodeUnicode(item.keyword);
      return {
        name: decodedKeyword,
        value: item.frequency,
      };
    });
    
    // 按频率排序并只取前50个
    const top70Data = data.sort((a, b) => b.value - a.value).slice(0, 100);
    console.log('排序后前70个关键词:', top70Data);
  
    // 配置词云图选项
    const option = {
      tooltip: {
        show: true,
        formatter(params: any) {
          return `${params.name}: ${params.value}`;
        },
      },
      series: [
        {
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '70%',  // 减小宽度，确保不超出容器
          height: '70%', // 减小高度，确保不超出容器
          right: null,
          bottom: null,
          sizeRange: [12, 40], // 减小最大字体大小
          rotationRange: [-30, 30], // 减小旋转角度范围
          rotationStep: 15,
          gridSize: 10, // 增加网格大小，使词语之间间隔更大
          drawOutOfBound: false, // 确保不绘制超出边界的词
          layoutAnimation: true,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            color() {
              return `rgb(${[
                Math.round(Math.random() * 160 + 50),
                Math.round(Math.random() * 160 + 50),
                Math.round(Math.random() * 160 + 50),
              ].join(',')})`;
            },
          },
          emphasis: {
            textStyle: {
              shadowBlur: 10,
              shadowColor: '#333',
            },
          },
          data: top70Data,
        },
      ],
    };

    // 设置图表选项并渲染
    console.log('设置echarts选项');
    try {
      chart.setOption(option);
      console.log('词云图渲染完成');
    } catch (error) {
      console.error('词云图渲染失败:', error);
    }
  };

  // 获取关键词数据并渲染词云图
  const fetchData = async () => {
    try {
      setLoading(true);
      console.log('开始获取关键词数据');
      const response = await getKeywords();
      
      if (response && response.code === 20000 && Array.isArray(response.data)) {
        console.log('获取到的关键词数据:', response.data);
        renderWordCloud(response.data);
      } else if (response.data && response.data.code === 20000 && Array.isArray(response.data.data)) {
        console.log('获取到的关键词数据:', response.data.data);
        renderWordCloud(response.data.data);
      } else {
        console.error('关键词数据格式不正确:', response);
      }
    } catch (err) {
      console.error('获取关键词数据出错', err);
    } finally {
      setLoading(false);
    }
  };

  onMounted(() => {
    console.log('组件挂载完成');
    
    // 确保容器有正确的尺寸
    setTimeout(() => {
      if (chartRef.value) {
        console.log(
          '图表容器尺寸:',
          chartRef.value.offsetWidth,
          chartRef.value.offsetHeight
        );
        
        // 检查echarts版本
        console.log('echarts版本:', echarts.version);
        
        // 尝试手动注册wordCloud组件
        if (typeof echarts.registerMap === 'function') {
          try {
            // 确保wordCloud组件已注册
            if (!echarts.getMap || !echarts.getMap('wordCloud')) {
              console.log('尝试手动注册wordCloud组件');
              // 这里不需要实际注册，因为echarts-wordcloud会自动注册
            }
          } catch (e) {
            console.error('注册wordCloud组件失败:', e);
          }
        }
      } else {
        console.error('图表容器不存在');
      }
      
      fetchData();
    }, 500); // 延迟500ms确保DOM已完全渲染
    
    window.addEventListener('resize', handleResize);
  });

  onBeforeUnmount(() => {
    if (chart) {
      chart.dispose();
      chart = null;
    }
    window.removeEventListener('resize', handleResize);
  });
</script>

<style scoped lang="less">
  .general-card {
    display: flex;
    flex-direction: column;
    max-height: 425px;
  }

  .wordcloud-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 350px;
  }
</style>