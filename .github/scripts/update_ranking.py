#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import pandas as pd
from datetime import datetime

# 获取排行榜数据的函数
def fetch_ranking_data(rid=0, ranking_type='all'):
    """获取B站视频排行榜数据
    
    参数:
        rid: 分区ID，默认为0（全站）
        ranking_type: 排行榜类型，可选值：all（全部）, rookie（新人）, origin（原创）
    
    返回:
        排行榜数据列表
    """
    url = "https://api.bilibili.com/x/web-interface/ranking/v2"
    
    params = {
        "rid": rid,
        "type": ranking_type,
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 添加重试机制
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            
            if data["code"] == 0 and "data" in data and "list" in data["data"]:
                return data["data"]["list"]
            else:
                error_msg = data.get('message', f"错误码: {data['code']}")
                print(f"获取排行榜失败: {error_msg}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"正在进行第{retry_count}次重试...")
                    time.sleep(2)  # 等待2秒后重试
                else:
                    return []
        except Exception as e:
            print(f"请求异常: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"正在进行第{retry_count}次重试...")
                time.sleep(2)  # 等待2秒后重试
            else:
                return []

# 生成美观的Markdown表格
def generate_markdown_table(ranking_data, title):
    """
    将排行榜数据转换为美观的Markdown表格
    
    参数:
        ranking_data: 排行榜数据列表
        title: 表格标题
    
    返回:
        Markdown格式的表格字符串
    """
    if not ranking_data:
        return f"## {title}\n\n*暂无数据*\n\n"
    
    # 提取需要的字段
    table_data = []
    for i, item in enumerate(ranking_data[:20]):  # 只取前20条数据
        try:
            # 确保所有必要的字段都存在，使用更安全的方式获取嵌套数据
            owner = item.get("owner", {})
            stat = item.get("stat", {})
            pic = item.get("pic", "")
            
            # 构建数据行
            # 处理标题中的竖线符号，避免在Markdown表格中被误解为列分隔符
            title = item.get("title", "未知")
            title = title.replace("|", "｜")  # 将竖线替换为全角竖线
            
            row_data = {
                "排名": i + 1,
                "缩略图": f"![缩略图]({pic})" if pic else "无图片",
                "标题": title,
                "UP主": owner.get("name", "未知") if owner else "未知",
                "播放量": format_number(stat.get("view", 0)) if stat else "0",
                "弹幕数": format_number(stat.get("danmaku", 0)) if stat else "0",
                "发布时间": format_timestamp(item.get("pubdate", 0)),
                "视频链接": f"https://www.bilibili.com/video/{item.get('bvid', '')}"
            }
            
            table_data.append(row_data)
        except Exception as e:
            print(f"处理数据时出错 (排名 {i+1}): {e}")
            # 添加一个占位行，确保排名连续
            table_data.append({
                "排名": i + 1,
                "缩略图": "无图片",
                "标题": "[数据处理错误]",  # 这里不需要处理竖线，因为是固定文本
                "UP主": "未知",
                "播放量": "0",
                "弹幕数": "0",
                "发布时间": "未知",
                "视频链接": ""
            })
    
    # 转换为DataFrame以便格式化
    df = pd.DataFrame(table_data)
    
    # 生成Markdown表格
    markdown_table = f"## {title}\n\n"
    markdown_table += df.to_markdown(index=False) + "\n\n"
    
    return markdown_table

# 格式化数字（添加千位分隔符）
def format_number(num):
    """
    格式化数字，添加千位分隔符
    
    参数:
        num: 需要格式化的数字
    
    返回:
        格式化后的字符串
    """
    if num >= 10000:
        return f"{num/10000:.1f}万"
    return f"{num:,}"

# 格式化时间戳
def format_timestamp(timestamp):
    """
    将时间戳转换为可读的日期格式
    
    参数:
        timestamp: Unix时间戳
    
    返回:
        格式化后的日期字符串
    """
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return "未知"

# 生成README.md文件
def generate_readme():
    """
    生成README.md文件，包含全站、原创和新人排行榜
    """
    # 获取不同类型的排行榜数据
    all_ranking = fetch_ranking_data(rid=0, ranking_type='all')
    origin_ranking = fetch_ranking_data(rid=0, ranking_type='origin')
    rookie_ranking = fetch_ranking_data(rid=0, ranking_type='rookie')
    
    # 添加动画区排行榜
    anime_ranking = fetch_ranking_data(rid=1, ranking_type='all')
    
    # 生成当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 组合Markdown内容
    markdown_content = f"# B站视频排行榜\n\n更新时间: {current_time}\n\n"
    markdown_content += generate_markdown_table(all_ranking, "全站排行榜")
    markdown_content += generate_markdown_table(origin_ranking, "原创排行榜")
    markdown_content += generate_markdown_table(rookie_ranking, "新人排行榜")
    markdown_content += generate_markdown_table(anime_ranking, "动画区排行榜")
    
    # 添加页脚
    markdown_content += "\n---\n\n*数据来源: [Bilibili API](https://api.bilibili.com/x/web-interface/ranking/v2)*\n"
    markdown_content += "*此文件由 GitHub Action 自动生成*\n"
    
    # 写入README.md文件
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print("README.md 文件已更新")

# 主函数
if __name__ == "__main__":
    generate_readme()