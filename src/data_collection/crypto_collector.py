"""
数字货币数据采集模块
使用 Binance API / CoinGecko
"""

import asyncio
import requests
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class CryptoCollector:
    """数字货币数据采集器"""
    
    def __init__(self):
        self.name = "数字货币"
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.symbols = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'ripple']
        
    async def collect(self) -> Dict:
        """采集数字货币数据"""
        logger.info("₿ 采集数字货币数据...")
        
        try:
            loop = asyncio.get_event_loop()
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'coins': {},
                'global': {},
                'fear_greed': {},
                'market_summary': {}
            }
            
            # 采集主要币种数据
            coins_data = await loop.run_in_executor(
                None, self._get_coins_data
            )
            data['coins'] = coins_data
            
            # 全球市场数据
            global_data = await loop.run_in_executor(
                None, self._get_global_data
            )
            data['global'] = global_data
            
            # 恐慌贪婪指数
            fear_greed = await loop.run_in_executor(
                None, self._get_fear_greed_index
            )
            data['fear_greed'] = fear_greed
            
            # 市场摘要
            data['market_summary'] = self._calculate_summary(data)
            
            btc_price = data['coins'].get('bitcoin', {}).get('current_price', 'N/A')
            logger.success(f"✅ 数字货币采集完成 - BTC: ${btc_price}")
            return data
            
        except Exception as e:
            logger.error(f"❌ 数字货币采集失败: {e}")
            raise
    
    def _get_coins_data(self) -> Dict:
        """获取币种数据"""
        try:
            ids = ','.join(self.symbols)
            url = f"{self.coingecko_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': ids,
                'order': 'market_cap_desc',
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = {}
            for coin in response.json():
                coin_id = coin['id']
                data[coin_id] = {
                    'symbol': coin['symbol'],
                    'name': coin['name'],
                    'current_price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'total_volume': coin['total_volume'],
                    'price_change_24h': coin['price_change_24h'],
                    'price_change_percentage_24h': coin['price_change_percentage_24h'],
                    'market_cap_rank': coin['market_cap_rank'],
                    'ath': coin['ath'],
                    'ath_change_percentage': coin['ath_change_percentage'],
                    'high_24h': coin['high_24h'],
                    'low_24h': coin['low_24h']
                }
                
            return data
            
        except Exception as e:
            logger.error(f"获取币种数据失败: {e}")
            return {}
    
    def _get_global_data(self) -> Dict:
        """获取全球市场数据"""
        try:
            url = f"{self.coingecko_url}/global"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()['data']
            
            return {
                'total_market_cap_usd': data['total_market_cap']['usd'],
                'total_volume_usd': data['total_volume']['usd'],
                'market_cap_percentage': data['market_cap_percentage'],
                'active_cryptocurrencies': data['active_cryptocurrencies'],
                'markets': data['markets']
            }
            
        except Exception as e:
            logger.error(f"获取全球市场数据失败: {e}")
            return {}
    
    def _get_fear_greed_index(self) -> Dict:
        """获取恐慌贪婪指数"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()['data'][0]
            
            return {
                'value': int(data['value']),
                'value_classification': data['value_classification'],
                'timestamp': data['timestamp']
            }
            
        except Exception as e:
            logger.error(f"获取恐慌贪婪指数失败: {e}")
            return {'value': 50, 'value_classification': 'Neutral'}
    
    def _calculate_summary(self, data: Dict) -> Dict:
        """计算市场摘要"""
        btc = data.get('coins', {}).get('bitcoin', {})
        eth = data.get('coins', {}).get('ethereum', {})
        fg = data.get('fear_greed', {})
        
        if not btc:
            return {'mood': '未知'}
            
        btc_change = btc.get('price_change_percentage_24h', 0)
        
        # 根据BTC涨跌幅和恐慌贪婪指数判断
        if btc_change > 5:
            mood = '极度乐观'
        elif btc_change > 2:
            mood = '乐观'
        elif btc_change > -2:
            mood = '中性'
        elif btc_change > -5:
            mood = '谨慎'
        else:
            mood = '恐慌'
            
        # 结合恐慌贪婪指数
        fg_value = fg.get('value', 50)
        if fg_value > 75:
            fg_mood = '贪婪'
        elif fg_value > 55:
            fg_mood = '乐观'
        elif fg_value > 45:
            fg_mood = '中性'
        elif fg_value > 25:
            fg_mood = '恐惧'
        else:
            fg_mood = '极度恐惧'
            
        return {
            'mood': mood,
            'btc_change_24h': round(btc_change, 2),
            'fear_greed': fg_value,
            'fear_greed_mood': fg_mood,
            'dominance': 'BTC主导' if btc_change > eth.get('price_change_percentage_24h', 0) else 'ETH主导'
        }
