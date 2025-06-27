#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序 B：用户搜索切换模块（基于 Selenium 实现）
功能说明：
  1. 读取存放用户搜索链接的 txt 文件，每行格式为：
       https://www.douyin.com/search/xxx?type=user   (xxx 为用户名)
  2. 针对每个搜索链接：
       - 打开页面并等待搜索结果加载
       - 遍历页面中所有目标元素（嵌套结构：span.j5WZJdp > span > span > span > span），
         检查其文本是否与用户名一致；
       - 若匹配，则点击该元素进入用户主页；
       - 进入主页后调用爬取主页信息的功能（此部分后续再实现，目前留空）；
       - 将返回的用户信息（包含用户基本信息与视频信息）保存到 JSON 文件中，文件名为用户ID
         （若未获取到，则使用 unknown_用户名 命名）。
  3. 整个过程中保证已登录状态（启动后要求用户登录后按回车继续）及日志记录。
"""

import os
import re
import json
import time
import logging
from urllib.parse import quote
from bs4 import BeautifulSoup
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 日志配置
log_file = "process.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def wait_for_user_homepage(driver, timeout):
    """
    等待页面加载到用户主页，根据页面中是否存在用户信息特有的元素进行判断。
    判断依据： div[class="mZmVWLzR"] 且 data-e2e="user-info"
    """
    for i in range(timeout):
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        user_container = soup.find("div", attrs={"class": "mZmVWLzR", "data-e2e": "user-info"})
        if user_container:
            logging.info("检测到用户主页加载成功。")
            return True
        time.sleep(1)
    logging.error("等待用户主页加载超时！")
    return False

def crawl_user_homepage(driver):
    """
    爬取用户主页下所有视频信息与用户信息，并返回 JSON 格式的数据。

    抓取内容包括：
      1. 用户基本信息：昵称、年龄、关注数、粉丝数、获赞数、抖音号、IP 属地
      2. 视频信息：视频ID、标题、视频标签、点赞数
    """
    # 首先通过 find_element 定位到用户详细信息容器
    try:
        wait = WebDriverWait(driver, 3)
        user_container = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='user_detail_element']/div/div[2]/div[2]")
        ))
    except Exception as e:
        logging.error("等待用户信息容器超时：%s", e)
        return {
            "user_info": {},
            "videos": []
        }

    def convert_number(text):
        try:
            text = text.strip()
            if text.endswith("万"):
                number = float(text[:-1].strip()) * 10000
                return int(number)
            elif text.endswith("亿"):
                number = float(text[:-1].strip()) * 100000000
                return int(number)
            else:
                return int(text.replace(',', ''))
        except Exception as e:
            logging.error("转换数字 '%s' 失败: %s", text, e)
            return text

    # 使用 user_container 在内部查找各个元素

    # 提取昵称，直接从 h1 标签中获取文本
    try:
        nickname_elem = user_container.find_element(
            By.XPATH,
            ".//div[1]/h1"
        )
        nickname = nickname_elem.text.strip()
    except Exception as e:
        logging.error("未找到 nickname 元素：%s", e)
        nickname = ""

    # 提取年龄（去掉 text() 的部分）
    try:
        age_elem = user_container.find_element(
            By.XPATH,
            ".//p/span[3]/span"
        )
        age_text = age_elem.text.strip()
        match = re.match(r'(\d+)', age_text)
        age = match.group(1) if match else ""
    except Exception as e:
        logging.error("未找到年龄元素：%s", e)
        age = ""

    # 提取关注数
    try:
        follow_elem = user_container.find_element(
            By.XPATH,
            ".//div[2]/div[1]/div[2]"
        )
        follow_count = convert_number(follow_elem.text.strip())
    except Exception as e:
        logging.error("未找到关注数量元素：%s", e)
        follow_count = ""

    # 提取粉丝数
    try:
        fans_elem = user_container.find_element(
            By.XPATH,
            ".//div[2]/div[2]/div[2]"
        )
        fans_count = convert_number(fans_elem.text.strip())
    except Exception as e:
        logging.error("未找到粉丝数量元素：%s", e)
        fans_count = ""

    # 提取获赞数
    try:
        like_elem = user_container.find_element(
            By.XPATH,
            ".//div[2]/div[3]/div[2]"
        )
        like_count = convert_number(like_elem.text.strip())
    except Exception as e:
        logging.error("未找到获赞数量元素：%s", e)
        like_count = ""

    # 提取抖音号
    try:
        douyin_elem = user_container.find_element(
            By.XPATH,
            ".//p/span[1]"
        )
        douyin_text = douyin_elem.text.strip()
        douyin_id = douyin_text.replace("抖音号", "").strip()
    except Exception as e:
        logging.error("未找到抖音号元素：%s", e)
        douyin_id = ""

    # 提取 IP 属地（注意将 text() 替换为直接定位包含相关文本的标签）
    try:
        ip_elem = user_container.find_element(
            By.XPATH,
            ".//p/span[2]"
        )
        ip_text = ip_elem.text.strip()
        ip_location = ip_text.split("：", 1)[1].strip() if "：" in ip_text else ip_text
    except Exception as e:
        logging.error("未找到 IP 属地元素：%s", e)
        ip_location = ""

    # 提取描述（注意将 text() 替换为直接定位包含相关文本的标签）
    try:
        des_elem = user_container.find_element(
            By.XPATH,
            ".//div[3]/div/span/span/span/span/span[1]/span"
            # "//*[@id='user_detail_element']/div/div[2]/div[2]"
            # //*[@id="user_detail_element"]/div/div[2]/div[2]/div[3]/div/span/span/span/span/span[1]/span
        )
        des_text = des_elem.text.strip()
        # descri = des_text.split("：", 1)[1].strip() if "：" in ip_text else ip_text
    except Exception as e:
        logging.error("未找到 IP 属地元素：%s", e)
        des_text = ""

    user_info = {
        "user_id": douyin_id,
        "user_name": nickname,
        "age": age,
        "follow_count": follow_count,
        "fans_count": fans_count,
        "like_count": like_count,
        "douyin_id": douyin_id,
        "ip_location": ip_location,
        "self_description": des_text
    }

    # 模拟页面下滑，以加载更多视频内容，每次下滑后等待1秒，直至页面无法继续下滑
    MAX_SCROLL = 100      # 防止出现无限循环的上限
    scroll_pause_time = 1 # 每次下滑后等待1秒
    scroll_count = 0
    while scroll_count < MAX_SCROLL:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            logging.info("页面已到底部，无需继续下滑。")
            break

        scroll_count += 1

# 页面下滑结束后，再重新获取页面元素以保证加载所有内容

    # 使用 XPath 定位所有视频信息容器（li 元素）
    try:
        video_elements = driver.find_elements(
            By.XPATH,
            "//*[@id='user_detail_element']/div/div[3]/div/div/div[2]/div[2]/div[2]/ul/li"
        )
    except Exception as e:
        logging.error("未找到视频列表容器：%s", e)
        video_elements = []

    videos = []
    for video_elem in video_elements:
        # 利用每个 li 元素的 outerHTML 构造 BeautifulSoup 对象，
        # 便于提取内部信息
        video_html = video_elem.get_attribute("outerHTML")
        li = BeautifulSoup(video_html, "html.parser")

        video_link_elem = li.find("a", href=True)
        if not video_link_elem:
            logging.error("未找到视频链接元素。")
            continue
        video_href = video_link_elem.get("href", "")
        video_id_match = re.search(r"/video/(\d+)", video_href)
        if video_id_match:
            video_id = video_id_match.group(1)
        else:
            logging.error("视频链接中未匹配到视频ID: %s", video_href)
            continue

        title_elem = li.select_one("a p.Ja95nb2Z.VdTyguLN")
        if title_elem:
            full_text = title_elem.get_text(strip=True)
            parts = full_text.split('#')
            title = parts[0].strip()
            labels = [fragment.strip() for fragment in parts[1:] if fragment.strip()]
        else:
            title = ""
            labels = []
            logging.error("未找到视频标题元素 for video_id %s", video_id)

        likes_elem = li.select_one("span.YzDRRUWc.author-card-user-video-like span.b3Dh2ia8")
        if likes_elem:
            likes_text = likes_elem.get_text(strip=True)
            likes = convert_number(likes_text)
        else:
            likes = 0
            logging.error("未找到视频点赞元素 for video_id %s", video_id)

        video_info = {
            "video_id": video_id,
            "title": title,
            "video_label": labels,
            "likes": likes
        }
        videos.append(video_info)

    logging.info("成功爬取用户信息：%s", user_info)
    return {
        "user_info": user_info,
        "videos": videos
    }

def user_search():
    """
    根据 txt 文件中存放的搜索链接逐行处理：
      1. 获取每行中存放的用户名或搜索关键字；
      2. 构造搜索 URL 并打开页面；
      3. 等待目标 span 元素加载后，通过比对文本确认候选用户；
      4. 模拟点击候选用户，确认是否为目标用户；
      5. 若确认，将调用爬取用户主页信息的函数，并保存结果为 JSON 文件；
      6. 每次处理完毕后返回搜索页面，准备处理下一个用户。
    """
    filepath = input("请输入包含用户搜索链接的txt文件路径（默认：usernames.txt）：").strip()
    if not filepath:
        filepath = r"C:\Users\PENG\Desktop\CS\vscode pyhton\class\compete\test\user\usernames.txt"

    if not os.path.exists(filepath):
        logging.error("指定文件不存在：%s", filepath)
        return

    # 创建保存爬取结果的文件夹
    result_folder = "user_results"
    os.makedirs(result_folder, exist_ok=True)

    # 配置 ChromeOptions
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 添加下面这一行启用不安全的 swiftshader 软件渲染，解决 WebGL 回退问题
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    service = Service(r"D:\Application\chromedriver-win32\chromedriver-win32\chromedriver.exe")
    # 若希望启动无头模式（不显示浏览器界面），可以取消注释以下行：
    # chrome_options.add_argument("--headless")
    # service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(3)
    
    # 打开抖音首页并要求用户手动登录
    driver.get("https://www.douyin.com/")
    config_path = r"C:\Users\PENG\Desktop\CS\vscode pyhton\class\compete\test\user\config_cookies.txt"
    with open(config_path, 'r', encoding='utf8') as f:
        listCookies = json.loads(f.read())
        # Add cookies to the browser
        for cookie in listCookies:
            # Ensure the domain matches the current page's domain
            if 'domain' in cookie:
                cookie['domain'] = '.douyin.com'  # Adjust this to match the domain you are visiting
                driver.add_cookie(cookie)
        # Refresh the page for cookies to take effect
        driver.refresh()
    input("请登录指定账户后，登录完毕后直接敲回车继续：")

    # 读取待搜索的用户名，每行应包含用户名或搜索关键字
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        username = line.strip()
        if not username:
            continue
        # 构造搜索 URL，注意对用户名进行 URL 编码
        search_url = f"https://www.douyin.com/search/{quote(username)}?type=user"
        logging.info("开始搜索用户: %s", username)
        try:
            driver.get(search_url)
        except Exception as e:
            logging.error("打开URL失败：%s, 错误: %s", search_url, e)
            continue

        # 等待目标 span 元素出现，最多等待10秒
        found = False
        elements = []
        for _ in range(10):
            soup = BeautifulSoup(driver.page_source, "html.parser")
            try:
                elements = driver.find_elements(
                    By.XPATH,
                    "//*[@id='search-result-container']/div[3]/ul/li/div/a/div[1]/div/div/p/span/span/span/span/span/span"
                )
                # driver.find_elements(By.XPATH, "//*[@id='search-result-container']/div[3]/ul/li[1]/div/a/div[1]/div/div/p/span/span/span/span/span/span")
            except Exception as e:
                logging.error("查找元素时出错：%s", e)
                elements = []
            if elements:
                found = True
                break
            time.sleep(1)

        if not found:
            logging.warning("在搜索页面未找到目标元素：%s", username)
            continue

        # 收集所有文本与用户名完全一致的候选元素
        candidates = driver.find_elements(
            By.XPATH,
            "//*[@id='search-result-container']/div[3]/ul/li/div/a/div[1]/div/div/p/span/span/span/span/span/span"
        )
        candidates = [elem for elem in candidates if elem.text.strip() == username]
        if not candidates:
            logging.warning("未找到匹配用户名的候选元素：%s", username)
            continue

        found_target = False
        # while candidates:
        #     try:
        #         # 使用 JS 模拟点击候选用户
        #         result = driver.execute_script("arguments[0].click(); return true;", candidates[0])
        #         if not result:
        #             logging.error("模拟点击候选用户元素失败：%s", username)
        #             candidates.pop(0)
        #             continue
        #         logging.info("已模拟点击候选用户：%s", username)
        #     except Exception as e:
        #         logging.error("点击候选用户名元素失败：%s, 错误：%s", username, e)
        #         candidates.pop(0)
        #         continue

        #     # 等待页面跳转加载
        #     time.sleep(2)
            
        #     # 检查是否有新窗口被打开，若有则切换到新窗口
        #     if len(driver.window_handles) > 1:
        #         driver.switch_to.window(driver.window_handles[-1])
            
        #     # 等待用户主页页面加载完成（检查特定的用户主页元素）
        #     if not wait_for_user_homepage(driver, timeout=15):
        #         logging.error("用户主页加载异常，返回搜索页面：%s", username)
        #         # 如果新窗口被打开，则关闭新窗口并切换回搜索页面
        #         if len(driver.window_handles) > 1:
        #             driver.close()
        #             driver.switch_to.window(driver.window_handles[0])
        #         candidates.pop(0)
        #         continue

        #     # 让操作人员确认当前页面是否为目标用户页面
        #     user_input = input("候选用户页面是否为目标用户？(y/n): ").strip().lower()
        #     if user_input == "y":
        #         found_target = True
        #         break   # 退出候选循环
        #     else:
        #         logging.info("操作人员确认当前候选用户不是目标用户，返回上一页面尝试下一个候选。")
        #         # 如果新窗口被打开，则关闭新窗口，并切换回搜索结果页面
        #         if len(driver.window_handles) > 1:
        #             driver.close()
        #             driver.switch_to.window(driver.window_handles[0])
        #         else:
        #             # 若在同一窗口，则使用后退按钮返回
        #             driver.back()
        #         time.sleep(2)
        #         # 再次查找候选元素，同时去掉已经尝试过的第一个候选
        #         candidates = driver.find_elements(
        #             By.XPATH,
        #             "//*[@id='search-result-container']/div[3]/ul/li/div/a/div[1]/div/div/p/span/span/span/span/span/span"
        #         )
        #         candidates = [elem for elem in candidates if elem.text.strip() == username]
        #         if candidates:
        #             candidates.pop(0)
        # if not found_target:
        #     logging.warning("所有候选用户均不符合目标：%s", username)
        #     continue

        # # 可选：等待用户主页加载完成（例如调用 wait_for_user_homepage）
        # # if not wait_for_user_homepage(driver, timeout=10):
        # #     logging.error("用户主页加载异常，跳过该用户：%s", username)
        # #     continue
        
        # # 新代码
        # # 确认目标用户页面后，调用爬取用户主页数据的函数
        # user_data = crawl_user_homepage(driver)
        # user_id = user_data.get("user_info", {}).get("user_id")
        # if not user_id:
        #     user_id = f"unknown_{username}"
        # json_filename = os.path.join(result_folder, f"{user_id}.json")
        # try:
        #     with open(json_filename, "w", encoding="utf-8") as f_out:
        #         json.dump(user_data, f_out, ensure_ascii=False, indent=2)
        #     logging.info("已保存用户信息到 JSON 文件：%s", json_filename)
        # except Exception as e:
        #     logging.error("保存 JSON 文件失败：%s", e)
        
        # # 如果目标用户页面是在新窗口，则关闭该窗口，并切换回搜索页面
        # if len(driver.window_handles) > 1:
        #     driver.close()
        #     driver.switch_to.window(driver.window_handles[0])
        # else:
        #     # 若在同一窗口，则使用后退返回到搜索页面
        #     try:
        #         driver.back()
        #     except Exception as e:
        #         logging.error("返回上一页失败：%s", e)
        # time.sleep(2)
        while candidates:
            try:
                # 使用 JS 模拟点击候选用户
                driver.execute_script("arguments[0].click();", candidates[0])
                logging.info("已模拟点击候选用户：%s", username)
            except Exception as e:
                logging.error("点击候选用户名元素失败：%s, 错误：%s", username, e)
                candidates.pop(0)
                continue

            # 等待页面跳转加载
            time.sleep(2)
            
            # 如果目标用户页面是以新窗口/tab打开，则切换到新窗口
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                logging.info("切换到新窗口，当前URL：%s", driver.current_url)
            
            # 等待用户主页中具有特征的元素加载（例如判断用户信息的标识）
            if not wait_for_user_homepage(driver, timeout=15):
                logging.error("用户主页加载异常，返回搜索页面：%s", username)
                # 新窗口情况：关闭新窗口并切换回搜索页面，否则使用后退返回
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    driver.back()
                candidates.pop(0)
                continue

            # 让操作人员确认当前页面是否为目标用户
            user_input = input("候选用户页面是否为目标用户？(y/n): ").strip().lower()
            if user_input == "y":
                found_target = True
                # 【修改点1】确认后确保当前页面为目标用户页面：
                # 如果候选用户页面是在新窗口中，强制切换至该窗口，并给页面额外等待时间以保证加载稳定
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    logging.info("确认目标用户，保持新窗口进行后续爬取。")
                time.sleep(3)  # 确保页面加载稳定，再进行爬取
                break  # 确认目标后跳出循环
            else:
                logging.info("操作人员确认当前候选用户不是目标用户，返回搜索页面尝试下一个候选。")
                # 如果目标页面在新窗口，则关闭该窗口并切换回搜索页面
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    driver.back()
                time.sleep(2)
                # 重新查找候选元素，并去掉已尝试的第一个候选
                candidates = driver.find_elements(
                    By.XPATH,
                    "//*[@id='search-result-container']/div[3]/ul/li/div/a/div[1]/div/div/p/span/span/span/span/span/span"
                )
                candidates = [elem for elem in candidates if elem.text.strip() == username]
                if candidates:
                    candidates.pop(0)

        if not found_target:
            logging.warning("所有候选用户均不符合目标：%s", username)
            continue

        time.sleep(1)
        # 调用爬取函数，对当前目标用户页（即已确认的候选页面）进行操作（包含下滑加载视频列表）
        user_data = crawl_user_homepage(driver)
        user_id = user_data.get("user_info", {}).get("user_id")
        if not user_id:
            user_id = f"unknown_{username}"
        json_filename = os.path.join(result_folder, f"{user_id}.json")
        try:
            with open(json_filename, "w", encoding="utf-8") as f_out:
                json.dump(user_data, f_out, ensure_ascii=False, indent=2)
            logging.info("已保存用户信息到 JSON 文件：%s", json_filename)
        except Exception as e:
            logging.error("保存 JSON 文件失败：%s", e)

        # -------------------------------
        # 【修改点2】返回搜索页面：
        # 如果目标用户页面是在新窗口中，则关闭该窗口并切换回原窗口，
        # 否则（同一窗口）使用后退按钮返回
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            try:
                driver.back()
            except Exception as e:
                logging.error("返回上一页失败：%s", e)
        time.sleep(2)

    logging.info("所有用户搜索流程已结束。")
    driver.quit()

if __name__ == "__main__":
    user_search()