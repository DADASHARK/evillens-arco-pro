import { mergeConfig } from 'vite';
import baseConfig from './vite.config.base';
import configCompressPlugin from './plugin/compress';
import configVisualizerPlugin from './plugin/visualizer';
import configArcoResolverPlugin from './plugin/arcoResolver';
import configImageminPlugin from './plugin/imagemin';

export default mergeConfig(
  {
    mode: 'production',
    plugins: [
      configCompressPlugin('gzip'),
      configVisualizerPlugin(),
      configArcoResolverPlugin(),
      configImageminPlugin(),
    ],
    build: {
      rollupOptions: {
        external: [
          // 使用相对路径而不是别名路径
          '@/views/introduce/index.vue',
          '@/views/visualization/data-analysis/mock',
          '@/views/visualization/multi-dimension-data-analysis/mock',
          '@/views/user/info/mock',
          '@/views/user/setting/mock',
          '@/store',
        ],
        output: {
          manualChunks: {
            arco: ['@arco-design/web-vue'],
            chart: ['echarts', 'vue-echarts'],
            vue: ['vue', 'vue-router', 'pinia', '@vueuse/core', 'vue-i18n'],
          },
        },
        onwarn(warning, warn) {
          // 忽略特定的解析错误
          if (
            warning.code === 'PARSE_ERROR' &&
            warning.message.includes('App.vue')
          ) {
            return;
          }
          // 对其他警告使用默认处理
          warn(warning);
        },
      },
      chunkSizeWarningLimit: 2000,
    },
  },
  baseConfig
);
