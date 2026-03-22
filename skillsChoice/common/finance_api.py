#!/usr/bin/env python3
"""
统一金融数据API接口
整合AkShare、腾讯财经、同花顺等多个数据源
"""

import requests
import json
from typing import Optional, Dict, List
from datetime import datetime


class FinanceDataAPI:
    """统一金融数据接口"""
    
    # 同花顺Token
    THS_TOKEN = "b06d60d5efce5454b45a29cde92a1e892019ca45.signs_ODQ0NjM0NjEz"
    
    def __init__(self):
        self.ths_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.THS_TOKEN}"
        }
    
    def get_realtime_quote(self, codes: List[str]) -> Optional[Dict]:
        """
        获取实时行情 - 使用腾讯财经API
        """
        try:
            # 腾讯财经API
            codes_formatted = []
            for c in codes:
                if c.startswith('6'):
                    codes_formatted.append(f"sh{c}")
                else:
                    codes_formatted.append(f"sz{c}")
            
            url = f"https://qt.gtimg.cn/q={','.join(codes_formatted)}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # 解析腾讯财经返回数据
                result = {}
                lines = response.text.strip().split(';')
                for line in lines:
                    if not line.strip():
                        continue
                    # 提取代码和数据
                    if 'v_' in line:
                        parts = line.split('=')
                        if len(parts) >= 2:
                            code_key = parts[0].split('_')[-1].replace('sh', '').replace('sz', '')
                            data_str = parts[1].strip('"')
                            data_fields = data_str.split('~')
                            if len(data_fields) >= 45:
                                result[code_key] = {
                                    "name": data_fields[1],
                                    "price": data_fields[3],
                                    "change": data_fields[4],
                                    "change_percent": data_fields[5],
                                    "volume": data_fields[6],
                                    "amount": data_fields[37],
                                    "market_cap": data_fields[45],
                                    "pe": data_fields[52] if len(data_fields) > 52 else None,
                                    "pb": data_fields[46] if len(data_fields) > 46 else None,
                                    "data_source": "腾讯财经"
                                }
                return {"data": result, "source": "腾讯财经"}
            else:
                return None
        except Exception as e:
            print(f"获取实时行情异常: {e}")
            return None
    
    def get_financial_data(self, code: str) -> Optional[Dict]:
        """
        获取财务数据 - 使用东方财富API
        """
        try:
            # 东方财富财务指标API
            url = f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYFXListV2?code={code}&type=3"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') and data['result'].get('data'):
                    latest = data['result']['data'][0]
                    return {
                        "roe": latest.get('ROE'),
                        "roa": latest.get('ROA'),
                        "eps": latest.get('EPS'),
                        "bvps": latest.get('BPS'),
                        "net_profit": latest.get('NET_PROFIT'),
                        "revenue": latest.get('TOTAL_OPERATE_REVENUE'),
                        "data_source": "东方财富"
                    }
            return None
        except Exception as e:
            print(f"获取财务数据异常: {e}")
            return None


# 股票代码映射
STOCK_CODES = {
    # 银行
    "工商银行": "601398", "建设银行": "601939", "农业银行": "601288",
    "中国银行": "601988", "招商银行": "600036", "交通银行": "601328",
    "邮储银行": "601658", "兴业银行": "601166", "平安银行": "000001",
    "中信银行": "601998", "浦发银行": "600000", "光大银行": "601818",
    "民生银行": "600016", "华夏银行": "600015", "北京银行": "601169",
    "上海银行": "601229", "南京银行": "601009", "宁波银行": "002142",
    "杭州银行": "600926", "江苏银行": "600919", "成都银行": "601838",
    # 券商
    "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
    "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
    "中国银河": "601881", "中信建投": "601066", "中金公司": "601995",
    "东方证券": "600958", "光大证券": "601788", "国信证券": "002736",
    "申万宏源": "000166", "方正证券": "601901", "兴业证券": "601377",
    "浙商证券": "601878",
    # 保险
    "中国平安": "601318", "中国人寿": "601628", "中国太保": "601601",
    "新华保险": "601336", "中国人保": "601319"
}


def get_stock_code(name: str) -> Optional[str]:
    """获取股票代码"""
    return STOCK_CODES.get(name)


if __name__ == "__main__":
    # 测试
    api = FinanceDataAPI()
    print("金融数据API接口测试")
    
    # 测试实时行情
    result = api.get_realtime_quote(["600036", "601318"])
    print(f"实时行情: {json.dumps(result, ensure_ascii=False, indent=2) if result else 'None'}")
