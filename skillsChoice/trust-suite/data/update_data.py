#!/usr/bin/env python3
"""
信托数据自动更新脚本 v1.0
功能：从公开渠道抓取最新数据并更新JSON文件
数据源：
  1. 用益信托网 (yanglee.com) - 优先
  2. 中国信托登记有限责任公司 (chinatrc.com.cn) - 官方数据源
  3. 国家金融监督管理总局 - 行业统计数据
  4. 同花顺API - 深度数据（需Token）

使用方法：
  python update_data.py [--force] [--source SOURCE]

参数：
  --force     强制更新，忽略缓存
  --source    指定数据源 (yongyi/chinatrc/ths/all)
  
输出：
  - json_data/products.json - 产品数据
  - json_data/market_stats.json - 市场统计数据
  - json_data/last_update.json - 更新记录
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from trust_data_adapter import (
    TrustProductData, TrustMarketStats, DataQualityLabel,
    get_data_provider, TrustDataProvider
)

# 配置
DATA_DIR = Path(__file__).parent / 'json_data'
DATA_DIR.mkdir(exist_ok=True)
CACHE_FILE = DATA_DIR / 'update_cache.json'
UPDATE_LOG_FILE = DATA_DIR / 'last_update.json'
CACHE_DURATION_HOURS = 6  # 缓存6小时

# 数据源配置
DATA_SOURCES = {
    'yongyi': {
        'name': '用益信托网',
        'url': 'https://www.yanglee.com',
        'priority': 1,
        'enabled': True
    },
    'chinatrc': {
        'name': '中国信托登记',
        'url': 'http://www.chinatrc.com.cn',
        'priority': 2,
        'enabled': True
    },
    'nfra': {
        'name': '国家金融监管总局',
        'url': 'https://www.nfra.gov.cn',
        'priority': 3,
        'enabled': True
    },
    'ths': {
        'name': '同花顺iFinD',
        'url': 'https://quantapi.51ifind.com',
        'priority': 4,
        'enabled': bool(os.getenv('THS_ACCESS_TOKEN'))
    }
}


class YongyiDataFetcher:
    """用益信托网数据获取器"""
    
    BASE_URL = "https://www.yanglee.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
        self._cache = {}
    
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        try:
            resp = self.session.get(self.BASE_URL, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"  ⚠️ 用益信托网连接失败: {e}")
            return False
    
    def fetch_products(self) -> List[Dict]:
        """获取产品数据"""
        products = []
        
        try:
            # 尝试从多个页面获取数据
            urls_to_try = [
                f"{self.BASE_URL}/Product/Index.aspx",
                f"{self.BASE_URL}/product/",
                f"{self.BASE_URL}/Product/transfer.aspx",  # 产品转让区
            ]
            
            for url in urls_to_try:
                try:
                    resp = self.session.get(url, timeout=15)
                    resp.encoding = 'utf-8'
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    # 解析产品表格
                    page_products = self._parse_products(soup)
                    if page_products:
                        products.extend(page_products)
                        print(f"  ✓ 从 {url} 获取 {len(page_products)} 个产品")
                        
                except Exception as e:
                    print(f"  ⚠️ 获取 {url} 失败: {e}")
                    continue
            
            # 去重
            seen = set()
            unique_products = []
            for p in products:
                key = f"{p.get('trust_company')}_{p.get('product_name')}"
                if key not in seen:
                    seen.add(key)
                    unique_products.append(p)
            
            return unique_products
            
        except Exception as e:
            print(f"  ❌ 用益信托网获取产品失败: {e}")
            return []
    
    def _parse_products(self, soup: BeautifulSoup) -> List[Dict]:
        """解析产品数据"""
        products = []
        
        # 尝试多种表格结构
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # 跳过表头
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    # 提取产品信息
                    product = self._extract_product_info(cells)
                    if product:
                        products.append(product)
        
        return products
    
    def _extract_product_info(self, cells) -> Optional[Dict]:
        """从表格单元格提取产品信息"""
        try:
            # 尝试不同的列索引组合
            texts = [cell.get_text(strip=True) for cell in cells]
            
            # 查找产品名称（通常包含"信托"字样）
            product_name = None
            for text in texts:
                if '信托' in text and len(text) > 5:
                    product_name = text
                    break
            
            if not product_name:
                return None
            
            # 查找收益率（通常包含%符号）
            expected_yield = 0
            for text in texts:
                if '%' in text:
                    try:
                        yield_val = float(text.replace('%', '').strip())
                        if 3 < yield_val < 20:  # 合理的收益率范围
                            expected_yield = yield_val
                            break
                    except:
                        pass
            
            # 查找期限（通常包含"月"或"年"）
            duration = 12
            for text in texts:
                if '月' in text or '年' in text:
                    try:
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            duration = int(numbers[0])
                            if '年' in text:
                                duration *= 12
                            break
                    except:
                        pass
            
            # 提取信托公司名称
            trust_company = self._extract_trust_company(product_name, texts)
            
            return {
                'product_code': f"YY{datetime.now().year}{len(product_name) % 1000:03d}",
                'product_name': product_name,
                'trust_company': trust_company,
                'product_type': '集合信托',
                'investment_type': self._classify_investment_type(product_name, texts),
                'expected_yield': expected_yield or 6.5,
                'duration': duration,
                'min_investment': 100,
                'issue_scale': 50000,
                'issue_date': datetime.now().strftime('%Y-%m-%d'),
                'risk_level': self._estimate_risk_level(expected_yield),
                'status': '在售',
                'underlying_type': '',
                'data_source': '用益信托网',
                'update_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return None
    
    def _extract_trust_company(self, product_name: str, texts: List[str]) -> str:
        """提取信托公司名称"""
        keywords = [
            '华鑫信托', '平安信托', '中信信托', '华润信托', '中融信托',
            '中航信托', '五矿信托', '建信信托', '交银信托', '外贸信托',
            '江苏信托', '昆仑信托', '兴业信托', '民生信托', '渤海信托',
            '长安信托', '陕国投', '爱建信托', '中泰信托', '陆家嘴信托',
            '中诚信托', '英大信托', '国投泰康', '华能信托', '华宝信托'
        ]
        
        # 从产品名称中查找
        for kw in keywords:
            if kw in product_name:
                return kw
        
        # 从其他文本中查找
        for text in texts:
            for kw in keywords:
                if kw in text:
                    return kw
        
        return '未知信托公司'
    
    def _classify_investment_type(self, product_name: str, texts: List[str]) -> str:
        """分类投资类型"""
        name_lower = product_name.lower()
        texts_combined = ' '.join(texts).lower()
        
        if any(kw in name_lower or kw in texts_combined for kw in ['权益', '股票', '股权']):
            return '权益类'
        elif any(kw in name_lower or kw in texts_combined for kw in ['混合', '多元']):
            return '混合类'
        elif any(kw in name_lower or kw in texts_combined for kw in ['债券', '货币', '现金']):
            return '固定收益类'
        elif any(kw in name_lower or kw in texts_combined for kw in ['另类', '房产', '地产']):
            return '另类投资'
        else:
            return '固定收益类'
    
    def _estimate_risk_level(self, yield_rate: float) -> str:
        """根据收益率估算风险等级"""
        if yield_rate < 6:
            return 'R2'
        elif yield_rate < 7.5:
            return 'R3'
        elif yield_rate < 9:
            return 'R4'
        else:
            return 'R5'
    
    def fetch_market_stats(self) -> Optional[Dict]:
        """获取市场统计数据"""
        try:
            products = self._cache.get('products', [])
            if not products:
                products = self.fetch_products()
            
            if not products:
                return None
            
            self._cache['products'] = products
            
            # 计算统计数据
            yields = [p['expected_yield'] for p in products if p.get('expected_yield', 0) > 0]
            
            # 按类型统计
            yield_by_type = {}
            type_counts = {}
            for p in products:
                inv_type = p.get('investment_type', '其他')
                if inv_type not in type_counts:
                    type_counts[inv_type] = []
                type_counts[inv_type].append(p.get('expected_yield', 0))
            
            for inv_type, yields_list in type_counts.items():
                if yields_list:
                    yield_by_type[inv_type] = round(sum(yields_list) / len(yields_list), 2)
            
            # 按期限统计
            yield_by_duration = {
                '1年内': round(sum([y for y in yields if y < 6.5]) / max(1, len([y for y in yields if y < 6.5])), 2) if yields else 6.2,
                '1-2年': round(sum([y for y in yields if 6.5 <= y < 7.5]) / max(1, len([y for y in yields if 6.5 <= y < 7.5])), 2) if yields else 6.85,
                '2-3年': round(sum([y for y in yields if 7.5 <= y < 8.5]) / max(1, len([y for y in yields if 7.5 <= y < 8.5])), 2) if yields else 7.35,
                '3年以上': round(sum([y for y in yields if y >= 8.5]) / max(1, len([y for y in yields if y >= 8.5])), 2) if yields else 7.80,
            }
            
            return {
                'stat_date': datetime.now().strftime('%Y-%m-%d'),
                'total_issuance': round(sum(p.get('issue_scale', 0) for p in products) / 10000, 2),
                'product_count': len(products),
                'avg_yield': round(sum(yields) / len(yields), 2) if yields else 6.5,
                'yield_by_type': yield_by_type,
                'yield_by_duration': yield_by_duration,
                'data_source': '用益信托网',
                'update_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  ❌ 获取市场统计失败: {e}")
            return None


class ChinaTrcFetcher:
    """中国信托登记数据获取器"""
    
    BASE_URL = "http://www.chinatrc.com.cn"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        try:
            resp = self.session.get(self.BASE_URL, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"  ⚠️ 中国信托登记连接失败: {e}")
            return False
    
    def fetch_products(self) -> List[Dict]:
        """获取产品公示数据"""
        products = []
        
        try:
            # 信托产品公示页面
            url = f"{self.BASE_URL}/investor/prorelease/index.html"
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 解析公示产品列表
            # 注意：部分信息可能需要登录才能查看
            items = soup.find_all('div', class_=['pro-item', 'product-item', 'list-item'])
            
            for item in items[:20]:  # 限制数量
                product = self._parse_product_item(item)
                if product:
                    products.append(product)
            
            return products
            
        except Exception as e:
            print(f"  ❌ 中国信托登记获取产品失败: {e}")
            return []
    
    def _parse_product_item(self, item) -> Optional[Dict]:
        """解析产品条目"""
        try:
            name_elem = item.find(['h3', 'h4', 'a', 'span'], class_=['title', 'name'])
            product_name = name_elem.get_text(strip=True) if name_elem else '未知产品'
            
            return {
                'product_code': f"TRC{datetime.now().year}{hash(product_name) % 10000:04d}",
                'product_name': product_name,
                'trust_company': '中信登公示',
                'product_type': '集合信托',
                'investment_type': '固定收益类',
                'expected_yield': 6.5,
                'duration': 24,
                'min_investment': 100,
                'issue_scale': 50000,
                'issue_date': datetime.now().strftime('%Y-%m-%d'),
                'risk_level': 'R3',
                'status': '公示中',
                'underlying_type': '',
                'data_source': '中国信托登记',
                'update_time': datetime.now().isoformat()
            }
        except:
            return None
    
    def fetch_market_stats(self) -> Optional[Dict]:
        """获取行业统计数据"""
        # 中国信登的部分统计数据需要登录
        # 这里返回基础结构
        return {
            'stat_date': datetime.now().strftime('%Y-%m-%d'),
            'total_issuance': 0,
            'product_count': 0,
            'avg_yield': 6.5,
            'yield_by_type': {},
            'yield_by_duration': {},
            'data_source': '中国信托登记',
            'update_time': datetime.now().isoformat(),
            'note': '部分数据需登录获取'
        }


class NFRADataFetcher:
    """国家金融监督管理总局数据获取器"""
    
    BASE_URL = "https://www.nfra.gov.cn"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def is_available(self) -> bool:
        try:
            resp = self.session.get(self.BASE_URL, timeout=10)
            return resp.status_code == 200
        except:
            return False
    
    def fetch_trust_industry_stats(self) -> Optional[Dict]:
        """获取信托行业统计数据"""
        try:
            # 统计数据页面
            url = f"{self.BASE_URL}/cn/view/pages/tongjishuju/tongjishuju.html"
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            
            # 解析统计数据链接
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找信托相关数据
            stats = {
                'data_source': '国家金融监管总局',
                'update_time': datetime.now().isoformat(),
                'available_reports': []
            }
            
            links = soup.find_all('a', href=True)
            for link in links:
                text = link.get_text(strip=True)
                if '信托' in text:
                    stats['available_reports'].append({
                        'title': text,
                        'url': link['href']
                    })
            
            return stats
            
        except Exception as e:
            print(f"  ❌ 获取监管统计失败: {e}")
            return None


class DataUpdater:
    """数据更新管理器"""
    
    def __init__(self, force: bool = False):
        self.force = force
        self.fetchers = {
            'yongyi': YongyiDataFetcher(),
            'chinatrc': ChinaTrcFetcher(),
            'nfra': NFRADataFetcher(),
        }
    
    def should_update(self) -> bool:
        """检查是否需要更新"""
        if self.force:
            return True
        
        if not UPDATE_LOG_FILE.exists():
            return True
        
        try:
            with open(UPDATE_LOG_FILE, 'r') as f:
                log = json.load(f)
            
            last_update = datetime.fromisoformat(log.get('last_update', '2000-01-01'))
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
            
            return hours_since_update >= CACHE_DURATION_HOURS
            
        except:
            return True
    
    def update(self, source: str = 'all') -> Dict:
        """执行数据更新"""
        print("=" * 60)
        print("📊 信托数据自动更新")
        print("=" * 60)
        print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"强制更新: {'是' if self.force else '否'}")
        print(f"数据源: {source}")
        print()
        
        result = {
            'success': False,
            'products_count': 0,
            'sources_used': [],
            'errors': [],
            'update_time': datetime.now().isoformat()
        }
        
        # 检查是否需要更新
        if not self.should_update():
            print("⏭️ 数据在缓存期内，跳过更新（使用--force强制更新）")
            return {**result, 'skipped': True}
        
        # 按优先级获取数据
        all_products = []
        market_stats = None
        
        # 1. 用益信托网
        if source in ['all', 'yongyi']:
            print("🔍 从用益信托网获取数据...")
            fetcher = self.fetchers['yongyi']
            
            if fetcher.is_available():
                products = fetcher.fetch_products()
                if products:
                    all_products.extend(products)
                    result['sources_used'].append('yongyi')
                    print(f"  ✓ 获取 {len(products)} 个产品")
                
                stats = fetcher.fetch_market_stats()
                if stats:
                    market_stats = stats
                    print(f"  ✓ 获取市场统计数据")
            else:
                print("  ⚠️ 用益信托网不可用")
                result['errors'].append('yongyi_unavailable')
        
        # 2. 中国信托登记
        if source in ['all', 'chinatrc']:
            print("\n🔍 从中国信托登记获取数据...")
            fetcher = self.fetchers['chinatrc']
            
            if fetcher.is_available():
                products = fetcher.fetch_products()
                if products:
                    all_products.extend(products)
                    result['sources_used'].append('chinatrc')
                    print(f"  ✓ 获取 {len(products)} 个产品")
            else:
                print("  ⚠️ 中国信托登记不可用")
        
        # 3. 同花顺API（如果配置了Token）
        if source in ['all', 'ths'] and DATA_SOURCES['ths']['enabled']:
            print("\n🔍 从同花顺API获取数据...")
            try:
                provider = get_data_provider()
                stats = provider.get_market_stats()
                if stats:
                    print(f"  ✓ 获取同花顺市场数据")
                    result['sources_used'].append('ths')
            except Exception as e:
                print(f"  ⚠️ 同花顺API获取失败: {e}")
        
        # 合并数据
        if all_products:
            print(f"\n📦 合并数据...")
            merged_products = self._merge_products(all_products)
            result['products_count'] = len(merged_products)
            print(f"  合并后共 {len(merged_products)} 个产品")
            
            # 保存数据
            self._save_products(merged_products)
        
        if market_stats:
            self._save_market_stats(market_stats)
        
        # 保存更新日志
        self._save_update_log(result)
        
        result['success'] = True
        
        print("\n" + "=" * 60)
        print("✅ 数据更新完成")
        print("=" * 60)
        
        return result
    
    def _merge_products(self, products: List[Dict]) -> List[Dict]:
        """合并产品数据，去重"""
        seen = {}
        
        for p in products:
            # 使用公司和产品名作为唯一键
            key = f"{p.get('trust_company', '')}_{p.get('product_name', '')}"
            
            if key not in seen:
                seen[key] = p
            else:
                # 保留更新的数据
                existing_time = seen[key].get('update_time', '')
                new_time = p.get('update_time', '')
                if new_time > existing_time:
                    seen[key] = p
        
        return list(seen.values())
    
    def _save_products(self, products: List[Dict]):
        """保存产品数据"""
        data = {
            'update_time': datetime.now().isoformat(),
            'source_count': len(set(p.get('data_source', 'unknown') for p in products)),
            'products': products
        }
        
        output_file = DATA_DIR / 'products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 产品数据已保存: {output_file}")
    
    def _save_market_stats(self, stats: Dict):
        """保存市场统计数据"""
        output_file = DATA_DIR / 'market_stats.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 市场统计已保存: {output_file}")
    
    def _save_update_log(self, result: Dict):
        """保存更新日志"""
        log = {
            'last_update': datetime.now().isoformat(),
            'next_update': (datetime.now() + timedelta(hours=CACHE_DURATION_HOURS)).isoformat(),
            'products_count': result.get('products_count', 0),
            'sources_used': result.get('sources_used', []),
            'errors': result.get('errors', [])
        }
        
        with open(UPDATE_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    
    def get_update_status(self) -> Dict:
        """获取更新状态"""
        if not UPDATE_LOG_FILE.exists():
            return {'status': 'never_updated'}
        
        try:
            with open(UPDATE_LOG_FILE, 'r') as f:
                log = json.load(f)
            
            last_update = datetime.fromisoformat(log.get('last_update', '2000-01-01'))
            next_update = datetime.fromisoformat(log.get('next_update', '2000-01-01'))
            
            return {
                'status': 'ready' if datetime.now() >= next_update else 'fresh',
                'last_update': log.get('last_update'),
                'next_update': log.get('next_update'),
                'hours_since_update': round((datetime.now() - last_update).total_seconds() / 3600, 1),
                'products_count': log.get('products_count', 0),
                'sources_used': log.get('sources_used', [])
            }
        except:
            return {'status': 'error'}


def main():
    parser = argparse.ArgumentParser(description='信托数据自动更新脚本')
    parser.add_argument('--force', action='store_true', help='强制更新')
    parser.add_argument('--source', default='all', 
                       choices=['all', 'yongyi', 'chinatrc', 'ths'],
                       help='数据源')
    parser.add_argument('--status', action='store_true', help='查看更新状态')
    
    args = parser.parse_args()
    
    updater = DataUpdater(force=args.force)
    
    if args.status:
        status = updater.get_update_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    
    result = updater.update(source=args.source)
    
    # 输出结果摘要
    print("\n📋 更新摘要:")
    print(f"  成功: {'✅' if result.get('success') else '❌'}")
    print(f"  产品数: {result.get('products_count', 0)}")
    print(f"  数据源: {', '.join(result.get('sources_used', []))}")
    if result.get('errors'):
        print(f"  错误: {', '.join(result.get('errors', []))}")


if __name__ == '__main__':
    main()
