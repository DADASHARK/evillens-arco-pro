<template>
  <a-card class="general-card">
    <a-space direction="vertical" fill :size="16">
      <!-- 邪典视频定义 -->
      <div class="section">
        <div class="section-title">邪典视频定义</div>
        <div class="section-content">
          邪典视频是指以儿童熟悉的卡通人物、经典动画形象或教育形式为伪装，实则包含暴力、血腥、色情、虐待等有害元素的视频或动画短片。
        </div>
      </div>

      <!-- 背景引入 -->
      <div class="section">
        <div class="section-title">背景引入</div>
        <div class="section-content">
          随着互联网的快速发展和移动设备的普及，短视频平台已深度融入当代儿童的日常生活。平台推荐机制推动下，部分创作者伪装成“儿童益智动画”，实则在内容中融入暴力、性暗示、恐怖画面等不适宜内容，构成“邪典视频”现象。
          <br />
          本研究团队在多维度内容审计中发现，部分创作者通过标签伪装策略（如标注"儿童益智动画""早教视频"等合规标识），利用AI对经典动画IP实施恶意篡改或借助AI合成具有感官不适性与价值观偏差的内容，形成新型隐蔽性传播风险。
          <br /><br />
          当检索关键词"儿童益智动画"时，平台推荐算法推送中就有视频对小猪佩奇进行“魔改”，视频中，猪妈妈和佩奇的脸被严重扭曲和变形，并且情节为妈妈使用“金钱的力量”将佩奇“救上来”，
          强化了拜金主义的价值导向，对未成年人的认知发展构成潜在威胁：
          <div class="img-wrapper">
            <img
              src="@/assets/images/kepu1.png"
              alt="艾莎门事件截图"
              class="parallax-img"
            />
            <div class="img-caption">图片：小猪佩奇邪典内容</div>
          </div>
          <br /><br />
          部分时长偏长的视频以正常的动画开头，但中间会忽然穿插猎奇画面，比如这个全身遍布血管，身体扭曲被奇怪的拼接的“美人鱼”：
          <div class="img-wrapper">
            <img
              src="@/assets/images/kepu2.png"
              alt="小猪佩奇魔改版截图"
              class="parallax-img"
            />
            <div class="img-caption">图片：魔改美人鱼截图</div>
          </div>
          <br /><br />
          还有的使用AI将动画人物进行恶意改动，如图1-6的恐怖版“Hellokitty”:
          <div class="img-wrapper">
            <img
              src="@/assets/images/kepu3.png"
              alt="邪典化Hello Kitty形象"
              class="parallax-img"
            />
            <div class="img-caption">图片：邪典化Hello Kitty形象</div>
          </div>
        </div>
      </div>

      <!-- 儿童定义 -->
      <div class="section">
        <div class="section-title">儿童定义</div>
        <div class="section-content">
          依据 WHO
          儿童生长发育标准及《中国未成年人保护法》对低龄儿童的优先保护原则划定，特指
          12
          周岁（含）以下人群。该年龄段的认知发展特征（如有限的风险评估能力）使其更易受到不良视听内容的心理侵害。
        </div>
      </div>

      <!-- 邪典视频危害 -->
      <div class="section">
        <div class="section-title">邪典视频危害</div>
        <ul class="section-list">
          <li>诱发恐惧、焦虑、暴力等负面情绪，影响心理健康</li>
          <li>误导价值观，模糊是非观念，影响正常成长</li>
          <li>可能导致模仿危险行为，带来人身安全隐患</li>
          <li>破坏家庭关系，增加家长监管难度</li>
        </ul>
      </div>

      <!-- 警告信息 -->
      <div class="section warning">
        <div class="warning-icon">⚠️</div>
        <div class="warning-text"> 及时识别和防范邪典视频的传播！ </div>
      </div>
    </a-space>
  </a-card>
</template>

<script lang="ts" setup>
  import useThemes from '@/hooks/themes';

  useThemes();
</script>

<style scoped lang="less">
  .general-card {
    background-color: rgb(10 25 47 / 85%) !important;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgb(0 0 0 / 30%);
    backdrop-filter: blur(8px);

    :deep(.arco-card-body) {
      padding: 24px 28px;
      color: rgb(255 255 255 / 85%);
    }

    .arco-card-header {
      .arco-card-header-title {
        color: #64ffda;
        font-weight: 600;
        font-size: 24px;
        letter-spacing: 0.5px;

        &.dark-mode & {
          color: #49b1f5;
        }
      }
    }

    .section {
      display: flex;
      flex-direction: column;
      margin-bottom: 28px;

      .section-title {
        position: relative;
        margin-top: 24px;
        margin-bottom: 16px;
        padding-left: 14px;
        color: #64ffda;
        font-weight: 600;
        font-size: 20px;
        letter-spacing: 0.8px;

        &::before {
          position: absolute;
          top: 50%;
          left: 0;
          width: 4px;
          height: 18px;
          background: #64ffda;
          border-radius: 2px;
          transform: translateY(-50%);
          content: '';
        }

        &.dark-mode & {
          color: #49b1f5;
        }
      }

      .section-content {
        margin-bottom: 16px;
        color: rgb(255 255 255 / 90%);
        font-size: 15px;
        line-height: 1.8;
        letter-spacing: 0.3px;
        text-align: justify;

        strong {
          color: #b2e9ff;
          font-weight: 500;
        }
      }

      .img-wrapper {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 24px 0 16px;

        &::after {
          position: absolute;
          bottom: -8px;
          left: 50%;
          width: 40%;
          height: 1px;
          background: linear-gradient(
            90deg,
            transparent,
            rgb(100 255 218 / 50%),
            transparent
          );
          transform: translateX(-50%);
          content: '';
        }
      }

      .parallax-img {
        width: 85%;
        max-width: 450px;
        margin-bottom: 12px;
        border: 1px solid rgb(100 255 218 / 15%);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgb(0 0 0 / 35%);
        transition: all 0.5s cubic-bezier(0.2, 1, 0.3, 1);
      }

      .parallax-img:hover {
        border-color: rgb(100 255 218 / 30%);
        box-shadow: 0 12px 40px rgb(0 0 0 / 45%);
        transform: scale(1.03) translateY(-6px);
      }

      .img-caption {
        margin: 8px 0 12px;
        color: #b2e9ff;
        font-weight: 500;
        font-size: 14px;
        letter-spacing: 1px;
        text-align: center;
        opacity: 0.9;
      }

      .section-list {
        margin: 8px 0 20px;
        padding-left: 8px;
        color: rgb(255 255 255 / 90%);
        font-size: 15px;
        line-height: 1.8;
        list-style-type: none;

        li {
          position: relative;
          margin-bottom: 12px;
          padding-left: 22px;

          &::before {
            position: absolute;
            top: 0;
            left: 0;
            color: #64ffda;
            font-size: 18px;
            line-height: 1.5;
            content: '•';
          }
        }
      }
    }

    .warning {
      display: flex;
      align-items: center;
      margin-top: 10px;
      padding: 16px 20px;
      color: #64ffda;
      font-weight: 500;
      font-size: 15px;
      letter-spacing: 0.5px;
      background: rgb(15 40 70 / 70%);
      border-left: 4px solid #64ffda;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgb(0 0 0 / 15%);

      .warning-icon {
        margin-right: 12px;
        font-size: 20px;
      }

      &.dark-mode & {
        color: #5ca8e7;
        background: #2a2d30;
        border-left-color: #5ca8e7;
      }
    }
  }

  // 添加一些动画效果
  @keyframes fadeIn {
    from {
      transform: translateY(10px);
      opacity: 0;
    }

    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .section {
    animation: fadeIn 0.6s ease-out forwards;
  }
</style>
