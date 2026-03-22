#!/usr/bin/env python3
"""
用益信托网数据爬虫 - 增强版
支持获取信托产品列表、收益排行、市场统计等数据
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class YongyiProduct:
    """用益信托网产品数据"""
    product_name: str
    trust_company: str
    expected_yield: float
    duration: int
    min_investment: float
    investment_type: str
    issue_date: str
    status: str
    product_type: str = "集合信托"


class YongyiTrustCrawler:
    """用益信托网爬虫"""
    
    BASE_URL = "https://www.yanglee.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self._cache = {}
        self._cache_time = {}
        self.cache_duration = 1800  # 缓存30分钟
    
    def is_available(self) -> bool:
        """检查网站是否可访问"""
        try:
            resp = self.session.get(self.BASE_URL, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"用益信托网连接失败: {e}")
            return False
    
    def _get_cache(self, key: str):
        """获取缓存"""
        if key in self._cache:
            cache_time = self._cache_time.get(key, 0)
            if time.time() - cache_time < self.cache_duration:
                return self._cache[key]
        return None
    
    def _set_cache(self, key: str, data):
        """设置缓存"""
        self._cache[key] = data
        self._cache_time[key] = time.time()
    
    def get_hot_products(self, product_type='trust', period='week') -> List[Dict]:
        """
        获取热门产品排行 - 优先从产品转让区获取真实数据
        
        Args:
            product_type: 'trust'(信托), 'asset'(资管), 'private'(私募)
            period: 'week'(周排行), 'month'(月排行)
        
        Returns:
            产品列表
        """
        cache_key = f"hot_{product_type}_{period}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        products = []
        
        try:
            url = f"{self.BASE_URL}/Product/Index.aspx"
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 方法1: 从产品转让区获取真实产品数据
            transfer_products = self._parse_transfer_products(soup)
            if transfer_products:
                products.extend(transfer_products)
            
            # 方法2: 从排行表格获取
            if not products:
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for i, row in enumerate(rows[:10], 1):
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            name_link = cells[1].find('a')
                            product_name = name_link.get_text(strip=True) if name_link else cells[1].get_text(strip=True)
                            yield_text = cells[2].get_text(strip=True)
                            
                            try:
                                expected_yield = float(yield_text.replace('%', '').strip())
                                if expected_yield > 0:  # 过滤无效数据
                                    products.append({
                                        'rank': i,
                                        'product_name': product_name,
                                        'expected_yield': expected_yield,
                                        'source': '用益信托网'
                                    })
                            except:
                                pass
            
            self._set_cache(cache_key, products)
            return products
            
        except Exception as e:
            print(f"获取热门产品失败: {e}")
            return []
    
    def _parse_transfer_products(self, soup) -> List[Dict]:
        """解析产品转让区的真实产品数据"""
        products = []
        
        try:
            # 查找"产品转让"区域
            # 通常在一个table中，包含"名称"、"转让收益"、"状态"列
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for i, row in enumerate(rows[1:], 1):  # 跳过表头
                    cells = row.find_all('td')
                    
                    # 检查是否是产品转让表格 (有名称、收益、状态三列)
                    if len(cells) >= 3:
                        name = cells[0].get_text(strip=True)
                        yield_text = cells[1].get_text(strip=True)
                        status = cells[2].get_text(strip=True)
                        
                        # 解析收益率
                        try:
                            expected_yield = float(yield_text.replace('%', '').strip())
                            # 只保留有效的信托产品数据
                            if expected_yield > 0 and ('信托' in name or status == '待转让'):
                                # 尝试提取信托公司名称
                                trust_company = self._extract_trust_company(name)
                                
                                products.append({
                                    'rank': i,
                                    'product_name': name,
                                    'expected_yield': expected_yield,
                                    'status': status,
                                    'trust_company': trust_company,
                                    'source': '用益信托网-产品转让'
                                })
                        except:
                            pass
        
        except Exception as e:
            print(f"解析产品转让数据失败: {e}")
        
        return products
    
    def _extract_trust_company(self, product_name: str) -> str:
        """从产品名称中提取信托公司名称"""
        # 常见信托公司关键词
        keywords = [
            '华鑫信托', '平安信托', '中信信托', '华润信托', '中融信托',
            '中航信托', '五矿信托', '建信信托', '交银信托', '外贸信托',
            '江苏信托', '昆仑信托', '兴业信托', '民生信托', '渤海信托',
            '长安信托', '陕国投', '爱建信托', '中泰信托', '陆家嘴信托'
        ]
        
        for kw in keywords:
            if kw in product_name:
                return kw
        
        return '未知信托公司'
    
    def _get_products_from_api(self, product_type: str, period: str) -> List[Dict]:
        """尝试从API获取产品数据"""
        try:
            # 用益信托网可能有AJAX接口
            url = f"{self.BASE_URL}/ajax/Product/GetRankList"
            params = {
                'type': product_type,
                'period': period,
                'page': 1,
                'size': 10
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('success') and data.get('data'):
                    return data['data']
        except:
            pass
        
        return []
    
    def get_market_statistics(self) -> Optional[Dict]:
        """
        获取信托市场统计数据
        
        Returns:
            市场统计数据字典
        """
        cache_key = "market_stats"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.BASE_URL}/Studio/Research.aspx"
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取用益信托指数相关信息
            stats = {
                'source': '用益信托网',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'trust_index': None,
                'market_trend': None
            }
            
            # 查找指数相关内容
            content_div = soup.find('div', class_='content') or soup
            text = content_div.get_text()
            
            # 用益信托指数说明
            if '用益信托指数' in text:
                stats['trust_index_description'] = '用益推出的国内第一个反映信托市场景气程度的指数'
            
            # 尝试获取更详细的数据
            # 可能需要访问其他页面
            
            self._set_cache(cache_key, stats)
            return stats
            
        except Exception as e:
            print(f"获取市场统计失败: {e}")
            return None
    
    def get_trust_company_rank(self) -> List[Dict]:
        """
        获取信托公司综合评价排名
        
        Returns:
            信托公司排名列表
        """
        cache_key = "company_rank"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.BASE_URL}/Studio/Research.aspx"
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 解析公司评价信息
            companies = []
            
            # 查找链接到信托公司排名的页面
            links = soup.find_all('a', href=True)
            for link in links:
                if '公司排名' in link.get_text() or '综合评价' in link.get_text():
                    rank_url = link['href']
                    if not rank_url.startswith('http'):
                        rank_url = self.BASE_URL + rank_url
                    
                    # 获取排名详情
                    rank_resp = self.session.get(rank_url, timeout=10)
                    rank_resp.encoding = 'utf-8'
                    rank_soup = BeautifulSoup(rank_resp.text, 'html.parser')
                    
                    # 解析排名表格
                    tables = rank_soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 4:
                                companies.append({
                                    'rank': cells[0].get_text(strip=True),
                                    'company': cells[1].get_text(strip=True),
                                    'score': cells[2].get_text(strip=True),
                                    'grade': cells[3].get_text(strip=True)
                                })
                    break
            
            self._set_cache(cache_key, companies)
            return companies
            
        except Exception as e:
            print(f"获取公司排名失败: {e}")
            return []
    
    def get_product_yield_curve(self) -> Dict[str, float]:
        """
        获取信托产品收益率曲线
        
        Returns:
            不同期限的收益率
        """
        cache_key = "yield_curve"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            # 获取热门产品计算收益率分布
            products = self.get_hot_products('trust', 'week')
            
            # 按收益率分组统计
            yield_ranges = {
                '6%以下': [],
                '6%-7%': [],
                '7%-8%': [],
                '8%-9%': [],
                '9%以上': []
            }
            
            for p in products:
                y = p.get('expected_yield', 0)
                if y < 6:
                    yield_ranges['6%以下'].append(y)
                elif y < 7:
                    yield_ranges['6%-7%'].append(y)
                elif y < 8:
                    yield_ranges['7%-8%'].append(y)
                elif y < 9:
                    yield_ranges['8%-9%'].append(y)
                else:
                    yield_ranges['9%以上'].append(y)
            
            # 计算各区间平均收益率
            curve = {}
            for k, v in yield_ranges.items():
                curve[k] = sum(v) / len(v) if v else 0
            
            self._set_cache(cache_key, curve)
            return curve
            
        except Exception as e:
            print(f"获取收益率曲线失败: {e}")
            return {}
    
    def generate_report(self) -> str:
        """生成用益信托网数据报告"""
        report = []
        report.append("=" * 60)
        report.append("📊 用益信托网数据报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 检查连接
        if not self.is_available():
            report.append("❌ 用益信托网连接失败")
            return "\n".join(report)
        
        report.append("✅ 用益信托网连接成功")
        report.append("")
        
        # 热门产品
        report.append("-" * 60)
        report.append("🔥 热门信托产品 (周排行)")
        report.append("-" * 60)
        
        products = self.get_hot_products('trust', 'week')
        if products:
            report.append(f"获取到 {len(products)} 个产品:\n")
            for p in products[:5]:
                report.append(f"  {p['rank']}. {p['product_name']}")
                report.append(f"     预期收益: {p['expected_yield']}%")
        else:
            report.append("  ⚠️ 暂未获取到产品数据")
        
        report.append("")
        
        # 市场统计
        report.append("-" * 60)
        report.append("📈 市场统计")
        report.append("-" * 60)
        
        stats = self.get_market_statistics()
        if stats:
            report.append(f"  数据来源: {stats.get('source', 'N/A')}")
            report.append(f"  更新时间: {stats.get('update_time', 'N/A')}")
            if stats.get('trust_index_description'):
                report.append(f"  用益信托指数: {stats['trust_index_description'][:50]}...")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def test_yongyi_crawler():
    """测试用益信托网爬虫"""
    print("🔧 用益信托网爬虫测试")
    print("=" * 60)
    
    crawler = YongyiTrustCrawler()
    
    # 测试连接
    print("\n1. 测试网站连接...")
    if crawler.is_available():
        print("   ✅ 用益信托网可访问")
    else:
        print("   ❌ 用益信托网连接失败")
        return
    
    # 获取热门产品
    print("\n2. 获取热门产品...")
    products = crawler.get_hot_products('trust', 'week')
    print(f"   获取到 {len(products)} 个产品")
    
    for p in products[:5]:
        print(f"   {p['rank']}. {p['product_name'][:20]}... - {p['expected_yield']}%")
    
    # 获取市场统计
    print("\n3. 获取市场统计...")
    stats = crawler.get_market_statistics()
    if stats:
        print(f"   数据源: {stats.get('source')}")
    
    # 生成完整报告
    print("\n4. 生成完整报告...")
    print(crawler.generate_report())


if __name__ == '__main__':
    test_yongyi_crawler()
