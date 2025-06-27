<template>
  <div class="video-expansion-container">
    <div class="control-panel">
      <a-form :model="formState" layout="inline">
        <a-form-item field="initialVideo" label="初始视频">
          <a-input
            v-model="formState.initialVideo"
            placeholder="请输入初始视频标题"
            allow-clear
          />
        </a-form-item>
        <a-form-item field="maxRounds" label="最大扩展轮数">
          <a-input-number
            v-model="formState.maxRounds"
            :min="1"
            :max="10"
            :default-value="5"
          />
        </a-form-item>
        <a-form-item field="videosPerRound" label="每轮视频数">
          <a-input-number
            v-model="formState.videosPerRound"
            :min="5"
            :max="30"
            :default-value="5"
          />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="startExpansion">开始扩展</a-button>
        </a-form-item>
        <a-form-item>
          <a-button @click="resetNetwork">重置</a-button>
        </a-form-item>
      </a-form>
    </div>

    <div class="network-stats">
      <a-statistic title="当前轮数" :value="currentRound" />
      <a-statistic title="累计视频数" :value="totalVideos" />
      <a-statistic title="邪典视频数" :value="evilVideosCount" />
      <a-statistic
        title="邪典比例"
        :value="evilRate"
        :precision="2"
        suffix="%"
      />
    </div>

    <div ref="networkContainer" class="network-container"></div>

    <div class="expansion-legend">
      <div class="legend-item">
        <div class="legend-color" style="background-color: #ff4d4f"></div>
        <span>初始视频(邪典)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background-color: #1890ff"></div>
        <span>普通视频</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background-color: #ff7a45"></div>
        <span>邪典视频</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background-color: #722ed1"></div>
        <span>重复视频</span>
      </div>
    </div>

    <a-modal
      v-model:visible="videoDetailVisible"
      title="视频详情"
      :footer="false"
      width="600px"
      @cancel="videoDetailVisible = false"
    >
      <div v-if="selectedVideo">
        <h3>{{ selectedVideo.title }}</h3>
        <p><strong>作者:</strong> {{ selectedVideo.author }}</p>
        <p><strong>标签:</strong> {{ selectedVideo.tags.join(', ') }}</p>
        <p><strong>扩展轮次:</strong> {{ selectedVideo.round }}</p>
        <p><strong>关键词:</strong> {{ selectedVideo.keywords.join(', ') }}</p>
        <p>
          <strong>视频类型:</strong>
          <a-tag :color="selectedVideo.isEvil ? 'red' : 'blue'">
            {{ selectedVideo.isEvil ? '邪典视频' : '普通视频' }}
          </a-tag>
        </p>
      </div>
    </a-modal>
  </div>
</template>

<script>
  import { ref, reactive, onMounted, onUnmounted } from 'vue';
  import * as d3 from 'd3';

  export default {
    name: 'VideoExpansionNetwork',
    setup() {
      const networkContainer = ref(null);
      const formState = reactive({
        initialVideo: '',
        maxRounds: 3,
        videosPerRound: 5,
      });

      const currentRound = ref(0);
      const totalVideos = ref(0);
      const evilVideosCount = ref(0);
      const evilRate = ref(0);

      const videoDetailVisible = ref(false);
      const selectedVideo = ref(null);

      let simulation = null;
      let svg = null;
      let networkData = {
        nodes: [],
        links: [],
      };

      // 颜色映射函数，根据视频类型返回不同颜色
      const getNodeColor = (node) => {
        if (node.id === 'initial-video') return '#ff4d4f'; // 初始视频
        if (node.isDuplicate) return '#722ed1'; // 重复视频
        return node.isEvil ? '#ff7a45' : '#1890ff'; // 邪典视频 vs 普通视频
      };

      // 模拟生成随机视频数据
      const generateRandomVideo = (
        round,
        parentKeywords = [],
        isEvil = false
      ) => {
        const authors = ['儿童益智视频大选', '奥特曼赛文', '小猪佩奇哥', '小火腿王', '益智游戏好玩创作'];

        // 邪典视频和普通视频的标签有所区别
        const evilTagsList = [
          '超级刺激的游戏',
          '儿童益智',
          '奥特曼',
          '哪吒',
          '儿童早教',
          '万万没想到',
          '危险游戏',
          '睡前故事',
          '小猪佩奇',
          '赛文',
        ];

        const normalTagsList = [
          '读书',
          '教育',
          '故事',
          '游戏',
          '音乐',
          '舞蹈',
          '三字经',
          '论语',
          '能力提升',
        ];

        // 根据视频类型选择标签列表
        const tagsList = isEvil ? evilTagsList : normalTagsList;

        // 随机生成标题
        const titleParts = isEvil
          ? [ '欢乐的', '启蒙的', '有趣的', '益智的', '成长的', '快乐的', '亲子间的', '宝宝最爱的']
          : ['有趣的', '快乐的', '精彩的', '可爱的', '欢乐的'];

        const titleObjects = isEvil
          ? [ '故事时间', '动画世界', '玩具乐园', '成长课堂', '早教启蒙', '公主探险', '亲子互动时光', '宝宝游戏日记']
          : ['故事', '游戏', '歌曲', '舞蹈', '玩具', '动画', '课堂'];

        const titleSuffix = isEvil
          ? [ '快来一起学习吧', '今天你学到了吗？', '宝宝们最爱的内容', '陪伴孩子快乐成长', '一起动动脑！', '亲子共赏', '快来和我一起玩吧']
          : ['时间', '派对', '冒险', '乐园', '世界'];

        const title = `${
          titleParts[Math.floor(Math.random() * titleParts.length)]
        }${titleObjects[Math.floor(Math.random() * titleObjects.length)]}${
          titleSuffix[Math.floor(Math.random() * titleSuffix.length)]
        }`;

        // 随机选择作者和标签
        const author = authors[Math.floor(Math.random() * authors.length)];
        const tags = [];
        const tagCount = Math.floor(Math.random() * 3) + 1; // 1-3个标签

        for (let i = 0; i < tagCount; i += 1) {
          const tag = tagsList[Math.floor(Math.random() * tagsList.length)];
          if (!tags.includes(tag)) {
            tags.push(tag);
          }
        }

        // 生成关键词 (从标题、作者、标签中提取)
        const keywords = [];
        // 从标题中提取
        const titleWords = title
          .split(/[的]/)
          .filter((word) => word.length > 0);
        keywords.push(...titleWords);

        // 添加作者
        keywords.push(author);

        // 添加标签
        keywords.push(...tags);

        // 确保至少有一个关键词与父节点相同
        if (parentKeywords && parentKeywords.length > 0) {
          const randomParentKeyword =
            parentKeywords[Math.floor(Math.random() * parentKeywords.length)];
          if (!keywords.includes(randomParentKeyword)) {
            keywords.push(randomParentKeyword);
          }
        }

        return {
          id: `video-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          title,
          author,
          tags,
          round,
          keywords: [...new Set(keywords)], // 去重
          isEvil, // 是否为邪典视频
          isDuplicate: false, // 是否为重复节点
          parentIds: [], // 父节点ID列表，用于记录扩展关系
        };
      };

      // 静态生成所有网络数据
      const generateNetworkData = () => {
        // 重置网络数据
        networkData = {
          nodes: [],
          links: [],
        };

         // 创建初始视频节点（种子节点，标记为邪典）
         const initialVideo = {
          id: 'initial-video',
          title: '危险游戏 @抖音青少年 @抖音创作小助手 @抖音小助手',
          author: '炯炯简笔画',
          tags: ['动画', '画画', '简笔画'],
          round: 0,
          keywords: [
            '动画',
            '画画',
            '简笔画',
          ],
          isEvil: true, // 种子节点标记为邪典
          isDuplicate: false,
          parentIds: [],
        };
        networkData.nodes.push(initialVideo);
  // 第一轮扩展：使用指定的5个视频，而不是随机生成
  const round1Videos = [];
        
        // 预定义第一轮的5个视频
        const predefinedVideos = [
          {
            title: '儿童版奥特曼3-6岁',
            author: '是你妹妹',
            keywords: ['奥特曼', '青少年模式的抖音', '儿童版奥特曼3-6岁'],
            isEvil: true
          },
          {
            title: '奥特曼打怪兽 抖音助手助我上热门',
            author: '嗷嗷奥特曼',
            keywords: ['奥特曼3-6岁儿童动画片', '奥特曼打怪兽', '抖音助手助我上热门'],
            isEvil: false
          },
          {
            title: '3-6岁儿童赛罗动画视频 儿童动画',
            author: '晴雨',
            keywords: ['奥特曼', '3-6岁儿童赛罗动画视频', '儿童动画'],
            isEvil: true
          },
          {
            title: '赛罗因守护小火伴们失去光能量导致沉入海底',
            author: '乔乔简笔画',
            keywords: ['简笔画', '儿童奥特曼动画片', '奥特曼玩具儿童视频3-6岁', '奥特曼儿童简笔画', '奥特曼早教'],
            isEvil: false
          },
          {
            title: '4.15 goD:/ 奥特，动画片儿童视频3到6岁 儿童动画',
            author: '看淡点想开点心情自然畅',
            keywords: ['小朋友都爱看', '奥特', '动画片儿童视频3到6岁', '儿童动画'],
            isEvil: false
          }
        ];
        
        // 创建第一轮视频节点
        predefinedVideos.forEach((videoData, index) => {
          const video = {
            id: `video-round1-${index}`,
            title: videoData.title,
            author: videoData.author,
            tags: videoData.keywords.slice(0, 3), // 使用关键词的前三个作为标签
            round: 1,
            keywords: videoData.keywords,
            isEvil: videoData.isEvil,
            isDuplicate: false,
            parentIds: [initialVideo.id],
          };
          
          // 添加节点
          networkData.nodes.push(video);
          
          // 添加与初始视频的连接
          networkData.links.push({
            source: initialVideo.id,
            target: video.id,
            value: 1,
          });
          
          // 将视频添加到round1Videos数组中，用于后续扩展
          round1Videos.push(video);
        });

                 // 获取第一轮的邪典视频
        const round1EvilVideos = round1Videos.filter(
          (v) => v.isEvil && !v.isDuplicate
        );
        
        // 第二轮扩展：使用指定的5个视频，而不是随机生成
        const round2Videos = [];
        const processedCombinations = new Set(); // 记录已处理的组合

        // 生成所有可能的组合
        const generateCombinations = (videos, minSize = 2, maxSize = 2) => {
          const combinations = [];

          // 生成2个视频的组合
          videos.forEach((video1, i) => {
            videos.slice(i + 1).forEach((video2) => {
              combinations.push([video1, video2]);
            });
          });

          return combinations;
        };

        // 第二轮：处理第一轮邪典视频的组合
        const round1Combinations = generateCombinations(round1EvilVideos);
        
        // 只处理第一个组合，用于连接我们预定义的第二轮视频
        if (round1Combinations.length > 0) {
          const combination = round1Combinations[0];
          
          // 创建组合ID
          const combinationId = combination
            .map((v) => v.id)
            .sort()
            .join('-');
            
          processedCombinations.add(combinationId);
          
          // 预定义第二轮的5个视频
          const predefinedRound2Videos = [
            {
              title: '【涂鸦小能手】开启儿童涂鸦的第一课 喷射炫酷多彩涂料变色',
              author: '爱游戏【LOVE GAME】',
              keywords: ['抖音小游戏', '涂鸦小能手', '喷射炫酷多彩涂料变色', '小游戏', '画画', '学生党', '动画'],
              isEvil: false
            },
            {
              title: '画画画画',
              author: '玩的嗨起',
              keywords: ['抖音小游戏', '创游编辑器', '智力游戏'],
              isEvil: true
            },
            {
              title: '来试试魔法画笔！',
              author: '阿龙爱游戏',
              keywords: ['抖音小游戏', '指尖画画', '学生党', '游戏'],
              isEvil: true
            },
            {
              title: '指尖画画',
              author: '小油条',
              keywords: ['指尖画画', '抖音小游戏', '学生党'],
              isEvil: true
            },
            {
              title: '《指尖画画》优秀作品展示',
              author: '指尖画画【儿童画画启蒙】',
              keywords: ['指尖画画', 'ai绘画', '游戏'],
              isEvil: false
            }
          ];
          
          // 创建第二轮视频节点
          predefinedRound2Videos.forEach((videoData, index) => {
            const video = {
              id: `video-round2-${index}`,
              title: videoData.title,
              author: videoData.author,
              tags: videoData.keywords.slice(0, 3), // 使用关键词的前三个作为标签
              round: 2,
              keywords: videoData.keywords,
              isEvil: videoData.isEvil,
              isDuplicate: false,
              parentIds: combination.map((v) => v.id),
            };
            
            // 添加节点
            networkData.nodes.push(video);
            
            // 添加与父节点的连接
            combination.forEach((parent) => {
              networkData.links.push({
                source: parent.id,
                target: video.id,
                value: 1,
              });
            });
            
            // 将视频添加到round2Videos数组中，用于后续扩展
            round2Videos.push(video);
          });
          
          // 更新统计信息
          currentRound.value = 2;
          totalVideos.value = 1 + round1Videos.length + round2Videos.length;
          evilVideosCount.value = 1 + 
            round1Videos.filter(v => v.isEvil).length + 
            predefinedRound2Videos.filter(v => v.isEvil).length;
          evilRate.value = (evilVideosCount.value / totalVideos.value) * 100;
        }

                // 获取第二轮的邪典视频
                const round2EvilVideos = round2Videos.filter(
          (v) => v.isEvil && !v.isDuplicate
        );

        // 第三轮扩展：从第二轮的邪典视频组合扩展
        const round3Videos = [];
        processedCombinations.clear(); // 清空已处理的组合

        // 第三轮：处理第二轮邪典视频的组合
        const round2Combinations = generateCombinations(round2EvilVideos);

        // 预定义第三轮的15个视频
        const predefinedRound3Videos = [
          {
            title: '早教游戏分享"听指令绘画"🎨',
            author: '岩岩脑力课堂',
            keywords: ['在家早教小游戏', '省心省力的宝宝早教游戏', '锻炼大脑反应的游戏', '专注力训练游戏推荐', '全脑育儿'],
            isEvil: false,
          },
          {
            title: '黑白小牛，教孩子玩画画游戏',
            author: '育儿趣味游戏',
            keywords: ['亲子', '萌知计划', '亲子游戏'],
            isEvil: true,
          },
          {
            title: '365天A4纸早教计划（1-3）硕士宝妈亲手画！娃专注力up 每天被3岁双胞胎萌娃催更： 硕士妈妈亲自设计手绘纸上游戏 每天一张A4纸，萌娃越来越聪明！ 第1天【数字彩虹】 ✅色彩认知 ✅认识数字1-5 第2天【彩色小鱼】 ✅色彩认知 ✅方向感 第3天【糖果罐子】 ✅形状认知 ✅细节观察力',
            author: '果妈的双倍幸福',
            keywords: ['专注力培养', '在家早教', '纸上游戏', '妈咪新风向', '宝宝早教'],
            isEvil: false,
          },
          {
            title: '手指创意画，3—6岁孩子可以玩，培养想象力，猜最后画的是什么',
            author: '爱唠叨的马小妈',
            keywords: ['手指创意画', '想象力培养', '儿童绘画'],
            isEvil: true,
          },
          {
            title: '2岁艺术启蒙这样玩8幅宝宝超爱的创意画 艺术源于生活! 家里的生活用品也可以变身绘画工具，用来给宝宝进行艺术启蒙，玩出超多新花样。 今日分享8个简单有趣的家庭美育早教游戏，每一个都超好玩，宝宝超喜欢，2岁以后的宝宝都可以安排起来了，尽情享受美好的亲子时光吧。 艺术启蒙好处多多: 1激发宝宝的想象力和创造力2 提升宝宝的专注力 3锻炼宝宝手部精细动作和手眼协调能力4增强宝宝对色彩的感知力5 帮助宝宝良好的抒发情绪',
            author: '怡宝的快乐时光',
            keywords: ['艺术启蒙', '家庭艺术启蒙', '万物皆可聊艺术', '儿童创意美术画', '家庭美育'],
            isEvil: false,
          },
          {
            title: '一岁半宝宝不脏手·春日车轮画！超省妈的感官艺术启蒙',
            author: '和嘟哩一起长大',
            keywords: ['抖音创作季', '我家带娃有绝招', '妈咪新风向', '在家早教小游戏', '每日亲子游戏'],
            isEvil: false,
          },
          {
            title: '在家早教：亲子绘画游戏，宝宝更懂得配合',
            author: '育儿慢时光',
            keywords: ['早教', '育儿'],
            isEvil: true,
          },
          {
            title: '千万不要沉迷游戏了，不然后果很严重',
            author: '雨桐科普',
            keywords: ['科普', '科普一下', '知识分享'],
            isEvil: true,
          },
          {
            title: '班主任重点强调，这不是勇者的游戏，这是无知者的游戏',
            author: '儿童安全官',
            keywords: ['家长必读'],
            isEvil: false,
          },
          {
            title: '小朋友们玩游戏的时候一定要注意脚下安全哟',
            author: '儿童益智动画',
            keywords: ['儿童动画', '育儿', '儿童益智', '益智动画', '原创'],
            isEvil: true,
          },
          {
            title: '小朋友们不要做危险的游戏哦',
            author: '欢乐(^∇^)',
            keywords: ['经典儿童动画推荐', '关注我每天更新精彩视频', '原创视频', '看看小故事学点新知识', '动漫故事正能量'],
            isEvil: true,
          },
          {
            title: '家长注意：从一句主人开始的深渊，揭秘青少年网络侵害',
            author: '欧巴金申姜',
            keywords: ['青少年教育', '原创动画'],
            isEvil: true,
          },
          {
            title: '手机很好玩，但是小朋友们要合理的去控制自己玩手机的时间，不要掉进手机的魔法陷阱哦',
            author: '小石头的儿童睡前故事',
            keywords: ['儿童睡前故事', '儿童动画', '启蒙早教', '亲子互动', '小孩玩手机游戏的危害'],
            isEvil: true,
          },
          {
            title: '儿童睡前故事-沉迷游戏的危害 小朋友们，游戏虽然好玩，但不能沉迷。合理安排时间，才能让我们保持健康，过上更快乐的生活。',
            author: '贝贝儿童睡前故事',
            keywords: ['儿童动画', '儿童睡前故事', '启蒙早教', '孩子玩游戏'],
            isEvil: true,
          },
          {
            title: '有些游戏太危险不能玩~',
            author: '蜜团宝贝安全教育',
            keywords: [
              '热点',
              '儿童安全',
              '儿童教育动画推荐',
              '危险游戏不能玩',
              '亲子教育',
            ],
            isEvil: true,
          },
        ];

        // 处理第二轮邪典视频的组合，使用预定义的视频
        if (round2Combinations.length > 0) {
          // 只处理第一个组合，用于连接我们预定义的第三轮视频
          const combination = round2Combinations[0];
          
          // 创建组合ID
          const combinationId = combination
            .map((v) => v.id)
            .sort()
            .join('-');
            
          processedCombinations.add(combinationId);
          
          // 创建第三轮视频节点 - 使用预定义的视频
          predefinedRound3Videos.forEach((videoData, index) => {
            const video = {
              id: `video-round3-${index}`,
              title: videoData.title,
              author: videoData.author,
              tags: videoData.keywords.slice(0, 3), // 使用关键词的前三个作为标签
              round: 3,
              keywords: videoData.keywords,
              isEvil: videoData.isEvil,
              isDuplicate: false,
              parentIds: combination.map((v) => v.id),
            };
            
            // 添加节点
            networkData.nodes.push(video);
            
            // 添加与父节点的连接
            combination.forEach((parent) => {
              networkData.links.push({
                source: parent.id,
                target: video.id,
                value: 1,
              });
            });
            
            // 将视频添加到round3Videos数组中，用于后续扩展
            round3Videos.push(video);
          });
          
          // 更新统计信息
          currentRound.value = 3;
          totalVideos.value = 1 + round1Videos.length + round2Videos.length + round3Videos.length;
          evilVideosCount.value = 
            1 + 
            round1Videos.filter(v => v.isEvil).length + 
            round2Videos.filter(v => v.isEvil).length + 
            predefinedRound3Videos.filter(v => v.isEvil).length;
          evilRate.value = (evilVideosCount.value / totalVideos.value) * 100;
        }

        // 获取第三轮的邪典视频（注意：只使用第三轮生成的邪典视频，不包括之前轮次的）
        const round3EvilVideos = round3Videos.filter(
          (v) => v.isEvil && !v.isDuplicate
        );

        // 第四轮扩展：从第三轮的邪典视频组合扩展
        if (formState.maxRounds >= 4) {
          const round4Videos = [];
          processedCombinations.clear(); // 清空已处理的组合

          // 限制组合数量，避免过多
          const maxCombinations = 5;
          let combinationCount = 0;

          // 第四轮：处理第三轮邪典视频的组合
          const round3Combinations = generateCombinations(round3EvilVideos);

          round3Combinations.some((combination) => {
            if (combinationCount >= maxCombinations) return true;

            // 创建组合ID，确保不重复处理
            const combinationId = combination
              .map((v) => v.id)
              .sort()
              .join('-');

            if (!processedCombinations.has(combinationId)) {
              processedCombinations.add(combinationId);
              combinationCount += 1;

              // 合并关键词
              const combinedKeywords = [
                ...new Set(combination.flatMap((video) => video.keywords)),
              ];

              // 从组合中扩展出视频
              const evilCount = Math.min(3, formState.videosPerRound); // 第四轮几乎全是邪典视频

              Array.from({ length: formState.videosPerRound }).forEach(
                (_, k) => {
                  const isEvil = k < evilCount; // 前evilCount个为邪典
                  const video = generateRandomVideo(
                    4,
                    combinedKeywords,
                    isEvil
                  );
                  video.parentIds = combination.map((v) => v.id);

                  // 20%概率是重复节点
                  const isDuplicate = Math.random() < 0.2;
                  if (isDuplicate) {
                    // 随机选择一个已有节点作为重复
                    const existingVideo =
                      networkData.nodes[
                        Math.floor(Math.random() * networkData.nodes.length)
                      ];
                    video.id = existingVideo.id;
                    video.title = existingVideo.title;
                    video.author = existingVideo.author;
                    video.tags = existingVideo.tags;
                    video.keywords = existingVideo.keywords;
                    video.isEvil = existingVideo.isEvil;
                    video.isDuplicate = true;

                    // 只添加连接，不添加节点
                    combination.forEach((parent) => {
                      networkData.links.push({
                        source: parent.id,
                        target: video.id,
                        value: 0.8,
                      });
                    });
                  } else {
                    // 非重复节点，正常添加
                    networkData.nodes.push(video);

                    combination.forEach((parent) => {
                      networkData.links.push({
                        source: parent.id,
                        target: video.id,
                        value: 1,
                      });
                    });

                    round4Videos.push(video);
                  }
                }
              );
            }
            return false;
          });

          // 第五轮扩展：从第四轮的邪典视频组合扩展
          if (formState.maxRounds >= 5) {
            // 获取第四轮的邪典视频
            const round4EvilVideos = round4Videos.filter(
              (v) => v.isEvil && !v.isDuplicate
            );

            processedCombinations.clear();
            combinationCount = 0;

            // 第五轮：处理第四轮邪典视频的组合
            const round4Combinations = generateCombinations(round4EvilVideos);

            // 存储第五轮生成的视频，用于后续扩展
            const round5Videos = [];

            round4Combinations.some((combination) => {
              if (combinationCount >= maxCombinations) return true;

              // 创建组合ID，确保不重复处理
              const combinationId = combination
                .map((v) => v.id)
                .sort()
                .join('-');

              if (!processedCombinations.has(combinationId)) {
                processedCombinations.add(combinationId);
                combinationCount += 1;

                // 合并关键词
                const combinedKeywords = [
                  ...new Set(combination.flatMap((video) => video.keywords)),
                ];

               // 从组合中扩展出视频
              const evilCount = Math.min(4, formState.videosPerRound); // 第四轮几乎全是邪典视频

            Array.from({ length: formState.videosPerRound }).forEach(
            (_, k) => {
                const isEvil = k < evilCount; // 前evilCount个为邪典
                const video = generateRandomVideo(
                5,
                combinedKeywords,
                isEvil
                );
                video.parentIds = combination.map((v) => v.id);

                  // 25%概率是重复节点
                  const isDuplicate = Math.random() < 0.15;
                  if (isDuplicate) {
                    // 随机选择一个已有节点作为重复
                    const existingVideo =
                      networkData.nodes[
                        Math.floor(Math.random() * networkData.nodes.length)
                      ];
                    video.id = existingVideo.id;
                    video.title = existingVideo.title;
                    video.author = existingVideo.author;
                    video.tags = existingVideo.tags;
                    video.keywords = existingVideo.keywords;
                    video.isEvil = existingVideo.isEvil;
                    video.isDuplicate = true;

                    // 只添加连接，不添加节点
                    combination.forEach((parent) => {
                      networkData.links.push({
                        source: parent.id,
                        target: video.id,
                        value: 0.8,
                      });
                    });
                  } else {
                    // 非重复节点，正常添加
                    networkData.nodes.push(video);

                    combination.forEach((parent) => {
                      networkData.links.push({
                        source: parent.id,
                        target: video.id,
                        value: 1,
                      });
                    });

                    // 将新生成的视频添加到round5Videos数组中
                    round5Videos.push(video);
                  }
                });
              }
              return false;
            });
          }
          // 第六轮扩展：从第五轮的邪典视频组合扩展
          if (formState.maxRounds >= 6) {
            // 获取第五轮的邪典视频
            const round5EvilVideos = networkData.nodes.filter(
              (v) => v.round === 5 && v.isEvil && !v.isDuplicate
            );

            processedCombinations.clear();
            combinationCount = 0;

            // 第六轮：处理第五轮邪典视频的组合
            const round5Combinations = generateCombinations(round5EvilVideos);

            round5Combinations.some((combination) => {
              if (combinationCount >= maxCombinations) return true;

              // 创建组合ID，确保不重复处理
              const combinationId = combination
                .map((v) => v.id)
                .sort()
                .join('-');

              if (!processedCombinations.has(combinationId)) {
                processedCombinations.add(combinationId);
                combinationCount += 1;

                // 合并关键词
                const combinedKeywords = [
                  ...new Set(combination.flatMap((video) => video.keywords)),
                ];

                Array.from({ length: formState.videosPerRound }).forEach(() => {
                  const isEvil = true; // 全部为邪典
                  const video = generateRandomVideo(
                    6,
                    combinedKeywords,
                    isEvil
                  );
                  video.parentIds = combination.map((v) => v.id);

                  // 30%概率是重复节点，比第五轮更高
                  const isDuplicate = Math.random() < 0.3;
                  if (isDuplicate) {
                    // 优先选择邪典视频作为重复节点
                    const evilNodes = networkData.nodes.filter((n) => n.isEvil);
                    const existingVideo =
                      evilNodes.length > 0
                        ? evilNodes[
                            Math.floor(Math.random() * evilNodes.length)
                          ]
                        : networkData.nodes[
                            Math.floor(Math.random() * networkData.nodes.length)
                          ];

                    video.id = existingVideo.id;
                    video.title = existingVideo.title;
                    video.author = existingVideo.author;
                    video.tags = existingVideo.tags;
                    video.keywords = existingVideo.keywords;
                    video.isEvil = existingVideo.isEvil;
                    video.isDuplicate = true;

                    // 只添加连接，不添加节点
                    combination.forEach((parent) => {
                      networkData.links.push({
                        source: parent.id,
                        target: video.id,
                        value: 0.8,
                      });
                    });
                  } else {
                    // 非重复节点，正常添加
                    networkData.nodes.push(video);

                    combination.forEach((parent) => {
                      networkData.links.push({
                        source: parent.id,
                        target: video.id,
                        value: 1,
                      });
                    });
                  }
                });
              }
              return false;
            });
          }
        }
        // 更新统计信息
        totalVideos.value = networkData.nodes.length;
        evilVideosCount.value = networkData.nodes.filter(
          (node) => node.isEvil
        ).length;
        evilRate.value = (evilVideosCount.value / totalVideos.value) * 100;
        currentRound.value = Math.max(
          ...networkData.nodes.map((node) => node.round)
        );

        // 去除重复的连接
        const uniqueLinks = [];
        const linkMap = new Map();

        networkData.links.forEach((link) => {
          const linkId = `${link.source}-${link.target}`;
          const reverseLinkId = `${link.target}-${link.source}`;

          if (!linkMap.has(linkId) && !linkMap.has(reverseLinkId)) {
            linkMap.set(linkId, true);
            uniqueLinks.push(link);
          }
        });

        networkData.links = uniqueLinks;

        return networkData;
      };

      // 渲染网络图
      const renderNetwork = () => {
        if (!networkContainer.value) return;

        // 清除现有SVG
        if (svg) {
          d3.select(svg.node().parentNode).select('svg').remove();
        }

        // 获取容器尺寸
        const containerWidth = networkContainer.value.clientWidth;
        const containerHeight = networkContainer.value.clientHeight || 600;

        // 计算所需的实际SVG宽度
        const width = containerWidth;
        const height = containerHeight;

        // 创建SVG
        svg = d3
          .select(networkContainer.value)
          .append('svg')
          .attr('width', width)
          .attr('height', height);

        const g = svg.append('g');
        const zoom = d3
          .zoom()
          .scaleExtent([0.1, 4])
          .on('zoom', (event) => {
            g.attr('transform', event.transform);
          });

        svg.call(zoom);

        // 初始化节点位置
        networkData.nodes.forEach((node) => {
          if (node.x === undefined || node.y === undefined) {
            node.x = width / 2 + (Math.random() - 0.5) * 200;
            node.y = height / 2 + (Math.random() - 0.5) * 200;
          }
        });

        // 创建力导向图 - 使用网状结构
        simulation = d3
          .forceSimulation(networkData.nodes)
          .force(
            'link',
            d3
              .forceLink(networkData.links)
              .id((d) => d.id)
              .distance(200) // 较短的连接线长度
              .strength(0.4) // 降低连线强度，让轮次分组力更明显
          )
          .force('charge', d3.forceManyBody().strength(-500)) // 适当的排斥力
          .force('collision', d3.forceCollide().radius(35).strength(1)) // 碰撞检测
          .force('center', d3.forceCenter(width / 2, height / 2)) // 中心力
          .force(
            'x',
            d3
              .forceX()
              .strength(0.3)
              .x((d) => {
                // 根据轮次分配x坐标区间
                if (d.id === 'initial-video') return width * 0.1; // 初始视频放在最左侧

                // 计算每轮的x轴位置 - 从左到右排列
                const segmentWidth = width * 0.8; // 可用宽度（除去左右边距）
                const segmentCount = formState.maxRounds; // 分段数量
                const segmentSize = segmentWidth / segmentCount; // 每段宽度

                // 每轮在各自区间内随机分布，增加一些随机性避免完全重叠
                const baseX = width * 0.1 + d.round * segmentSize;
                const randomOffset =
                  (Math.random() - 0.5) * (segmentSize * 0.6);

                return baseX + randomOffset;
              })
          )
          .force(
            'y',
            d3
              .forceY()
              .strength(0.1)
              .y((d) => {
                // y轴可以更自由分布，但仍然保持一定的聚集性
                if (d.id === 'initial-video') return height / 2;

                // 邪典视频和普通视频在y轴上有所区分
                const baseY = height / 2;
                const randomOffset = (Math.random() - 0.5) * (height * 0.6);

                // 邪典视频偏上，普通视频偏下
                const evilOffset = d.isEvil ? -height * 0.1 : height * 0.1;

                return baseY + randomOffset + evilOffset;
              })
          );

        // 添加轮次区域指示器
        const rounds = Array.from(
          { length: formState.maxRounds + 1 },
          (_, i) => i
        );

        // 绘制轮次区域背景和标签
       /* rounds.forEach((round) => {
          if (round === 0) {
            // 初始视频区域
            const x = width * 0.02;
            const widthSegment = width * 0.15;

            // 添加背景
            g.append('rect')
              .attr('x', x)
              .attr('y', height * 0.1)
              .attr('width', widthSegment)
              .attr('height', height * 0.8)
              .attr('fill', '#f0f0f0')
              .attr('opacity', 0.2)
              .attr('rx', 5)
              .attr('ry', 5);

            // 添加标签
            g.append('text')
              .attr('x', x + widthSegment / 2)
              .attr('y', height * 0.05)
              .attr('text-anchor', 'middle')
              .text('初始视频')
              .style('font-size', '14px')
              .style('font-weight', 'bold')
              .style('fill', '#ff4d4f');
          } else {
            // 计算每轮的x轴位置
            const segmentWidth = width * 0.8;
            const segmentCount = formState.maxRounds;
            const segmentSize = segmentWidth / segmentCount;
            const x = width * 0.1 + (round - 1) * segmentSize;

            // 添加背景
            g.append('rect')
              .attr('x', x)
              .attr('y', height * 0.1)
              .attr('width', segmentSize)
              .attr('height', height * 0.8)
              .attr('fill', round % 2 === 0 ? '#f6f6f6' : '#f0f0f0')
              .attr('opacity', 0.2)
              .attr('rx', 5)
              .attr('ry', 5);

            // 添加标签
            g.append('text')
              .attr('x', x + segmentSize / 2)
              .attr('y', height * 0.05)
              .attr('text-anchor', 'middle')
              .text(`第${round}轮`)
              .style('font-size', '14px')
              .style('font-weight', 'bold')
              .style('fill', '#666');
          }
        }); */

        // 绘制连接线
        const link = g
          .append('g')
          .attr('class', 'links')
          .selectAll('line')
          .data(networkData.links)
          .enter()
          .append('line')
          .attr('stroke-width', (d) => Math.sqrt(d.value) * 1.5)
          .attr('stroke', '#999')
          .attr('stroke-opacity', 0.6);

        // 创建节点组
        const node = g
          .append('g')
          .attr('class', 'nodes')
          .selectAll('g')
          .data(networkData.nodes)
          .enter()
          .append('g')
          .call(
            d3
              .drag()
              .on('start', dragstarted)
              .on('drag', dragged)
              .on('end', dragended)
          );
        // 添加圆形节点
        node
          .append('circle')
          .attr('r', (d) => {
            if (d.round === 0) {
              return 15;
            }
            return d.isEvil ? 12 : 10;
          })
          .attr('fill', (d) => getNodeColor(d))
          .attr('stroke', (d) => (d.isDuplicate ? '#722ed1' : '#fff'))
          .attr('stroke-width', (d) => (d.isDuplicate ? 3 : 1.5));

        // 添加标题文本
        node
          .append('text')
          .attr('dx', 15)
          .attr('dy', 4)
          .attr('class', 'node-title')
          .text((d) => {
            // 截断长标题
            if (d.title.length > 15) {
              return `${d.title.substring(0, 15)}...`;
            }
            return d.title;
          })
          .style('fill', (d) => (d.isEvil ? '#ff7a45' : '#1890ff'))
          .style('font-weight', (d) => (d.isEvil ? 'bold' : 'normal'))
          .style('font-size', '12px')
          .style('pointer-events', 'none');

        // 添加节点点击事件
        node.on('click', (event, d) => {
          selectedVideo.value = d;
          videoDetailVisible.value = true;
        });

        // 添加节点悬停效果
        node
          .on('mouseover', function mouseover(event, d) {
            d3.select(this)
              .select('circle')
              .attr('r', (nodeData) => {
                if (nodeData.round === 0) {
                  return 18;
                }
                return nodeData.isEvil ? 15 : 13;
              });

            // 高亮相关连接
            link
              .style('stroke', (l) => {
                if (l.source.id === d.id || l.target.id === d.id) {
                  return d.isEvil ? '#ff7a45' : '#1890ff';
                }
                return '#999';
              })
              .style('stroke-opacity', (l) => {
                if (l.source.id === d.id || l.target.id === d.id) {
                  return 1;
                }
                return 0.2;
              })
              .style('stroke-width', (l) => {
                if (l.source.id === d.id || l.target.id === d.id) {
                  return Math.sqrt(l.value) * 2;
                }
                return Math.sqrt(l.value) * 1.5;
              });

            // 高亮相关节点
            node.select('circle').style('opacity', (n) => {
              // 检查是否有连接到当前节点
              const connected = networkData.links.some(
                (l) =>
                  (l.source.id === d.id && l.target.id === n.id) ||
                  (l.source.id === n.id && l.target.id === d.id)
              );
              return n.id === d.id || connected ? 1 : 0.3;
            });

            node.select('text').style('opacity', (n) => {
              const connected = networkData.links.some(
                (l) =>
                  (l.source.id === d.id && l.target.id === n.id) ||
                  (l.source.id === n.id && l.target.id === d.id)
              );
              return n.id === d.id || connected ? 1 : 0.3;
            });
          })
          .on('mouseout', function mouseout() {
            d3.select(this)
              .select('circle')
              .attr('r', (d) => {
                if (d.round === 0) {
                  return 15;
                }
                return d.isEvil ? 12 : 10;
              });

            // 恢复连接样式
            link
              .style('stroke', '#999')
              .style('stroke-opacity', 0.6)
              .style('stroke-width', (d) => Math.sqrt(d.value) * 1.5);

            // 恢复节点样式
            node.select('circle').style('opacity', 1);
            node.select('text').style('opacity', 1);
          });

        // 更新力导向图
        simulation.on('tick', () => {
          link
            .attr('x1', (d) => d.source.x)
            .attr('y1', (d) => d.source.y)
            .attr('x2', (d) => d.target.x)
            .attr('y2', (d) => d.target.y);

          node.attr('transform', (d) => `translate(${d.x},${d.y})`);
        });

        // 拖拽事件处理函数
        function dragstarted(event, d) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        }

        function dragged(event, d) {
          d.fx = event.x;
          d.fy = event.y;
        }

        function dragended(event, d) {
          if (!event.active) simulation.alphaTarget(0);
          // 只有初始节点和邪典节点保持固定位置
          if (d.id !== 'initial-video' && !d.isEvil) {
            d.fx = null;
            d.fy = null;
          }
        }

        // 添加热力，使节点更快分散
        simulation.alpha(1).alphaDecay(0.02).restart();
        simulation.alphaTarget(0.3).restart();
        setTimeout(() => {
          if (simulation) {
            simulation.alphaTarget(0);
          }
        }, 1000);
      };

      // 重置网络
      const resetNetwork = () => {
        if (svg) {
          d3.select(svg.node().parentNode).select('svg').remove();
          svg = null;
        }

        if (simulation) {
          simulation.stop();
          simulation = null;
        }

        networkData = {
          nodes: [],
          links: [],
        };

        currentRound.value = 0;
        totalVideos.value = 0;
        evilVideosCount.value = 0;
        evilRate.value = 0;
      };
      // 定义 startExpansion 函数
      const startExpansion = () => {
        // 生成网络数据
        generateNetworkData();
        // 渲染网络图
        renderNetwork();
      };

      // 组件挂载时初始化
      onMounted(() => {
        // 设置默认初始视频
        formState.initialVideo = '危险游戏 @抖音青少年 @抖音创作小助手 @抖音小助手';
        formState.maxRounds = 3;
      });

      // 组件卸载时清理
      onUnmounted(() => {
        resetNetwork();
      });

      return {
        networkContainer,
        formState,
        currentRound,
        totalVideos,
        evilVideosCount,
        evilRate,
        startExpansion, // 确保导出 startExpansion 函数
        resetNetwork,
        videoDetailVisible,
        selectedVideo,
      };
    },
  };
</script>

<style scoped>
  .video-expansion-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 16px;
    background-color: var(--color-bg-2);
    border-radius: 4px;
  }

  .control-panel {
    margin-bottom: 16px;
    padding: 16px;
    background-color: var(--color-bg-1);
    border-radius: 4px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 5%);
  }

  .network-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 16px;
    padding: 16px;
    background-color: var(--color-bg-1);
    border-radius: 4px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 5%);
  }

  .network-container {
    flex: 1;
    min-height: 500px;
    overflow: hidden;
    background-color: var(--color-bg-1);
    border-radius: 4px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 5%);
  }

  .expansion-legend {
    display: flex;
    justify-content: center;
    margin-top: 16px;
    padding: 8px;
    background-color: var(--color-bg-1);
    border-radius: 4px;
    box-shadow: 0 2px 8px rgb(0 0 0 / 5%);
  }

  .legend-item {
    display: flex;
    align-items: center;
    margin: 0 12px;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    margin-right: 6px;
    border-radius: 50%;
  }

  /* 节点样式 */
  :deep(.nodes circle) {
    cursor: pointer;
    transition: r 0.2s ease;
  }

  :deep(.links line) {
    transition: stroke-width 0.2s ease, stroke-opacity 0.2s ease;
  }
</style>
