#!/usr/bin/env python3
"""信托投后监控"""
import json
from datetime import datetime

class PostInvestmentMonitor:
    def monitor(self, portfolio: list) -> dict:
        alerts = []
        for asset in portfolio:
            if asset.get('risk_score', 0) > 70:
                alerts.append({
                    'asset': asset['name'],
                    'level': 'high',
                    'reason': '风险评分过高'
                })
        
        return {
            'status': 'success',
            'total_assets': len(portfolio),
            'alerts': alerts,
            'alert_count': len(alerts),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--portfolio', required=True)
    args = parser.parse_args()
    
    with open(args.portfolio) as f:
        data = json.load(f)
    
    monitor = PostInvestmentMonitor()
    print(json.dumps(monitor.monitor(data), ensure_ascii=False, indent=2))
