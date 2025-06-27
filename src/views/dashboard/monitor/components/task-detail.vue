<template>
  <a-modal
    v-model:visible="localVisible"
    @cancel="close"
    :title="t('monitor.modal.taskDetail')"
    :footer="false"
    width="800px"
    :mask-style="{ backdropFilter: 'blur(4px)' }"
    :body-style="{ padding: '24px', background: 'var(--color-bg-2)' }"
  >
    <a-spin :loading="loading">
      <div v-if="taskReport" class="task-detail-container">
        <div class="info-card">
          <a-descriptions
            :title="t('monitor.descriptions.taskInfo')"
            :column="{ xs: 1, sm: 2, md: 3 }"
            :data="[
              {
                label: t('monitor.label.taskId'),
                value: taskReport.task_info.task_id,
                icon: 'code',
              },
              {
                label: t('monitor.label.status'),
                value: taskReport.task_info.status === 'completed' 
                  ? t('monitor.status.completed') 
                  : t('monitor.status.processing'),
                icon: taskReport.task_info.status === 'completed' ? 'check-circle' : 'loading',
              },
              {
                label: t('monitor.label.createdAt'),
                value: formatTime(taskReport.task_info.created_at),
                icon: 'calendar',
              },
              {
                label: t('monitor.label.completedAt'),
                value: formatTime(taskReport.task_info.completed_at),
                icon: 'clock-circle',
              },
              {
                label: t('monitor.label.totalVideos'),
                value: taskReport.summary.total_videos,
                icon: 'video-camera',
              },
              {
                label: t('monitor.label.evilVideos'),
                value: taskReport.summary.evil_videos,
                icon: 'exclamation-circle',
              },
            ]"
            :label-style="{ fontWeight: '500' }"
            :value-style="{ color: 'var(--color-text-1)' }"
            bordered
          >
            <template #label="{ label, data }">
              <a-space>
                <icon-hover>
                  <component :is="`icon-${data.icon}`" />
                </icon-hover>
                <span>{{ label }}</span>
              </a-space>
            </template>
          </a-descriptions>
        </div>

        <a-divider style="margin: 24px 0" />

        <div v-if="taskReport.task_info.status === 'completed'" class="video-results-section">
          <h3 class="section-title">
            <icon-video-camera class="section-icon" />
            {{ t('monitor.title.videoResults') }}
          </h3>
          
          <div v-if="roundsData.length > 0" class="rounds-container">
            <a-collapse :bordered="false" accordion>
              <a-collapse-item
                v-for="round in roundsData"
                :key="round.round"
                :header="`${t('monitor.label.round')} ${round.round} (${round.video_count} ${t('monitor.label.videos')})`"
              >
                <a-list :bordered="false" :split="true" class="video-list">
                  <a-list-item v-for="video in round.videos" :key="video.vd_id" class="video-item">
                    <a-space direction="vertical" style="width: 100%" :size="8">
                      <a-space>
                        <icon-play-circle-fill class="video-icon" />
                        <span class="video-title">{{ video.vd_title }}</span>
                        <a-tag v-if="taskReport.evil_video_ids.includes(video.vd_id)" color="red" class="evil-tag">
                          <icon-exclamation-circle-fill style="margin-right: 4px" />
                          {{ t('monitor.tag.evil') }}
                        </a-tag>
                      </a-space>
                      <a-space :size="16">
                        <span class="video-author">
                          <icon-user style="margin-right: 4px" />{{ t('monitor.label.author') }}: {{ video.author }}
                        </span>
                        <span class="video-stats">
                          <icon-thumb-up style="margin-right: 4px" />{{ video.likes }}
                        </span>
                        <span class="video-stats">
                          <icon-star style="margin-right: 4px" />{{ video.collects }}
                        </span>
                      </a-space>
                      <div class="video-tags">
                        <a-tag 
                          v-for="tag in video.tags" 
                          :key="tag"
                          color="arcoblue"
                          bordered
                          class="tag-item"
                        >
                          <icon-tag style="margin-right: 4px; font-size: 12px" />
                          {{ tag }}
                        </a-tag>
                      </div>
                    </a-space>
                  </a-list-item>
                </a-list>
              </a-collapse-item>
            </a-collapse>
          </div>
          <a-empty v-else :description="t('monitor.empty.noVideos')" />
        </div>
        <a-result
          v-else
          status="info"
          :title="t('monitor.result.processing')"
          :sub-title="t('monitor.result.waitProcessing')"
          class="processing-result"
        >
          <template #icon>
            <a-spin :size="64" />
          </template>
        </a-result>
      </div>
      <a-empty v-else :description="t('monitor.empty.noTaskData')" />
    </a-spin>
  </a-modal>
</template>

<script lang="ts" setup>
  // 保持原有脚本不变
  import { ref, defineProps, defineEmits, watch } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import {
    getTaskReport,
    getTaskDetail,
    getAllRoundVideos,
    getTaskList, // 添加这个导入
    TaskReport,
    TaskDetail,
    AllRoundsResult,
    TaskItem,
  } from '@/api/dashboard';
  import { useI18n } from 'vue-i18n';

  const { t } = useI18n();

  const props = defineProps({
    visible: {
      type: Boolean,
      default: false,
    },
    taskId: {
      type: String,
      default: '',
    },
  });

  const emit = defineEmits(['update:visible', 'close']);

  // 使用本地变量代替直接修改props
  const localVisible = ref(props.visible);
  const loading = ref(false);
  const taskReport = ref<TaskReport | null>(null);
  const roundsData = ref<AllRoundsResult['rounds']>([]);
  const fetchRetryCount = ref(0);
  const taskInfo = ref<TaskItem | null>(null);

  // 获取任务详情和轮次数据
  const fetchTaskDetail = async (taskId: string) => {
    if (!taskId) return;
    
    loading.value = true;
    try {
      // 先获取任务列表，查找当前任务的基本信息
      const taskListRes = await getTaskList();
      if (taskListRes.data && taskListRes.data.tasks) {
        const currentTask = taskListRes.data.tasks.find(
          (task: TaskItem) => task.task_id === taskId
        );
        if (currentTask) {
          taskInfo.value = currentTask;
        }
      }
      
      // 再获取任务详情
      const detailRes = await getTaskDetail(taskId);
      if (detailRes.data) {
        // 构建与 TaskReport 兼容的数据结构
        taskReport.value = {
          task_info: {
            task_id: detailRes.data.task_id,
            status: detailRes.data.status,
            created_at: detailRes.data.created_at,
            completed_at: detailRes.data.updated_at,
            evil_video_ids: detailRes.data.evil_video_ids || [],
          },
          summary: {
            // 使用从任务列表获取的数据填充视频数量
            total_videos: taskInfo.value?.all_video_count || 0,
            evil_videos: taskInfo.value?.evil_video_count || 0,
            normal_videos: 
              (taskInfo.value?.all_video_count || 0) -
              (taskInfo.value?.evil_video_count || 0),
          },
          evil_video_ids: detailRes.data.evil_video_ids || [],
        };
        
        // 如果任务已完成，获取详细报告和轮次数据
        if (detailRes.data.status === 'completed') {
          try {
            // 尝试获取任务报告以获取更详细的信息
            const reportRes = await getTaskReport(taskId);
            if (reportRes.data) {
              // 更新报告数据，但保留从任务列表获取的视频数量信息
              const updatedReport = reportRes.data;
              
              // 如果报告中的视频数量为0，但任务列表中有数据，则使用任务列表中的数据
              if (
                updatedReport.summary.total_videos === 0 &&
                taskInfo.value?.all_video_count
              ) {
                updatedReport.summary.total_videos = 
                  taskInfo.value.all_video_count;
                updatedReport.summary.evil_videos = 
                  taskInfo.value.evil_video_count;
                updatedReport.summary.normal_videos = 
                  taskInfo.value.all_video_count -
                  taskInfo.value.evil_video_count;
              }
              
              taskReport.value = updatedReport;
            }
          } catch (reportErr: any) {
            // 报告获取失败不影响整体显示
          }
          
          // 获取轮次数据
          try {
            const roundsRes = await getAllRoundVideos(taskId);
            if (roundsRes.data && roundsRes.data.rounds) {
              roundsData.value = roundsRes.data.rounds;
            } else {
              roundsData.value = [];
            }
          } catch (err: any) {
            // 轮次数据获取失败不影响整体显示
            roundsData.value = [];
          }
        } else if (
          detailRes.data.status === 'processing' &&
          fetchRetryCount.value < 5
        ) {
          // 如果任务还在处理中，且重试次数小于5次，则3秒后重试
          fetchRetryCount.value += 1;
          setTimeout(() => {
            fetchTaskDetail(taskId);
          }, 3000);
        }
      }
    } catch (err: any) {
      // 错误处理
      if (err.message && err.message.includes('任务尚未完成')) {
        // 如果是任务未完成的错误，且重试次数小于5次，则3秒后重试
        if (fetchRetryCount.value < 5) {
          fetchRetryCount.value += 1;
          setTimeout(() => {
            fetchTaskDetail(taskId);
          }, 3000);
          return;
        }
      }
      
      if (fetchRetryCount.value < 5) {
        // 如果获取失败且重试次数小于5次，则3秒后重试
        fetchRetryCount.value += 1;
        setTimeout(() => {
          fetchTaskDetail(taskId);
        }, 3000);
      } else {
        Message.error(`获取任务详情失败: ${err.message || '未知错误'}`);
      }
    } finally {
      loading.value = false;
    }
  };

  // 关闭弹窗
  const close = () => {
    localVisible.value = false;
    emit('update:visible', false);
    emit('close');
    // 重置重试计数器
    fetchRetryCount.value = 0;
  };

  // 格式化时间
  const formatTime = (timeStr: string | null) => {
    if (!timeStr) return '-';
    const date = new Date(timeStr);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
      2,
      '0'
    )}-${String(date.getDate()).padStart(2, '0')} ${String(
      date.getHours()
    ).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  };

  // 监听props.visible变化
  watch(
    () => props.visible,
    (val) => {
      localVisible.value = val;
      if (val && props.taskId) {
        // 重置重试计数器
        fetchRetryCount.value = 0;
        fetchTaskDetail(props.taskId);
      }
    }
  );

  // 监听localVisible变化
  watch(
    () => localVisible.value,
    (val) => {
      emit('update:visible', val);
    }
  );

  // 监听任务ID变化，加载数据
  watch(
    () => props.taskId,
    (newTaskId) => {
      if (newTaskId && localVisible.value) {
        // 重置重试计数器
        fetchRetryCount.value = 0;
        fetchTaskDetail(newTaskId);
      }
    }
  );
</script>

<style scoped lang="less">
  .task-detail-container {
    padding: 12px;
  }

  .info-card {
    padding: 16px;
    background-color: var(--color-bg-1);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 5%);
  }

  .section-title {
    position: relative;
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    padding-left: 12px;
    color: var(--color-text-1);
    font-weight: 500;
    font-size: 18px;
    
    &::before {
      position: absolute;
      top: 50%;
      left: 0;
      width: 4px;
      height: 16px;
      background-color: var(--color-primary-6);
      border-radius: 2px;
      transform: translateY(-50%);
      content: '';
    }
    
    .section-icon {
      margin-right: 8px;
      color: var(--color-primary-6);
    }
  }

  .rounds-container {
    margin-top: 16px;
  }

  .video-list {
    padding: 0 8px;
  }

  .video-item {
    margin-bottom: 8px;
    padding: 12px;
    background-color: var(--color-bg-1);
    border-radius: 8px;
    transition: all 0.2s;
    
    &:hover {
      background-color: var(--color-fill-2);
      box-shadow: 0 4px 10px rgb(0 0 0 / 5%);
      transform: translateY(-2px);
    }
  }

  .video-icon {
    color: var(--color-primary-6);
    font-size: 16px;
  }

  .video-title {
    color: var(--color-text-1);
    font-weight: 600;
    font-size: 15px;
    line-height: 1.5;
  }

  .evil-tag {
    display: flex;
    align-items: center;
    padding: 0 8px;
    font-weight: 500;
  }

  .video-author {
    display: flex;
    align-items: center;
    padding: 2px 8px;
    color: var(--color-text-2);
    font-size: 13px;
    background-color: var(--color-fill-1);
    border-radius: 4px;
  }

  .video-stats {
    display: flex;
    align-items: center;
    padding: 2px 8px;
    color: var(--color-text-3);
    font-size: 13px;
    background-color: var(--color-fill-1);
    border-radius: 4px;
  }

  .video-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
  }

  .tag-item {
    display: flex;
    align-items: center;
    height: 22px;
    margin-right: 0;
    padding: 0 8px;
    font-size: 12px;
    line-height: 20px;
  }

  .processing-result {
    margin: 24px 0;
    padding: 16px;
    background-color: var(--color-bg-1);
    border-radius: 8px;
  }
</style>
