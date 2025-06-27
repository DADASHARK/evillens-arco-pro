<template>
  <a-card
    class="general-card chat-panel"
    :title="t('monitor.title.chatPanel')"
    :bordered="false"
    :header-style="{ paddingBottom: '0' }"
    :body-style="{
      height: '100%',
      paddingTop: '16px',
      display: 'flex',
      flexFlow: 'column',
    }"
  >
    <!-- 添加自定义头部插槽，将下载按钮和删除按钮放在标题旁边 -->
    <template #extra>
      <a-space>
        <a-button type="text" size="small" @click="refreshTaskList">
          <template #icon><icon-refresh /></template>
        </a-button>
        <a-button type="text" size="small" @click="clearAllTasks">
          <template #icon><icon-delete /></template>
        </a-button>
      </a-space>
    </template>

    <a-spin :loading="loading" style="flex: 1; overflow: auto">
      <a-list :bordered="false" :max-height="400">
        <a-list-item
          v-for="task in taskList"
          :key="task.task_id"
          class="task-item"
          @click="handleTaskClick(task)"
        >
          <a-space direction="vertical" style="width: 100%">
            <a-space>
              <span class="task-id">{{ task.task_id }}</span>
              <a-tag :color="getStatusColor(task.status)">
                {{ getStatusText(task.status) }}
              </a-tag>
            </a-space>
            <a-space>
              <span class="task-time">{{ formatTime(task.created_at) }}</span>
              <span class="task-count">
                视频数量: {{ task.all_video_count }}
                <span v-if="task.evil_video_count > 0" class="evil-count">
                  (邪典: {{ task.evil_video_count }})
                </span>
              </span>
            </a-space>
          </a-space>
        </a-list-item>
        <a-empty v-if="taskList.length === 0" />
      </a-list>
    </a-spin>

    <task-detail
      v-model:visible="resultModalVisible"
      :task-id="currentTaskId"
    />
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted, onBeforeUnmount } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { useI18n } from 'vue-i18n';
  import useLoading from '@/hooks/loading';
  import { getTaskList, TaskItem } from '@/api/dashboard';
  import TaskDetail from './task-detail.vue';

  const { t } = useI18n();
  const { loading, setLoading } = useLoading(true);
  const taskList = ref<TaskItem[]>([]);
  const resultModalVisible = ref(false);
  const currentTaskId = ref('');
  const refreshInterval = ref<number | null>(null);
  const lastTaskListHash = ref(''); // 用于比较任务列表是否有变化

  // 定义事件
  const emit = defineEmits(['selectTask']);

  // 声明函数，解决循环引用问题
  let fetchTaskList: (force?: boolean) => Promise<void>;

  // 停止自动刷新
  const stopAutoRefresh = () => {
    if (refreshInterval.value) {
      window.clearInterval(refreshInterval.value);
      refreshInterval.value = null;
    }
  };

  // 重启自动刷新
  const restartAutoRefresh = (interval = 10000) => {
    stopAutoRefresh();
    refreshInterval.value = window.setInterval(() => {
      fetchTaskList();
    }, interval);
  };

  // 处理新建任务事件
  const handleDetectTaskCreated = (event: CustomEvent) => {
    const { taskId } = event.detail;
    
    if (!taskId) {
      return;
    }

    // 检查任务是否已存在于列表中
    const existingTask = taskList.value.find((task) => task.task_id === taskId);
    if (existingTask) {
      return;
    }
  
    // 添加一个临时任务到列表
    const newTask: TaskItem = {
      task_id: taskId,
      status: 'processing',
      created_at: new Date().toISOString(),
      completed_at: null,
      evil_video_count: 0,
      all_video_count: 0,
    };
  
    // 将新任务添加到列表开头
    taskList.value = [newTask, ...taskList.value];
    
    // 更新哈希值，防止后续刷新时被过滤掉
    lastTaskListHash.value = JSON.stringify(taskList.value);
  
    // 立即刷新一次，确保获取最新数据
    setTimeout(() => {
      fetchTaskList(true);
    }, 1000);
  
    // 修改轮询逻辑，确保能够捕获任务完成状态
    let pollCount = 0;
    const pollInterval = setInterval(() => {
      // 检查任务是否已完成或者是否还存在
      const updatedTask = taskList.value.find(
        (task) => task.task_id === taskId
      );
  
      if (!updatedTask) {
        // 如果任务不存在了，重新添加到列表中
        taskList.value = [newTask, ...taskList.value];
        return;
      }
      
      if (updatedTask.status === 'completed') {
        clearInterval(pollInterval);
        // 任务完成后，显示详情
        currentTaskId.value = taskId;
        resultModalVisible.value = true;
      } else {
        // 如果任务还在处理中，尝试刷新任务列表
        fetchTaskList(true).catch(() => {
          // 如果刷新失败，保持任务在列表中
        });
      }
  
      pollCount += 1;
      if (pollCount >= 24) {
        // 最多轮询24次（约2分钟）
        clearInterval(pollInterval);
      }
    }, 5000);
  };

  // 获取任务列表
  fetchTaskList = async (force = false) => {
    try {
      // 只在强制刷新或首次加载时显示加载状态
      if (force || taskList.value.length === 0) {
        setLoading(true);
      }
  
      const response = await getTaskList();
  
      // 增强错误处理
      if (!response.data || !response.data.tasks) {
        // 如果返回数据为空或格式不正确，但不影响现有任务显示
        setLoading(false);
        return;
      }
  
      // 按创建时间降序排序
      const serverTasks = response.data.tasks.sort(
        (a: TaskItem, b: TaskItem) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
  
      // 计算当前任务列表的哈希值，用于比较是否有变化
      const newTaskListHash = JSON.stringify(serverTasks);
  
      // 只有当任务列表有变化时才更新
      if (force || newTaskListHash !== lastTaskListHash.value) {
        // 修改这里：保留本地处理中的任务
        const localProcessingTasks = taskList.value.filter(
          (task) => task.status === 'processing'
        );
        
        // 检查本地处理中的任务是否在服务器返回的任务中
        const mergedTasks = [...serverTasks];
        
        // 将本地处理中的任务添加到合并列表中（如果服务器返回中不存在）
        localProcessingTasks.forEach((localTask) => {
          const existsInServer = serverTasks.some(
            (serverTask: TaskItem) => serverTask.task_id === localTask.task_id
          );
          
          if (!existsInServer) {
            mergedTasks.push(localTask);
          }
        });
        
        // 重新排序合并后的任务列表
        mergedTasks.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        
        taskList.value = mergedTasks;
        lastTaskListHash.value = newTaskListHash;
  
        // 检查是否有任务状态发生变化
        const processingTasks = taskList.value.filter(
          (task) => task.status === 'processing'
        );
  
        // 如果有正在处理的任务，可以缩短刷新间隔
        if (processingTasks.length > 0) {
          restartAutoRefresh(5000); // 有处理中任务时，5秒刷新一次
        } else {
          restartAutoRefresh(10000); // 没有处理中任务时，10秒刷新一次
        }
      }
    } catch (error: any) {
      // 错误时不清空现有任务列表，保持用户体验
    } finally {
      setLoading(false);
    }
  };

  // 处理任务点击
  const handleTaskClick = (task: TaskItem) => {
    currentTaskId.value = task.task_id;

    // 无论任务状态如何，都显示详情弹窗
    resultModalVisible.value = true;
    emit('selectTask', task.task_id);

    // 如果任务还在处理中，提示用户并继续轮询
    if (task.status !== 'completed') {
      Message.info(t('monitor.message.taskProcessing'));

      // 每5秒刷新一次，直到任务完成
      const checkInterval = setInterval(() => {
        fetchTaskList(true).then(() => {
          // 检查任务是否已完成
          const updatedTask = taskList.value.find(
            (item) => item.task_id === task.task_id
          );
          if (updatedTask && updatedTask.status === 'completed') {
            clearInterval(checkInterval);
            // 刷新详情弹窗
            resultModalVisible.value = false;
            setTimeout(() => {
              resultModalVisible.value = true;
            }, 100);
          }
        });
      }, 5000);
    }
  };

  // 刷新任务列表
  const refreshTaskList = () => {
    fetchTaskList(true); // 强制刷新
  };

  // 清空所有任务
  const clearAllTasks = () => {
    // 调用后端API清空任务
    import('axios').then(({ default: axios }) => {
      axios
        .post('/api/detect/clear_tasks')
        .then(() => {
          Message.success(t('monitor.message.cleared'));
          fetchTaskList(true);
        })
        .catch((err) => {
          Message.error(`${t('monitor.message.fetchFailed')}: ${err.message}`);
        });
    });
  };

  // 格式化时间
  const formatTime = (timeStr: string) => {
    if (!timeStr) return '';
    const date = new Date(timeStr);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(date.getDate()).padStart(2, '0')} ${String(
      date.getHours()
    ).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'blue';
      case 'processing':
        return 'orange';
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待中';
      case 'processing':
        return '处理中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      default:
        return '未知';
    }
  };

  // 组件挂载时
  onMounted(() => {
    // 初始加载任务列表
    fetchTaskList(true);
    
    // 启动自动刷新
    restartAutoRefresh();
    
    // 添加事件监听，监听新任务创建
    // 使用一个命名函数而不是匿名函数，以便正确移除
    const detectTaskCreatedHandler = (event: any) => {
      handleDetectTaskCreated(event);
    };
    
    window.addEventListener('detect-task-created', detectTaskCreatedHandler);
    
    // 保存事件处理函数引用，以便在卸载时正确移除
    (window as any).detectTaskCreatedHandler = detectTaskCreatedHandler;
  });

  // 组件卸载前
  onBeforeUnmount(() => {
    // 停止自动刷新
    stopAutoRefresh();
    
    // 移除事件监听
    if ((window as any).detectTaskCreatedHandler) {
      window.removeEventListener(
        'detect-task-created',
        (window as any).detectTaskCreatedHandler
      );
      delete (window as any).detectTaskCreatedHandler;
    }
  });
</script>

<style scoped>
  .task-item {
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .task-item:hover {
    background-color: var(--color-fill-2);
  }

  .task-id {
    color: var(--color-text-1);
    font-weight: bold;
  }

  .task-time {
    color: var(--color-text-3);
    font-size: 12px;
  }

  .task-count {
    color: var(--color-text-2);
    font-size: 12px;
  }

  .evil-count {
    color: #f53f3f;
    font-weight: bold;
  }
</style>