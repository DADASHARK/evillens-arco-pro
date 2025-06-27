/// <reference types="vite/client" />
/// <reference types="vue/macros-global" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
}

// 添加 JSX 命名空间定义
declare namespace JSX {
  interface IntrinsicElements {
    [elem: string]: any;
  }
}
