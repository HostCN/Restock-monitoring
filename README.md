# Restock-monitoring

集成telegram，用于补货监控推送，快黑五了，速速用起来！

可以把上述两个文件打包放在/root/monitor/商家名字/路径下，方便管理


检查进程
```
ps -ef | grep python
```

常驻命令
```
nohup python3 /root/monitor/bwh/monitor.py &
```

临时命令
```
python3 /root/monitor/bwh/monitor.py
```
```
python3 /root/monitor/stock/monitor.py
```
删除文件锁
```
rm /tmp/monitor_script.lock
```
终止monitor.py
```
pkill -f monitor.py
```
`python3-cfscrape` 并不是官方的系统包，因此通过 `apt` 无法直接安装。请使用以下推荐的解决方案来正确安装 `cfscrape`：

---

### **推荐解决方案：使用虚拟环境**
虚拟环境可以隔离项目依赖，不会影响系统的 Python 环境。

1. **安装虚拟环境工具（如果未安装）**：
   ```bash
   sudo apt update
   sudo apt install python3-venv
   ```

2. **创建虚拟环境**：
   ```bash
   python3 -m venv ~/myenv
   ```
   这会在 `~/myenv` 目录中创建一个虚拟环境。

3. **激活虚拟环境**：
   ```bash
   source ~/myenv/bin/activate
   ```

4. **在虚拟环境中安装 `cfscrape`**：
   ```bash
   pip install cfscrape
   ```

5. **运行脚本**：
   确保在激活虚拟环境后运行脚本：
   ```bash
   python /root/monitor/stock/monitor.py
   ```

6. **退出虚拟环境**（完成工作后）：
   ```bash
   deactivate
   ```
   
7. 安装兼容版本的 `urllib3`：
   ```bash
   pip install "urllib3<2.0"
   ```

8. 安装 `beautifulsoup4`：
   ```bash
   pip install beautifulsoup4
   ```

9. 安装 `python-telegram-bot`：
   ```bash
   pip install python-telegram-bot
   ```

10. **运行脚本**：
   确保在安装完成后运行脚本：
   ```bash
   python /root/monitor/stock/monitor.py
   ```
