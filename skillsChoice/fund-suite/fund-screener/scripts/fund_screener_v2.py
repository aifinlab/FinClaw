#!/usr/bin/env python3
"""
基金筛选器核心模块（真实数据版）
Fund Screener Core Module - Real Data Edition

功能：基金筛选、评级、对比
数据源：AkShare / 同花顺iFinD
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-screener/scripts')
# 添加数据适配器路径
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics

# 尝试导入pandas

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("警告：pandas未安装，使用基础数据结构")

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False
    print(f"警告：数据适配器未加载: {e}")


@dataclass
class FundInfo:
    """基金信息数据类"""
    fund_code: str
    fund_name: str
    fund_type: str
    nav: float = 0.0
    nav_date: str = ""
    return_1y: float = 0.0
    return_3y: float = 0.0
    return_5y: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    scale: float = 0.0  # 规模（亿元）
    manager: str = ""
    manager_exp: int = 0  # 从业年限
    expense_ratio: float = 0.0
    establish_date: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundRating:
    """基金评级"""
    fund_code: str
    overall: int = 0  # 1-5星
    return_rating: int = 0
    risk_rating: int = 0
    scale_rating: int = 0
    manager_rating: int = 0
    fee_rating: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FundScreener:
    """基金筛选器主类"""
    
    def __init__(self, use_real_data: bool = True):
        self.fund_data = []
        self.ratings_cache = {}
        self.data_adapter = None
        self.data_source = "模拟数据"
        
        if use_real_data and DATA_ADAPTER_AVAILABLE:
            self._init_data_adapter()
        
        self._load_data()
    
    def _init_data_adapter(self):
        """初始化数据适配器"""
        try:
            self.data_adapter = get_fund_adapter(prefer_ths=False)
            self.data_source = self.data_adapter.get_data_source()
            print(f"✅ 数据源: {self.data_source}")
        except Exception as e:
            print(f"⚠️ 数据适配器初始化失败: {e}")
            self.data_adapter = None
    
    def _load_data(self):
        """加载基金数据（优先真实数据）"""
        if self.data_adapter:
            try:
                self._load_real_data()
                if self.fund_data:
                    print(f"✅ 已加载 {len(self.fund_data)} 只基金的真实数据")
                    return
            except Exception as e:
                print(f"⚠️ 真实数据加载失败: {e}，使用模拟数据")
        
        self._load_sample_data()
        print(f"⚠️ 已加载 {len(self.fund_data)} 只模拟基金数据")
    
    def _load_real_data(self):
        """从真实数据源加载基金数据"""
        # 获取热门基金列表（示例：从排行中获取）
        try:
            import akshare as ak
            df = ak.fund_open_fund_rank_em()
            
            if df.empty:
                return
            
            # 取前50只基金
            df = df.head(50)
            
            for _, row in df.iterrows():
                fund_code = str(row.get('基金代码', ''))
                if not fund_code:
                    continue
                
                # 解析收益率
                def parse_return(val):
                    if pd.isna(val):
                        return 0.0
                    if isinstance(val, str):
                        return float(val.replace('%', ''))
                    return float(val)
                
                fund = FundInfo(
                    fund_code=fund_code,
                    fund_name=str(row.get('基金简称', '')),
                    fund_type=self._detect_fund_type(str(row.get('基金简称', ''))),
                    return_1y=parse_return(row.get('近1年')),
                    return_3y=parse_return(row.get('近3年')),
                    return_5y=0.0,  # 排行数据可能不包含5年
                    nav=0.0,  # 需要单独获取
                    nav_date=datetime.now().strftime('%Y-%m-%d'),
                    volatility=0.0,
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    scale=0.0,
                    manager='',
                    manager_exp=0,
                    expense_ratio=0.0,
                    establish_date=''
                )
                
                self.fund_data.append(fund)
                
        except Exception as e:
            print(f"加载真实数据失败: {e}")
            raise
    
    def _load_sample_data(self):
        """加载示例基金数据（备用）"""
        self.data_source = "模拟数据"
        self.fund_data = [
            FundInfo("000001", "华夏成长混合", "混合型", 1.5234, "2026-03-20", 
                    25.3, 45.2, 68.5, 18.5, 1.45, -15.2, 156.8, "张三", 8, 1.2),
            FundInfo("000002", "易方达蓝筹精选", "混合型", 2.1234, "2026-03-20",
                    22.1, 55.2, 72.3, 16.2, 1.42, -12.8, 234.5, "李四", 12, 1.5),
            FundInfo("000003", "中欧时代先锋", "股票型", 1.8234, "2026-03-20",
                    21.7, 48.9, 58.2, 20.1, 1.15, -18.5, 89.3, "王五", 6, 1.2),
            FundInfo("000004", "富国天惠成长", "混合型", 3.2345, "2026-03-20",
                    28.5, 52.3, 75.1, 17.8, 1.52, -14.2, 189.5, "赵六", 10, 1.0),
            FundInfo("000005", "景顺长城新兴", "股票型", 2.5678, "2026-03-20",
                    19.8, 38.5, 52.3, 22.5, 0.95, -21.5, 67.8, "孙七", 5, 1.5),
            FundInfo("000006", "嘉实沪深300", "指数型", 1.3456, "2026-03-20",
                    15.2, 35.8, 48.2, 18.5, 0.85, -16.8, 456.2, "周八", 15, 0.8),
            FundInfo("000007", "招商中证白酒", "指数型", 2.7890, "2026-03-20",
                    32.5, 68.9, 85.2, 25.3, 1.35, -22.5, 523.8, "吴九", 7, 1.0),
            FundInfo("000008", "南方稳健成长", "混合型", 1.6789, "2026-03-20",
                    12.8, 28.5, 42.3, 12.5, 1.08, -10.2, 123.4, "郑十", 9, 1.2),
            FundInfo("000009", "广发科技创新", "股票型", 1.8901, "2026-03-20",
                    35.2, 42.8, 38.5, 28.5, 1.28, -25.8, 45.6, "钱十一", 4, 1.5),
            FundInfo("000010", "工银瑞信战略", "混合型", 2.0123, "2026-03-20",
                    17.5, 32.6, 48.9, 15.8, 1.18, -13.5, 78.9, "孙十二", 6, 1.2),
        ]
    
    def _detect_fund_type(self, fund_name: str) -> str:
        """根据基金名称识别类型"""
        name = fund_name.upper()
        if '货币' in name:
            return '货币型'
        elif '债券' in name or '纯债' in name:
            return '债券型'
        elif '指数' in name or 'ETF' in name or '沪深300' in name or '中证' in name:
            return '指数型'
        elif '混合' in name:
            return '混合型'
        elif '股票' in name:
            return '股票型'
        elif 'FOF' in name:
            return 'FOF'
        elif 'QDII' in name:
            return 'QDII'
        return '混合型'
    
    def screen(self, 
               fund_type: Optional[str] = None,
               min_return_1y: Optional[float] = None,
               max_return_1y: Optional[float] = None,
               min_return_3y: Optional[float] = None,
               max_volatility: Optional[float] = None,
               min_scale: Optional[float] = None,
               max_scale: Optional[float] = None,
               max_fee: Optional[float] = None,
               min_sharpe: Optional[float] = None,
               manager_exp: Optional[int] = None,
               rating_min: Optional[int] = None,
               limit: int = 20) -> List[Dict]:
        """
        筛选基金
        
        Args:
            fund_type: 基金类型（股票型/混合型/债券型/指数型）
            min_return_1y: 近1年最小收益(%)
            max_return_1y: 近1年最大收益(%)
            min_return_3y: 近3年最小收益(%)
            max_volatility: 最大波动率(%)
            min_scale: 最小规模(亿元)
            max_scale: 最大规模(亿元)
            max_fee: 最大管理费率(%)
            min_sharpe: 最小夏普比率
            manager_exp: 基金经理最小从业年限
            rating_min: 最低星级(1-5)
            limit: 返回数量限制
        
        Returns:
            符合条件的基金列表
        """
        results = []
        
        for fund in self.fund_data:
            # 应用筛选条件
            if fund_type and fund.fund_type != fund_type:
                continue
            if min_return_1y is not None and fund.return_1y < min_return_1y:
                continue
            if max_return_1y is not None and fund.return_1y > max_return_1y:
                continue
            if min_return_3y is not None and fund.return_3y < min_return_3y:
                continue
            if max_volatility is not None and fund.volatility > max_volatility:
                continue
            if min_scale is not None and fund.scale < min_scale:
                continue
            if max_scale is not None and fund.scale > max_scale:
                continue
            if max_fee is not None and fund.expense_ratio > max_fee:
                continue
            if min_sharpe is not None and fund.sharpe_ratio < min_sharpe:
                continue
            if manager_exp is not None and fund.manager_exp < manager_exp:
                continue
            
            # 计算评级
            rating = self._calculate_rating(fund)
            
            if rating_min is not None and rating.overall < rating_min:
                continue
            
            # 添加到结果
            fund_dict = fund.to_dict()
            fund_dict['rating'] = rating.to_dict()
            fund_dict['peer_rank'] = self._get_peer_rank(fund)
            fund_dict['data_source'] = self.data_source
            results.append(fund_dict)
        
        # 排序：综合评分降序
        results.sort(key=lambda x: x['rating']['overall'], reverse=True)
        
        # 添加排名
        for i, fund in enumerate(results[:limit], 1):
            fund['rank'] = i
        
        return results[:limit]
    
    def _calculate_rating(self, fund: FundInfo) -> FundRating:
        """计算基金评级"""
        rating = FundRating(fund_code=fund.fund_code)
        
        # 收益评级（近1年收益排名）
        all_returns = [f.return_1y for f in self.fund_data]
        return_pct = self._get_percentile(fund.return_1y, all_returns)
        rating.return_rating = self._pct_to_star(return_pct)
        
        # 风险评级（波动率越低越好）
        all_vols = [f.volatility for f in self.fund_data if f.volatility > 0]
        if all_vols:
            vol_pct = 100 - self._get_percentile(fund.volatility, all_vols)
            rating.risk_rating = self._pct_to_star(vol_pct)
        else:
            rating.risk_rating = 3
        
        # 规模评级
        if fund.scale >= 100:
            rating.scale_rating = 5
        elif fund.scale >= 50:
            rating.scale_rating = 4
        elif fund.scale >= 20:
            rating.scale_rating = 3
        elif fund.scale >= 10:
            rating.scale_rating = 2
        else:
            rating.scale_rating = 1
        
        # 基金经理评级
        if fund.manager_exp >= 10:
            rating.manager_rating = 5
        elif fund.manager_exp >= 7:
            rating.manager_rating = 4
        elif fund.manager_exp >= 5:
            rating.manager_rating = 3
        elif fund.manager_exp >= 3:
            rating.manager_rating = 2
        else:
            rating.manager_rating = 1
        
        # 费率评级（越低越好）
        if fund.expense_ratio <= 0.5:
            rating.fee_rating = 5
        elif fund.expense_ratio <= 0.8:
            rating.fee_rating = 4
        elif fund.expense_ratio <= 1.2:
            rating.fee_rating = 3
        elif fund.expense_ratio <= 1.5:
            rating.fee_rating = 2
        else:
            rating.fee_rating = 1
        
        # 综合评级（加权平均）
        weights = {'return': 0.30, 'risk': 0.25, 'scale': 0.15, 
                   'manager': 0.20, 'fee': 0.10}
        overall = (rating.return_rating * weights['return'] +
                   rating.risk_rating * weights['risk'] +
                   rating.scale_rating * weights['scale'] +
                   rating.manager_rating * weights['manager'] +
                   rating.fee_rating * weights['fee'])
        rating.overall = round(overall)
        
        return rating
    
    def _get_percentile(self, value: float, all_values: List[float]) -> float:
        """获取百分位排名（0-100）"""
        if not all_values:
            return 50.0
        sorted_values = sorted(all_values)
        n = len(sorted_values)
        
        # 找到位置
        for i, v in enumerate(sorted_values):
            if value <= v:
                return (i / n) * 100
        return 100.0
    
    def _pct_to_star(self, pct: float) -> int:
        """百分位转换为星级"""
        if pct >= 80:
            return 5
        elif pct >= 60:
            return 4
        elif pct >= 40:
            return 3
        elif pct >= 20:
            return 2
        else:
            return 1
    
    def _get_peer_rank(self, fund: FundInfo) -> Dict:
        """获取同类排名"""
        peers = [f for f in self.fund_data if f.fund_type == fund.fund_type]
        if not peers:
            return {'rank': 1, 'total': 1, 'percentile': 100}
        
        sorted_peers = sorted(peers, key=lambda x: x.return_1y, reverse=True)
        rank = next((i for i, p in enumerate(sorted_peers, 1) if p.fund_code == fund.fund_code), len(peers))
        
        return {
            'rank': rank,
            'total': len(peers),
            'percentile': round((1 - rank / len(peers)) * 100, 1)
        }
    
    def compare(self, fund_codes: List[str]) -> Dict:
        """
        对比多只基金
        
        Args:
            fund_codes: 基金代码列表
        
        Returns:
            对比结果
        """
        funds = [f for f in self.fund_data if f.fund_code in fund_codes]
        
        if not funds:
            return {'error': '未找到指定的基金'}
        
        comparison = {
            'funds': [],
            'summary': {},
            'data_source': self.data_source
        }
        
        for fund in funds:
            rating = self._calculate_rating(fund)
            fund_dict = fund.to_dict()
            fund_dict['rating'] = rating.to_dict()
            comparison['funds'].append(fund_dict)
        
        # 生成对比摘要
        if len(funds) >= 2:
            comparison['summary'] = {
                'best_return_1y': max(funds, key=lambda x: x.return_1y).fund_name,
                'lowest_volatility': min(funds, key=lambda x: x.volatility).fund_name,
                'largest_scale': max(funds, key=lambda x: x.scale).fund_name,
                'lowest_fee': min(funds, key=lambda x: x.expense_ratio).fund_name,
                'highest_rating': max(funds, key=lambda x: self._calculate_rating(x).overall).fund_name
            }
        
        return comparison


def main():
    parser = argparse.ArgumentParser(description='基金筛选器')
    parser.add_argument('--action', choices=['screen', 'compare'], default='screen',
                       help='操作类型')
    parser.add_argument('--fund-type', help='基金类型')
    parser.add_argument('--min-return-1y', type=float, help='近1年最小收益')
    parser.add_argument('--max-return-1y', type=float, help='近1年最大收益')
    parser.add_argument('--min-return-3y', type=float, help='近3年最小收益')
    parser.add_argument('--max-volatility', type=float, help='最大波动率')
    parser.add_argument('--min-scale', type=float, help='最小规模')
    parser.add_argument('--max-scale', type=float, help='最大规模')
    parser.add_argument('--max-fee', type=float, help='最大费率')
    parser.add_argument('--min-sharpe', type=float, help='最小夏普比率')
    parser.add_argument('--rating-min', type=int, help='最低评级(1-5)')
    parser.add_argument('--limit', type=int, default=10, help='返回数量限制')
    parser.add_argument('--codes', help='对比用基金代码（逗号分隔）')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    screener = FundScreener(use_real_data=use_real)
    
    if args.action == 'screen':
        results = screener.screen(
            fund_type=args.fund_type,
            min_return_1y=args.min_return_1y,
            max_return_1y=args.max_return_1y,
            min_return_3y=args.min_return_3y,
            max_volatility=args.max_volatility,
            min_scale=args.min_scale,
            max_scale=args.max_scale,
            max_fee=args.max_fee,
            min_sharpe=args.min_sharpe,
            rating_min=args.rating_min,
            limit=args.limit
        )
        
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == 'compare':
        if not args.codes:
            print('错误：对比模式需要指定--codes参数')
            return
        
        codes = args.codes.split(',')
        results = screener.compare(codes)
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
