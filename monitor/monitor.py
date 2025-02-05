# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
from playwright.async_api import async_playwright
import asyncio
import json
import os
import fcntl
import sys
import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest
import time
import html
import signal
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置为 DEBUG 以查看更多调试信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/root/monitor/monitor_script.log')
    ]
)
logger = logging.getLogger()

def acquire_lock(lock_file_path='/root/monitor/monitor_script.lock', retries=3, wait_time=5):
    """尝试获取文件锁，若失败则重试。"""
    lock_file = open(lock_file_path, 'w')
    attempt = 0
    while attempt < retries:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("成功获取文件锁。")
            return lock_file
        except IOError:
            logger.warning(f"第 {attempt + 1} 次尝试获取锁失败，{wait_time} 秒后重试...")
            attempt += 1
            time.sleep(wait_time)
    logger.error("多次尝试后仍无法获取文件锁。")
    sys.exit(1)

def handle_shutdown(signum, frame):
    """处理脚本关闭信号，释放文件锁。"""
    logger.info("正在优雅关闭...")
    if 'lock_file' in globals():
        lock_file.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def get_random_user_agent():
    """返回一个随机的 User-Agent。"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    ]
    return random.choice(user_agents)

async def fetch_page_content(url, enable_javascript=False, retries=3, expected_title=None):
    """提取整个页面内容，支持动态启用/禁用 JavaScript。"""
    for attempt in range(retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=get_random_user_agent(),  # 随机 User-Agent
                    java_script_enabled=enable_javascript  # 动态启用/禁用 JavaScript
                )
                page = await context.new_page()

                # 模拟人类行为：随机延迟
                response = await page.goto(url, wait_until='networkidle', timeout=120000)
                if response.status != 200:
                    logger.warning(f"HTTP 请求失败，状态码: {response.status}。URL: {url}")
                    await browser.close()
                    return None

                await page.wait_for_timeout(random.randint(3000, 7000))  # 随机延迟 3-7 秒

                # 模拟鼠标移动
                await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                await page.wait_for_timeout(random.randint(1000, 3000))  # 随机延迟 1-3 秒

                # 如果启用 JavaScript，模拟点击 "Order" 按钮
                if enable_javascript:
                    await page.click('button:has-text("Order")')  # 假设按钮文本为 "Order"
                    await page.wait_for_timeout(5000)  # 等待页面加载

                # 提取整个页面内容
                page_content = await page.content()

                # 检查 <title> 标签内容
                if expected_title:
                    soup = BeautifulSoup(page_content, 'html.parser')
                    title_tag = soup.find('title')
                    if not title_tag or expected_title not in title_tag.text:
                        logger.warning(f"页面标题不符合预期。URL: {url}")
                        await browser.close()
                        return None

                await browser.close()
                logger.info(f"成功提取页面内容。URL: {url}, JavaScript: {'启用' if enable_javascript else '禁用'}")
                return page_content
        except Exception as e:
            logger.warning(f"第 {attempt + 1} 次尝试失败，URL: {url}，错误: {e}")
            if attempt == retries - 1:
                logger.error(f"经过 {retries} 次尝试后仍无法获取 URL: {url} 的内容")
                return None
            await asyncio.sleep(5)  # 重试前等待

def parse_stock(page_content, out_of_stock_text, url, enable_javascript):
    """根据页面内容解析库存信息。"""
    try:
        if page_content is None:
            logger.warning(f"页面内容为空。URL: {url}")
            return False

        soup = BeautifulSoup(page_content, 'html.parser')

        # 优先检查页面内容
        if soup.find(string=lambda text: text and out_of_stock_text in text):
            logger.info(f"无库存（根据页面内容）。URL: {url}")
            return False

        # 如果启用 JavaScript，继续检查 errors 数组
        if enable_javascript:
            script_tag = soup.find_all('script', string=re.compile(r'(?:var|let|const)\s+errors\s*=\s*\['))
            if not script_tag:
                logger.warning(f"未找到包含 errors 数组的脚本标签。URL: {url}")
                return True  # 假设有库存

            script_content = script_tag[0].string
            logger.debug(f"脚本内容: {script_content}")  # 调试输出
            match = re.search(r'(?:var|let|const)\s+errors\s*=\s*(\[.*?\]);', script_content, re.DOTALL)
            if not match:
                logger.warning(f"未找到 errors 数组的内容。URL: {url}")
                return True  # 假设有库存

            errors_array = match.group(1)
            try:
                errors_list = json.loads(errors_array)  # 使用 json.loads 解析
            except json.JSONDecodeError as e:
                logger.error(f"解析 errors 数组时出错。URL: {url}, 错误: {e}")
                return True  # 假设有库存

            logger.debug(f"errors 数组内容: {errors_list}")

            # 如果 errors 数组包含 out_of_stock_text，则无库存
            if errors_list and any(out_of_stock_text in error for error in errors_list):
                logger.info(f"无库存（根据 errors 数组）。URL: {url}")
                return False
            else:
                logger.info(f"有库存（根据 errors 数组）。URL: {url}")
                return True
        else:
            logger.info(f"有库存（根据页面内容）。URL: {url}")
            return True
    except Exception as e:
        logger.error(f"解析页面内容时出错。URL: {url}, 错误: {e}")
        return True  # 假设解析错误意味着有库存

async def send_notification(config, merchant, stock, in_stock, message_id=None):
    """发送 Telegram 通知。"""
    bot = Bot(token=config['telegram_token'])
    title = f"{merchant['name']}-{stock['title']}"
    tag = html.escape(merchant['tag'])
    price = html.escape(stock['price'])
    hardware_info = f"<a href=\"{stock['buy_url']}\">{html.escape(stock['hardware_info'])}</a>"
    stock_info = f'🛒 <a href="{stock["buy_url"]}">库   存：{"有 - 抢购吧！" if in_stock else "无 - 已售罄！"}</a>'
    buy_link = f"🔗 <s>{stock['buy_url']}</s>" if not in_stock else f"🔗 {stock['buy_url']}"
    annual_coupon = f"🎁 优惠码：<code>{merchant['coupon_annual']}</code>" if merchant.get('coupon_annual') else ""
    coupon_section = f"\n\n{annual_coupon}\n\n" if annual_coupon else "\n\n"

    message = (
        f"<b>{title}</b>\n\n"
        f"💰 价  格: <b>{price}</b>\n\n"
        f"📜 配  置：{hardware_info}\n\n"
        f"ℹ️ {tag}"
        f"{coupon_section}"
        f"{stock_info}\n\n"
        f"{buy_link}"
    )

    try:
        if in_stock:
            sent_message = await bot.send_message(
                chat_id=config['telegram_chat_id'],
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            return sent_message.message_id
        elif message_id:
            await bot.edit_message_text(
                chat_id=config['telegram_chat_id'],
                message_id=message_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
    except BadRequest as e:
        logger.error(f"发送或编辑消息时出错: {e}")
    return None

async def load_config(filename='/root/monitor/config.json'):
    """加载配置文件。"""
    if not os.path.exists(filename):
        logger.error(f"配置文件 {filename} 不存在。")
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as f:
        logger.info(f"已加载配置文件: {filename}")
        return json.load(f)

async def load_stock_status(filename='/root/monitor/stock_status.json'):
    """加载库存状态。如果文件不存在，自动初始化。"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Initialize an empty dictionary for stock status
        return {}

async def save_stock_status(stock_status, filename='/root/monitor/stock_status.json'):
    """保存库存状态，包括最后检查时间。"""
    for unique_identifier, status in stock_status.items():
        # Ensure that 'last_check' is always updated to the current time (timestamp)
        status['last_check'] = int(time.time())  # Store timestamp for the last check
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stock_status, f, ensure_ascii=False, indent=4)

async def initialize_stock_status(config, stock_status):
    """初始化库存状态，如果之前没有状态则生成默认状态。"""
    for merchant in config['merchants']:
        for stock in merchant['stock_urls']:
            unique_identifier = stock['title']
            if unique_identifier not in stock_status:
                # Initialize stock entry with default values
                stock_status[unique_identifier] = {
                    'in_stock': True,
                    'message_id': None,
                    'last_check': None  # First time check, no last_check yet
                }
    return stock_status

async def main():
    """主函数。"""
    lock_file = acquire_lock()

    try:
        while True:
            config = await load_config()  # 每次循环重新加载配置文件
            stock_status = await load_stock_status()

            # Initialize stock status with default values if not present
            stock_status = await initialize_stock_status(config, stock_status)

            tasks = []
            for merchant in config['merchants']:
                if merchant['enabled']:
                    for stock in merchant['stock_urls']:
                        enable_javascript = stock.get('enable_javascript', False)
                        expected_title = stock.get('expected_title', None)
                        tasks.append(fetch_page_content(stock['check_url'], enable_javascript, expected_title=expected_title))
            results = await asyncio.gather(*tasks)
            result_index = 0

            for merchant in config['merchants']:
                if not merchant['enabled']:
                    continue
                for stock in merchant['stock_urls']:
                    page_content = results[result_index]
                    result_index += 1

                    if page_content is None:
                        continue

                    in_stock = parse_stock(page_content, merchant['out_of_stock_text'], stock['check_url'], stock.get('enable_javascript', False))
                    unique_identifier = stock['title']
                    previous_status = stock_status.get(unique_identifier, {'in_stock': True})

                    if in_stock and not previous_status['in_stock']:
                        message_id = await send_notification(config, merchant, stock, in_stock)
                        stock_status[unique_identifier] = {'in_stock': True, 'message_id': message_id, 'last_check': int(time.time())}
                    elif not in_stock and previous_status['in_stock']:
                        await send_notification(config, merchant, stock, in_stock, previous_status['message_id'])
                        stock_status[unique_identifier] = {'in_stock': False, 'message_id': previous_status['message_id'], 'last_check': int(time.time())}

            await save_stock_status(stock_status)
            await asyncio.sleep(config.get('check_interval', 600))

    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        lock_file.close()

if __name__ == '__main__':
    asyncio.run(main())
