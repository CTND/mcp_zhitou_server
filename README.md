# mcp_zhitou_server
mcp_zhitou_server



# ✨ Zhitou HS Data MCP Server (Python Edition) ✨

<p align="center">
  <em> empowering AI Agents like Cursor & Cline with real-time China A-Share stock market data! 🚀</em>
</p>

Hey Coder 小伙伴们！👋 我是 **PGFA**！欢迎来到我的 Zhitou HS Data MCP Server 项目！

这个项目是一个用 **Python** 编写的 **模型上下文协议 (MCP)** 服务端实现。它的核心使命是充当你的 AI 智能体（比如超火的 Cursor 编辑器或 Cline 命令行助手）和 **智兔数服沪深数据 API** ([https://www.zhituapi.com/hsstockapi.html](https://www.zhituapi.com/hsstockapi.html)) 之间的桥梁 🌉。

简单来说，有了它，你就可以直接在 AI Agent 的聊天框里，用自然语言让 AI 帮你查询实时的 A 股股票列表、公司信息、资金流向等等，再也不用手动去查啦！是不是超级酷炫，效率 up up！📈

## 🌟 主要特性

*   **MCP 标准实现:** 通过标准输入/输出 (stdio) 与兼容 MCP 的客户端进行 JSON-RPC 通信。
*   **直连 Zhitou API:** 无缝对接智兔数服提供的丰富沪深市场数据接口。
*   **Python 编写:** 代码简洁易懂，方便二次开发和扩展。 (Python大法好！🐍)
*   **即插即用:** 提供清晰的配置指南，轻松在 Cursor 或 Cline 中启用。
*   **工具化封装:** 将常用的 Zhitou API 封装成 MCP 工具，方便 AI 调用。
*   **基础日志与错误处理:** 包含必要的日志记录和异常处理，方便调试。

## 🛠️ 快速开始

跟上 PGFA 的节奏，三步搞定！

### 1. 环境准备 (Prerequisites)

*   **Python:** 确认你的环境安装了 Python (推荐 3.8 或更高版本)。
*   **Requests 库:** 我们需要它来调用 API。打开你的终端/命令行，运行：
    ```bash
    pip install requests
    ```
*   **智兔 API Token:** 你必须拥有一个智兔数服 ([https://www.zhituapi.com/](https://www.zhituapi.com/)) 的账号，并获取你的 **API Token**。
*   **MCP 客户端:** 安装 Cursor ([https://cursor.sh/](https://cursor.sh/)) 或 Cline ([https://github.com/SaudriData/cline](https://github.com/SaudriData/cline))。

### 2. 获取代码 & 配置 Token

*   **下载本仓库唯一文件mcp_zhitou_server.py**

*   **🔥【宇宙级重要】🔥 配置你的 API Token:**
    打开主脚本文件 `mcp_zhitou_server.py` (或者你命名的其他主文件)，找到下面这行：
    ```python
    # 🔥🔥🔥【请务必替换为你自己的有效 Token! 测试 Token 有限制!】🔥🔥🔥
    ZHITU_TOKEN = "ZHITU_TOKEN_LIMIT_TEST"
    ```
    将 `"ZHITU_TOKEN_LIMIT_TEST"` **替换成你自己在智兔数服获取到的真实 API Token**！ 否则服务无法正常工作哦！

  

### 3. 配置 MCP 客户端

根据你使用的客户端进行配置：

*   **如果你用 Cline:**
    1.  打开 Cline (独立版或 VS Code 插件均可)。
    2.  进入设置，找到 MCP Servers 管理界面。
    3.  添加一个新的 MCP Server。
    4.  **Name:** 随意填，比如 `Zhitou_HS_API`。
    5.  **Command:** 填入**完整**的 Python 解释器路径和你保存的脚本**绝对路径**。
        *   *Mac/Linux 示例:* `/usr/local/bin/python3 /path/to/your/project/mcp_zhitou_server.py`
        *   *Windows 示例:* `C:\Python311\python.exe C:\Users\PGFA\project\mcp_zhitou_server.py` (路径请根据你的实际情况修改！)
    6.  保存配置。启动 Cline 后，应该能看到这个 Server 处于连接状态。

*   **如果你用 Cursor:**
    1.  在你的项目**根目录**下，创建一个名为 `.cursor` 的文件夹（如果不存在）。
    2.  在 `.cursor` 文件夹内，创建一个名为 `mcp.json` 的文件。
    3.  将以下 JSON 内容粘贴进去，**并修改 `args` 中的脚本路径为你的实际绝对路径**：

        ```json
        {
          "mcpServers": {
            "zhitou_hs": { // 服务器的唯一标识符，可以自定义
              "command": "python", // 或 python3
              "args": ["/path/to/your/project/mcp_zhitou_server.py"], // ⚠️⚠️⚠️ 修改为你的脚本实际路径！
              // "workingDirectory": "/path/to/your/project/", // 可选，但建议设置
              "tools": [
                // 建议把你实现的工具在这里声明一下，方便 Agent 发现
                {"name": "get_stock_list", "description": "获取基础 A 股股票列表 (代码, 名称, 交易所)。"},
                {"name": "get_new_stock_calendar", "description": "获取新股日历 (申购信息, 上市日期等)。"},
                {"name": "get_company_profile", "description": "获取指定股票代码的上市公司简介。", "parameters": {"stock_code": {"type":"string", "description": "股票代码, e.g., '000001'"}}},
                {"name": "get_capital_daily_trend", "description": "获取指定股票代码的每日资金流入趋势 (近十年)。", "parameters": {"stock_code": {"type":"string"}}},
                {"name": "get_all_announcements", "description": "获取指定股票代码的历史所有公告列表。", "parameters": {"stock_code": {"type":"string"}}}
                // ... 如果添加了更多工具，也在这里声明 ...
              ]
            }
          }
        }
        ```
    4.  保存 `mcp.json` 文件。重启 Cursor 或让它重新加载项目配置。

### 4. 开始玩耍！🎉

现在，打开你的 Cursor 或 Cline 聊天窗口，试试用自然语言和 AI 对话，让它调用我们定义的工具吧！

*   "用 `get_stock_list` 工具帮我看看最新的股票列表。"
*   "查询一下 000001 的公司简介，使用 `get_company_profile` 工具。"
*   "今天的新股日历是啥？" (AI 应该会选择 `get_new_stock_calendar`)
*   "帮我看看股票 600519 最近的所有公告。" (AI 应该会选择 `get_all_announcements`)

观察 AI 的回复和你的终端日志，享受 AI 帮你干活的乐趣吧！😉

## 🔧 可用工具列表 (Tools Available)

当前已实现的 MCP 工具 (对应 Python 函数)：

*   **`get_stock_list`**: 获取基础 A 股股票列表 (代码, 名称, 交易所)。
*   **`get_new_stock_calendar`**: 获取新股日历 (申购信息, 上市日期等)。
*   **`get_company_profile`**: 获取指定股票代码的上市公司简介。(需要 `stock_code` 参数)
*   **`get_capital_daily_trend`**: 获取指定股票代码的每日资金流入趋势 (近十年)。(需要 `stock_code` 参数)
*   **`get_all_announcements`**: 获取指定股票代码的历史所有公告列表。(需要 `stock_code` 参数)
*   *(欢迎添加更多工具！)*

## 🚀 如何扩展？(Adding More Tools)

想让你的 AI 助手更强大？完全 OK！

1.  **查阅智兔 API 文档:** 找到你想添加功能的 API 端点。
2.  **编写 Python 函数:** 在 `mcp_zhitou_server.py` 中，仿照现有的工具函数，编写一个新的函数来调用这个 API，记得处理好参数和返回值。给函数写上清晰的 `docstring` 哦！
3.  **注册工具:** 在 `TOOLS` 字典里，添加一行，把新的工具名和你刚写的函数关联起来。
4.  **(可选) 更新客户端配置:** 如果你的客户端配置 (如 Cursor 的 `mcp.json`) 需要显式声明工具列表，记得把新工具加进去。
5.  重启你的 MCP 服务（通常客户端会自动重启或重新连接）。

搞定！你的 AI 又解锁了新技能！😎

## 📜 许可证 (License)

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢 (Acknowledgements)

*   感谢 **智兔数服** 提供稳定易用的沪深数据 API。
*   感谢 **Anthropic** 提出 MCP 协议，开启了 AI Agent 的新时代。
*   感谢屏幕前的你！点个 Star ⭐ 支持一下 PGFA 吧！

---

希望这份 README 对你有帮助！快去试试看，让你的 AI 动起来吧！有问题欢迎在 Issues 区提出。Have Fun Coding! 💖
