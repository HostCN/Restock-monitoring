Here’s a detailed `README.md` file in English for your stock monitoring script:

---

# Stock Monitoring Script

This stock monitoring script checks the availability of products from multiple merchant websites at regular intervals. It sends notifications via Telegram when the stock status changes, helping you stay updated on whether a product is in stock or out of stock. The script supports pages with JavaScript rendering and can intelligently detect changes in stock availability.

## Features

- Monitor multiple merchants and products.
- Support for JavaScript-rendered pages.
- Send notifications via Telegram when stock status changes.
- Supports file locking to ensure the script runs as a single instance.
- Automatic retry mechanism to ensure reliable scraping.
- Configuration file allows dynamic adjustment of monitoring parameters.

## System Requirements

- Python 3.7 or higher
- Debian or other Unix-like systems (e.g., Ubuntu)
- Required Python libraries:
  - `beautifulsoup4`
  - `playwright`
  - `telegram`
  - `asyncio`
  - `fcntl`
  - `json`
  - `logging`

## Installation Steps

### 1. Install Python

If Python 3 is not installed, you can download and install it from [Python Downloads](https://www.python.org/downloads/).

### 2. Install Dependencies

Use `pip3` to install the required dependencies:

```bash
pip3 install beautifulsoup4 playwright telegram
```

Install the necessary browsers for `Playwright`:

```bash
python3 -m playwright install
```

If you only need one browser (e.g., Chromium), you can install it using:

```bash
python3 -m playwright install chromium
```

### 3. Configure Telegram Bot

1. Create a Telegram Bot: Interact with [BotFather](https://core.telegram.org/bots#botfather) to create a new bot.
2. Get the Bot Token and Chat ID:
   - `Bot Token`: You will receive a `token` from BotFather, which you'll need to place in your configuration file.
   - `Chat ID`: You can get your chat ID by interacting with your bot or using the [getUpdates API](https://core.telegram.org/bots/api#getupdates). Send a message to the bot, and then check the Chat ID via the API.

### 4. Configure the Script

In your project directory, copy and rename `config.json.sample` to `config.json`. Modify the configuration as needed:

```json
{
  "telegram_token": "your_telegram_token",
  "telegram_chat_id": "your_telegram_chat_id",
  "merchants": [
    {
      "enabled": true,
      "name": "Merchant Name",
      "tag": "#merchant_tag",
      "coupon_annual": "Annual Coupon Code",
      "stock_urls": [
        {
          "title": "Product Name",
          "check_url": "Product URL",
          "buy_url": "Purchase Link",
          "price": "Product Price",
          "hardware_info": "Product Hardware Info",
          "out_of_stock_text": "Out of Stock Text",
          "enable_javascript": true
        }
      ]
    }
  ],
  "check_interval": 600
}
```

- `telegram_token`: Your Telegram Bot Token.
- `telegram_chat_id`: The target chat ID (could be a personal or group ID).
- `merchants`: A list of merchants and their product configurations. Each merchant can monitor multiple products.
  - `enabled`: Enable or disable monitoring for this merchant.
  - `name`: The merchant’s name, which will be shown in Telegram notifications.
  - `tag`: A merchant tag to label the notifications.
  - `coupon_annual`: An optional annual coupon code that will be displayed in notifications.
  - `stock_urls`: A list of products to monitor. Each product has the following configuration:
    - `title`: Product name.
    - `check_url`: URL for checking the product’s stock status.
    - `buy_url`: Purchase link.
    - `price`: Product price.
    - `hardware_info`: Product hardware information.
    - `out_of_stock_text`: Text on the page that indicates the product is out of stock.
    - `enable_javascript`: Whether to enable JavaScript rendering (default is `false`).

### 5. Stock Status File Configuration

The script will save the stock status in the `stock_status.json` file. If the file doesn't exist, the script will create and initialize it automatically.

### 6. Run the Script

After installing dependencies and configuring the `config.json`, you can start the script using the following command:

```bash
python3 /root/monitor/monitor.py
```

The script will begin checking the merchants' stock at regular intervals and send notifications via Telegram when stock status changes.

### 7. Stop the Script

You can stop the script by pressing `Ctrl+C`, and the script will gracefully shut down and release the file lock.

## Configuration Options

### Merchant Configuration

```json
{
  "enabled": true,
  "name": "Merchant Name",
  "tag": "#merchant_tag",
  "coupon_annual": "Annual Coupon Code",
  "stock_urls": [
    {
      "title": "Product Name",
      "check_url": "Product URL",
      "buy_url": "Purchase Link",
      "price": "Product Price",
      "hardware_info": "Product Hardware Info",
      "out_of_stock_text": "Out of Stock Text",
      "enable_javascript": true
    }
  ]
}
```

- `enabled`: Whether the merchant's stock monitoring is enabled or disabled.
- `name`: The merchant’s name, which will appear in the Telegram notification.
- `tag`: A tag for the merchant, which will appear in the message.
- `coupon_annual`: Annual discount code (optional) that will appear in the notification.
- `stock_urls`: Each merchant can monitor multiple products. Each product configuration includes:
  - `title`: Product name.
  - `check_url`: The URL for checking stock.
  - `buy_url`: The purchase link.
  - `price`: Product price.
  - `hardware_info`: Product hardware information.
  - `out_of_stock_text`: Text that indicates the product is out of stock.
  - `enable_javascript`: Whether to enable JavaScript rendering (default is `false`).

### Page Check

The script accesses the `check_url` to retrieve the product page and checks if the page content contains the out-of-stock text (`out_of_stock_text`). If the text is found, the script considers the product out of stock.

### Telegram Notifications

When the stock status changes, the script will send a Telegram notification. The message will include:
- Product name and merchant name.
- Product price and hardware details.
- Stock status (in stock or out of stock).
- Coupon code (if available).
- Purchase link.

### Error and Retry Mechanism

The script includes an automatic retry mechanism. If a page load fails, the script will retry up to 3 times, with a 5-second delay between each attempt.

### Periodic Checking

The script will check for stock changes based on the `check_interval` configuration (in seconds). By default, it checks every 600 seconds (10 minutes).

## Logs

The script logs output to both the console and the file `/root/monitor/monitor_script.log`. The log level is set to `INFO` by default, but you can modify the level for more detailed debugging.

## Troubleshooting

### 1. "Unable to Acquire File Lock" Error

This error occurs when another instance of the script is running. Ensure only one instance of the script is running at any given time, or delete the lock file `/root/monitor/monitor_script.lock` and try again:

```bash
sudo rm /root/monitor/monitor_script.lock
```

### 2. Telegram Message Not Sending

Ensure that your `telegram_token` and `telegram_chat_id` are correctly configured. If you are using a group ID, make sure your bot is added to the group and has permission to send messages.

### 3. Playwright Browser Not Installed

If you encounter an error stating that the browser is not installed, run the following command to install the required browsers:

```bash
python3 -m playwright install
```

### 4. Python Dependency Installation Issues

If you encounter issues installing Python libraries, make sure `pip3` is installed. You can install the dependencies using:

```bash
pip3 install beautifulsoup4 playwright telegram
```

## Contributing

Feel free to contribute! If you have any improvements or fixes, please submit a Pull Request or open an issue.

## License

This project is licensed under the [MIT License](LICENSE).

---

This `README.md` provides a comprehensive overview of the script’s functionality, installation instructions, configuration options, and troubleshooting tips, ensuring users can get up and running quickly. You can adjust the content to fit your specific needs and usage scenario.
