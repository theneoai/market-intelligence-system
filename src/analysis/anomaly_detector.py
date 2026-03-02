"""
价格异常检测模块
多维度异常检测
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class AnomalyDetector:
    """价格异常检测器"""
    
    def __init__(self):
        self.name = "异常检测"
        self.thresholds = {
            'price_change': 5.0,      # 5% 价格变动
            'volume_spike': 3.0,       # 3倍成交量
            'rsi_extreme': 70,         # RSI 极值
            'volatility_spike': 2.0    # 波动率异常
        }
        
    async def detect(self, market: str, data: Dict) -> List[Dict]:
        """检测异常"""
        logger.info(f"🚨 检测 {market} 异常...")
        
        anomalies = []
        
        try:
            if market == 'a_share':
                anomalies.extend(self._detect_a_share_anomalies(data))
            elif market == 'gold':
                anomalies.extend(self._detect_gold_anomalies(data))
            elif market == 'crypto':
                anomalies.extend(self._detect_crypto_anomalies(data))
            elif market == 'bond':
                anomalies.extend(self._detect_bond_anomalies(data))
                
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            
        return anomalies
    
    def _detect_a_share_anomalies(self, data: Dict) -> List[Dict]:
        """检测A股异常"""
        anomalies = []
        
        # 检查指数异常波动
        for idx_name, idx_data in data.get('indices', {}).items():
            if not idx_data:
                continue
                
            change_pct = idx_data.get('change_pct', 0)
            
            if abs(change_pct) > self.thresholds['price_change']:
                anomalies.append({
                    'type': 'price_spike',
                    'market': 'a_share',
                    'symbol': idx_name,
                    'severity': 'high' if abs(change_pct) > 7 else 'medium',
                    'value': change_pct,
                    'description': f"{idx_name} 指数{'暴涨' if change_pct > 0 else '暴跌'} {abs(change_pct):.2f}%"
                })
                
        # 检查成交量异常
        # 可以添加更多检测逻辑
        
        return anomalies
    
    def _detect_gold_anomalies(self, data: Dict) -> List[Dict]:
        """检测黄金异常"""
        anomalies = []
        
        futures = data.get('futures', {}).get('GC=F', {})
        if not futures:
            return anomalies
            
        change_pct = futures.get('change_pct', 0)
        
        if abs(change_pct) > self.thresholds['price_change']:
            anomalies.append({
                'type': 'price_spike',
                'market': 'gold',
                'symbol': 'GC=F',
                'severity': 'high' if abs(change_pct) > 3 else 'medium',
                'value': change_pct,
                'description': f"黄金期货{'暴涨' if change_pct > 0 else '暴跌'} {abs(change_pct):.2f}%"
            })
            
        # 检查与美元指数反向关系异常
        correlation = data.get('correlation', {})
        if '正相关' in correlation.get('gold_dxy_correlation', ''):
            anomalies.append({
                'type': 'correlation_breakdown',
                'market': 'gold',
                'symbol': 'GC=F',
                'severity': 'medium',
                'description': "黄金与美元呈现正相关，关系异常"
            })
            
        return anomalies
    
    def _detect_crypto_anomalies(self, data: Dict) -> List[Dict]:
        """检测数字货币异常"""
        anomalies = []
        
        for coin_id, coin_data in data.get('coins', {}).items():
            change_pct = coin_data.get('price_change_percentage_24h', 0)
            
            if abs(change_pct) > self.thresholds['price_change'] * 2:  # 数字货币波动更大
                anomalies.append({
                    'type': 'price_spike',
                    'market': 'crypto',
                    'symbol': coin_id,
                    'severity': 'high' if abs(change_pct) > 10 else 'medium',
                    'value': change_pct,
                    'description': f"{coin_id} {'暴涨' if change_pct > 0 else '暴跌'} {abs(change_pct):.2f}%"
                })
                
        return anomalies
    
    def _detect_bond_anomalies(self, data: Dict) -> List[Dict]:
        """检测国债异常"""
        anomalies = []
        
        # 检查收益率曲线倒挂
        curve = data.get('yield_curve', {})
        if '倒挂' in curve.get('shape', ''):
            anomalies.append({
                'type': 'yield_curve_inversion',
                'market': 'bond',
                'symbol': 'US_TREASURY',
                'severity': 'high',
                'value': curve.get('10y_2y_spread', 0),
                'description': f"收益率曲线倒挂 ({curve.get('10y_2y_spread', 0):.2f}%)，经济衰退风险"
            })
            
        # 检查利差异常
        spread = data.get('spread', {})
        us_cn_spread = spread.get('us_cn_10y_spread', 0)
        
        if us_cn_spread > 2 or us_cn_spread < 0:
            anomalies.append({
                'type': 'spread_anomaly',
                'market': 'bond',
                'symbol': 'US_CN_SPREAD',
                'severity': 'medium',
                'value': us_cn_spread,
                'description': f"中美利差异常 ({us_cn_spread:.2f}%)"
            })
            
        return anomalies
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0.0
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns) * np.sqrt(252))  # 年化波动率
