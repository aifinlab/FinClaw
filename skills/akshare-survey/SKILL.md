# akshare-survey

机构调研数据查询与分析 Skill。提供A股市场机构调研记录、调研热度排行、调研问答分析等功能。

## 功能

- 最新机构调研数据查询
- 个股调研历史
- 调研热度排行
- 机构调研统计
- 调研问答详情

## 使用示例

查询最新调研：
```bash
python scripts/survey_latest.py --limit 30
```

查询个股调研：
```bash
python scripts/survey_stock.py --code 000001
```

调研热度排行：
```bash
python scripts/survey_rank.py
```

## 数据来源

- AkShare 机构调研数据接口

## License

MIT
