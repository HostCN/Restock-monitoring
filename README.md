Here’s the updated `README.md` with sections on pausing the script and deleting the lock file:

---

# Stock Monitoring Script

This script monitors the stock availability of products from various merchants. It uses Telegram notifications to alert when a product is in stock or out of stock.

## Features

- **Product Monitoring**: Monitors multiple products from different merchants.
- **Telegram Notifications**: Sends notifications to a specified Telegram channel when a product's stock status changes.
- **File Locking**: Prevents multiple instances of the script from running at the same time.
- **Customizable Configuration**: Easily configure the merchants, stock URLs, check intervals, and more via a JSON configuration file.
- **Error Handling**: Automatically retries if there is an issue fetching the product page or parsing the stock information.

## Requirements

- Python 3.x
- `cfscrape`: For bypassing Cloudflare protection.
- `beautifulsoup4`: For parsing HTML content.
- `telegram`: For sending notifications to Telegram.
- `json`, `os`, `re`, `time`: Standard Python libraries used for file handling, regular expressions, and timing.

### Install Dependencies

Install the required Python libraries:

```bash
pip install cfscrape beautifulsoup4 python-telegram-bot
```

## Setup

1. **Clone the repository** (if it's a Git repository):
    ```bash
    git clone <repo-url>
    cd <repo-directory>
    ```

2. **Create a configuration file**: You need to create a `config.json` file to define the merchants, stock URLs, check intervals, and your Telegram bot token.

    Example `config.json`:
    ```json
    {
        "telegram_token": "<Your-Telegram-Bot-Token>",
        "telegram_chat_id": "<Your-Telegram-Chat-ID>",
        "check_interval": 600,
        "merchants": [
            {
                "name": "BandwagonHost",
                "tag": "#BandwagonHost",
                "enabled": true,
                "coupon_annual": "BWHCGLUKKB",
                "stock_urls": [
                    {
                        "title": "搬瓦工 CN2 GIA-E",
                        "check_url": "https://bwh81.net/cart.php?a=add&pid=104",
                        "buy_url": "https://bwh81.net/aff.php?aff=55580&pid=87",
                        "price": "$169.99",
                        "hardware_info": "2核, 1GB, 20GB, 1000GB/月, 2.5Gbps, DC6 CN2 GIA-E",
                        "out_of_stock_text": "currently unavailable"
                    }
                ]
            }
        ]
    }
    ```

    - Replace `<Your-Telegram-Bot-Token>` and `<Your-Telegram-Chat-ID>` with your actual Telegram bot token and chat ID.
    - You can customize the merchants and product details as needed.

3. **Ensure you have a lock file**: The script will create a lock file (`monitor_script.lock`) to prevent multiple instances from running at once.

    If the script is stopped or interrupted, you may need to manually delete this lock file to resume execution:
    ```bash
    rm /root/monitor/stock/monitor_script.lock
    ```

## Running the Script

To run the script, use the following command:

```bash
python3 /root/monitor/stock/monitor.py
```

This will start the script, and it will begin checking the stock status of all listed products at the interval defined in the configuration file (`check_interval`).

## Pausing the Script

If you want to pause the script temporarily, you can use one of the following methods:

### 1. **Pause with `Ctrl + Z` (Terminal)**
   - If you're running the script in the terminal, you can press `Ctrl + Z` to suspend it. This will stop the script temporarily and move it to the background.

### 2. **Pause the Script Using the `kill` Command**
   - You can suspend the script process by sending a `SIGSTOP` signal to it. First, find the process ID (PID) of the script:
     ```bash
     ps aux | grep monitor.py
     ```
   - Then, use the `kill` command to suspend it:
     ```bash
     kill -SIGSTOP <PID>
     ```
   - To resume the script, use the `SIGCONT` signal:
     ```bash
     kill -SIGCONT <PID>
     ```

### 3. **Stop the Script Using `systemd` or `supervisord`**
   - If the script is managed by `systemd` or `supervisord`, you can stop it using the following commands:
     ```bash
     sudo systemctl stop <your-service-name>
     ```
     or
     ```bash
     supervisorctl stop <your-program-name>
     ```

## Deleting the Lock File

The script uses a lock file (`monitor_script.lock`) to prevent multiple instances from running simultaneously. If the script is stopped unexpectedly or you need to start it again, you may need to manually remove the lock file:

```bash
rm /root/monitor/stock/monitor_script.lock
```

## Script Workflow

1. **Acquiring File Lock**: The script ensures only one instance is running at a time by creating a file lock (`monitor_script.lock`).
2. **Fetching Product Information**: The script retrieves the HTML content of the product page.
3. **Parsing Stock Information**: It looks for the stock availability on the product page and checks if the product is in or out of stock.
4. **Sending Notifications**: If the stock status changes (e.g., from out of stock to in stock), the script sends a notification to a Telegram channel. The message contains product details, price, hardware info, and a link to purchase.
5. **Error Handling**: The script automatically retries fetching the page if there is a failure (up to 3 attempts by default).

## File Structure

```
/root/monitor/stock/
│
├── monitor.py          # Main script to monitor stock availability
├── config.json         # Configuration file for merchants and product details
├── monitor_script.lock # Lock file to prevent multiple script instances
├── stock_status.json   # Stores the current stock status of products
└── monitor_script.log  # Log file for script output and errors
```

## Logging

Logs are generated for every run of the script and stored in `monitor_script.log`. The log includes:

- Time of execution
- Information on the product stock status
- Errors or issues with fetching/parsing data

## Notifications

- When a product is **in stock**, a message is sent to the specified Telegram channel with details about the product.
- When a product is **out of stock**, the message is updated to show that the product is sold out.

The message includes:
- Product name, price, and configuration
- A link to the product's purchase page
- A coupon code (if available)

Example Telegram message:
```
💰 价  格: <b>$169.99</b>

📜 配  置：<a href="https://bwh81.net/aff.php?aff=55580&pid=87">2核, 1GB, 20GB, 1000GB/月, 2.5Gbps, DC6 CN2 GIA-E</a>

ℹ️ #BandwagonHost

🛒 <a href="https://bwh81.net/cart.php?a=add&pid=104">库   存：有 - 抢购吧！</a>

🎁 优惠码：<code>BWHCGLUKKB</code>

🔗 https://bwh81.net/aff.php?aff=55580&pid=87
```

## Troubleshooting

- **Problem**: The script isn't running.
  - **Solution**: Ensure that there is no other instance running by checking for the lock file. Delete it if necessary (`rm /root/monitor/stock/monitor_script.lock`).

- **Problem**: The script isn't sending notifications.
  - **Solution**: Check the Telegram bot token and chat ID in the `config.json` file.

- **Problem**: The stock information is incorrect.
  - **Solution**: The parsing logic may need to be adjusted depending on the format of the product page. Update the parsing logic in `parse_stock()`.

## Contributing

Feel free to open issues or submit pull requests if you encounter any bugs or would like to add new features.

## License

This project is open-source and available under the MIT License.

---

Now the README includes instructions for pausing the script and handling the lock file. Let me know if you'd like to adjust anything else!
