#!/usr/bin/env python3
"""
券商研报评级分析器
接入东方财富研报数据(AkShare: stock_research_report_em)
功能: 研报获取、解析、评分
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import Counter
import argparse
import warnings

warnings.filterwarnings('ignore')


@dataclass
class ResearchReport:
    """研报数据结构"""
    report_title: str
    rating: str
    institution: str
    report_date: str
    industry: str
    pdf_url: str
    eps_2025: Optional[float] = None
    pe_2025: Optional[float] = None
    eps_2026: Optional[float] = None
    pe_2026: Optional[float] = None
    eps_2027: Optional[float] = None
    pe_2027: Optional[float] = None


@dataclass
class RatingScore:
    """评级评分结构"""
    total_reports: int
    rating_distribution: Dict[str, int]
    latest_rating: str
    latest_institution: str
    latest_date: str
    buy_ratio: float
    neutral_ratio: float
    sell_ratio: float
    avg_pe_2025: Optional[float] = None
    avg_pe_2026: Optional[float] = None
    avg_eps_2025: Optional[float] = None
    avg_eps_2026: Optional[float] = None
    composite_score: float = 0.0
    recommendation: str = ""


class SecuritiesRatingAnalyzer:
    """券商研报评级分析器"""
    
    # 评级权重映射
    RATING_WEIGHTS = {
        '买入': 5,
        '增持': 4,
        '中性': 3,
        '减持': 2,
        '卖出': 1,
        '强烈推荐': 5,
        '推荐': 4,
        '谨慎推荐': 3,
        '回避': 1,
        '': 0
    }
    
    # 头部券商映射表 (股票代码 -> 名称)
    TOP_BROKERAGES = {
        '600030': '中信证券',
        '601688': '华泰证券', 
        '600837': '海通证券',
        '601211': '国泰君安',
        '600999': '招商证券',
        '000776': '广发证券',
        '601995': '中金公司',
        '601066': '中信建投',
        '600958': '东方证券',
        '601377': '兴业证券',
        '601788': '光大证券',
        '002736': '国信证券',
        '000166': '申万宏源',
        '601881': '中国银河',
        '601901': '方正证券',
        '601878': '浙商证券',
        '601555': '东吴证券',
        '601108': '财通证券',
        '600109': '国金证券',
        '600909': '华安证券',
        '002926': '华西证券',
        '601990': '南京证券',
        '601162': '天风证券',
        '600864': '哈投股份',
        '300059': '东方财富',
    }
    
    def __init__(self):
        self._akshare_available = self._check_akshare()
    
    def _check_akshare(self) -> bool:
        """检查AkShare是否可用"""
        try:
            import akshare as ak
            return True
        except ImportError:
            return False
    
    def get_stock_reports(self, symbol: str) -> List[ResearchReport]:
        """
        获取个股研报数据
        
        Args:
            symbol: 股票代码，如 '000001'
            
        Returns:
            List[ResearchReport]: 研报列表
        """
        if not self._akshare_available:
            raise RuntimeError("AkShare not installed. Please install: pip install akshare")
        
        import akshare as ak
        
        try:
            df = ak.stock_research_report_em(symbol=symbol)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch research reports for {symbol}: {e}")
        
        if df.empty:
            return []
        
        reports = []
        for _, row in df.iterrows():
            # 解析数值字段
            def parse_float(val):
                try:
                    return float(val) if val and str(val) != 'nan' else None
                except (ValueError, TypeError):
                    return None
            
            report = ResearchReport(
                report_title=str(row.get('报告名称', '')),
                rating=str(row.get('东财评级', '')).strip(),
                institution=str(row.get('机构', '')),
                report_date=str(row.get('日期', '')),
                industry=str(row.get('行业', '')),
                pdf_url=str(row.get('报告PDF链接', '')),
                eps_2025=parse_float(row.get('2025-盈利预测-收益')),
                pe_2025=parse_float(row.get('2025-盈利预测-市盈率')),
                eps_2026=parse_float(row.get('2026-盈利预测-收益')),
                pe_2026=parse_float(row.get('2026-盈利预测-市盈率')),
                eps_2027=parse_float(row.get('2027-盈利预测-收益')),
                pe_2027=parse_float(row.get('2027-盈利预测-市盈率'))
            )
            reports.append(report)
        
        return reports
    
    def analyze_ratings(self, reports: List[ResearchReport]) -> RatingScore:
        """
        分析研报评级数据
        
        Args:
            reports: 研报列表
            
        Returns:
            RatingScore: 评级分析结果
        """
        if not reports:
            return RatingScore(
                total_reports=0,
                rating_distribution={},
                latest_rating="无数据",
                latest_institution="",
                latest_date="",
                buy_ratio=0,
                neutral_ratio=0,
                sell_ratio=0,
                composite_score=0,
                recommendation="暂无研报覆盖"
            )
        
        # 评级分布统计
        rating_dist = Counter([r.rating for r in reports if r.rating])
        
        # 最新研报
        latest = reports[0]
        
        # 计算各类评级比例
        total = len(reports)
        buy_count = rating_dist.get('买入', 0) + rating_dist.get('强烈推荐', 0) + rating_dist.get('推荐', 0)
        neutral_count = rating_dist.get('中性', 0) + rating_dist.get('谨慎推荐', 0)
        sell_count = rating_dist.get('减持', 0) + rating_dist.get('卖出', 0) + rating_dist.get('回避', 0)
        
        buy_ratio = round(buy_count / total * 100, 2) if total > 0 else 0
        neutral_ratio = round(neutral_count / total * 100, 2) if total > 0 else 0
        sell_ratio = round(sell_count / total * 100, 2) if total > 0 else 0
        
        # 计算平均预测值
        pe_2025_list = [r.pe_2025 for r in reports if r.pe_2025 is not None]
        pe_2026_list = [r.pe_2026 for r in reports if r.pe_2026 is not None]
        eps_2025_list = [r.eps_2025 for r in reports if r.eps_2025 is not None]
        eps_2026_list = [r.eps_2026 for r in reports if r.eps_2026 is not None]
        
        avg_pe_2025 = round(sum(pe_2025_list) / len(pe_2025_list), 2) if pe_2025_list else None
        avg_pe_2026 = round(sum(pe_2026_list) / len(pe_2026_list), 2) if pe_2026_list else None
        avg_eps_2025 = round(sum(eps_2025_list) / len(eps_2025_list), 2) if eps_2025_list else None
        avg_eps_2026 = round(sum(eps_2026_list) / len(eps_2026_list), 2) if eps_2026_list else None
        
        # 计算综合评分 (0-100)
        composite_score = self._calculate_composite_score(
            reports, buy_ratio, neutral_ratio, sell_ratio
        )
        
        # 生成投资建议
        recommendation = self._generate_recommendation(composite_score, buy_ratio, latest.rating)
        
        return RatingScore(
            total_reports=total,
            rating_distribution=dict(rating_dist),
            latest_rating=latest.rating,
            latest_institution=latest.institution,
            latest_date=latest.report_date,
            buy_ratio=buy_ratio,
            neutral_ratio=neutral_ratio,
            sell_ratio=sell_ratio,
            avg_pe_2025=avg_pe_2025,
            avg_pe_2026=avg_pe_2026,
            avg_eps_2025=avg_eps_2025,
            avg_eps_2026=avg_eps_2026,
            composite_score=composite_score,
            recommendation=recommendation
        )
    
    def _calculate_composite_score(self, reports: List[ResearchReport], 
                                   buy_ratio: float, neutral_ratio: float, 
                                   sell_ratio: float) -> float:
        """计算综合评分"""
        if not reports:
            return 0
        
        # 基础分数（基于评级分布）
        base_score = buy_ratio * 1.0 + neutral_ratio * 0.5 + sell_ratio * 0.0
        
        # 研报覆盖度加分（研报越多，覆盖度越高，置信度越高）
        coverage_bonus = min(len(reports) * 0.5, 20)
        
        # 一致性加分（买入比例高且卖出比例低）
        consistency_bonus = 0
        if buy_ratio >= 70 and sell_ratio == 0:
            consistency_bonus = 15
        elif buy_ratio >= 50 and sell_ratio < 5:
            consistency_bonus = 10
        elif buy_ratio >= 30 and sell_ratio < 10:
            consistency_bonus = 5
        
        # 时间新鲜度加分（最近3个月有研报）
        freshness_bonus = 0
        try:
            latest_date = datetime.strptime(reports[0].report_date, '%Y-%m-%d')
            if (datetime.now() - latest_date) <= timedelta(days=30):
                freshness_bonus = 10
            elif (datetime.now() - latest_date) <= timedelta(days=90):
                freshness_bonus = 5
        except:
            pass
        
        total_score = min(base_score + coverage_bonus + consistency_bonus + freshness_bonus, 100)
        return round(total_score, 2)
    
    def _generate_recommendation(self, score: float, buy_ratio: float, latest_rating: str) -> str:
        """生成投资建议"""
        if score >= 80:
            return "强烈看好 - 机构一致看多，研报覆盖充分"
        elif score >= 60:
            return "看好 - 机构观点积极，建议关注"
        elif score >= 40:
            return "中性 - 机构观点分歧，谨慎观望"
        elif score >= 20:
            return "偏空 - 机构观点偏谨慎，注意风险"
        else:
            return "看空或覆盖不足 - 建议谨慎"
    
    def get_brokerage_research_analysis(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        获取券商研报分析
        
        Args:
            symbol: 股票代码，如不提供则分析头部券商
            
        Returns:
            Dict: 分析结果
        """
        if symbol:
            # 分析单只股票
            return self._analyze_single_stock(symbol)
        else:
            # 分析头部券商
            return self._analyze_top_brokerages()
    
    def _analyze_single_stock(self, symbol: str) -> Dict[str, Any]:
        """分析单只股票的研报数据"""
        try:
            reports = self.get_stock_reports(symbol)
            analysis = self.analyze_ratings(reports)
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "data_source": "东方财富研报数据 (AkShare)",
                "analysis": {
                    "total_reports": analysis.total_reports,
                    "rating_distribution": analysis.rating_distribution,
                    "latest_report": {
                        "rating": analysis.latest_rating,
                        "institution": analysis.latest_institution,
                        "date": analysis.latest_date
                    },
                    "ratios": {
                        "buy_ratio": f"{analysis.buy_ratio}%",
                        "neutral_ratio": f"{analysis.neutral_ratio}%",
                        "sell_ratio": f"{analysis.sell_ratio}%"
                    },
                    "predictions": {
                        "avg_eps_2025": analysis.avg_eps_2025,
                        "avg_pe_2025": analysis.avg_pe_2025,
                        "avg_eps_2026": analysis.avg_eps_2026,
                        "avg_pe_2026": analysis.avg_pe_2026
                    },
                    "composite_score": analysis.composite_score,
                    "recommendation": analysis.recommendation
                },
                "recent_reports": [
                    {
                        "title": r.report_title,
                        "rating": r.rating,
                        "institution": r.institution,
                        "date": r.report_date,
                        "pdf_url": r.pdf_url
                    } for r in reports[:10]
                ]
            }
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "error": str(e),
                "note": "请检查股票代码是否正确"
            }
    
    def _analyze_top_brokerages(self) -> Dict[str, Any]:
        """分析头部券商的研报覆盖情况"""
        results = []
        
        for code, name in self.TOP_BROKERAGES.items():
            try:
                reports = self.get_stock_reports(code)
                analysis = self.analyze_ratings(reports)
                
                results.append({
                    "code": code,
                    "name": name,
                    "total_reports": analysis.total_reports,
                    "composite_score": analysis.composite_score,
                    "latest_rating": analysis.latest_rating,
                    "latest_institution": analysis.latest_institution,
                    "latest_date": analysis.latest_date,
                    "recommendation": analysis.recommendation
                })
            except Exception as e:
                results.append({
                    "code": code,
                    "name": name,
                    "error": str(e)
                })
        
        # 按综合评分排序
        results.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "东方财富研报数据 (AkShare)",
            "top_brokerages": results,
            "summary": {
                "total_analyzed": len(self.TOP_BROKERAGES),
                "high_score_count": len([r for r in results if r.get('composite_score', 0) >= 60]),
                "avg_score": round(sum(r.get('composite_score', 0) for r in results) / len(results), 2) if results else 0
            }
        }
    
    def search_by_institution(self, institution_name: str, sample_symbols: List[str] = None) -> Dict[str, Any]:
        """
        按券商机构名称搜索研报
        
        Args:
            institution_name: 机构名称，如 '中信证券'
            sample_symbols: 样本股票代码列表
            
        Returns:
            Dict: 搜索结果
        """
        if sample_symbols is None:
            # 默认使用一些热门股票作为样本
            sample_symbols = ['000001', '600030', '601688', '600519', '300059', 
                            '000858', '002594', '300750', '601398', '601857']
        
        all_reports = []
        
        for symbol in sample_symbols:
            try:
                reports = self.get_stock_reports(symbol)
                # 筛选特定机构的研报
                filtered = [r for r in reports if institution_name in r.institution]
                all_reports.extend(filtered)
            except:
                continue
        
        if not all_reports:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "institution": institution_name,
                "found": False,
                "message": f"未找到 {institution_name} 的研报数据"
            }
        
        # 按日期排序
        all_reports.sort(key=lambda x: x.report_date, reverse=True)
        
        # 统计
        rating_dist = Counter([r.rating for r in all_reports if r.rating])
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "institution": institution_name,
            "found": True,
            "total_reports": len(all_reports),
            "rating_distribution": dict(rating_dist),
            "recent_reports": [
                {
                    "title": r.report_title,
                    "rating": r.rating,
                    "stock": r.report_title[:10] + "..." if len(r.report_title) > 10 else r.report_title,
                    "date": r.report_date,
                    "pdf_url": r.pdf_url
                } for r in all_reports[:20]
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="券商研报评级分析器 (东方财富数据源)")
    parser.add_argument("--symbol", "-s", help="股票代码，如 000001, 600030")
    parser.add_argument("--all", "-a", action="store_true", help="分析头部券商")
    parser.add_argument("--institution", "-i", help="按机构名称搜索，如 '中信证券'")
    
    args = parser.parse_args()
    analyzer = SecuritiesRatingAnalyzer()
    
    if args.institution:
        result = analyzer.search_by_institution(args.institution)
    elif args.symbol:
        result = analyzer.get_brokerage_research_analysis(symbol=args.symbol)
    else:
        result = analyzer.get_brokerage_research_analysis()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
