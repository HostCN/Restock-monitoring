以下是一个详细的 `README.md` 文件示例，适用于你的库存监控脚本。这个 `README.md` 文件包括了脚本的介绍、安装步骤、配置说明、使用方法等内容：

---

# 库存监控脚本

该库存监控脚本用于定期检查多个商家网站上的商品库存状态，并通过 Telegram 发送通知，帮助你实时了解商品是否缺货或补货。脚本支持 JavaScript 渲染的页面，能够智能地识别库存状态变化。

## 特性

- 支持多个商家和多个商品的监控。
- 支持动态加载的 JavaScript 页面解析。
- 库存状态变化时，通过 Telegram 发送通知。
- 支持文件锁，确保脚本的唯一运行。
- 自动重试机制，确保抓取稳定。
- 支持配置文件动态调整监控参数。

## 系统要求

- Python 3.7 或更高版本
- Debian 或其他类 Unix 系统（例如 Ubuntu）
- 必须安装以下 Python 库：
  - `beautifulsoup4`
  - `playwright`
  - `telegram`
  - `asyncio`
  - `fcntl`
  - `json`
  - `logging`

## 安装步骤

### 1. 安装 Python 环境

如果你尚未安装 Python 3，可以从官方网站下载并安装：[Python 下载](https://www.python.org/downloads/)

### 2. 安装依赖

使用 `pip3` 安装所需的依赖：

```bash
pip3 install beautifulsoup4 playwright telegram
```

安装 `Playwright` 所需的浏览器：

```bash
python3 -m playwright install
```

如果你只需要安装某一种浏览器（例如 `chromium`），可以使用：

```bash
python3 -m playwright install chromium
```

### 3. 配置 Telegram Bot

1. 创建一个 Telegram Bot：通过与 [BotFather](https://core.telegram.org/bots#botfather) 互动来创建一个新的 Bot。
2. 获取 Bot Token 和 Chat ID：
   - `Bot Token`：BotFather 会给你一个 `token`，你需要将其放入配置文件中。
   - `Chat ID`：你可以通过与自己的 Bot 互动，或使用 [getUpdates API](https://core.telegram.org/bots/api#getupdates) 来获取你的聊天 ID。可以通过 Telegram 机器人发送消息到群组，然后查看 Chat ID。

### 4. 配置脚本

在项目目录下，复制并重命名 `config.json.sample` 为 `config.json`。然后根据需要修改其中的配置项：

```json
{
  "telegram_token": "你的telegram_token",
  "telegram_chat_id": "你的telegram_chat_id",
  "merchants": [
    {
      "enabled": true,
      "name": "商家名称",
      "tag": "#商家标签",
      "coupon_annual": "年终优惠码",
      "stock_urls": [
        {
          "title": "产品名称",
          "check_url": "产品URL",
          "buy_url": "购买链接",
          "price": "产品价格",
          "hardware_info": "产品硬件信息",
          "out_of_stock_text": "缺货文本",
          "enable_javascript": true
        }
      ]
    }
  ],
  "check_interval": 600
}
```

- `telegram_token`: 你的 Telegram Bot Token。
- `telegram_chat_id`: 目标聊天 ID，可以是个人或群组 ID。
- `merchants`: 商家和商品的配置列表。每个商家可以有多个产品监控配置。
  - `enabled`: 启用或禁用该商家的库存监控。
  - `name`: 商家名称，将显示在 Telegram 消息标题中。
  - `tag`: 商家标签，用于消息中标记商家。
  - `coupon_annual`: 年终优惠码（如果有），将显示在通知消息中。
  - `stock_urls`: 产品数组，每个产品包含以下配置：
    - `title`: 产品名称。
    - `check_url`: 用于检查库存的产品页面 URL。
    - `buy_url`: 购买链接。
    - `price`: 产品价格。
    - `hardware_info`: 产品硬件信息。
    - `out_of_stock_text`: 页面上标识缺货的文本。
    - `enable_javascript`: 是否启用 JavaScript，默认为 `false`。

### 5. 配置库存状态文件

库存状态将会保存在 `stock_status.json` 文件中。如果文件不存在，脚本会自动创建并初始化。

### 6. 启动脚本

安装完依赖并配置好 `config.json` 后，你可以通过以下命令启动脚本：

```bash
python3 /root/monitor/monitor.py
```

脚本会开始定期检查商家的库存，并在库存状态发生变化时通过 Telegram 发送通知。

### 7. 停止脚本

你可以通过按 `Ctrl+C` 停止脚本运行，脚本会优雅地关闭并释放文件锁。

## 配置选项说明

### 商家配置

```json
{
  "enabled": true,
  "name": "商家名称",
  "tag": "#商家标签",
  "coupon_annual": "年终优惠码",
  "stock_urls": [
    {
      "title": "产品名称",
      "check_url": "产品URL",
      "buy_url": "购买链接",
      "price": "产品价格",
      "hardware_info": "产品硬件信息",
      "out_of_stock_text": "缺货文本",
      "enable_javascript": true
    }
  ]
}
```

- `enabled`: 启用或禁用该商家的库存监控。
- `name`: 商家名称，脚本会在 Telegram 消息中显示该名称。
- `tag`: 商家标签，用于消息中标记商家。
- `coupon_annual`: 年终优惠码，用于显示在通知消息中。
- `stock_urls`: 每个商家可以监控多个产品。每个产品配置如下：
  - `title`: 产品名称。
  - `check_url`: 用于检查库存的 URL。
  - `buy_url`: 购买链接。
  - `price`: 产品价格。
  - `hardware_info`: 产品硬件信息。
  - `out_of_stock_text`: 页面中表示缺货的文本。
  - `enable_javascript`: 是否启用 JavaScript 渲染，默认为 `false`。

### 页面检查

脚本通过访问 `check_url` 来获取商品页面，并检查页面内容是否包含缺货标志文本（`out_of_stock_text`）。如果页面内容匹配缺货标志，脚本会判断商品缺货。

### Telegram 通知

当库存状态发生变化时，脚本会通过 Telegram Bot 发送通知。消息内容包括：
- 商品名称和商家名称。
- 商品价格和硬件规格。
- 库存状态（有库存或无库存）。
- 优惠码（如果有）。
- 购买链接。

### 错误和重试机制

脚本具有自动重试机制，如果页面加载失败，会重试最多 3 次，每次间隔 5 秒。

### 定期检查

脚本会根据 `check_interval` 配置项指定的时间间隔（单位：秒）定期检查商家的库存。

## 日志

脚本会将日志输出到控制台，并同时保存在 `/root/monitor/monitor_script.log` 文件中。日志级别默认是 `INFO`，你可以根据需要修改日志级别以输出更多调试信息。

## 常见问题

### 1. "无法获取文件锁" 错误

该错误表示脚本已经在运行。请确保只有一个实例在运行，或者删除锁文件 `/root/monitor/monitor_script.lock` 后重试。

```bash
sudo rm /root/monitor/monitor_script.lock
```

### 2. Telegram 消息无法发送

确保你的 `telegram_token` 和 `telegram_chat_id` 配置正确。如果你使用群组 ID，请确保你的 Bot 已经加入该群组并具有发送消息的权限。

### 3. Playwright 浏览器未安装

如果你遇到浏览器未安装的错误，请执行以下命令来安装 Playwright 所需的浏览器：

```bash
python3 -m playwright install
```

### 4. Python 依赖库安装问题

如果在安装 Python 库时遇到问题，确保你已经安装了 `pip3`。可以通过以下命令安装依赖：

```bash
pip3 install beautifulsoup4 playwright telegram
```

## 贡献

欢迎贡献代码！如果你有任何改进建议或修复，请提交 Pull Request 或提出问题。

## 许可

该项目采用 [MIT 许可证](LICENSE) 开源。

---

此 `README.md` 文件详细介绍了脚本的功能、配置方法、安装步骤和常见问题，帮助用户快速入门并解决可能遇到的问题。根据实际需求，你可以根据具体情况进一步修改或补充内容。
