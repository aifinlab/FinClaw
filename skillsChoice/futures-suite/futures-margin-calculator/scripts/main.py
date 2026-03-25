#!/usr/bin/env python3
"""期货保证金计算器 - 接入AkShare实时数据源"""

import json
from datetime import datetime
import argparse


class FuturesMarginCalculator:
    """期货保证金计算器 - 接入AkShare数据源"""
    
    # 交易所代码映射
    EXCHANGE_MAP = {
        'SHFE': '上海期货交易所',
        'DCE': '大连商品交易所', 
        'CZCE': '郑州商品交易所',
        'INE': '上海国际能源交易中心',
        'CFFEX': '中国金融期货交易所',
        'GFEX': '广州期货交易所'
    }
    
    # 品种代码到交易所的映射（用于确定品种所属交易所）
    SYMBOL_EXCHANGE_MAP = {
        # 上海期货交易所
        'CU': 'SHFE', 'AL': 'SHFE', 'ZN': 'SHFE', 'PB': 'SHFE', 'NI': 'SHFE', 'SN': 'SHFE',
        'AU': 'SHFE', 'AG': 'SHFE', 'RB': 'SHFE', 'WR': 'SHFE', 'HC': 'SHFE', 'SS': 'SHFE',
        'FU': 'SHFE', 'BU': 'SHFE', 'RU': 'SHFE', 'NR': 'SHFE', 'SP': 'SHFE', 'AO': 'SHFE',
        # 大连商品交易所
        'M': 'DCE', 'Y': 'DCE', 'P': 'DCE', 'C': 'DCE', 'CS': 'DCE', 'A': 'DCE', 'B': 'DCE',
        'I': 'DCE', 'J': 'DCE', 'JM': 'DCE', 'L': 'DCE', 'PP': 'DCE', 'V': 'DCE', 'EG': 'DCE',
        'PG': 'DCE', 'EB': 'DCE', 'RR': 'DCE', 'JD': 'DCE', 'LH': 'DCE', 'FB': 'DCE',
        # 郑州商品交易所
        'SR': 'CZCE', 'CF': 'CZCE', 'TA': 'CZCE', 'MA': 'CZCE', 'FG': 'CZCE', 'SA': 'CZCE',
        'UR': 'CZCE', 'RM': 'CZCE', 'OI': 'CZCE', 'AP': 'CZCE', 'SF': 'CZCE', 'SM': 'CZCE',
        'ZC': 'CZCE', 'CY': 'CZCE', 'PF': 'CZCE', 'PR': 'CZCE', 'CJ': 'CZCE', 'RI': 'CZCE',
        'WH': 'CZCE', 'RS': 'CZCE', 'JR': 'CZCE', 'LR': 'CZCE', 'PM': 'CZCE', 'PK': 'CZCE',
        # 上海国际能源交易中心
        'SC': 'INE', 'LU': 'INE', 'BC': 'INE',
        # 中国金融期货交易所
        'IF': 'CFFEX', 'IC': 'CFFEX', 'IH': 'CFFEX', 'IM': 'CFFEX',
        'T': 'CFFEX', 'TF': 'CFFEX', 'TS': 'CFFEX', 'TL': 'CFFEX',
        # 广州期货交易所
        'SI': 'GFEX', 'LC': 'GFEX'
    }
    
    def __init__(self):
        self._margin_data = None
        self._data_timestamp = None
        self._cache_duration = 300  # 缓存5分钟
    
    def _load_akshare_data(self) -> dict:
        """从AkShare加载保证金数据 - 使用futures_comm_info接口"""
        try:
            import akshare as ak
            import pandas as pd
            
            # 获取所有交易所的保证金数据
            all_data = []
            exchanges = ['上海期货交易所', '大连商品交易所', '郑州商品交易所', 
                        '上海国际能源交易中心', '中国金融期货交易所', '广州期货交易所']
            
            for exchange in exchanges:
                try:
                    df = ak.futures_comm_info(symbol=exchange)
                    if df is not None and not df.empty:
                        df['交易所'] = exchange
                        all_data.append(df)
                except Exception as e:
                    # 单个交易所失败不影响其他
                    continue
            
            if not all_data:
                return {}
            
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 转换为字典格式，以品种代码+合约为key
            margin_dict = {}
            for _, row in combined_df.iterrows():
                contract_code = str(row.get('合约代码', '')).strip()
                if contract_code:
                    # 提取保证金率 - 处理百分比格式
                    long_margin = row.get('保证金-买开', 0)
                    short_margin = row.get('保证金-卖开', 0)
                    
                    # 如果是百分比字符串，转换为小数
                    if isinstance(long_margin, str):
                        long_margin = float(long_margin.replace('%', '')) / 100
                    elif isinstance(long_margin, (int, float)) and long_margin > 1:
                        long_margin = long_margin / 100
                    
                    if isinstance(short_margin, str):
                        short_margin = float(short_margin.replace('%', '')) / 100
                    elif isinstance(short_margin, (int, float)) and short_margin > 1:
                        short_margin = short_margin / 100
                    
                    margin_dict[contract_code] = {
                        'name': row.get('合约名称', ''),
                        'exchange': row.get('交易所', ''),
                        'long_margin_rate': long_margin,
                        'short_margin_rate': short_margin,
                        'margin_per_lot': row.get('保证金-每手', 0),
                        'current_price': row.get('现价', 0),
                        'price_update_time': str(row.get('价格更新时间', ''))
                    }
            
            self._data_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return margin_dict
            
        except ImportError:
            return {"error": "AkShare未安装，请运行: pip install akshare"}
        except Exception as e:
            return {"error": f"获取AkShare数据失败: {str(e)}"}
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._margin_data is None or self._data_timestamp is None:
            return False
        try:
            last_update = datetime.strptime(self._data_timestamp, "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - last_update).seconds < self._cache_duration
        except:
            return False
    
    def _get_product_code(self, symbol: str) -> str:
        """从合约代码提取品种代码"""
        # 提取字母部分作为品种代码
        product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
        return product_code
    
    def _get_contract_multiplier(self, symbol: str) -> int:
        """获取合约乘数（从AkShare获取或默认配置）"""
        # 常见品种合约乘数配置
        MULTIPLIER_MAP = {
            'CU': 5, 'AL': 5, 'ZN': 5, 'PB': 5, 'NI': 1, 'SN': 1,
            'AU': 1000, 'AG': 15, 'RB': 10, 'WR': 10, 'HC': 10, 'SS': 5,
            'FU': 10, 'BU': 10, 'RU': 10, 'NR': 10, 'SP': 10, 'AO': 20,
            'M': 10, 'Y': 10, 'P': 10, 'C': 10, 'CS': 10, 'A': 10, 'B': 10,
            'I': 100, 'J': 100, 'JM': 60, 'L': 5, 'PP': 5, 'V': 5, 'EG': 10,
            'PG': 20, 'EB': 5, 'RR': 10, 'JD': 5, 'LH': 16, 'FB': 500,
            'SR': 10, 'CF': 5, 'TA': 5, 'MA': 10, 'FG': 20, 'SA': 20,
            'UR': 20, 'RM': 10, 'OI': 10, 'AP': 10, 'SF': 5, 'SM': 5,
            'ZC': 100, 'CY': 5, 'PF': 5, 'PR': 5, 'CJ': 5, 'RI': 20,
            'WH': 20, 'RS': 10, 'JR': 20, 'LR': 10, 'PM': 50, 'PK': 5,
            'SC': 1000, 'LU': 10, 'BC': 5,
            'IF': 300, 'IC': 200, 'IH': 300, 'IM': 200,
            'T': 10000, 'TF': 10000, 'TS': 10000, 'TL': 10000,
            'SI': 5, 'LC': 1
        }
        product_code = self._get_product_code(symbol)
        return MULTIPLIER_MAP.get(product_code, 10)  # 默认10
    
    def get_margin_from_akshare(self, symbol: str) -> dict:
        """从AkShare获取指定合约的保证金数据"""
        if not self._is_cache_valid():
            self._margin_data = self._load_akshare_data()
        
        if isinstance(self._margin_data, dict) and 'error' in self._margin_data:
            return self._margin_data
        
        # 尝试直接匹配合约代码
        if symbol.upper() in self._margin_data:
            return self._margin_data[symbol.upper()]
        
        # 尝试小写匹配
        if symbol.lower() in self._margin_data:
            return self._margin_data[symbol.lower()]
        
        return None
    
    def calculate_margin(self, symbol: str, price: float = None, lots: int = 1, 
                        firm_multiplier: float = 1.2, direction: str = "long") -> dict:
        """
        计算保证金
        
        Args:
            symbol: 合约代码(如: RB2501)
            price: 合约价格(如不提供，尝试从AkShare获取)
            lots: 手数
            firm_multiplier: 期货公司保证金倍数
            direction: 方向(long/short)，影响保证金率
        """
        # 提取品种代码
        product_code = self._get_product_code(symbol)
        
        # 获取AkShare数据
        ak_data = self.get_margin_from_akshare(symbol)
        
        if ak_data and 'error' in ak_data:
            return ak_data
        
        # 确定保证金率
        if ak_data:
            if direction.lower() == "short":
                exchange_rate = ak_data.get('short_margin_rate', 0)
            else:
                exchange_rate = ak_data.get('long_margin_rate', 0)
            
            current_price = price if price else ak_data.get('current_price', 0)
            product_name = ak_data.get('name', product_code)
            exchange = ak_data.get('exchange', '未知')
            data_source = f"AkShare实时数据 ({ak_data.get('price_update_time', '')})"
        else:
            # 使用默认数据回退
            exchange_rate = 0.10  # 默认10%
            current_price = price if price else 0
            product_name = product_code
            exchange = self.EXCHANGE_MAP.get(self.SYMBOL_EXCHANGE_MAP.get(product_code, ''), '未知')
            data_source = "默认配置(未获取到AkShare数据)"
        
        if current_price <= 0:
            return {
                "error": f"未获取到合约{symbol}的价格数据，请手动提供--price参数",
                "symbol": symbol,
                "suggestion": f"示例: python main.py --symbol {symbol} --price 3500 --lots 1"
            }
        
        # 获取合约乘数
        contract_multiplier = self._get_contract_multiplier(symbol)
        
        # 计算保证金
        contract_value = current_price * contract_multiplier
        exchange_margin = contract_value * exchange_rate
        firm_margin = exchange_margin * firm_multiplier
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": data_source,
            "symbol": symbol,
            "product_code": product_code,
            "product_name": product_name,
            "exchange": exchange,
            "direction": direction,
            "price": current_price,
            "lots": lots,
            "contract_multiplier": contract_multiplier,
            "contract_value": round(contract_value, 2),
            "exchange_rate": f"{exchange_rate*100:.2f}%",
            "exchange_margin": round(exchange_margin, 2),
            "firm_multiplier": firm_multiplier,
            "firm_margin": round(firm_margin, 2),
            "total_margin": round(firm_margin * lots, 2),
            "note": "保证金率随市场风险调整，请以交易所最新公告为准"
        }
    
    def get_margin_rates(self, exchange: str = None) -> dict:
        """
        获取所有品种保证金率
        
        Args:
            exchange: 交易所代码(SHFE/DCE/CZCE/INE/CFFEX/GFEX)，为空则返回所有
        """
        if not self._is_cache_valid():
            self._margin_data = self._load_akshare_data()
        
        if isinstance(self._margin_data, dict) and 'error' in self._margin_data:
            return self._margin_data
        
        # 过滤指定交易所
        filtered_data = {}
        target_exchange = self.EXCHANGE_MAP.get(exchange, '') if exchange else ''
        
        for contract_code, data in self._margin_data.items():
            if not target_exchange or data.get('exchange') == target_exchange:
                filtered_data[contract_code] = data
        
        # 按交易所分组
        grouped = {}
        for contract_code, data in filtered_data.items():
            exch = data.get('exchange', '其他')
            if exch not in grouped:
                grouped[exch] = []
            grouped[exch].append({
                "合约代码": contract_code,
                "合约名称": data.get('name', ''),
                "买开保证金率": f"{data.get('long_margin_rate', 0)*100:.2f}%",
                "卖开保证金率": f"{data.get('short_margin_rate', 0)*100:.2f}%",
                "每手保证金": data.get('margin_per_lot', 0),
                "当前价格": data.get('current_price', 0)
            })
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": f"AkShare实时数据",
            "total_contracts": len(filtered_data),
            "margin_rates_by_exchange": grouped,
            "note": "保证金率会随市场风险调整，请以交易所最新公告为准"
        }
    
    def compare_margin(self, symbols: list, price: float = None, 
                      lots: int = 1, firm_multiplier: float = 1.2) -> dict:
        """
        对比多个合约的保证金
        
        Args:
            symbols: 合约代码列表(如: ["RB2501", "HC2501"])
            price: 合约价格(如不指定，使用AkShare实时价格)
            lots: 手数
            firm_multiplier: 期货公司保证金倍数
        """
        results = []
        for symbol in symbols:
            result = self.calculate_margin(symbol, price, lots, firm_multiplier)
            if 'error' not in result:
                results.append({
                    "symbol": result['symbol'],
                    "product_name": result['product_name'],
                    "exchange": result['exchange'],
                    "price": result['price'],
                    "exchange_rate": result['exchange_rate'],
                    "total_margin": result['total_margin']
                })
        
        # 按保证金金额排序
        results.sort(key=lambda x: x['total_margin'], reverse=True)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "AkShare实时数据",
            "comparison": results,
            "summary": {
                "合约数量": len(results),
                "最高保证金": results[0]['total_margin'] if results else 0,
                "最低保证金": results[-1]['total_margin'] if results else 0
            }
        }


def main():
    parser = argparse.ArgumentParser(description="期货保证金计算器(接入AkShare实时数据)")
    parser.add_argument("--symbol", required=True, help="合约代码(如: RB2501)")
    parser.add_argument("--price", type=float, default=None, help="合约价格(如不指定，使用AkShare实时价格)")
    parser.add_argument("--lots", type=int, default=1, help="手数")
    parser.add_argument("--multiplier", type=float, default=1.2, help="期货公司保证金倍数")
    parser.add_argument("--direction", type=str, default="long", choices=["long", "short"],
                       help="交易方向(long=做多/short=做空)")
    parser.add_argument("--list", action="store_true", help="列出所有品种保证金率")
    parser.add_argument("--exchange", type=str, default=None, 
                       help="指定交易所(SHFE/DCE/CZCE/INE/CFFEX/GFEX)")
    parser.add_argument("--compare", type=str, default=None,
                       help="对比多个合约，逗号分隔(如: RB2501,HC2501)")
    
    args = parser.parse_args()
    calculator = FuturesMarginCalculator()
    
    if args.list:
        result = calculator.get_margin_rates(args.exchange)
    elif args.compare:
        symbols = [s.strip() for s in args.compare.split(',')]
        result = calculator.compare_margin(symbols, args.price, args.lots, args.multiplier)
    else:
        result = calculator.calculate_margin(
            args.symbol, args.price, args.lots, args.multiplier, args.direction
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
