# B站排行榜GitHub Action设置指南

本项目使用GitHub Action自动获取B站视频排行榜数据，并将结果更新到README.md文件中。以下是设置和使用指南。

## 设置步骤

1. **Fork或克隆本仓库**

   将本仓库Fork到你的GitHub账号下，或者克隆到本地后推送到你的GitHub仓库。

2. **启用GitHub Actions**

   - 进入你的GitHub仓库
   - 点击顶部的「Actions」选项卡
   - 如果看到提示，点击「I understand my workflows, go ahead and enable them」启用工作流

3. **验证工作流设置**

   - 检查`.github/workflows/update-ranking.yml`文件，确保定时任务设置正确
   - 默认设置为每天UTC时间0点和12点运行（对应北京时间8点和20点）

4. **手动触发工作流（可选）**

   - 在「Actions」选项卡中，点击左侧的「Update Bilibili Ranking」工作流
   - 点击「Run workflow」按钮，选择分支，然后点击绿色的「Run workflow」按钮

## 自定义设置

### 修改更新频率

如果你想修改排行榜更新的频率，可以编辑`.github/workflows/update-ranking.yml`文件中的cron表达式：

```yaml
schedule:
  - cron: '0 0,12 * * *'  # UTC时间每天0点和12点
```

### 修改排行榜分区

默认情况下，脚本获取全站排行榜。如果你想获取特定分区的排行榜，可以修改`.github/scripts/update_ranking.py`文件中的`rid`参数：

```python
# 获取不同类型的排行榜数据
all_ranking = fetch_ranking_data(rid=0, ranking_type='all')  # rid=0表示全站
```

可用的分区ID可以参考B站API文档或者ranking.md文件中的说明。

## 故障排除

如果GitHub Action运行失败，可以：

1. 检查Actions日志，查看具体错误信息
2. 确保仓库有正确的权限来创建和推送提交
3. 检查API是否发生变化，可能需要更新请求参数或处理逻辑

## 注意事项

- 此脚本仅用于学习和研究目的，请勿用于商业用途
- 请遵守B站的使用条款和API使用规范
- 过于频繁的API请求可能会导致IP被临时限制