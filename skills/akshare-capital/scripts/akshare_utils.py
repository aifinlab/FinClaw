#!/usr/bin/env python3
"""
AkShare 工具模块 - 带延迟和重试机制
防止被东方财富限流
"""

import time
import random
import functools

def akshare_delay(min_delay=2, max_delay=5):
    """
    AkShare 请求延迟装饰器
    
    Args:
        min_delay: 最小延迟秒数
        max_delay: 最大延迟秒数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 随机延迟，模拟人类行为
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def akshare_retry(max_retries=3, delay=3):
    """
    AkShare 重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔秒数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (attempt + 1) + random.uniform(0, 2)
                        print(f"请求失败，{wait_time:.1f}秒后重试({attempt + 1}/{max_retries - 1})...")
                        time.sleep(wait_time)
                    else:
                        print(f"请求失败，已达最大重试次数: {e}")
            raise last_exception
        return wrapper
    return decorator

class AkshareRateLimiter:
    """AkShare 频率限制器"""
    
    def __init__(self, min_delay=2, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """等待适当时间后再请求"""
        elapsed = time.time() - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < delay:
            wait_time = delay - elapsed
            time.sleep(wait_time)
        
        self.last_request_time = time.time()

# 全局频率限制器实例
rate_limiter = AkshareRateLimiter(min_delay=2, max_delay=5)

def safe_ak_call(ak_func, *args, **kwargs):
    """
    安全的 AkShare 调用（带延迟和重试）
    
    Args:
        ak_func: akshare 函数
        *args, **kwargs: 函数参数
        
    Returns:
        函数返回值或 None
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # 频率限制
            rate_limiter.wait()
            
            # 执行请求
            result = ak_func(*args, **kwargs)
            return result
            
        except Exception as e:
            if "RemoteDisconnected" in str(e) or "Connection aborted" in str(e):
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1) + random.uniform(0, 3)
                    print(f"连接被关闭，{wait_time:.1f}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"请求失败: {e}")
                    return None
            else:
                print(f"请求错误: {e}")
                return None
    
    return None

if __name__ == "__main__":
    print("AkShare工具模块 - 用于防止被东方财富限流")
    print("使用方式:")
    print("  from akshare_utils import safe_ak_call, rate_limiter")
    print("  result = safe_ak_call(ak.stock_individual_fund_flow_rank, indicator='今日')")
