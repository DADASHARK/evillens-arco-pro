<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card
      class="general-card"
      :header-style="{ paddingBottom: 0 }"
      :body-style="{ paddingTop: '20px' }"
      :title="$t('workplace.contentData')"
    >
      <a-carousel
        indicator-type="slider"
        show-arrow="hover"
        auto-play
        class="full-width-carousel"
      >
        <a-carousel-item v-for="video in localVideos" :key="video.id">
          <div class="carousel-video-item">
            <img
              :src="video.coverimgUrl"
              class="carousel-video-cover"
              @click="openVideo(video)"
            />
            <div class="carousel-info-overlay">
              <div class="carousel-title">
                {{ $t('workplace.contentTitle') }} {{ video.mainTitle }}
              </div>
              <div class="carousel-tags">
                {{ $t('workplace.contentTag') }}{{ video.tags.join(' ') }}
              </div>
            </div>
          </div>
        </a-carousel-item>
      </a-carousel>

      <!-- 添加视频播放模态框 -->
      <a-modal
        v-model:visible="showPlayer"
        :footer="false"
        width="720px"
        :closable="true"
        @cancel="closeVideo"
      >
        <template #title>
          {{ currentVideo?.mainTitle || '视频播放' }}
        </template>
        <video
          v-if="currentVideo"
          :src="currentVideo.videoUrl"
          controls
          autoplay
          style="width: 100%; height: 400px; background: #000"
        ></video>
      </a-modal>
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  // import { graphic } from 'echarts';
  // import { queryEvilVideos, EvilVideo} from '@/api/dashboard';
  import useLoading from '@/hooks/loading';
  import cover1 from '@/assets/images/cover1.png';
  import cover2 from '@/assets/images/cover2.png';
  import cover3 from '@/assets/images/cover3.png';
  import xiedian1 from '@/assets/images/xiedian1.mp4';
  import xiedian2 from '@/assets/images/xiedian2.mp4';
  import xiedian3 from '@/assets/images/xiedian3.mp4';
  import useChartOption from '@/hooks/chart-option';
  // import { computed } from 'vue';
  import useThemes from '@/hooks/themes';

  const { isDark } = useThemes();

  // import { queryContentData, ContentDataRecord } from '@/api/dashboard';

  // import useChartOption from '@/hooks/chart-option';
  // import { ToolTipFormatterParams } from '@/types/echarts';
  // import { AnyObject } from '@/types/global';

  // function graphicFactory(side: AnyObject) {
  //   return {
  //     type: 'text',
  //     bottom: '8',
  //     ...side,
  //     style: {
  //       text: '',
  //       textAlign: 'center',
  //       fill: '#4E5969',
  //       fontSize: 12,
  //     },
  //   };
  // }
  // interface EnhancedEvilVideo extends EvilVideo {
  //   mainTitle: string;
  //   tags: string[];
  // }
  interface LocalVideo {
    id: string;
    coverimgUrl: string;
    mainTitle: string;
    tags: string[];
    videoUrl: string;
  }
  const { loading, setLoading } = useLoading(true);
  // 新增的邪典视频展示部分
  // const videos = ref<EnhancedEvilVideo[]>([]);
  const router = useRouter();
  const localVideos = ref<LocalVideo[]>([
    {
      id: '7467058417874652473',
      coverimgUrl: cover2,
      mainTitle: '狗狗的进化',
      tags: ['#儿童动画', '#儿童乐园', '#蹦蹦跳跳没烦恼'],
      videoUrl: xiedian2,
    },
    {
      id: '7469771473175989545',
      coverimgUrl: cover1,
      mainTitle: '帮助乔治抓住冒牌货',
      tags: ['#野猪佩奇'],
      videoUrl: xiedian1,
    },

    {
      id: '7494220065760382242',
      coverimgUrl: cover3,
      mainTitle: '🐱💥💣调皮小猫玩炸弹变异成巨型怪兽啦！快救小猫！🚨🙀',
      tags: ['#猫咪', '#萌宠出道计划', '#猫猫', '#神奇动物在抖音', '#ai绘画'],
      videoUrl: xiedian3,
    },
  ]);

  //   const fetchData = async () => {
  //   // console.log('fetchData start');
  //   setLoading(true);
  //   try {
  //     const { data } = await queryEvilVideos();
  //     videos.value = data.map((item: EvilVideo) => {
  //       // 拆分 title
  //       const parts = item.title.split('#');
  //       const mainTitle = parts[0].trim() || '无';
  //       const tags = parts.slice(1).map(tag => tag.trim()).filter(Boolean);
  //       return {
  //         ...item,
  //         mainTitle,
  //         tags,
  //       };
  //     });
  //     console.log('videos.value:', videos.value);
  //   } catch (err) {
  //     console.error('请求出错', err);
  //   } finally {
  //     setLoading(false);
  //     // console.log('fetchData end');
  //   }
  // };
  // fetchData();
  const showPlayer = ref(false);
  const currentVideo = ref<LocalVideo | null>(null);

  function openVideo(video: LocalVideo) {
    currentVideo.value = video;
    showPlayer.value = true;
  }
  function closeVideo() {
    showPlayer.value = false;
    currentVideo.value = null;
  }
  // function goDetail(videoId: string) {
  //   router.push({ name: 'VideoDetail', params: { id: videoId } });
  // }

  onMounted(() => {
    // 模拟加载过程
    setTimeout(() => {
      setLoading(false);
    }, 500);
  });
  // const xAxis = ref<string[]>([]);
  // const chartsData = ref<number[]>([]);
  // const graphicElements = ref([
  //   graphicFactory({ left: '2.6%' }),
  //   graphicFactory({ right: 0 }),
  // ]);
  // const { chartOption } = useChartOption(() => {
  //   return {
  //     grid: {
  //       left: '2.6%',
  //       right: '0',
  //       top: '10',
  //       bottom: '30',
  //     },
  //     xAxis: {
  //       type: 'category',
  //       offset: 2,
  //       data: xAxis.value,
  //       boundaryGap: false,
  //       axisLabel: {
  //         color: '#4E5969',
  //         formatter(value: number, idx: number) {
  //           if (idx === 0) return '';
  //           if (idx === xAxis.value.length - 1) return '';
  //           return `${value}`;
  //         },
  //       },
  //       axisLine: {
  //         show: false,
  //       },
  //       axisTick: {
  //         show: false,
  //       },
  //       splitLine: {
  //         show: true,
  //         interval: (idx: number) => {
  //           if (idx === 0) return false;
  //           if (idx === xAxis.value.length - 1) return false;
  //           return true;
  //         },
  //         lineStyle: {
  //           color: '#E5E8EF',
  //         },
  //       },
  //       axisPointer: {
  //         show: true,
  //         lineStyle: {
  //           color: '#23ADFF',
  //           width: 2,
  //         },
  //       },
  //     },
  //     yAxis: {
  //       type: 'value',
  //       axisLine: {
  //         show: false,
  //       },
  //       axisLabel: {
  //         formatter(value: any, idx: number) {
  //           if (idx === 0) return value;
  //           return `${value}k`;
  //         },
  //       },
  //       splitLine: {
  //         show: true,
  //         lineStyle: {
  //           type: 'dashed',
  //           color: '#E5E8EF',
  //         },
  //       },
  //     },
  //     tooltip: {
  //       trigger: 'axis',
  //       formatter(params) {
  //         const [firstElement] = params as ToolTipFormatterParams[];
  //         return `<div>
  //           <p class="tooltip-title">${firstElement.axisValueLabel}</p>
  //           <div class="content-panel"><span>总内容量</span><span class="tooltip-value">${(
  //             Number(firstElement.value) * 10000
  //           ).toLocaleString()}</span></div>
  //         </div>`;
  //       },
  //       className: 'echarts-tooltip-diy',
  //     },
  //     graphic: {
  //       elements: graphicElements.value,
  //     },
  //     series: [
  //       {
  //         data: chartsData.value,
  //         type: 'line',
  //         smooth: true,
  //         // symbol: 'circle',
  //         symbolSize: 12,
  //         emphasis: {
  //           focus: 'series',
  //           itemStyle: {
  //             borderWidth: 2,
  //           },
  //         },
  //         lineStyle: {
  //           width: 3,
  //           color: new graphic.LinearGradient(0, 0, 1, 0, [
  //             {
  //               offset: 0,
  //               color: 'rgba(30, 231, 255, 1)',
  //             },
  //             {
  //               offset: 0.5,
  //               color: 'rgba(36, 154, 255, 1)',
  //             },
  //             {
  //               offset: 1,
  //               color: 'rgba(111, 66, 251, 1)',
  //             },
  //           ]),
  //         },
  //         showSymbol: false,
  //         areaStyle: {
  //           opacity: 0.8,
  //           color: new graphic.LinearGradient(0, 0, 0, 1, [
  //             {
  //               offset: 0,
  //               color: 'rgba(17, 126, 255, 0.16)',
  //             },
  //             {
  //               offset: 1,
  //               color: 'rgba(17, 128, 255, 0)',
  //             },
  //           ]),
  //         },
  //       },
  //     ],
  //   };
  // });
  // const fetchData = async () => {
  //   setLoading(true);
  //   try {
  //     const { data: chartData } = await queryContentData();
  //     chartData.forEach((el: ContentDataRecord, idx: number) => {
  //       xAxis.value.push(el.x);
  //       chartsData.value.push(el.y);
  //       if (idx === 0) {
  //         graphicElements.value[0].style.text = el.x;
  //       }
  //       if (idx === chartData.length - 1) {
  //         graphicElements.value[1].style.text = el.x;
  //       }
  //     });
  //   } catch (err) {
  //     // you can report use errorHandler or other
  //   } finally {
  //     setLoading(false);
  //   }
  // };
  // fetchData();
</script>
<!-- <style scoped lang="less"></style> -->
<style scoped lang="less">
  // 添加深蓝色背景样式
  .general-card {
    background-color: rgb(10 25 47 / 85%) !important;

    // 修改标题样式：左对齐
    :deep(.arco-card-header-title) {
      display: block;
      width: 100%;
      color: #64ffda;
      font-weight: bold;
      font-size: 20px;
      text-align: left; // 由 center 改为 left
    }

    :deep(.arco-card-body) {
      color: rgb(255 255 255 / 85%);
    }
  }

  // 添加全宽轮播图样式
  .full-width-carousel {
    width: 100% !important;
    overflow: hidden;
    border-radius: 4px;
    aspect-ratio: 16 / 6; // 新增，设置宽高比为16:9

    :deep(.arco-carousel-indicator) {
      margin-bottom: 16px;
    }

    :deep(.arco-carousel-arrow) {
      background-color: rgb(0 0 0 / 30%);

      &:hover {
        background-color: rgb(0 0 0 / 50%);
      }
    }
  }

  .carousel-video-item {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    cursor: pointer;
  }

  .carousel-video-cover {
    width: 100%;
    max-width: 100%;
    height: 100%;
    max-height: 100%;
    object-fit: cover;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 8%);
  }

  .carousel-info-overlay {
    position: absolute;
    bottom: 24px;
    left: 24px;
    z-index: 2;
    text-align: left;
  }

  .carousel-title {
    margin-bottom: 10px;
    color: #fff;
    font-weight: bold;
    font-size: 28px;
    font-family: 'Microsoft YaHei', '黑体', SimHei, Arial, sans-serif;
    text-align: left;
    text-shadow: 0 2px 8px rgb(0 0 0 / 40%);
  }

  .carousel-tags {
    color: #fff;
    font-weight: bold;
    font-size: 20px;
    font-family: 'Microsoft YaHei', '黑体', SimHei, Arial, sans-serif;
    text-align: left;
    text-shadow: 0 2px 8px rgb(0 0 0 / 40%);
  }

  .carousel-video-cover {
    width: auto;
    max-width: 90%;
    height: 480px;
    margin-bottom: 8px;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 8%);
  }

  // 其他样式保持不变
</style>
