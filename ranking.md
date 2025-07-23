# 视频排行榜

<img src="../../assets/img/ranking.svg" width="100" height="100"/>

- [获取分区视频排行榜列表](#获取分区视频排行榜列表)

---

## 获取分区视频排行榜列表

> https://api.bilibili.com/x/web-interface/ranking/v2

*请求方式：GET*

鉴权方式: 请求头 `User-Agent` 非敏感字符串

获取稿件内容质量，近期的数据前100个稿件，动态更新。

**url参数：**

| 参数名       | 类型   | 内容         | 必要性 | 备注 |
| ------------ | ------ | ------------ | ------ | ------------------------------------- |
| rid          | number | 目标分区 tid | 非必要 | 默认为 0 (全站), 详细参见 [视频分区一览](../video/video_zone.md#视频分区一览), 仅支持主分区 |
| type         | string | 排行榜类型   | 非必要 | 全部: all<br />新人: rokkie<br />原创: origin |
| web_location | string | 333.934      | 非必要 |      |
| w_rid        | string | WBI 签名     | 非必要 | 参见 [WBI 签名](../misc/sign/wbi.md) |
| wts          | number | Unix 时间戳  | 非必要 | 参见 [WBI 签名](../misc/sign/wbi.md) |

**json回复：**

根对象：

| 字段    | 类型  | 内容     | 备注                        |
| ------- | ----- | -------- | --------------------------- |
| code    | num   | 返回值   | 0：成功<br />-400：请求错误 |
| message | str   | 错误信息 | 默认为0                     |
| ttl     | num   | 1        |                             |
| data    | array | 视频列表 |                             |

`data`对象：

| 字段 | 类型 | 内容 | 备注 |
| --- | --- | --- | --- |
| note | str | “根据稿件内容质量、近期的数据综合展示，动态更新” | 目前恒为此结果 |
| list | list | 视频列表 | 暂无 |

`list`列表：

| 项  | 类型 | 内容            | 备注 |
| --- | ---- | --------------- | ---- |
| 0   | obj  | 排行榜第1名     |      |
| n   | obj  | 排行榜第(n+1)名 |      |
| ……  | obj  | ……              | ……   |
| 99  | obj  | 排行榜第100名    |      |

`list`列表中的对象：

每个视频对象包含以下主要字段：

| 字段 | 类型 | 内容 | 备注 |
| --- | --- | --- | --- |
| aid | num | 稿件avid | |
| bvid | str | 稿件bvid | |
| cid | num | 视频cid | |
| title | str | 稿件标题 | |
| desc | str | 稿件简介 | |
| pic | str | 稿件封面图片url | |
| owner | obj | 稿件UP主信息 | |
| stat | obj | 稿件数据 | |
| duration | num | 稿件总时长(所有分P) | 单位为秒 |
| pubdate | num | 稿件发布时间 | 时间戳 |
| rights | obj | 稿件属性标志 | |

更多详细字段信息可参考[获取视频详细信息（web端）](../video/info.md#获取视频详细信息（web端）)中的data对象。

**示例：**

获取原创排行榜：
```
GET https://api.bilibili.com/x/web-interface/ranking/v2?type=origin
```

