#!/usr/bin/env python3
"""
FinClaw 统一行情查询工具 - 优先使用国内数据源
支持 A股、港股、美股、指数

Usage:
    python quote.py <code>

Example:
    python quote.py 000001     # 上证指数
    python quote.py 00700     # 腾讯控股(港股)
    python quote.py AAPL      # 苹果(美股)
    python quote.py GSPC      # 标普500
"""

import sys
import json
import socket
from datetime import datetime

# 强制使用 IPv4
socket.getaddrinfo_orig = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return socket.getaddrinfo_orig(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

import requests
import re

# 数据源优先级: 腾讯 > 新浪 > Yahoo
DATA_SOURCES = {
    'tencent': {
        'name': '腾讯财经',
        'base_url': 'https://qt.gtimg.cn/q='
    },
    'sina': {
        'name': '新浪财经', 
        'base_url': 'https://hq.sinajs.cn/list='
    }
}

def parse_tencent_data(data_str):
    """解析腾讯财经数据"""
    try:
        # 格式: v_sh000001="1~上证指数~000001~..." 或 v_hk00700="100~腾讯控股~00700~..."
        match = re.search(r'v_\w+="(.+?)"', data_str)
        if not match:
            return None

        parts = match.group(1).split('~')
        if len(parts) < 35:
            return None

        # 腾讯字段映射 (港股和A股字段位置略有不同)
        # parts[0]: 市场代码(1=sh, 51=sz, 100=hk, etc)
        # parts[1]: 名称
        # parts[2]: 代码
        # parts[3]: 最新价
        # parts[4]: 昨收
        # parts[5]: 今开
        # parts[6]: 成交量(股)
        # parts[30]: 时间
        # parts[31]: 涨跌额
        # parts[32]: 涨跌幅(%)
        # parts[33]: 最高
        # parts[34]: 最低
        # parts[35]: 成交额?

        result = {
            'name': parts[1],
            'code': parts[2],
            'price': float(parts[3]) if parts[3] else 0,
            'yesterday_close': float(parts[4]) if parts[4] else 0,
            'open': float(parts[5]) if parts[5] else 0,
            'volume': int(float(parts[6])) if parts[6] else 0,
        }

        # 添加可选字段
        if len(parts) > 31 and parts[31]:
            result['price_change'] = float(parts[31])
        if len(parts) > 32 and parts[32]:
            result['price_change_pct'] = float(parts[32])
        if len(parts) > 33 and parts[33]:
            result['high'] = float(parts[33])
        if len(parts) > 34 and parts[34]:
            result['low'] = float(parts[34])

        # 成交额(字段位置可能变化)
        if len(parts) > 37 and parts[37]:
            try:
                result['volume_amount'] = float(parts[37])
            except:
                pass

        # PE/PB/市值 (字段位置较后，可能不存在)
        if len(parts) > 39 and parts[39]:
            try:
                result['pe'] = float(parts[39])
            except:
                pass
        if len(parts) > 46 and parts[46]:
            try:
                result['pb'] = float(parts[46])
            except:
                pass
        if len(parts) > 44 and parts[44]:
            try:
                result['market_cap'] = float(parts[44])
            except:
                pass

        return result
    except Exception as e:
        print(f"[DEBUG] 腾讯解析错误: {e}", file=sys.stderr)
        return None

def get_sina_quote(code):
    """从新浪财经获取行情 (美股备用)"""
    try:
        # 新浪财经接口格式
        # 美股: gb_前缀，如 gb_aapl
        # 港股: hk_前缀，如 hk_00700
        # A股: sh/sz 前缀
        
        if code.isalpha():  # 美股代码是纯字母
            prefix = 'gb_'
            full_code = f"{prefix}{code.lower()}"
        elif code.isdigit() and len(code) == 5:  # 港股
            prefix = 'hk_'
            full_code = f"{prefix}{code}"
        else:
            return None  # A股用腾讯财经
        
        url = f"https://hq.sinajs.cn/list={full_code}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            return parse_sina_us_data(response.text, code)
        return None
    except Exception as e:
        print(f"[DEBUG] 新浪请求错误: {e}", file=sys.stderr)
        return None


def parse_sina_us_data(data_str, code):
    """解析新浪财经美股数据"""
    try:
        # 格式: var hq_str_gb_aapl="苹果,250.1200,-2.21,2026-03-14 08:14:43,-5.6400,255.4800,256.3300,249.5200,..."
        match = re.search(r'var hq_str_\w+="([^"]*)"', data_str)
        if not match:
            return None
        
        data = match.group(1)
        if not data:  # 空数据表示无此股票
            return None
        
        parts = data.split(',')
        if len(parts) < 11:
            return None
        
        # 美股字段映射 (新浪财经)
        # parts[0]: 中文名称
        # parts[1]: 最新价
        # parts[2]: 涨跌额(未复权)
        # parts[3]: 时间(字符串，非数字)
        # parts[4]: 涨跌额(复权)
        # parts[5]: 开盘价
        # parts[6]: 最高价
        # parts[7]: 最低价
        # parts[8]: 52周最高
        # parts[9]: 52周最低
        # parts[10]: 成交量
        
        price = float(parts[1]) if parts[1] else 0
        # 昨收需要通过最新价和涨跌额计算
        change = float(parts[4]) if parts[4] else 0  # 使用复权涨跌额
        prev_close = price - change if price and change else 0
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return {
            'name': f"{parts[0]}({code})" if parts[0] else code,
            'code': code,
            'price': price,
            'yesterday_close': round(prev_close, 4),
            'open': float(parts[5]) if parts[5] else 0,
            'high': float(parts[6]) if parts[6] else 0,
            'low': float(parts[7]) if parts[7] else 0,
            'price_change': round(change, 4),
            'price_change_pct': round(change_pct, 2),
            'volume': int(float(parts[10])) if parts[10] else 0,
            'currency': 'USD',
        }
    except Exception as e:
        print(f"[DEBUG] 新浪美股解析错误: {e}", file=sys.stderr)
        return None


def parse_sina_data(data_str):
    """解析新浪财经数据"""
    try:
        # 格式: var hq_str_sh000001="上证指数,4080.61,..."
        match = re.search(r'"(.+?)"', data_str)
        if not match:
            return None
        
        parts = match.group(1).split(',')
        if len(parts) < 30:
            return None
        
        return {
            'name': parts[0],
            'price': float(parts[1]),
            'price_change': float(parts[2]),
            'price_change_pct': float(parts[3]),
            'volume': int(float(parts[4])),
            'volume_amount': float(parts[5]),
            'open': float(parts[6]),
            'yesterday_close': float(parts[7]),
            'high': float(parts[8]),
            'low': float(parts[9]),
        }
    except Exception as e:
        print(f"[DEBUG] 新浪解析错误: {e}", file=sys.stderr)
        return None

def get_tencent_quote(code):
    """从腾讯财经获取行情"""
    try:
        # 确定市场前缀
        # 1. A股指数代码
        if code in ('000001', '000300', '000016', '000688'):
            prefix = 'sh'
        # 2. 港股：5位数字
        elif code.isdigit() and len(code) == 5:
            prefix = 'hk'
        # 3. A股上海：6开头
        elif code.startswith('6'):
            prefix = 'sh'
        # 4. A股深圳：0, 2, 3开头
        elif code.startswith('0') or code.startswith('2') or code.startswith('3'):
            prefix = 'sz'
        # 5. 北交所：8, 4开头
        elif code.startswith('8') or code.startswith('4'):
            prefix = 'bj'
        else:
            prefix = 'us'
        
        full_code = f"{prefix}{code}"
        url = f"https://qt.gtimg.cn/q={full_code}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            return parse_tencent_data(response.text)
        return None
    except Exception as e:
        print(f"[DEBUG] 腾讯请求错误: {e}", file=sys.stderr)
        return None

def get_yahoo_quote(ticker):
    """从 Yahoo Finance 获取行情 (备用)"""
    original_timeout = None
    try:
        import yfinance as yf
        import socket
        import urllib.request
        
        # 设置超时
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(5)
        
        # 先测试 Yahoo 是否可连接
        try:
            test_url = "https://query1.finance.yahoo.com"
            req = urllib.request.Request(test_url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req, timeout=3) as resp:
                pass
        except Exception:
            print(f"[DEBUG] Yahoo Finance 连接失败，跳过", file=sys.stderr)
            socket.setdefaulttimeout(original_timeout)
            return None
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or 'regularMarketPrice' not in info:
            return None
        
        return {
            'name': info.get('longName', info.get('shortName', ticker)),
            'code': ticker,
            'price': info.get('regularMarketPrice', 0),
            'yesterday_close': info.get('regularMarketPreviousClose', 0),
            'open': info.get('regularMarketOpen', 0),
            'high': info.get('regularMarketDayHigh', 0),
            'low': info.get('regularMarketDayLow', 0),
            'volume': info.get('regularMarketVolume', 0),
            'price_change': info.get('regularMarketChange', 0),
            'price_change_pct': info.get('regularMarketChangePercent', 0),
            'market_cap': info.get('marketCap', 0),
            'pe': info.get('trailingPE', 0),
            'pb': info.get('priceToBook', 0),
            'currency': info.get('currency', 'USD'),
        }
    except Exception as e:
        print(f"[DEBUG] Yahoo 错误: {e}", file=sys.stderr)
        return None
    finally:
        # 恢复默认超时
        try:
            socket.setdefaulttimeout(original_timeout)
        except:
            pass

def format_output(data, source):
    """格式化输出"""
    if not data:
        return
    
    change_emoji = "📈" if data.get('price_change', 0) >= 0 else "📉"
    currency = data.get('currency', 'CNY')
    
    print(f"\n🌐 {data.get('name', 'Unknown')} ({data.get('code', '')})")
    print(f"{'='*60}")
    print(f"  数据源: {source}")
    print(f"  最新价: {data.get('price', 0):.2f} {currency}")
    
    if data.get('price_change_pct'):
        print(f"  涨跌幅: {change_emoji} {data.get('price_change_pct'):.2f}%")
    if data.get('price_change'):
        print(f"  涨跌额: {data.get('price_change'):.2f}")
    
    print(f"  今开: {data.get('open', 0):.2f}")
    print(f"  最高: {data.get('high', 0):.2f}")
    print(f"  最低: {data.get('low', 0):.2f}")
    print(f"  昨收: {data.get('yesterday_close', 0):.2f}")
    
    if data.get('volume'):
        print(f"  成交量: {data.get('volume'):,}")
    if data.get('volume_amount'):
        print(f"  成交额: {data.get('volume_amount'):,.0f} 万")
    if data.get('market_cap'):
        cap = data['market_cap']
        if cap > 1e8:
            print(f"  总市值: {cap/1e8:.2f} 亿")
        else:
            print(f"  总市值: {cap:,.0f}")
    if data.get('pe'):
        print(f"  市盈率: {data.get('pe'):.2f}")
    if data.get('pb'):
        print(f"  市净率: {data.get('pb'):.2f}")
    
    # JSON 输出
    print(f"\n##QUOTE_META##")
    print(json.dumps(data, ensure_ascii=False, default=str))

def get_quote(code):
    """获取行情 - 按优先级尝试多个数据源"""
    code = code.strip().upper()
    
    # 1. 尝试腾讯财经 (A股/港股)
    # 港股代码是5位数字，A股是6位
    if code.isdigit() and (len(code) == 6 or len(code) == 5):
        print(f"[INFO] 尝试腾讯财经获取 {code}...", file=sys.stderr)
        data = get_tencent_quote(code)
        if data:
            format_output(data, '腾讯财经')
            return
    
    # 2. 尝试新浪财经 (美股优先)
    if code.isalpha() or (not code.isdigit() and '.' not in code):
        print(f"[INFO] 尝试新浪财经获取 {code}...", file=sys.stderr)
        data = get_sina_quote(code)
        if data:
            format_output(data, '新浪财经')
            return
    
    # 3. 尝试 Yahoo Finance (美股/指数备用)
    print(f"[INFO] 尝试 Yahoo Finance 获取 {code}...", file=sys.stderr)
    
    # 转换代码格式
    ticker = code
    if code == 'GSPC':
        ticker = '^GSPC'
    elif code == 'IXIC':
        ticker = '^IXIC'
    elif code == 'DJI':
        ticker = '^DJI'
    elif code == 'HSI':
        ticker = '^HSI'
    
    data = get_yahoo_quote(ticker)
    if data:
        format_output(data, 'Yahoo Finance')
        return
    
    print(f"[ERROR] 无法获取 {code} 的行情数据", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quote.py <code>")
        print("Example:")
        print("  python quote.py 000001    # 上证指数")
        print("  python quote.py 00700     # 腾讯控股")
        print("  python quote.py AAPL      # 苹果")
        print("  python quote.py GSPC      # 标普500")
        sys.exit(1)
    
    code = sys.argv[1]
    get_quote(code)
