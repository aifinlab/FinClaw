#!/usr/bin/env python3
"""期货保证金计算器"""

import json
from datetime import datetime
import argparse


class FuturesMarginCalculator:
    """期货保证金计算器"""
    
    # 主流品种保证金率（参考值，实际以交易所为准）
    MARGIN_RATES = {
        # 上海期货交易所
        "CU": {"name": "沪铜", "exchange_rate": 0.10, "contract_multiplier": 5},
        "AL": {"name": "沪铝", "exchange_rate": 0.10, "contract_multiplier": 5},
        "ZN": {"name": "沪锌", "exchange_rate": 0.10, "contract_multiplier": 5},
        "AU": {"name": "黄金", "exchange_rate": 0.08, "contract_multiplier": 1000},
        "AG": {"name": "白银", "exchange_rate": 0.12, "contract_multiplier": 15},
        "RB": {"name": "螺纹钢", "exchange_rate": 0.10, "contract_multiplier": 10},
        "HC": {"name": "热轧卷板", "exchange_rate": 0.10, "contract_multiplier": 10},
        "FU": {"name": "燃料油", "exchange_rate": 0.10, "contract_multiplier": 10},
        "BU": {"name": "沥青", "exchange_rate": 0.10, "contract_multiplier": 10},
        "RU": {"name": "天然橡胶", "exchange_rate": 0.10, "contract_multiplier": 10},
        # 大连商品交易所
        "M": {"name": "豆粕", "exchange_rate": 0.10, "contract_multiplier": 10},
        "Y": {"name": "豆油", "exchange_rate": 0.10, "contract_multiplier": 10},
        "P": {"name": "棕榈油", "exchange_rate": 0.10, "contract_multiplier": 10},
        "C": {"name": "玉米", "exchange_rate": 0.10, "contract_multiplier": 10},
        "CS": {"name": "玉米淀粉", "exchange_rate": 0.10, "contract_multiplier": 10},
        "A": {"name": "豆一", "exchange_rate": 0.10, "contract_multiplier": 10},
        "B": {"name": "豆二", "exchange_rate": 0.10, "contract_multiplier": 10},
        "I": {"name": "铁矿石", "exchange_rate": 0.15, "contract_multiplier": 100},
        "J": {"name": "焦炭", "exchange_rate": 0.20, "contract_multiplier": 100},
        "JM": {"name": "焦煤", "exchange_rate": 0.20, "contract_multiplier": 60},
        "L": {"name": "塑料", "exchange_rate": 0.10, "contract_multiplier": 5},
        "PP": {"name": "聚丙烯", "exchange_rate": 0.10, "contract_multiplier": 5},
        "V": {"name": "PVC", "exchange_rate": 0.10, "contract_multiplier": 5},
        "EG": {"name": "乙二醇", "exchange_rate": 0.10, "contract_multiplier": 10},
        "PG": {"name": "液化石油气", "exchange_rate": 0.10, "contract_multiplier": 20},
        # 郑州商品交易所
        "SR": {"name": "白糖", "exchange_rate": 0.10, "contract_multiplier": 10},
        "CF": {"name": "棉花", "exchange_rate": 0.10, "contract_multiplier": 5},
        "TA": {"name": "PTA", "exchange_rate": 0.10, "contract_multiplier": 5},
        "MA": {"name": "甲醇", "exchange_rate": 0.10, "contract_multiplier": 10},
        "FG": {"name": "玻璃", "exchange_rate": 0.10, "contract_multiplier": 20},
        "SA": {"name": "纯碱", "exchange_rate": 0.12, "contract_multiplier": 20},
        "UR": {"name": "尿素", "exchange_rate": 0.10, "contract_multiplier": 20},
        "RM": {"name": "菜粕", "exchange_rate": 0.10, "contract_multiplier": 10},
        "OI": {"name": "菜油", "exchange_rate": 0.10, "contract_multiplier": 10},
        "AP": {"name": "苹果", "exchange_rate": 0.10, "contract_multiplier": 10},
        # 上海国际能源交易中心
        "SC": {"name": "原油", "exchange_rate": 0.10, "contract_multiplier": 1000},
        "LU": {"name": "低硫燃料油", "exchange_rate": 0.10, "contract_multiplier": 10},
        # 中国金融期货交易所
        "IF": {"name": "沪深300股指", "exchange_rate": 0.12, "contract_multiplier": 300},
        "IC": {"name": "中证500股指", "exchange_rate": 0.12, "contract_multiplier": 200},
        "IH": {"name": "上证50股指", "exchange_rate": 0.12, "contract_multiplier": 300},
        "IM": {"name": "中证1000股指", "exchange_rate": 0.12, "contract_multiplier": 200},
        "T": {"name": "10年期国债", "exchange_rate": 0.02, "contract_multiplier": 10000},
        "TF": {"name": "5年期国债", "exchange_rate": 0.012, "contract_multiplier": 10000},
        "TS": {"name": "2年期国债", "exchange_rate": 0.005, "contract_multiplier": 10000}
    }
    
    def calculate_margin(self, symbol: str, price: float, lots: int = 1, firm_multiplier: float = 1.2) -> dict:
        """计算保证金"""
        # 提取品种代码（去掉合约月份）
        product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
        
        if product_code not in self.MARGIN_RATES:
            return {"error": f"未找到品种{product_code}的保证金数据"}
        
        info = self.MARGIN_RATES[product_code]
        
        contract_value = price * info["contract_multiplier"]
        exchange_margin = contract_value * info["exchange_rate"]
        firm_margin = exchange_margin * firm_multiplier
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "product_name": info["name"],
            "price": price,
            "lots": lots,
            "contract_multiplier": info["contract_multiplier"],
            "contract_value": contract_value,
            "exchange_rate": f"{info['exchange_rate']*100}%",
            "exchange_margin": exchange_margin,
            "firm_multiplier": firm_multiplier,
            "firm_margin": firm_margin,
            "total_margin": firm_margin * lots,
            "data_source": "各交易所官方保证金标准"
        }
    
    def get_margin_rates(self) -> dict:
        """获取所有品种保证金率"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "margin_rates": self.MARGIN_RATES,
            "note": "保证金率会随市场风险调整，请以交易所最新公告为准"
        }


def main():
    parser = argparse.ArgumentParser(description="期货保证金计算器")
    parser.add_argument("--symbol", required=True, help="合约代码(如: RB2501)")
    parser.add_argument("--price", type=float, required=True, help="合约价格")
    parser.add_argument("--lots", type=int, default=1, help="手数")
    parser.add_argument("--multiplier", type=float, default=1.2, help="期货公司保证金倍数")
    parser.add_argument("--list", action="store_true", help="列出所有品种保证金率")
    
    args = parser.parse_args()
    calculator = FuturesMarginCalculator()
    
    if args.list:
        result = calculator.get_margin_rates()
    else:
        result = calculator.calculate_margin(args.symbol, args.price, args.lots, args.multiplier)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
