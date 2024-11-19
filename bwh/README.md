常驻命令
```
nohup python3 /root/monitor/bwh/monitor.py &
```

临时命令
```
python3 /root/monitor/bwh/monitor.py
```


### 解决方法 1: 使用虚拟环境

1. **创建一个虚拟环境**：
   使用以下命令来创建一个新的虚拟环境。请确保已安装 `python3-venv` 软件包。如果没有安装，可以通过以下命令安装：

   ```bash
   sudo apt install python3-venv
   ```

   然后创建一个虚拟环境：

   ```bash
   python3 -m venv playwright-env
   ```

2. **激活虚拟环境**：
   激活虚拟环境：

   ```bash
   source playwright-env/bin/activate
   ```

3. **在虚拟环境中安装 Playwright**：
   在虚拟环境中安装 Playwright：

   ```bash
   pip install playwright
   ```

4. **安装浏览器依赖**：
   安装 Playwright 所需的浏览器：

   ```bash
   python -m playwright install
   ```

   这样，您就可以在虚拟环境中使用 Playwright，而不会影响系统环境。
   这个错误信息表明你的系统缺少了运行浏览器所需的一些依赖库。你需要安装这些依赖才能让 **Playwright** 正常运行。

安装缺少的依赖库：

#### 1. **使用 Playwright 自带的安装命令**

运行以下命令，Playwright 会自动安装所需的依赖：

```bash
playwright install-deps
```

如果这条命令不起作用，尝试手动安装依赖。

#### 2. **手动安装依赖库**

你可以使用 `apt` 命令来安装这些库，运行以下命令：

```bash
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

这条命令会安装所有 Playwright 所需的依赖库。
 **安装虚拟显示（Xvfb）**
如果你的环境没有图形界面（如服务器或容器），你可以使用 **Xvfb**（X Virtual Framebuffer）来模拟显示。这将允许 Chromium 启动并运行在虚拟显示环境中。

安装 Xvfb：
```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

然后，你可以通过 `xvfb-run` 命令来启动 Playwright：

```bash
xvfb-run --auto-servernum python3 your_script.py
```

这会在虚拟显示上运行你的脚本，从而避免 `Missing X server or $DISPLAY` 错误。

 **使用无头模式（Headless Mode）**
Playwright 和 Chromium 都支持无头模式（Headless Mode），它们通常在没有显示的环境中正常运行。如果你没有明确设置无头模式，可以尝试修改脚本以确保它启动浏览器时使用无头模式。

如果你是通过 Playwright 的 Python API 使用浏览器，可以设置无头模式：

```python
browser = await playwright.chromium.launch(headless=True)
```

无头模式可以防止启动图形界面，从而避免与 X 服务器相关的问题。
