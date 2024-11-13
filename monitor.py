import cfscrape
from bs4 import BeautifulSoup
import asyncio
import json
import os
import re
import fcntl
import sys
import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest
import time
import html  # 用于转义 HTML 字符

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到控制台
        logging.FileHandler('/tmp/monitor_script.log')  # 也写入到文件
    ]
)
logger = logging.getLogger()

def acquire_lock(lock_file_path='/tmp/monitor_script.lock', retries=3, wait_time=5):
    """尝试获取文件锁，若失败则重试。"""
    lock_file = open(lock_file_path, 'w')
    attempt = 0
    while attempt < retries:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("Acquired file lock.")
            return lock_file
        except IOError:
            logger.warning(f"Attempt {attempt + 1} to acquire lock failed. Retrying in {wait_time} seconds...")
            attempt += 1
            time.sleep(wait_time)  # 等待重试
    logger.error("Failed to acquire file lock after multiple attempts.")
    sys.exit(1)

def escape_markdown(text):
    """不进行任何转义操作，直接返回文本。"""
    return text

async def fetch_html(url, retries=3):
    scraper = cfscrape.create_scraper()
    for attempt in range(retries):
        try:
            response = scraper.get(url)
            if response.status_code == 200:
                if not response.text.strip():  # 检查是否为空页面
                    logger.warning(f"Empty page returned from {url}")
                    return None
                logger.info(f"Successfully fetched URL: {url}")
                return response.text
            else:
                logger.warning(f"Received status code {response.status_code} for URL {url}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e} (Attempt {attempt + 1} of {retries})")
            await asyncio.sleep(2)  # 重试等待时间
    logger.error(f"Failed to fetch URL after {retries} attempts: {url}")
    return None

def parse_stock(html, out_of_stock_text):
    """解析库存信息"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        stock_match = re.search(r'(\d+)\s+in stock', soup.get_text(), re.IGNORECASE)
        if stock_match:
            logger.info(f"Stock found: {stock_match.group(1)} in stock")
            return int(stock_match.group(1))
        elif out_of_stock_text in soup.get_text():
            logger.info("Out of stock.")
            return 0
        else:
            logger.info("Stock information not found, assuming in stock.")
            return float('inf')
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return None  # 返回 None 表示解析失败

async def check_stock(stock, out_of_stock_text):
    """检查商品库存"""
    url = stock['check_url']
    html = await fetch_html(url)
    if html is None:
        logger.warning(f"Skipping URL {url} due to repeated errors.")
        return None  # 如果获取失败，返回 None
    return parse_stock(html, out_of_stock_text)

async def load_config(filename='/root/monitor/bwh/config.json'):
    """加载配置文件"""
    if not os.path.exists(filename):
        logger.error(f"Config file {filename} not found.")
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as f:
        logger.info(f"Loaded config from {filename}")
        return json.load(f)

async def send_notification(config, merchant, stock, stock_quantity, message_id=None):
    """发送 Telegram 通知，使用 HTML 格式"""
    bot = Bot(token=config['telegram_token'])
    try:
        title = f"{merchant['name']}-{stock['title']}"
        tag = html.escape(merchant['tag'])  # 转义 HTML 特殊字符
        price = html.escape(stock['price'])  # 转义 HTML 特殊字符
        hardware_info = f"<a href=\"{stock['buy_url']}\">{html.escape(stock['hardware_info'])}</a>"

        stock_info = f'🛒 <a href="{stock["buy_url"]}">库   存：{"有 - 抢购吧！" if stock_quantity > 0 else "无 - 已售罄！"}</a>'

        annual_coupon = f"🎁 优惠码：<code>{merchant['coupon_annual']}</code>" if merchant.get('coupon_annual') else ""
        coupon_info = annual_coupon
        coupon_section = f"\n\n{coupon_info}\n\n" if coupon_info else "\n\n"

        buy_link = f"🔗 <s>{stock['buy_url']}</s>" if stock_quantity == 0 else f"🔗 {stock['buy_url']}"

        message = (
            f"<b>{title}</b>\n\n"
            f"💰 价  格: <b>{price}</b>\n\n"
            f"📜 配  置：{hardware_info}\n\n"
            f"ℹ️ {tag}"
            f"{coupon_section}"
            f"{stock_info}\n\n"
            f"{buy_link}"
        )

        if stock_quantity > 0:
            sent_message = await bot.send_message(
                chat_id=config['telegram_chat_id'], text=message, parse_mode=ParseMode.HTML
            )
            logger.info("Notification sent successfully.")
            return sent_message.message_id
        else:
            if message_id:
                try:
                    await bot.edit_message_text(
                        chat_id=config['telegram_chat_id'], message_id=message_id, text=message, parse_mode=ParseMode.HTML
                    )
                    logger.info("Message updated to out of stock status.")
                except BadRequest as e:
                    logger.error(f"Error editing message: {e}")
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
    return None

async def check_all_stocks(config, merchants):
    """检查所有商家的库存"""
    tasks = []
    for merchant in merchants:
        for stock in merchant['stock_urls']:
            tasks.append(check_stock(stock, merchant['out_of_stock_text']))
    return await asyncio.gather(*tasks)

async def main():
    """主函数"""
    lock_file = acquire_lock()  # 确保只运行一个实例

    try:
        merchant_status = {}
        message_ids = {}

        while True:
            config = await load_config()  # 加载配置
            check_interval = config.get('check_interval', 600)  # 获取检查间隔，默认为 600 秒

            results = await check_all_stocks(config, config['merchants'])

            for merchant, stock, stock_quantity in zip(config['merchants'], config['merchants'][0]['stock_urls'], results):
                if stock_quantity is None:
                    continue  # 处理失败的请求

                # 使用商品的标题作为唯一标识符
                unique_identifier = stock['title']

                previous_status = merchant_status.get(merchant['name'], {}).get(unique_identifier, {'in_stock': False})

                if stock_quantity > 0 and not previous_status['in_stock']:
                    message_id = await send_notification(config, merchant, stock, stock_quantity)
                    merchant_status.setdefault(merchant['name'], {})[unique_identifier] = {'in_stock': True}
                    message_ids[unique_identifier] = message_id
                elif stock_quantity == 0 and previous_status['in_stock']:
                    await send_notification(config, merchant, stock, stock_quantity, message_ids.get(unique_identifier))
                    merchant_status.setdefault(merchant['name'], {})[unique_identifier] = {'in_stock': False}

            logger.info(f"Waiting for {check_interval} seconds before checking again.")
            await asyncio.sleep(check_interval)
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()

if __name__ == '__main__':
    asyncio.run(main())
