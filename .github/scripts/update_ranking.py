#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import pandas as pd
from datetime import datetime
import os  # 导入os模块用于处理文件路径

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
        "web_location": "333.934"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    # 添加重试机制
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"正在获取排行榜数据 (rid={rid}, type={ranking_type})...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 验证响应内容
            if not response.text:
                raise ValueError("响应内容为空")
            
            data = response.json()
            
            if data.get("code") == 0 and "data" in data and "list" in data["data"]:
                ranking_list = data["data"]["list"]
                if ranking_list:
                    print(f"成功获取 {len(ranking_list)} 条排行榜数据")
                    return ranking_list
                else:
                    print("排行榜数据为空")
                    return []
            else:
                error_msg = data.get('message', f"错误码: {data.get('code', 'unknown')}")
                print(f"API返回错误: {error_msg}")
                print(f"完整响应数据: {data}")
                retry_count += 1
                if retry_count < max_retries:
                    # 使用指数退避算法，逐渐增加等待时间
                    wait_time = 2 ** retry_count
                    print(f"正在进行第{retry_count}次重试，等待{wait_time}秒...")
                    time.sleep(wait_time)
                else:
                    return []
        except requests.exceptions.Timeout:
            print("请求超时")
            retry_count += 1
            if retry_count < max_retries:
                # 使用指数退避算法，逐渐增加等待时间
                wait_time = 2 ** retry_count
                print(f"正在进行第{retry_count}次重试，等待{wait_time}秒...")
                time.sleep(wait_time)
            else:
                return []
        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {e}")
            retry_count += 1
            if retry_count < max_retries:
                # 使用指数退避算法，逐渐增加等待时间
                wait_time = 2 ** retry_count
                print(f"正在进行第{retry_count}次重试，等待{wait_time}秒...")
                time.sleep(wait_time)
            else:
                return []
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            retry_count += 1
            if retry_count < max_retries:
                # 使用指数退避算法，逐渐增加等待时间
                wait_time = 2 ** retry_count
                print(f"正在进行第{retry_count}次重试，等待{wait_time}秒...")
                time.sleep(wait_time)
            else:
                return []
        except Exception as e:
            print(f"未知异常: {e}")
            retry_count += 1
            if retry_count < max_retries:
                # 使用指数退避算法，逐渐增加等待时间
                wait_time = 2 ** retry_count
                print(f"正在进行第{retry_count}次重试，等待{wait_time}秒...")
                time.sleep(wait_time)
            else:
                return []
    
    print("所有重试均失败，返回空列表")
    return []

# 生成美观的Markdown表格
def generate_markdown_table(ranking_data, section_title):
    """
    将排行榜数据转换为美观的Markdown表格
    
    参数:
        ranking_data: 排行榜数据列表
        section_title: 表格标题
    
    返回:
        Markdown格式的表格字符串
    """
    # 清理标题中的特殊字符
    clean_title = section_title.replace("|", "｜").replace("\n", " ").replace("\r", " ")
    
    if not ranking_data:
        return f"## {clean_title}\n\n*暂无数据*\n\n"
    
    # 提取需要的字段
    table_data = []
    for i, item in enumerate(ranking_data[:20]):  # 只取前20条数据
        try:
            # 确保所有必要的字段都存在，使用更安全的方式获取嵌套数据
            owner = item.get("owner", {})
            stat = item.get("stat", {})
            pic = item.get("pic", "")
            
            # 构建数据行
            # 处理标题中的特殊字符，避免在Markdown表格中被误解
            video_title = item.get("title", "未知")
            video_title = video_title.replace("|", "｜")  # 将竖线替换为全角竖线
            video_title = video_title.replace("\n", " ")  # 替换换行符
            video_title = video_title.replace("\r", " ")  # 替换回车符
            
            # 构建带链接的标题（Markdown格式）
            bvid = item.get('bvid', '')
            if bvid:
                linked_title = f"[{video_title}](https://www.bilibili.com/video/{bvid})"
            else:
                linked_title = video_title
            
            row_data = {
                "排名": i + 1,
                "缩略图": f"![缩略图]({pic})" if pic else "无图片",
                "标题": linked_title,
                "UP主": owner.get("name", "未知") if owner else "未知",
                "播放量": format_number(stat.get("view", 0)) if stat else "0",
                "弹幕数": format_number(stat.get("danmaku", 0)) if stat else "0",
                "发布时间": format_timestamp(item.get("pubdate", 0))
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
                "发布时间": "未知"
            })
    
    # 转换为DataFrame以便格式化
    df = pd.DataFrame(table_data)
    
    # 生成Markdown表格
    markdown_table = f"## {section_title}\n\n"
    markdown_table += "*点击标题可直接跳转到对应视频*\n\n"
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
    try:
        num = int(num) if num else 0
        if num >= 10000:
            return f"{num/10000:.1f}万"
        return f"{num:,}"
    except (ValueError, TypeError):
        return "0"

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
        if not timestamp or timestamp <= 0:
            return "未知"
        return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
    except (ValueError, TypeError, OSError):
        return "未知"

# 生成README.md文件
def generate_readme():
    """
    生成README.md文件，包含全站、原创和新人排行榜
    """
    print("开始生成README.md文件...")
    
    # 获取不同类型的排行榜数据
    print("正在获取排行榜数据...")
    all_ranking = fetch_ranking_data(rid=0, ranking_type='all')
    origin_ranking = fetch_ranking_data(rid=0, ranking_type='origin')
    anime_ranking = fetch_ranking_data(rid=1, ranking_type='all')  # 动画分区
    digital_ranking = fetch_ranking_data(rid=188, ranking_type='all')  # 数码分区
    rookie_ranking = fetch_ranking_data(rid=0, ranking_type='rookie')
    
    # 生成当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 组合Markdown内容
    markdown_content = f"# B站视频排行榜\n\n更新时间: {current_time}\n\n"
    
    # 使用固定的分区标题，不再用视频标题替换
    if all_ranking:
        markdown_content += generate_markdown_table(all_ranking, "全站排行榜")
    else:
        markdown_content += generate_markdown_table([], "全站排行榜（数据获取失败）")
    
    if origin_ranking:
        markdown_content += generate_markdown_table(origin_ranking, "原创排行榜")
    else:
        markdown_content += generate_markdown_table([], "原创排行榜（数据获取失败）")
    
    if anime_ranking:
        markdown_content += generate_markdown_table(anime_ranking, "动画排行榜")
    else:
        markdown_content += generate_markdown_table([], "动画排行榜（数据获取失败）")
    
    if digital_ranking:
        markdown_content += generate_markdown_table(digital_ranking, "数码排行榜")
    else:
        markdown_content += generate_markdown_table([], "数码排行榜（数据获取失败）")
    
    if rookie_ranking:
        markdown_content += generate_markdown_table(rookie_ranking, "新人排行榜")
    else:
        markdown_content += generate_markdown_table([], "新人排行榜（数据获取失败）")
    
    # 添加页脚
    markdown_content += "\n---\n\n*数据来源: [Bilibili API](https://api.bilibili.com/x/web-interface/ranking/v2)*\n"
    markdown_content += "*此文件由 GitHub Action 自动生成*\n"
    
    # 写入README.md文件
    try:
        # 获取脚本当前路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建到项目根目录的路径
        project_root = os.path.join(script_dir, '..', '..')
        # 构建README.md的完整路径
        readme_path = os.path.join(project_root, 'README.md')
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"README.md 文件已成功更新于: {readme_path}")
    except Exception as e:
        print(f"写入README.md文件时出错: {e}")
        raise

# 主函数
if __name__ == "__main__":
    try:
        generate_readme()
        print("脚本执行完成")
    except Exception as e:
        print(f"脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)