<template>
  <a-card
    class="general-card"
    :title="$t('multiDAnalysis.card.title.contentPublishingSource')"
    :loading="loading"
  >
    <div class="user-profile-container">
      <!-- 搜索框 -->
      <div class="search-container">
        <a-input-search
          v-model="userId"
          :placeholder="$t('visualization.userProfile.searchPlaceholder')"
          search-button
          @search="handleSearch"
        />
      </div>

      <!-- 用户基本信息 -->
      <template v-if="userProfile">
        <div class="profile-header">
          <div class="avatar-container">
            <a-avatar :size="80" :style="{ backgroundColor: '#3370ff' }">
              {{ userProfile.user_name.substring(0, 1) }}
            </a-avatar>
          </div>
          <div class="user-info">
            <h2>{{ userProfile.user_name }}</h2>
            <p class="user-id">ID: {{ userProfile.user_id }}</p>
            <p class="location">
              <icon-location /> {{ userProfile.ip_location }}
            </p>
            <p class="description">{{ userProfile.self_description }}</p>
            <div class="ai-analysis">
              <a-tag color="arcoblue">AI分析</a-tag>
              {{ userProfile.ai_description }}
            </div>
          </div>
        </div>

        <!-- 用户统计数据 -->
        <div class="stats-container">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-statistic
                :title="$t('visualization.userProfile.followCount')"
                :value="userProfile.follow_count"
                :value-style="{ color: '#3370ff' }"
              >
                <template #suffix>
                  <icon-user />
                </template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic
                :title="$t('visualization.userProfile.fansCount')"
                :value="userProfile.fans_count"
                :value-style="{ color: '#f5222d' }"
              >
                <template #suffix>
                  <icon-heart />
                </template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic
                :title="$t('visualization.userProfile.likeCount')"
                :value="userProfile.like_count"
                :value-style="{ color: '#faad14' }"
              >
                <template #suffix>
                  <icon-thumb-up />
                </template>
              </a-statistic>
            </a-col>
          </a-row>
        </div>

        <!-- 视频列表 -->
        <div class="video-list">
          <div class="section-title">
            {{ $t('visualization.userProfile.videoList') }}
            ({{ userProfile.total }})
          </div>
          <a-table
            :data="userProfile.video_list"
            :pagination="false"
            :bordered="false"
            :scroll="{ y: 240 }"
          >
            <template #columns>
              <a-table-column title="视频名称" data-index="name" />
              <a-table-column title="发布时间" data-index="publish_time" />
              <a-table-column title="点赞数" data-index="likes">
                <template #cell="{ record }">
                  <span class="likes">
                    <icon-thumb-up /> {{ record.likes }}
                  </span>
                </template>
              </a-table-column>
              <a-table-column title="分享数" data-index="shares">
                <template #cell="{ record }">
                  <span class="shares">
                    <icon-share-alt /> {{ record.shares }}
                  </span>
                </template>
              </a-table-column>
              <a-table-column title="收藏数" data-index="collects">
                <template #cell="{ record }">
                  <span class="collects">
                    <icon-star /> {{ record.collects }}
                  </span>
                </template>
              </a-table-column>
            </template>
          </a-table>
        </div>
      </template>

      <!-- 无数据状态 -->
      <a-empty v-else :description="$t('visualization.userProfile.noData')" />
    </div>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { getUserProfile, UserProfileData } from '@/api/visualization';
  import { useI18n } from 'vue-i18n';
  import useLoading from '@/hooks/loading';

  const { t } = useI18n();
  const { loading, setLoading } = useLoading(false);
  const userId = ref('');
  const userProfile = ref<UserProfileData | null>(null);

  // 保留这些函数作为备用，但不再主动调用
  const generateMockVideoList = (isEvilContentCreator: boolean) => {
    const result = [];
    const count = isEvilContentCreator ? 12 : 5;
    const evilVideoTitles = [
      '小猪佩奇的噩梦冒险',
      '米老鼠恐怖屋',
      '蜘蛛侠变异记',
      '冰雪奇缘黑暗魔法',
      '熊出没之恐怖森林',
      '汪汪队立大功之黑暗任务',
      '超级飞侠诡异飞行',
      '小马宝莉诡异变身',
      '海绵宝宝恐怖烹饪',
      '奥特曼血腥格斗',
      '哆啦A梦恐怖道具',
      '猫和老鼠暴力版',
    ];
    
    const normalVideoTitles = [
      '周末旅行日记',
      '美食探店分享',
      '生活小技巧',
      '读书心得',
      '城市街拍',
    ];
    
    for (let i = 0; i < count; i += 1) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const formattedDate = `${date.getFullYear()}-${String(
        date.getMonth() + 1
      ).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(
        date.getHours()
      ).padStart(2, '0')}:${String(date.getMinutes()).padStart(
        2,
        '0'
      )}:${String(date.getSeconds()).padStart(2, '0')}`;
      
      const titles = isEvilContentCreator ? evilVideoTitles : normalVideoTitles;
      const title = titles[i % titles.length];
      
      result.push({
        vd_id: `vid${String(i).padStart(3, '0')}`,
        name: title,
        publish_time: formattedDate,
        likes: isEvilContentCreator
          ? Math.floor(Math.random() * 100000) + 10000
          : Math.floor(Math.random() * 5000) + 100,
        shares: isEvilContentCreator
          ? Math.floor(Math.random() * 10000) + 1000
          : Math.floor(Math.random() * 500) + 10,
        collects: isEvilContentCreator
          ? Math.floor(Math.random() * 50000) + 5000
          : Math.floor(Math.random() * 1000) + 50,
      });
    }
    
    return result;
  };

  // 生成模拟数据
  const generateMockData = (userIdParam: string): UserProfileData => {
    // 根据用户ID生成不同的模拟数据
    const isEvilContentCreator = userIdParam.includes('evil') || Math.random() > 0.7;
    
    return {
      user_id: userIdParam,
      user_name: isEvilContentCreator
        ? '儿童内容创作者'
        : `普通用户${userIdParam.slice(0, 3)}`,
      age: isEvilContentCreator ? 28 : 18 + Math.floor(Math.random() * 20),
      follow_count: Math.floor(Math.random() * 500) + 100,
      fans_count: isEvilContentCreator
        ? Math.floor(Math.random() * 50000) + 10000
        : Math.floor(Math.random() * 5000) + 100,
      like_count: isEvilContentCreator
        ? Math.floor(Math.random() * 1000000) + 100000
        : Math.floor(Math.random() * 10000) + 1000,
      ip_location: ['北京', '上海', '广州', '深圳', '杭州'][
        Math.floor(Math.random() * 5)
      ],
      self_description: isEvilContentCreator
        ? '专注儿童教育内容创作，让孩子在快乐中学习成长'
        : '分享生活，记录美好',
      ai_description: isEvilContentCreator
        ? '该账号发布内容中包含多个可能对儿童造成心理影响的视频，内容多以卡通形象为主，但存在恐怖、暴力等不适宜儿童观看的元素。建议重点关注该账号的内容发布动向。'
        : '普通内容创作者，内容健康积极，无明显风险倾向',
      video_list: generateMockVideoList(isEvilContentCreator),
      total: isEvilContentCreator ? 12 : 5,
    };
  };

  // 修改搜索用户函数，优先使用后端数据
  // 修改搜索用户函数，处理直接返回数据的情况
  const handleSearch = async () => {
    if (!userId.value) {
      Message.warning(t('visualization.userProfile.enterUserId'));
      return;
    }

    setLoading(true);
    try {
      // 调用后端API获取数据
      const res = await getUserProfile(userId.value);
      
      console.log('API返回数据:', res); // 添加调试日志
      
      // 检查返回的数据
      if (res.data) {
        // 判断返回的是标准响应结构还是直接的数据对象
        if (res.data.code === 20000 && res.data.data) {
          // 标准响应结构：{code, message, data}
          userProfile.value = res.data.data;
          Message.success(t('visualization.userProfile.searchSuccess'));
        } else if (res.data.user_id) {
          // 直接返回的数据对象：没有code和message字段，但有user_id字段
          userProfile.value = res.data;
          Message.success(t('visualization.userProfile.searchSuccess'));
        } else {
          // 返回的数据格式不符合预期
          userProfile.value = null;
          Message.warning('未找到该用户信息或数据格式不正确');
          console.error('数据格式不正确:', res.data);
        }
      } else {
        // API返回为空
        userProfile.value = null;
        Message.warning('API返回数据为空');
      }
    } catch (error) {
      console.error('获取用户画像失败:', error);
      Message.error(t('visualization.userProfile.searchFailed'));
      userProfile.value = null;
    } finally {
      setLoading(false);
    }
  };

  // 修改初始化函数，不再自动加载示例数据
  onMounted(() => {
    // 组件挂载时不自动加载数据，等待用户输入
    // 可以在这里添加一些初始化逻辑，但不再自动搜索
  });
</script>

<style scoped lang="less">
  .user-profile-container {
    padding: 8px;
  }

  .search-container {
    margin-bottom: 24px;
  }

  .profile-header {
    display: flex;
    margin-bottom: 24px;
    padding: 16px;
    background-color: var(--color-fill-2);
    border-radius: 4px;
  }

  .avatar-container {
    margin-right: 24px;
  }

  .user-info {
    flex: 1;

    h2 {
      margin-top: 0;
      margin-bottom: 8px;
      color: var(--color-text-1);
    }

    .user-id {
      margin-bottom: 8px;
      color: var(--color-text-3);
    }

    .location {
      margin-bottom: 8px;
      color: var(--color-text-2);
    }

    .description {
      margin-bottom: 16px;
      color: var(--color-text-2);
    }

    .ai-analysis {
      padding: 8px;
      background-color: var(--color-fill-3);
      border-radius: 4px;
    }
  }

  .stats-container {
    margin-bottom: 24px;
    padding: 16px;
    background-color: var(--color-fill-2);
    border-radius: 4px;
  }

  .video-list {
    .section-title {
      margin-bottom: 16px;
      color: var(--color-text-1);
      font-weight: 500;
      font-size: 16px;
    }

    .likes {
      color: #f5222d;
    }

    .shares {
      color: #3370ff;
    }

    .collects {
      color: #faad14;
    }
  }
</style>