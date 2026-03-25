#!/usr/bin/env python3
"""期货交割分析器 - 接入AkShare实时数据源"""

import json
from datetime import datetime, timedelta
import argparse


class FuturesDeliveryAnalyzer:
    """期货交割分析器 - 接入AkShare数据源"""
    
    # 交易所代码映射
    EXCHANGE_MAP = {
        'SHFE': '上海期货交易所',
        'DCE': '大连商品交易所', 
        'CZCE': '郑州商品交易所',
        'INE': '上海国际能源交易中心',
        'CFFEX': '中国金融期货交易所',
        'GFEX': '广州期货交易所'
    }
    
    # 品种代码到交易所的映射
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
        self._warehouse_data = None
        self._contract_info = None
        self._data_timestamp = None
        self._cache_duration = 300  # 缓存5分钟
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._data_timestamp is None:
            return False
        try:
            last_update = datetime.strptime(self._data_timestamp, "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - last_update).seconds < self._cache_duration
        except:
            return False
    
    def _get_product_code(self, symbol: str) -> str:
        """从合约代码提取品种代码"""
        product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
        return product_code
    
    def _get_exchange(self, symbol: str) -> str:
        """获取品种所属交易所"""
        product_code = self._get_product_code(symbol)
        return self.SYMBOL_EXCHANGE_MAP.get(product_code, 'SHFE')
    
    def _load_delivery_data(self, date: str = None) -> dict:
        """
        从AkShare加载交割数据 - 接入futures_delivery_shfe/czce/dce接口
        
        Args:
            date: 年月格式(YYYYMM)，默认当前月份
        """
        try:
            import akshare as ak
            
            if date is None:
                date = datetime.now().strftime("%Y%m")
            
            all_delivery_data = {}
            
            # 上期所交割数据
            try:
                shfe_data = ak.futures_delivery_shfe(date=date)
                if shfe_data is not None and not shfe_data.empty:
                    for _, row in shfe_data.iterrows():
                        variety = str(row.get('品种', '')).strip()
                        if variety:
                            all_delivery_data[variety] = {
                                'exchange': 'SHFE',
                                'exchange_name': '上海期货交易所',
                                'date': date,
                                'delivery_volume': row.get('交割量', 0),
                                'delivery_amount': row.get('交割金额', 0),
                                'delivery_units': row.get('交割手数', 0),
                                'data_source': 'futures_delivery_shfe'
                            }
            except Exception as e:
                pass  # 单个交易所失败不影响其他
            
            # 郑商所交割数据
            try:
                czce_data = ak.futures_delivery_czce(date=date)
                if czce_data is not None and not czce_data.empty:
                    for _, row in czce_data.iterrows():
                        variety = str(row.get('品种', '')).strip()
                        if variety:
                            all_delivery_data[variety] = {
                                'exchange': 'CZCE',
                                'exchange_name': '郑州商品交易所',
                                'date': date,
                                'delivery_volume': row.get('交割量', row.get('交割数量', 0)),
                                'delivery_amount': row.get('交割金额', 0),
                                'delivery_units': row.get('交割手数', row.get('配对数', 0)),
                                'data_source': 'futures_delivery_czce'
                            }
            except Exception as e:
                pass
            
            # 大商所交割数据
            try:
                dce_data = ak.futures_delivery_dce(date=date)
                if dce_data is not None and not dce_data.empty:
                    for _, row in dce_data.iterrows():
                        variety = str(row.get('品种', '')).strip()
                        if variety:
                            all_delivery_data[variety] = {
                                'exchange': 'DCE',
                                'exchange_name': '大连商品交易所',
                                'date': date,
                                'delivery_volume': row.get('交割量', row.get('交割数量', 0)),
                                'delivery_amount': row.get('交割金额', 0),
                                'delivery_units': row.get('交割手数', row.get('配对数', 0)),
                                'data_source': 'futures_delivery_dce'
                            }
            except Exception as e:
                pass
            
            self._data_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return all_delivery_data
            
        except ImportError:
            return {"error": "AkShare未安装，请运行: pip install akshare"}
        except Exception as e:
            return {"error": f"获取交割数据失败: {str(e)}"}
    
    def _load_contract_info(self, symbol: str) -> dict:
        """从AkShare加载合约详细信息"""
        try:
            import akshare as ak
            
            # 获取合约详情
            detail_df = ak.futures_contract_detail(symbol=symbol)
            if detail_df is not None and not detail_df.empty:
                # 转换为字典
                detail_dict = dict(zip(detail_df['item'], detail_df['value']))
                return {
                    'product_name': detail_dict.get('交易品种', ''),
                    'delivery_method': detail_dict.get('交割方式', ''),
                    'contract_unit': detail_dict.get('交易单位', ''),
                    'delivery_months': detail_dict.get('合约交割月份', ''),
                    'last_trading_day': detail_dict.get('最后交易日', ''),
                    'last_delivery_day': detail_dict.get('最后交割日', ''),
                    'delivery_grade': detail_dict.get('交割品级', ''),
                    'min_margin': detail_dict.get('最低交易保证金', ''),
                    'price_limit': detail_dict.get('涨跌停板幅度', ''),
                    'exchange': detail_dict.get('上市交易所', '')
                }
        except Exception as e:
            pass
        
        return {}
    
    def analyze_delivery(self, symbol: str, include_warehouse: bool = True, include_delivery: bool = True) -> dict:
        """
        分析合约交割信息
        
        Args:
            symbol: 合约代码(如: RB2501)
            include_warehouse: 是否包含仓单数据
            include_delivery: 是否包含交割统计数据
        """
        # 解析合约月份
        month_str = ''.join([c for c in symbol if c.isdigit()])
        
        if not month_str:
            return {"error": "无法识别合约月份"}
        
        # 解析交割年月
        if len(month_str) == 4:
            year = int("20" + month_str[:2])
            month = int(month_str[2:4])
        elif len(month_str) == 2:
            year = datetime.now().year
            current_year_short = year % 100
            month = int(month_str)
            month_short = month  # 用于比较
            # 如果合约月份小于当前月份，可能是下一年
            if month < datetime.now().month and month_short < current_year_short:
                year += 1
        else:
            year = datetime.now().year
            month = datetime.now().month
        
        product_code = self._get_product_code(symbol)
        exchange_code = self._get_exchange(symbol)
        
        # 获取合约详细信息
        contract_detail = self._load_contract_info(symbol)
        
        # 计算交割相关时间
        try:
            delivery_date = datetime(year, month, 15)  # 大多数品种交割月15日
            # 如果是周末，顺延到周一
            while delivery_date.weekday() >= 5:
                delivery_date += timedelta(days=1)
            
            days_to_delivery = (delivery_date - datetime.now()).days
        except:
            delivery_date = None
            days_to_delivery = None
        
        # 获取仓单数据
        warehouse_info = None
        if include_warehouse:
            warehouse_info = self._get_warehouse_data(product_code)
        
        # 获取交割统计数据
        delivery_info = None
        if include_delivery:
            delivery_info = self._get_delivery_data(product_code)
        
        # 交割风险分析
        risk_analysis = self._analyze_delivery_risk(days_to_delivery, warehouse_info, delivery_info)
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "AkShare实时数据 (交割: futures_delivery_*) + 交易所交割规则",
            "symbol": symbol,
            "product_code": product_code,
            "product_name": contract_detail.get('product_name', product_code),
            "exchange": self.EXCHANGE_MAP.get(exchange_code, exchange_code),
            "delivery_info": {
                "delivery_year": year,
                "delivery_month": month,
                "estimated_delivery_date": delivery_date.strftime("%Y-%m-%d") if delivery_date else None,
                "days_to_delivery": days_to_delivery,
                "last_trading_day": contract_detail.get('last_trading_day', ''),
                "last_delivery_day": contract_detail.get('last_delivery_day', ''),
                "delivery_method": contract_detail.get('delivery_method', ''),
                "delivery_grade": contract_detail.get('delivery_grade', '')[:100] + '...' if contract_detail.get('delivery_grade') and len(contract_detail.get('delivery_grade')) > 100 else contract_detail.get('delivery_grade', '')
            },
            "contract_specs": {
                "contract_unit": contract_detail.get('contract_unit', ''),
                "delivery_months": contract_detail.get('delivery_months', ''),
                "min_margin": contract_detail.get('min_margin', ''),
                "price_limit": contract_detail.get('price_limit', '')
            }
        }
        
        if warehouse_info:
            result["warehouse_receipt"] = warehouse_info
        
        if delivery_info:
            result["delivery_stats"] = delivery_info
        
        result["risk_analysis"] = risk_analysis
        
        return result
    
    def _get_warehouse_data(self, product_code: str) -> dict:
        """获取仓单数据"""
        try:
            import akshare as ak
            
            today = datetime.now()
            if today.weekday() >= 5:
                today = today - timedelta(days=today.weekday() - 4)
            date = today.strftime("%Y%m%d")
            
            # 上期所仓单
            try:
                shfe_data = ak.futures_shfe_warehouse_receipt(date=date)
                if shfe_data and isinstance(shfe_data, dict):
                    for variety, df in shfe_data.items():
                        if product_code in variety or variety in product_code:
                            if df is not None and not df.empty:
                                total_wrtwgts = df['WRTWGHTS'].sum() if 'WRTWGHTS' in df.columns else 0
                                total_change = df['WRTCHANGE'].sum() if 'WRTCHANGE' in df.columns else 0
                                return {
                                    'exchange': 'SHFE',
                                    'date': date,
                                    'total_quantity': int(total_wrtwgts),
                                    'daily_change': int(total_change),
                                    'warehouse_count': len(df),
                                    'data_source': 'futures_shfe_warehouse_receipt'
                                }
            except:
                pass
            
            # 郑商所仓单
            try:
                czce_data = ak.futures_warehouse_receipt_czce(date=date)
                if czce_data and isinstance(czce_data, dict):
                    for variety, df in czce_data.items():
                        if product_code in variety or variety in product_code:
                            if df is not None and not df.empty:
                                total_qty = df['仓单数量'].sum() if '仓单数量' in df.columns else 0
                                total_change = df['当日增减'].sum() if '当日增减' in df.columns else 0
                                return {
                                    'exchange': 'CZCE',
                                    'date': date,
                                    'total_quantity': int(total_qty),
                                    'daily_change': int(total_change),
                                    'warehouse_count': len(df),
                                    'data_source': 'futures_warehouse_receipt_czce'
                                }
            except:
                pass
        except:
            pass
        
        return None
    
    def _get_delivery_data(self, product_code: str) -> dict:
        """获取交割统计数据"""
        date = datetime.now().strftime("%Y%m")
        delivery_data = self._load_delivery_data(date)
        
        if isinstance(delivery_data, dict) and 'error' in delivery_data:
            return None
        
        # 尝试匹配品种
        for variety, data in delivery_data.items():
            if product_code in variety or variety in product_code:
                return data
        
        return None
    
    def _analyze_delivery_risk(self, days_to_delivery: int, warehouse_info: dict = None, delivery_info: dict = None) -> dict:
        """分析交割风险"""
        risk_level = "normal"
        warnings = []
        suggestions = []
        
        if days_to_delivery is not None:
            if days_to_delivery < 0:
                risk_level = "expired"
                warnings.append("合约已过期")
            elif days_to_delivery <= 5:
                risk_level = "critical"
                warnings.append("即将进入交割月，流动性风险极高")
                warnings.append("个人投资者需在交割月前平仓")
                suggestions.append("建议立即平仓或移仓至远月合约")
            elif days_to_delivery <= 15:
                risk_level = "high"
                warnings.append("临近交割月，流动性开始下降")
                suggestions.append("关注基差变化，考虑移仓")
            elif days_to_delivery <= 30:
                risk_level = "medium"
                warnings.append("接近交割月")
                suggestions.append("密切关注仓单变化和基差走势")
        
        # 仓单分析
        if warehouse_info:
            total_qty = warehouse_info.get('total_quantity', 0)
            daily_change = warehouse_info.get('daily_change', 0)
            
            if total_qty < 100:
                warnings.append("仓单量极低，注意逼仓风险")
                risk_level = "high" if risk_level not in ["critical", "expired"] else risk_level
            elif total_qty < 500:
                warnings.append("仓单量偏低")
            
            if daily_change > 1000:
                warnings.append(f"仓单大增{daily_change}，供应压力增加")
            elif daily_change < -1000:
                warnings.append(f"仓单大减{abs(daily_change)}，注意供应紧张")
        
        # 交割数据分析
        if delivery_info:
            delivery_volume = delivery_info.get('delivery_volume', 0)
            if delivery_volume and delivery_volume > 10000:
                suggestions.append("近期交割量较大，注意期现回归压力")
        
        return {
            "risk_level": risk_level,
            "risk_level_desc": {
                "normal": "正常",
                "medium": "中等风险",
                "high": "高风险",
                "critical": "极高风险",
                "expired": "已过期"
            }.get(risk_level, "未知"),
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def get_delivery_stats(self, symbol: str = None, date: str = None) -> dict:
        """
        获取交割统计数据
        
        Args:
            symbol: 品种代码(如: RB)，为空返回所有
            date: 年月(YYYYMM)，默认当前月份
        """
        delivery_data = self._load_delivery_data(date)
        
        if isinstance(delivery_data, dict) and 'error' in delivery_data:
            return delivery_data
        
        if symbol:
            product_code = self._get_product_code(symbol)
            # 过滤指定品种
            filtered = {}
            for variety, data in delivery_data.items():
                if product_code in variety or variety in product_code:
                    filtered[variety] = data
            delivery_data = filtered
        
        # 计算汇总
        total_varieties = len(delivery_data)
        total_volume = sum(d['delivery_volume'] for d in delivery_data.values() if isinstance(d.get('delivery_volume'), (int, float)))
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "AkShare - futures_delivery_shfe/czce/dce",
            "date": date or datetime.now().strftime("%Y%m"),
            "total_varieties": total_varieties,
            "total_delivery_volume": int(total_volume),
            "delivery_data": delivery_data
        }
    
    def compare_delivery(self, symbols: list) -> dict:
        """
        对比多个合约的交割信息
        
        Args:
            symbols: 合约代码列表
        """
        results = []
        for symbol in symbols:
            info = self.analyze_delivery(symbol, include_warehouse=False)
            if 'error' not in info:
                results.append({
                    "symbol": symbol,
                    "product_name": info.get('product_name', ''),
                    "exchange": info.get('exchange', ''),
                    "days_to_delivery": info['delivery_info'].get('days_to_delivery'),
                    "risk_level": info['risk_analysis'].get('risk_level')
                })
        
        # 按交割时间排序
        results.sort(key=lambda x: x['days_to_delivery'] if x['days_to_delivery'] is not None else 9999)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": results,
            "summary": {
                "即将交割(≤5天)": len([r for r in results if r['days_to_delivery'] is not None and r['days_to_delivery'] <= 5]),
                "临近交割(≤15天)": len([r for r in results if r['days_to_delivery'] is not None and 5 < r['days_to_delivery'] <= 15]),
                "正常": len([r for r in results if r['days_to_delivery'] is None or r['days_to_delivery'] > 15])
            }
        }


def main():
    parser = argparse.ArgumentParser(description="期货交割分析器(接入AkShare实时数据)")
    parser.add_argument("--symbol", required=True, help="合约代码(如: RB2505)")
    parser.add_argument("--no-warehouse", action="store_true", help="不包含仓单数据")
    parser.add_argument("--no-delivery", action="store_true", help="不包含交割统计数据")
    parser.add_argument("--delivery-only", action="store_true", help="仅获取交割统计数据")
    parser.add_argument("--date", type=str, default=None, help="指定年月(YYYYMM)")
    parser.add_argument("--compare", type=str, default=None, help="对比多个合约，逗号分隔")
    
    args = parser.parse_args()
    analyzer = FuturesDeliveryAnalyzer()
    
    if args.delivery_only:
        result = analyzer.get_delivery_stats(args.symbol, args.date)
    elif args.compare:
        symbols = [s.strip() for s in args.compare.split(',')]
        result = analyzer.compare_delivery(symbols)
    else:
        result = analyzer.analyze_delivery(
            args.symbol, 
            not args.no_warehouse,
            not args.no_delivery
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
