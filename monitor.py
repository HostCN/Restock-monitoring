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
        logging.FileHandler('/root/monitor/stock/monitor_script.log')  # 也写入到文件
    ]
)
logger = logging.getLogger()

def acquire_lock(lock_file_path='/root/monitor/stock/monitor_script.lock', retries=3, wait_time=5):
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

async def fetch_html(url, expected_title=None, retries=3):
    scraper = cfscrape.create_scraper()
    for attempt in range(retries):
        try:
            response = scraper.get(url)
            if response.status_code != 200:
                logger.warning(f"URL {url} 返回了非200状态码 {response.status_code}，跳过该页面。")
                return None  # 如果状态码不是 200，跳过该页面
            if not response.text.strip():  # 检查页面是否为空
                logger.warning(f"URL {url} 返回了空页面，跳过。")
                return None
            if expected_title:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else None
                if title and expected_title.lower() not in title.lower():
                    logger.warning(f"URL {url} 标题不匹配。期望包含：{expected_title}，实际：{title}，跳过该页面。")
                    return None  # 如果标题不包含期望的部分文本，跳过该页面
            logger.info(f"成功获取 URL: {url}")
            return response.text
        except Exception as e:
            logger.error(f"获取 {url} 时出错: {e} (尝试 {attempt + 1} 次，共 {retries} 次)")
            await asyncio.sleep(2)  # 等待重试
    logger.error(f"获取 URL {url} 失败，已尝试 {retries} 次。")
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

async def check_stock(stock, out_of_stock_text, expected_title=None):
    """检查商品库存"""
    url = stock['check_url']
    html = await fetch_html(url, expected_title=expected_title)
    if html is None:
        logger.warning(f"跳过 URL {url}，因获取失败或标题不匹配。")
        return None  # 如果获取失败或标题不匹配，跳过该页面
    return parse_stock(html, out_of_stock_text)

async def load_config(filename='/root/monitor/stock/config.json'):
    """加载配置文件"""
    if not os.path.exists(filename):
        logger.error(f"Config file {filename} not found.")
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as f:
        logger.info(f"Loaded config from {filename}")
        return json.load(f)

async def send_notification(config, merchant, stock, stock_quantity, message_id=None):
    """发送 Telegram 通知，使用 HTML 格式并禁用链接预览"""
    bot = Bot(token=config['telegram_token'])
    title = f"{merchant['name']}-{stock['title']}"
    tag = html.escape(merchant['tag'])  # 转义 HTML 特殊字符
    price = html.escape(stock['price'])  # 转义 HTML 特殊字符
    hardware_info = f"<a href=\"{stock['buy_url']}\">{html.escape(stock['hardware_info'])}</a>"

    # 根据库存数量设置显示的库存信息
    stock_info = f'🛒 <a href="{stock["buy_url"]}">库   存：{"有 - 抢购吧！" if stock_quantity > 0 else "无 - 已售罄！"}</a>'

    # 根据库存数量设置购买链接，库存为 0 时使用 <s> 标签
    buy_link = f"🔗 <s>{stock['buy_url']}</s>" if stock_quantity == 0 else f"🔗 {stock['buy_url']}"

    # 优惠码部分
    annual_coupon = f"🎁 优惠码：<code>{merchant['coupon_annual']}</code>" if merchant.get('coupon_annual') else ""
    coupon_info = annual_coupon
    coupon_section = f"\n\n{coupon_info}\n\n" if coupon_info else "\n\n"

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
        # 如果库存大于 0，发送新消息
        if stock_quantity > 0:
            sent_message = await bot.send_message(
                chat_id=config['telegram_chat_id'],
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True  # 禁用链接预览
            )
            return sent_message.message_id
        elif message_id:  # 如果库存为 0 且已有消息，更新已发送消息
            await bot.edit_message_text(
                chat_id=config['telegram_chat_id'],
                message_id=message_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True  # 禁用链接预览
            )
    except BadRequest as e:
        logger.error(f"Error updating message: {e}")
    return None

async def check_all_stocks(config, merchants):
    """检查所有商家的库存"""
    tasks = []
    for merchant in merchants:
        if merchant['enabled']:  # 只检查启用的商家
            for stock in merchant['stock_urls']:
                tasks.append(check_stock(stock, merchant['out_of_stock_text'], stock.get('expected_title')))
    results = await asyncio.gather(*tasks)
    return results  # 返回一个包含所有库存数量的列表

async def load_stock_status(filename='/root/monitor/stock/stock_status.json'):
    """加载之前保存的库存状态"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

async def save_stock_status(stock_status, filename='/root/monitor/stock/stock_status.json'):
    """保存库存状态"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stock_status, f, ensure_ascii=False, indent=4)

async def main():
    """主函数"""
    lock_file = acquire_lock()  # 确保只运行一个实例

    try:
        # 加载之前的库存状态
        stock_status = await load_stock_status()

        while True:
            config = await load_config()  # 加载配置
            check_interval = config.get('check_interval', 600)  # 获取检查间隔，默认为 600 秒

            # 获取当前所有商品的库存状态
            results = await check_all_stocks(config, config['merchants'])

            result_index = 0
            for merchant in config['merchants']:
                if not merchant['enabled']:  # 如果商家禁用，跳过
                    continue
                for stock in merchant['stock_urls']:
                    stock_quantity = results[result_index]
                    result_index += 1

                    if stock_quantity is None:
                        continue  # 处理失败的请求

                    # 使用商品的标题作为唯一标识符
                    unique_identifier = stock['title']

                    previous_status = stock_status.get(unique_identifier, {'in_stock': False})

                    if stock_quantity > 0 and not previous_status['in_stock']:
                        message_id = await send_notification(config, merchant, stock, stock_quantity)
                        stock_status[unique_identifier] = {'in_stock': True, 'message_id': message_id}
                    elif stock_quantity == 0 and previous_status['in_stock']:
                        # 编辑已有的消息
                        await send_notification(config, merchant, stock, stock_quantity, previous_status['message_id'])
                        stock_status[unique_identifier] = {'in_stock': False, 'message_id': previous_status['message_id']}

            # 每次循环后保存库存状态
            await save_stock_status(stock_status)

            logger.info(f"Waiting for {check_interval} seconds before checking again...")
            await asyncio.sleep(check_interval)

    except Exception as e:
        logger.error(f"Error in main function: {e}")
    finally:
        if lock_file:
            lock_file.close()

if __name__ == '__main__':
    asyncio.run(main())
