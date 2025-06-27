<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card
      class="general-card"
      :title="$t('multiDAnalysis.card.title.dataOverview')"
    >
      <!-- 上标 -->
      <!-- <a-row justify="space-between">
        <a-col v-for="(item, idx) in renderData" :key="idx" :span="6">
          <a-statistic
            :title="item.title"
            :value="item.value"
            show-group-separator
            :value-from="0"
            animation
          >
            <template #prefix>
              <span
                class="statistic-prefix"
                :style="{ background: item.prefix.background }"
              >
                <component
                  :is="item.prefix.icon"
                  :style="{ color: item.prefix.iconColor }"
                />
              </span>
            </template>
          </a-statistic>
        </a-col>
      </a-row> -->
      <!-- 地图热力图 -->
      <Chart style="height: 500px; margin-top: 20px" :option="mapChartOption" />
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { computed, ref, onMounted, onUnmounted } from 'vue';
  import { useI18n } from 'vue-i18n';
  import * as echarts from 'echarts';
  import 'echarts-gl';
  import 'echarts-extension-amap';
  // 添加中国地图数据
  // import chinaJson from 'echarts/map/json/china.json';
  import useLoading from '@/hooks/loading';
  import useThemes from '@/hooks/themes';
  import useChartOption from '@/hooks/chart-option';
  import { queryGeographyDistribution } from '@/api/visualization';

  const { t } = useI18n();
  const { loading, setLoading } = useLoading(true);
  const { isDark } = useThemes();

  // 省份数据
  const provinceData = ref<{ province: string; percentage: number }[]>([]);
  // 获取地域分布数据
  let refreshTimer: number | null = null;
  const fetchGeographyData = async () => {
    setLoading(true);
    try {
      // 使用对象解构
      const response = await queryGeographyDistribution();
      // console.log('地域分布API响应1:', response);
      const { data } = response;
      // console.log('地域分布API响应2:', data);
      // 确保类型转换正确
      provinceData.value = data.map((item: any) => {
        // 使用if-else逻辑代替嵌套三元表达式
        let percentage = 0;
        if (typeof item.percentage === 'string') {
          percentage = parseFloat(item.percentage) || 0;
        } else if (typeof item.percentage === 'number') {
          percentage = item.percentage;
        }
        const province = item.province.trim();
        return {
          province,
          percentage,
        };
      });
      console.log('数据已刷新，时间:', new Date().toLocaleTimeString());
      // 调试输出（可选）
      // console.log('处理后的地域数据:', provinceData.value);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('获取地域分布数据失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 注册中国地图
  onMounted(async () => {
    try {
      const cached = localStorage.getItem('china-map');
      let chinaJson;
      if (cached) {
        chinaJson = JSON.parse(cached);
      } else {
        const response = await fetch(
          'https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json'
        );
        chinaJson = await response.json();
        localStorage.setItem('china-map', JSON.stringify(chinaJson));
      }

      // 添加调试信息，输出地图中的省份名称
      // console.log('中国地图数据加载成功:', chinaJson.features.length);

      // 提取并输出所有省份名称，添加类型注解
      // const provinceNames = chinaJson.features.map((feature: any) => {
      //   return feature.properties.name;
      // });
      // console.log('地图中的标准省份名称:', provinceNames);

      // 注册地图数据
      echarts.registerMap('china', chinaJson);

      // 获取数据
      await fetchGeographyData();
      // 设置定时器，每5分钟刷新一次数据
      refreshTimer = window.setInterval(fetchGeographyData, 5 * 60 * 1000);
      // console.log('API返回数据长度:', provinceData.value.length);

      // 如果API没有返回数据，使用模拟数据
      if (provinceData.value.length === 0) {
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
          { province: '河北省', percentage: 0.035 },
          { province: '安徽省', percentage: 0.035 },
          { province: '福建省', percentage: 0.03 },
          { province: '重庆市', percentage: 0.025 },
          { province: '江西省', percentage: 0.025 },
          { province: '广西壮族自治区', percentage: 0.02 },
          { province: '云南省', percentage: 0.02 },
          { province: '陕西省', percentage: 0.02 },
          { province: '山西省', percentage: 0.018 },
          { province: '贵州省', percentage: 0.015 },
          { province: '辽宁省', percentage: 0.015 },
          { province: '黑龙江省', percentage: 0.012 },
          { province: '内蒙古自治区', percentage: 0.01 },
          { province: '天津市', percentage: 0.01 },
          { province: '甘肃省', percentage: 0.008 },
          { province: '新疆维吾尔自治区', percentage: 0.007 },
          { province: '宁夏回族自治区', percentage: 0.006 },
          { province: '青海省', percentage: 0.005 },
          { province: '西藏自治区', percentage: 0.004 },
          { province: '吉林省', percentage: 0.008 },
          { province: '海南省', percentage: 0.007 },
          { province: '台湾省', percentage: 0.005 },
          { province: '香港特别行政区', percentage: 0.004 },
          { province: '澳门特别行政区', percentage: 0.003 },
        ];
        // console.log('使用模拟数据:', provinceData.value);
      }

      // 使用nextTick确保DOM更新后再触发resize
      setTimeout(() => {
        // 使用RAF确保在下一帧渲染时触发resize
        requestAnimationFrame(() => {
          window.dispatchEvent(new Event('resize'));
        });
      }, 500); // 增加延迟时间，确保图表完全渲染
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('加载中国地图数据失败:', error);
      // 注册一个空地图作为后备
      echarts.registerMap('china', {
        type: 'FeatureCollection',
        features: [],
      });
      // 获取数据
      fetchGeographyData();
    }
  });
  onUnmounted(() => {
    if (refreshTimer !== null) {
      clearInterval(refreshTimer);
      refreshTimer = null;
      console.log('已清除数据刷新定时器');
    }
  });
  // 地图上面一行内容
  // 统计数据 - 使用computed确保响应式
  // const renderData = computed(() => [
  //   {
  //     title: t('multiDAnalysis.dataOverview.contentProduction'),
  //     value: 1902,
  //     prefix: {
  //       icon: 'icon-edit',
  //       background: isDark.value ? '#593E2F' : '#FFE4BA',
  //       iconColor: isDark.value ? '#F29A43' : '#F77234',
  //     },
  //   },
  //   {
  //     title: t('multiDAnalysis.dataOverview.contentClick'),
  //     value: 2445,
  //     prefix: {
  //       icon: 'icon-thumb-up',
  //       background: isDark.value ? '#3D5A62' : '#E8FFFB',
  //       iconColor: isDark.value ? '#6ED1CE' : '#33D1C9',
  //     },
  //   },
  //   {
  //     title: t('multiDAnalysis.dataOverview.contentExposure'),
  //     value: 3034,
  //     prefix: {
  //       icon: 'icon-heart',
  //       background: isDark.value ? '#354276' : '#E8F3FF',
  //       iconColor: isDark.value ? '#4A7FF7' : '#165DFF',
  //     },
  //   },
  //   {
  //     title: t('multiDAnalysis.dataOverview.activeUsers'),
  //     value: 1275,
  //     prefix: {
  //       icon: 'icon-user',
  //       background: isDark.value ? '#3F385E' : '#F5E8FF',
  //       iconColor: isDark.value ? '#8558D3' : '#722ED1',
  //     },
  //   },
  // ]);
  // 地图配置
  const { chartOption: mapChartOption } = useChartOption((dark) => {
    // 转换数据格式为 ECharts 需要的格式
    const mapData = provinceData.value.map((item) => {
      // 确保数值有效
      let percentage = 0;
      if (typeof item.percentage === 'number') {
        percentage = item.percentage;
      } else if (typeof item.percentage === 'string') {
        percentage = parseFloat(item.percentage) || 0; // 使用 || 0 防止 NaN
      }

      // 调试输出
      // console.log(
      //   `省份: ${item.province}, 原始百分比: ${item.percentage}, 转换后: ${percentage}`
      // );

      const value = percentage * 100;
      const formattedValue = Number.isNaN(value)
        ? 0
        : parseFloat(value.toFixed(2));
      return {
        name: item.province, // 使用原始省份名称
        value: formattedValue, // 转为百分比数值
      };
    });
    console.log('所有地图数据:', JSON.stringify(mapData, null, 2));

    // 创建省份到值的映射，用于tooltip
    // 添加索引签名解决TypeScript错误
    const provinceValueMap: { [key: string]: number } = {};
    mapData.forEach((item) => {
      provinceValueMap[item.name] = item.value;
    });
    // 添加调试输出，查看映射中的值
    console.log('省份值映射详情:', provinceValueMap);
    // 输出几个具体省份的值进行验证
    // console.log('广东省值:', provinceValueMap['广东省']);
    // console.log('广西壮族自治区:', provinceValueMap['广西壮族自治区']);
    // console.log('北京市值:', provinceValueMap['北京市']);

    // console.log('省份值映射:', provinceValueMap);
    // console.log('处理后的地图数据:', mapData);

    // 计算合理的最大值
    const values = mapData.map((item) => {
      const val =
        typeof item.value === 'number'
          ? item.value
          : parseFloat(String(item.value)) || 0;
      return val;
    });
    const maxValue = values.length > 0 ? Math.max(...values) : 20;

    // eslint-disable-next-line no-console
    console.log('最大值:', maxValue);

    return {
      title: {
        text: '邪典视频地域分布热力图',
        // 改标题的大小

        left: 'center',
        textStyle: {
          fontSize: 16,
          color: dark ? '#fff' : '#333',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          // 获取省份名称
          const name = params.name || '';
          let value = 0;

          // 调试输出
          // console.log('完整的params对象:', params);
          // console.log('地图数据:', mapData);

          // 从映射中获取值
          if (provinceValueMap[name] !== undefined) {
            // 优先从映射中获取
            value = provinceValueMap[name];
          } else if (
            params.value !== undefined &&
            !Number.isNaN(params.value)
          ) {
            // 如果映射中没有，再从params中获取
            value = params.value;
          }

          return `${name}<br/>占比: ${
            Number.isNaN(value) ? '0.00' : value.toFixed(2)
          }%`;
        },
      },
      visualMap: {
        min: 0,
        max: 9, // 使用计算出的最大值
        left: 'left',
        top: 'bottom',
        text: ['高', '低'],
        calculable: true,
        realtime: true, // 实时更新
        splitNumber: 5, // 指定分割段数
        inRange: {
          color: [
            '#e6f7ff', // 最浅的蓝色
            '#bae7ff',
            '#91d5ff',
            '#69c0ff',
            '#40a9ff',
            '#1890ff',
            '#096dd9',
            '#0050b3', // 最深的蓝色
          ],
        },
        textStyle: {
          color: dark ? '#fff' : '#333',
        },
        // 新增formatter属性
        formatter: (value: number) => `${value}%`,
      },
      series: [
        {
          name: '邪典视频分布',
          type: 'map',
          map: 'china',
          roam: true,
          zoom: 1.2,
          scaleLimit: {
            min: 1,
            max: 3,
          },
          emphasis: {
            label: {
              show: true,
            },
            itemStyle: {
              areaColor: '#0066ff', // 鼠标悬停区域颜色
              shadowBlur: 10,
              shadowColor: 'rgba(0, 102, 255, 0.5)',
            },
          },
          itemStyle: {
            borderColor: dark ? '#fff' : '#242526', // 省份边界颜色
            borderWidth: 0.4, // 省份边界宽度
          },
          data: mapData,
          // 启用nameMap，确保省份名称匹配
          // nameMap: {
          //   广东省: '广东',
          //   浙江省: '浙江',
          //   江苏省: '江苏',
          //   上海市: '上海',
          //   北京市: '北京',
          //   四川省: '四川',
          //   湖北省: '湖北',
          //   湖南省: '湖南',
          //   河南省: '河南',
          //   河北省: '河北',
          //   山东省: '山东',
          //   安徽省: '安徽',
          //   福建省: '福建',
          //   江西省: '江西',
          //   广西壮族自治区: '广西',
          //   海南省: '海南',
          //   重庆市: '重庆',
          //   贵州省: '贵州',
          //   云南省: '云南',
          //   西藏自治区: '西藏',
          //   陕西省: '陕西',
          //   甘肃省: '甘肃',
          //   青海省: '青海',
          //   宁夏回族自治区: '宁夏',
          //   新疆维吾尔自治区: '新疆',
          //   内蒙古自治区: '内蒙古',
          //   辽宁省: '辽宁',
          //   吉林省: '吉林',
          //   黑龙江省: '黑龙江',
          //   台湾省: '台湾',
          //   香港特别行政区: '香港',
          //   澳门特别行政区: '澳门',
          // },
        },
      ],
    };
  });
  // 获取数据
  // fetchGeographyData();
</script>

<style scoped lang="less">
  :deep(.arco-statistic) {
    .arco-statistic-title {
      color: rgb(var(--gray-10));
      font-weight: bold;
    }

    .arco-statistic-value {
      display: flex;
      align-items: center;
    }
  }

  .statistic-prefix {
    display: inline-block;
    width: 32px;
    height: 32px;
    margin-right: 8px;
    color: var(--color-white);
    font-size: 16px;
    line-height: 32px;
    text-align: center;
    vertical-align: middle;
    border-radius: 6px;
  }
</style>
