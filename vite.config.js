import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

// 导入生产环境和开发环境的配置
import devConfig from './config/vite.config.dev';
import prodConfig from './config/vite.config.prod';

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd());

  // 基础配置
  const baseConfig = {
    // 确保 base 路径正确设置为仓库名称
    base: mode === 'production' ? '/evillens-arco-pro/' : '/',
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        'vue-i18n': 'vue-i18n/dist/vue-i18n.cjs.js',
      },
    },
    css: {
      preprocessorOptions: {
        less: {
          modifyVars: {
            hack: `true; @import (reference) "${resolve(
              'src/assets/style/breakpoint.less'
            )}";`,
          },
          javascriptEnabled: true,
        },
      },
    },
    // 处理外部模块
    build: {
      rollupOptions: {
        external: [
          '@/views/introduce/index.vue',
          '@/views/visualization/data-analysis/mock',
          '@/views/visualization/multi-dimension-data-analysis/mock',
          '@/views/user/info/mock',
          '@/views/user/setting/mock',
          '@/store',
        ],
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
  };

  // 根据命令选择配置
  if (command === 'serve') {
    // 开发环境配置
    return { ...baseConfig, ...devConfig };
  } else {
    // 生产环境配置
    return { ...baseConfig, ...prodConfig };
  }
});
