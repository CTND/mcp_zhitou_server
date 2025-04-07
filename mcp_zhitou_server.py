#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import requests
import logging
import traceback

# --- 配置 ---
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

ZHITU_API_BASE_URL = "https://api.zhituapi.com/hs"
# 🔥🔥🔥【请务必替换为你自己的有效 Token! 测试 Token 有限制!】🔥🔥🔥
ZHITU_TOKEN = "ZHITU_TOKEN_LIMIT_TEST"

logging.info("MCP 服务脚本初始化...")
if ZHITU_TOKEN == "ZHITU_TOKEN_LIMIT_TEST":
    logging.warning("⚠️ 警告：当前使用的是测试 Token (ZHITU_TOKEN_LIMIT_TEST)，功能和次数可能受限。请替换为您自己的有效 Token！")


# --- API 调用辅助函数 ---
def call_zhitou_api(endpoint_path, params=None):
    url = f"{ZHITU_API_BASE_URL}/{endpoint_path}?token={ZHITU_TOKEN}"
    logging.info(f"准备调用 Zhitou API: {url}")
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        logging.info(f"API 调用成功，状态码: {response.status_code}")
        # 尝试解析 JSON
        try:
            data = response.json()
            # 可以在这里检查智兔 API 可能返回的业务错误码（如果文档有定义）
            # 例如: if data.get('code') != 0: logging.error(...) raise ValueError(...)
            return data
        except json.JSONDecodeError as e:
             logging.error(f"解析 Zhitou API 响应 JSON 失败: {e}. 响应内容: {response.text[:500]}...") # 记录部分响应内容
             raise ValueError(f"无法解析 Zhitou API 返回的 JSON 数据")
    except requests.exceptions.Timeout:
        logging.error(f"调用 Zhitou API 超时: {url}")
        raise TimeoutError(f"请求 Zhitou API 超时 ({url})")
    except requests.exceptions.RequestException as e:
        logging.error(f"调用 Zhitou API 失败: {e}")
        raise ConnectionError(f"无法连接或请求 Zhitou API 失败: {e}")


# --- MCP 工具函数 ---
def get_stock_list(**kwargs):
    """获取基础 A 股股票列表 (代码, 名称, 交易所)。"""
    logging.info("执行工具: get_stock_list")
    return call_zhitou_api("list/all")

def get_new_stock_calendar(**kwargs):
    """获取新股日历 (申购信息, 上市日期等)。"""
    logging.info("执行工具: get_new_stock_calendar")
    return call_zhitou_api("list/new")

def get_company_profile(stock_code, **kwargs):
    """获取指定股票代码的上市公司简介。
    Args:
        stock_code (str): 股票代码, 例如 '000001'。
    """
    if not stock_code:
        raise ValueError("工具 'get_company_profile' 需要 'stock_code' 参数。")
    logging.info(f"执行工具: get_company_profile, stock_code={stock_code}")
    return call_zhitou_api(f"gs/gsjj/{stock_code}")

def get_capital_daily_trend(stock_code, **kwargs):
    """获取指定股票代码的每日资金流入趋势 (近十年)。
    Args:
        stock_code (str): 股票代码, 例如 '000001'。
    """
    if not stock_code:
        raise ValueError("工具 'get_capital_daily_trend' 需要 'stock_code' 参数。")
    logging.info(f"执行工具: get_capital_daily_trend, stock_code={stock_code}")
    return call_zhitou_api(f"capital/lrqs/{stock_code}")

def get_all_announcements(stock_code, **kwargs):
     """获取指定股票代码的历史所有公告列表。
     Args:
         stock_code (str): 股票代码, 例如 '000001'。
     """
     if not stock_code:
         raise ValueError("工具 'get_all_announcements' 需要 'stock_code' 参数。")
     logging.info(f"执行工具: get_all_announcements, stock_code={stock_code}")
     return call_zhitou_api(f"msg/sygg/{stock_code}")

# --- 你可以继续添加更多工具函数在这里 ---


# --- MCP 工具映射 ---
TOOLS = {
    "get_stock_list": get_stock_list,
    "get_new_stock_calendar": get_new_stock_calendar,
    "get_company_profile": get_company_profile,
    "get_capital_daily_trend": get_capital_daily_trend,
    "get_all_announcements": get_all_announcements,
    # --- 如果添加了新函数，在这里加上映射 ---
}
logging.info(f"已注册的 MCP 工具: {list(TOOLS.keys())}")


# --- 请求处理函数 ---
def handle_request(request_data):
    request_id = request_data.get("id")

    if request_data.get("jsonrpc") != "2.0" or "method" not in request_data:
        logging.error(f"无效的请求格式: {request_data}")
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "无效请求 (Invalid Request)"},
            "id": request_id
        })

    method = request_data.get("method")
    params = request_data.get("params", {})
    response_payload = None

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        logging.info(f"收到工具调用请求 -> Tool: '{tool_name}', Arguments: {arguments}")

        if tool_name in TOOLS:
            try:
                tool_function = TOOLS[tool_name]
                result_data = tool_function(**arguments)
                response_payload = {"result": json.dumps(result_data, ensure_ascii=False)}
                logging.info(f"工具 '{tool_name}' 执行成功。")
            except (ValueError, TypeError) as e:
                 logging.warning(f"工具 '{tool_name}' 参数错误: {e}")
                 response_payload = {"error": {"code": -32602, "message": f"无效参数 (Invalid params): {e}"}}
            except (ConnectionError, TimeoutError, ValueError) as e:
                 logging.error(f"调用 Zhitou API 时出错 (工具 '{tool_name}'): {e}")
                 response_payload = {"error": {"code": -32000, "message": f"服务器错误: 调用外部 API 失败 - {e}"}}
            except Exception as e:
                logging.error(f"执行工具 '{tool_name}' 时发生未知错误: {e}\n{traceback.format_exc()}")
                response_payload = {"error": {"code": -32000, "message": f"服务器内部错误: {type(e).__name__}: {e}"}}
        else:
            logging.warning(f"请求的工具 '{tool_name}' 未在本服务中定义。")
            response_payload = {"error": {"code": -32601, "message": f"方法未找到 (Method not found): 工具 '{tool_name}' 不存在"}}

    elif method == "tools/list":
         logging.info("收到工具列表请求 (tools/list)")
         tool_list = []
         for name, func in TOOLS.items():
             doc = func.__doc__ or "无描述"
             param_info = {}
             if "Args:" in doc:
                 try:
                     args_section = doc.split("Args:")[1].split("Returns:")[0].split("Raises:")[0].strip()
                     for line in args_section.split('\n'):
                         parts = line.strip().split('(')
                         if len(parts) > 1:
                             param_name = parts[0].strip()
                             param_type = "string"
                             if "int" in parts[1].lower() or "number" in parts[1].lower(): param_type = "number"
                             elif "bool" in parts[1].lower(): param_type = "boolean"
                             param_info[param_name] = {"type": param_type}
                 except Exception as e:
                     logging.warning(f"解析工具 '{name}' 的 docstring 参数失败: {e}")
             tool_list.append({
                 "name": name,
                 "description": doc.split("Args:")[0].strip(),
                 "parameters": param_info
                 })
         response_payload = {"result": json.dumps(tool_list, ensure_ascii=False)}
         logging.info(f"返回工具列表: {tool_list}")
    else:
        logging.warning(f"收到不支持的方法请求: {method}")
        response_payload = {"error": {"code": -32601, "message": f"方法未找到 (Method not found): {method}"}}

    final_response = {"jsonrpc": "2.0", "id": request_id}
    final_response.update(response_payload)
    return json.dumps(final_response, ensure_ascii=False)


# --- 主循环 ---
def main():
    logging.info("✅ Zhitou API MCP 服务已启动，开始监听标准输入 (stdin)...")
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                logging.info("标准输入 (stdin) 已关闭，MCP 服务退出。")
                break
            line = line.strip()
            if not line: continue
            logging.debug(f"收到原始输入行: {line}")
            try:
                request_data = json.loads(line)
            except json.JSONDecodeError:
                logging.error(f"❌ 无法解析输入的 JSON 数据: {line}")
                continue
            response_str = handle_request(request_data)
            if response_str:
                logging.debug(f"准备发送响应: {response_str}")
                print(response_str, flush=True) # 关键！确保立即发送！
        except KeyboardInterrupt:
            logging.info("收到 KeyboardInterrupt (Ctrl+C)，正在关闭 MCP 服务...")
            break
        except BrokenPipeError:
             logging.warning("管道已断开 (BrokenPipeError)，可能是客户端已关闭。MCP 服务退出。")
             break
        except Exception as e:
            logging.error(f"❌ MCP 服务主循环发生严重错误: {e}\n{traceback.format_exc()}")
            continue
    logging.info("👋 MCP 服务已停止。")

# 脚本执行入口
if __name__ == "__main__":
    main()
