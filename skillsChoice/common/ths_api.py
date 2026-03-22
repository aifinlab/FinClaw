#!/usr/bin/env python3
"""
同花顺iFinD API 数据接口封装
提供统一的金融数据获取接口
"""

import requests
import json
from typing import Optional, Dict, List
from datetime import datetime


class THSDataAPI:
    """同花顺iFinD API 数据接口 - 使用OpenAPI格式"""
    
    BASE_URL = "https://ft.10jqka.com.cn/api/v1"
    ACCESS_TOKEN = "b06d60d5efce5454b45a29cde92a1e892019ca45.signs_ODQ0NjM0NjEz"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.ACCESS_TOKEN}"
        }
    
    def get_realtime_quote(self, codes: List[str]) -> Optional[Dict]:
        """
        获取实时行情 - 使用同花顺OpenAPI格式
        codes: 股票代码列表，如 ['000001', '600036']
        """
        try:
            url = f"{self.BASE_URL}/realtime_quotation"
            # 构建请求体
            codes_str = ",".join([c if '.' in c else f"{c}.SH" if c.startswith('6') else f"{c}.SZ" for c in codes])
            payload = {
                "codes": codes_str,
                "fields": "open,high,low,latest,change_percent,volume,amount,pe_ttm,pb"
            }
            
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取实时行情失败: HTTP {response.status_code}, 响应: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"获取实时行情异常: {e}")
            return None
    
    def get_basic_data(self, codes: List[str], indicators: List[str]) -> Optional[Dict]:
        """
        获取基本面数据
        """
        try:
            url = f"{self.BASE_URL}/basic_data_service"
            codes_str = ",".join([c if '.' in c else f"{c}.SH" if c.startswith('6') else f"{c}.SZ" for c in codes])
            payload = {
                "codes": codes_str,
                "indicators": ",".join(indicators),
                "start_date": "20240101",
                "end_date": datetime.now().strftime("%Y%m%d")
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取基本面数据失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"获取基本面数据异常: {e}")
            return None
    
    def get_history_quote(self, code: str, start_date: str, end_date: str) -> Optional[Dict]:
        """获取历史行情"""
        try:
            url = f"{self.BASE_URL}/history_quote"
            code_formatted = code if '.' in code else f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
            payload = {
                "code": code_formatted,
                "start_date": start_date,
                "end_date": end_date,
                "fields": "open,high,low,close,volume,amount"
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取历史行情失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"获取历史行情异常: {e}")
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
    api = THSDataAPI()
    print("同花顺API接口测试")
    print(f"Token: {api.ACCESS_TOKEN[:20]}...")
    
    # 测试实时行情
    result = api.get_realtime_quote(["600036", "601318"])
    print(f"实时行情结果: {json.dumps(result, ensure_ascii=False, indent=2) if result else 'None'}")
