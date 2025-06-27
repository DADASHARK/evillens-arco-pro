import os
import argparse
import shutil
import logging
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText  # 新增导入
from email import encoders
from config import SMTP_USERNAME, SMTP_PASSWORD, SMTP_SERVER,EMAIL_TO, EMAIL_SUBJECT, OUTPUT_DIR,SMTP_PORT # 导入配置常量

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def zip_directory(folder_path, output_path):
    """将指定目录打包为ZIP文件"""
    shutil.make_archive(output_path, 'zip', folder_path)
    return output_path + '.zip'


def send_email(attachment_path, subject=None, file_count=0, timestamp=None):
    """发送带品牌化HTML模板并包含团队署名的邮件"""
    sender = SMTP_USERNAME
    recipient = EMAIL_TO
    password = SMTP_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject or EMAIL_SUBJECT

    # 时间戳格式化
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else '未知时间'

    # 构建HTML内容（含内联CSS）
    html_content = f"""
    <html>
      <head>
        <style>
          /* 基础样式 */
          body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 700px;
            margin: 0 auto;
            padding: 0 20px;
          }}
          .header {{
            background: linear-gradient(to right, #2c3e50, #34495e);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
          }}
          .header h1 {{
            margin: 0;
            font-size: 24px;
            letter-spacing: 1px;
          }}
          .sub-header {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 8px;
          }}
          .content {{
            padding: 20px;
            background: #f9f9f9;
            border: 1px solid #eee;
            border-top: none;
            border-radius: 0 0 8px 8px;
          }}
          .section {{
            margin-bottom: 20px;
          }}
          .stats {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
          }}
          ul {{ 
            list-style-type: none;
            padding-left: 0;
          }}
          li {{ 
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
          }}
          .icon {{
            position: absolute;
            left: 0;
            top: 3px;
            color: #e74c3c;
          }}
          .footer {{
            margin-top: 30px;
            font-size: 0.9em;
            color: #7f8c8d;
            text-align: center;
          }}
          .team {{
            font-weight: bold;
            color: #2980b9;
          }}
          .shield {{
            color: #27ae60;
            font-weight: bold;
          }}
          /* 响应式设计 */
          @media only screen and (max-width: 600px) {{
            .header, .content {{
              padding: 15px;
            }}
          }}
        </style>
      </head>
      <body>
        <!-- 邮件头部 -->
        <div class="header">
          <h1>🛡️ EvilLens</h1>
          <div class="sub-header">基于多模态的儿童邪典视频挖掘治理平台</div>
        </div>

        <!-- 邮件正文 -->
        <div class="content">
          <!-- 概述部分 -->
          <div class="section">
            <p>尊敬的管理员您好：</p>
            <p>系统已检测到潜在违规内容，以下是检测摘要：</p>
          </div>

          <!-- 统计信息 -->
          <div class="section stats">
            <ul>
              <li><span class="icon">⏱️</span>检测时间：{timestamp_str}</li>
              <li><span class="icon">📁</span>发现可疑视频：{file_count} 个</li>
            </ul>
          </div>

          <!-- 治理说明 -->
          <div class="section">
            <p>附件中包含完整的检测文件报告，请及时进行人工复核。</p>
            <ol style="padding-left: 25px;">
            
            </ol>
          </div>
        </div>

        <!-- 邮件尾部 -->
        <div class="footer">
          <p>此邮件由EvilLens智能监测系统自动发出</p>
          <p>© 2025 SCU幼儿园五星上将 团队  所有检测结果均受<a href="#" style="color:#3498db; text-decoration:none;">数据安全法</a>保护</p>
        </div>
      </body>
    </html>
    """

    # 添加HTML正文
    msg.attach(MIMEText(html_content, 'html'))

    # 添加附件
    try:
        with open(attachment_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attachment_path)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)
    except Exception as e:
        logging.error(f"❌ 附件处理失败: {str(e)}")
        return False

    # 发送邮件
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        logging.info("✅ 邮件发送成功")
        return True
    except Exception as e:
        logging.error(f"❌ 邮件发送失败: {str(e)}")
        return False


def send_mail_api(zip_name=None):
    """供API调用的邮件发送函数（封装原main逻辑）"""
    default_zip = f"output_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    zip_filename = zip_name or default_zip

    folder_to_zip = OUTPUT_DIR
    if not os.path.isdir(folder_to_zip):
        logging.error(f"❌ 目录不存在: {folder_to_zip}")
        return False, "检测目录不存在"

    # 统计images子目录文件数
    image_folder = os.path.join(folder_to_zip, 'images')
    file_count = len([f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]) if os.path.isdir(image_folder) else 0

    # 打包目录
    try:
        zip_path = os.path.join(os.getcwd(), zip_filename)
        zip_filepath = zip_directory(folder_to_zip, zip_path)
    except Exception as e:
        return False, f"打包失败: {str(e)}"

    # 发送邮件
    success = send_email(zip_filepath, file_count=file_count, timestamp=datetime.datetime.now())

    # 清理临时ZIP文件
    if success:
        try:
            os.remove(zip_filepath)
        except Exception as e:
            return True, f"邮件发送成功，但清理临时文件失败: {str(e)}"
    return success, "邮件发送成功" if success else "邮件发送失败"

if __name__ == "__main__":
    main()