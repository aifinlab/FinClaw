#!/usr/bin/env python3
"""信托估值引擎"""
import json
import numpy as np
from datetime import datetime

class TrustValuationEngine:
    def __init__(self):
        self.models = {
            'dcf': self._dcf_valuation,
            'market': self._market_valuation,
            'nav': self._nav_calculation
        }
    
    def value(self, asset: dict, method: str = 'dcf') -> dict:
        valuer = self.models.get(method, self._dcf_valuation)
        return valuer(asset)
    
    def _dcf_valuation(self, asset: dict) -> dict:
        cashflows = asset.get('cashflows', [])
        discount_rate = asset.get('discount_rate', 0.08)
        
        npv = sum(cf / ((1 + discount_rate) ** (i+1)) 
                  for i, cf in enumerate(cashflows))
        
        return {
            'method': 'DCF',
            'value': round(npv, 2),
            'discount_rate': discount_rate,
            'timestamp': datetime.now().isoformat()
        }
    
    def _market_valuation(self, asset: dict) -> dict:
        comparables = asset.get('comparables', [])
        if not comparables:
            return {'value': 0, 'method': 'Market'}
        avg = np.mean([c.get('multiple', 1) for c in comparables])
        return {
            'method': 'Market',
            'value': round(avg * asset.get('ebitda', 1), 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def _nav_calculation(self, asset: dict) -> dict:
        assets = asset.get('total_assets', 0)
        liabilities = asset.get('total_liabilities', 0)
        return {
            'method': 'NAV',
            'value': round(assets - liabilities, 2),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', required=True)
    parser.add_argument('--method', default='dcf')
    args = parser.parse_args()
    
    with open(args.asset) as f:
        data = json.load(f)
    
    engine = TrustValuationEngine()
    print(json.dumps(engine.value(data, args.method), ensure_ascii=False, indent=2))
