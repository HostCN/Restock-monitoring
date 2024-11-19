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
