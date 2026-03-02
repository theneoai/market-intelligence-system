"""
市场情绪分析模块
多维度情绪分析
"""

import asyncio
from typing import Dict, List
from datetime import datetime
from loguru import logger


class SentimentAnalyzer:
    """市场情绪分析器"""
    
    def __init__(self):
        self.name = "情绪分析"
        
    async def analyze(self, market: str, data: Dict) -> Dict:
        """分析市场情绪"""
        logger.info(f"🎭 分析 {market} 市场情绪...")
        
        try:
            if market == 'a_share':
                return self._analyze_a_share_sentiment(data)
            elif market == 'gold':
                return self._analyze_gold_sentiment(data)
            elif market == 'crypto':
                return self._analyze_crypto_sentiment(data)
            elif market == 'bond':
                return self._analyze_bond_sentiment(data)
            else:
                return {'score': 50, 'mood': '中性'}
                
        except Exception as e:
            logger.error(f"情绪分析失败: {e}")
            return {'score': 50, 'mood': '未知', 'error': str(e)}
    
    def _analyze_a_share_sentiment(self, data: Dict) -> Dict:
        """分析A股情绪"""
        # 基于涨停数量、资金流向等
        zt_count = len(data.get('zt_pool', [])) if data.get('zt_pool') else 0
        summary = data.get('market_summary', {})
        
        # 简单情绪评分
        if zt_count > 100:
            score = 85
            mood = '极度乐观'
        elif zt_count > 50:
            score = 70
            mood = '乐观'
        elif zt_count > 20:
            score = 55
            mood = '中性偏乐观'
        elif zt_count > 5:
            score = 45
            mood = '中性偏谨慎'
        else:
            score = 30
            mood = '谨慎'
            
        return {
            'score': score,
            'mood': mood,
            'factors': {
                'zt_count': zt_count,
                'market_mood': summary.get('market_mood', '未知')
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_gold_sentiment(self, data: Dict) -> Dict:
        """分析黄金情绪"""
        futures = data.get('futures', {}).get('GC=F', {})
        summary = data.get('market_summary', {})
        correlation = data.get('correlation', {})
        
        change_pct = futures.get('change_pct', 0)
        
        # 黄金情绪通常与价格正相关
        if change_pct > 1.5:
            score = 80
            mood = '强烈看涨'
        elif change_pct > 0.5:
            score = 65
            mood = '看涨'
        elif change_pct > -0.5:
            score = 50
            mood = '中性'
        elif change_pct > -1.5:
            score = 35
            mood = '看跌'
        else:
            score = 20
            mood = '强烈看跌'
            
        return {
            'score': score,
            'mood': mood,
            'factors': {
                'price_change': change_pct,
                'dxy_correlation': correlation.get('gold_dxy_correlation', '未知')
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_crypto_sentiment(self, data: Dict) -> Dict:
        """分析数字货币情绪"""
        fg = data.get('fear_greed', {})
        summary = data.get('market_summary', {})
        
        fg_value = fg.get('value', 50)
        
        # 使用恐慌贪婪指数
        if fg_value > 75:
            mood = '极度贪婪'
        elif fg_value > 55:
            mood = '贪婪'
        elif fg_value > 45:
            mood = '中性'
        elif fg_value > 25:
            mood = '恐惧'
        else:
            mood = '极度恐惧'
            
        return {
            'score': fg_value,
            'mood': mood,
            'factors': {
                'fear_greed_index': fg_value,
                'btc_change': summary.get('btc_change_24h', 0)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_bond_sentiment(self, data: Dict) -> Dict:
        """分析国债情绪"""
        curve = data.get('yield_curve', {})
        summary = data.get('market_summary', {})
        
        # 国债情绪主要看收益率曲线
        shape = curve.get('shape', '')
        
        if '倒挂' in shape:
            score = 30
            mood = '避险情绪'
        elif '陡峭' in shape:
            score = 70
            mood = '风险偏好'
        else:
            score = 50
            mood = '中性'
            
        return {
            'score': score,
            'mood': mood,
            'factors': {
                'yield_curve': shape,
                'recession_risk': '倒挂' in shape
            },
            'timestamp': datetime.now().isoformat()
        }
