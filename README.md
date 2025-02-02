Here's a detailed `README.md` for your stock monitoring script:

---

# Stock Monitor Script

This Python script monitors the stock status of various products across multiple merchants, checking their availability at regular intervals. It sends notifications to a Telegram chat whenever the stock status changes, such as when a product goes from "out of stock" to "in stock" or vice versa.

## Features

- **Product Stock Monitoring**: Monitors the stock levels of products from various merchants by checking specific URLs.
- **Telegram Notifications**: Sends real-time updates about product availability to a Telegram chat, including product details, stock quantity, and discounts.
- **Product Locking**: Prevents the script from running multiple instances simultaneously by acquiring a lock on a file.
- **Retry Mechanism**: Automatically retries failed requests up to a defined number of attempts to ensure stable operation.
- **Configuration Support**: Allows for easy configuration of merchants, products, and notification settings through a JSON file.

## Prerequisites

- **Python 3.6+**
- **Required Libraries**:
  - `cfscrape` (for bypassing Cloudflare protection)
  - `beautifulsoup4` (for HTML parsing)
  - `requests` (for HTTP requests)
  - `python-telegram-bot` (for sending Telegram messages)
  - `flask` (for HTML escaping)
  - `fcntl` (for file locking)

To install the required dependencies, run:

```bash
pip3 install cfscrape beautifulsoup4 python-telegram-bot
```

## File Structure

```
/root/monitor/stock/
│
├── config.json           # Configuration file for merchants and stock settings
├── stock_status.json     # Stores the current stock status of products
├── monitor.py            # Main script for monitoring stock
├── monitor_script.lock   # Lock file to prevent multiple script instances
├── monitor_script.log    # Log file for script output and error messages
```

### Configuration File (`config.json`)

This JSON file contains the configuration for each merchant and the products you wish to monitor. You can customize the merchant's name, stock URLs, product details, and more.

#### Example `config.json`

```json
{
    "telegram_token": "your_telegram_bot_token",
    "telegram_chat_id": "@your_chat_id",
    "check_interval": 600,
    "merchants": [
        {
            "name": "BandwagonHost",
            "tag": "#BandwagonHost",
            "enabled": true,
            "coupon_annual": "BWHCGLUKKB",
            "stock_urls": [
                {
                    "title": "Product 1",
                    "check_url": "https://example.com/product1",
                    "buy_url": "https://example.com/product1/buy",
                    "price": "$169.99",
                    "hardware_info": "2 cores, 1GB RAM, 20GB SSD, 1Gbps",
                    "expected_title": "BandwagonHost Product 1",
                    "out_of_stock_text": "currently unavailable"
                }
            ]
        },
        {
            "name": "DMIT",
            "tag": "#DMIT",
            "enabled": false,
            "stock_urls": [
                {
                    "title": "Product 2",
                    "check_url": "https://example.com/product2",
                    "buy_url": "https://example.com/product2/buy",
                    "price": "$129.99",
                    "hardware_info": "1 core, 512MB RAM, 10GB SSD, 1Gbps",
                    "out_of_stock_text": "currently unavailable"
                }
            ]
        }
    ]
}
```

### Lock File (`monitor_script.lock`)

This file is used to ensure that only one instance of the script is running at any given time. If the script is already running, it will prevent another instance from starting.

### Stock Status File (`stock_status.json`)

This file stores the previous stock status of the products. It allows the script to compare the current stock status with the previous one and detect if there have been any changes.

#### Example `stock_status.json`

```json
{
    "Product 1": {
        "in_stock": true,
        "message_id": 123456789
    },
    "Product 2": {
        "in_stock": false,
        "message_id": 987654321
    }
}
```

## Usage

### 1. **Configure the script**:

Edit the `config.json` file with your merchant details, product URLs, and Telegram bot information. Make sure to replace placeholders such as `your_telegram_bot_token` and `@your_chat_id` with your actual bot token and chat ID.

### 2. **Run the script**:

Once the configuration is complete, run the script using the following command:

```bash
python3 /root/monitor/stock/monitor.py
```

The script will begin monitoring the specified stock URLs at the interval defined in `config.json` (`check_interval` in seconds). It will check for stock changes and send notifications to your Telegram chat.

### 3. **Receive Notifications**:

When the stock status of a product changes (from "out of stock" to "in stock" or vice versa), the script will send a Telegram notification with the product details, price, configuration, and available stock. If the stock goes out of stock, the script will update the existing notification.

### 4. **Check logs**:

Logs will be saved to `monitor_script.log`. You can view these logs to troubleshoot issues, such as HTTP request failures or parsing errors.

## How It Works

### Key Functions

- **acquire_lock()**: Ensures that only one instance of the script is running at any time. If the script is already running, it will not start another instance.
- **escape_markdown()**: Escapes Markdown characters to ensure that text is displayed correctly in the Telegram notification.
- **fetch_html()**: Fetches the HTML content of a URL and handles retries in case of failures.
- **parse_stock()**: Extracts the stock quantity from the HTML page. It can also check for out-of-stock messages based on a customizable text.
- **send_notification()**: Sends a stock update to a Telegram chat. It includes details like price, configuration, stock availability, and a purchase link.
- **check_all_stocks()**: Loops through all merchants and products to check the stock status.
- **load_stock_status()**: Loads the previous stock status from `stock_status.json` to compare with the current stock.
- **save_stock_status()**: Saves the current stock status to `stock_status.json` after each check.

### Error Handling

- **HTTP Request Failures**: If the script cannot fetch a page (e.g., due to network issues or non-existent pages), it will retry a specified number of times before skipping that product.
- **Stock Parsing Errors**: If the script encounters errors while parsing the stock information (e.g., if the stock information cannot be found), it will log the error and skip that product.
- **Telegram Notification Issues**: If there is an issue with sending or editing a message on Telegram, the error will be logged.

## Configuration Options

### 1. **check_interval**:
The interval in seconds between each stock check. The default is 600 seconds (10 minutes).

### 2. **merchants**:
A list of merchants you want to monitor. Each merchant can have multiple products to monitor.

- **enabled**: A flag to enable or disable monitoring for this merchant.
- **coupon_annual**: Optional. A coupon code to include in the notification for discounts.
- **stock_urls**: A list of products to monitor.
  - **title**: The product's name.
  - **check_url**: The URL where the product's stock status is checked.
  - **buy_url**: The URL to purchase the product.
  - **price**: The price of the product.
  - **hardware_info**: Details about the product's hardware (for example, RAM, disk size, etc.).
  - **expected_title**: Optional. The expected title of the webpage for validation.
  - **out_of_stock_text**: The text that appears on the product page when it is out of stock.

## Troubleshooting

- **Script is not running**: If the script is not running, make sure no other instance of the script is already running (check the lock file).
- **No notifications**: Ensure that the Telegram bot token and chat ID are correct in the `config.json` file. You can also check the Telegram API logs for any errors.
- **Stock information not found**: Ensure that the HTML parsing logic matches the structure of the product page. If the page layout changes, you may need to adjust the parsing code.

## License

This script is open-source and licensed under the MIT License. You are free to use, modify, and distribute it as needed.

---

This `README.md` should provide all necessary information for setting up, configuring, and using your stock monitor script. Let me know if you need any additional details or adjustments!
