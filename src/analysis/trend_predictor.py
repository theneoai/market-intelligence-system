"""
趋势预测模块
多因子趋势预测
"""

import numpy as np
from typing import Dict, List
from datetime import datetime
from loguru import logger


class TrendPredictor:
    """趋势预测器"""
    
    def __init__(self):
        self.name = "趋势预测"
        
    async def predict(self, market: str, data: Dict) -> Dict:
        """预测趋势"""
        logger.info(f"📈 预测 {market} 趋势...")
        
        try:
            if market == 'a_share':
                return self._predict_a_share_trend(data)
            elif market == 'gold':
                return self._predict_gold_trend(data)
            elif market == 'crypto':
                return self._predict_crypto_trend(data)
            elif market == 'bond':
                return self._predict_bond_trend(data)
            else:
                return {'direction': '未知', 'confidence': 0}
                
        except Exception as e:
            logger.error(f"趋势预测失败: {e}")
            return {'direction': '未知', 'confidence': 0, 'error': str(e)}
    
    def _predict_a_share_trend(self, data: Dict) -> Dict:
        """预测A股趋势"""
        indices = data.get('indices', {})
        summary = data.get('market_summary', {})
        
        # 简单趋势判断（实际应使用更多技术指标）
        up_indices = summary.get('indices_up', 0)
        down_indices = summary.get('indices_down', 0)
        
        if up_indices > down_indices:
            direction = '上涨'
            confidence = 60 + (up_indices - down_indices) * 10
        elif down_indices > up_indices:
            direction = '下跌'
            confidence = 60 + (down_indices - up_indices) * 10
        else:
            direction = '震荡'
            confidence = 50
            
        return {
            'direction': direction,
            'confidence': min(confidence, 95),
            'timeframe': '短期 (1-5天)',
            'factors': {
                'market_breadth': f"{up_indices} 涨 / {down_indices} 跌"
            },
            'suggestion': self._get_suggestion(direction),
            'timestamp': datetime.now().isoformat()
        }
    
    def _predict_gold_trend(self, data: Dict) -> Dict:
        """预测黄金趋势"""
        futures = data.get('futures', {}).get('GC=F', {})
        correlation = data.get('correlation', {})
        
        if not futures:
            return {'direction': '未知', 'confidence': 0}
            
        change_pct = futures.get('change_pct', 0)
        dxy_relation = correlation.get('gold_dxy_correlation', '')
        
        # 基于价格动量和美元关系
        if change_pct > 1 and '负相关' in dxy_relation:
            direction = '上涨'
            confidence = 70
        elif change_pct < -1 and '负相关' in dxy_relation:
            direction = '下跌'
            confidence = 70
        elif abs(change_pct) < 0.5:
            direction = '震荡'
            confidence = 55
        else:
            direction = '观望'
            confidence = 50
            
        return {
            'direction': direction,
            'confidence': confidence,
            'timeframe': '短期 (1-3天)',
            'factors': {
                'price_momentum': change_pct,
                'dxy_relation': dxy_relation
            },
            'suggestion': self._get_suggestion(direction),
            'timestamp': datetime.now().isoformat()
        }
    
    def _predict_crypto_trend(self, data: Dict) -> Dict:
        """预测数字货币趋势"""
        btc = data.get('coins', {}).get('bitcoin', {})
        fg = data.get('fear_greed', {})
        
        if not btc:
            return {'direction': '未知', 'confidence': 0}
            
        btc_change = btc.get('price_change_percentage_24h', 0)
        fg_value = fg.get('value', 50)
        
        # 结合价格动量和恐慌贪婪指数
        if btc_change > 5 and fg_value > 60:
            direction = '上涨'
            confidence = 65
        elif btc_change < -5 and fg_value < 40:
            direction = '下跌'
            confidence = 65
        elif abs(btc_change) < 2:
            direction = '震荡'
            confidence = 60
        else:
            direction = '观望'
            confidence = 50
            
        return {
            'direction': direction,
            'confidence': confidence,
            'timeframe': '短期 (1-2天)',
            'factors': {
                'btc_change': btc_change,
                'fear_greed': fg_value
            },
            'suggestion': self._get_suggestion(direction),
            'timestamp': datetime.now().isoformat()
        }
    
    def _predict_bond_trend(self, data: Dict) -> Dict:
        """预测国债趋势"""
        curve = data.get('yield_curve', {})
        spread = data.get('spread', {})
        
        shape = curve.get('shape', '')
        us_cn_spread = spread.get('us_cn_10y_spread', 0)
        
        # 基于收益率曲线和利差
        if '倒挂' in shape:
            direction = '收益率下行 (债价上涨)'
            confidence = 75
        elif '陡峭' in shape and us_cn_spread > 1:
            direction = '收益率上行 (债价下跌)'
            confidence = 65
        else:
            direction = '震荡'
            confidence = 55
            
        return {
            'direction': direction,
            'confidence': confidence,
            'timeframe': '中期 (1-4周)',
            'factors': {
                'yield_curve': shape,
                'us_cn_spread': us_cn_spread
            },
            'suggestion': self._get_suggestion(direction),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_suggestion(self, direction: str) -> str:
        """获取交易建议"""
        suggestions = {
            '上涨': '可考虑适度参与',
            '下跌': '建议观望或减仓',
            '震荡': '适合高抛低吸',
            '观望': '等待方向明朗',
            '收益率下行 (债价上涨)': '债券配置价值提升',
            '收益率上行 (债价下跌)': '关注利率风险'
        }
        return suggestions.get(direction, '保持关注')
