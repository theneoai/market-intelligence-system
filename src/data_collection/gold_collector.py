"""
黄金期货数据采集模块
使用 Yahoo Finance 获取黄金数据
"""

import asyncio
import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger


class GoldCollector:
    """黄金期货数据采集器"""
    
    def __init__(self):
        self.name = "黄金期货"
        self.symbols = {
            'GC=F': 'COMEX黄金期货',
            'GLD': 'SPDR黄金ETF',
            'IAU': 'iShares黄金ETF'
        }
        
    async def collect(self) -> Dict:
        """采集黄金期货数据"""
        logger.info("🪙 采集黄金期货数据...")
        
        try:
            loop = asyncio.get_event_loop()
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'futures': {},
                'etfs': {},
                'correlation': {},
                'market_summary': {}
            }
            
            # 采集期货数据
            for symbol, name in self.symbols.items():
                ticker_data = await loop.run_in_executor(
                    None, self._get_ticker_data, symbol, name
                )
                
                if symbol == 'GC=F':
                    data['futures'][symbol] = ticker_data
                else:
                    data['etfs'][symbol] = ticker_data
                    
            # 获取美元指数 (DXY)
            dxy = await loop.run_in_executor(
                None, self._get_ticker_data, "DX-Y.NYB", "美元指数"
            )
            data['dxy'] = dxy
            
            # 计算关联性
            data['correlation'] = self._calculate_correlation(data)
            
            # 市场摘要
            data['market_summary'] = self._calculate_summary(data)
            
            logger.success(f"✅ 黄金数据采集完成 - COMEX: ${data['futures'].get('GC=F', {}).get('close', 'N/A')}")
            return data
            
        except Exception as e:
            logger.error(f"❌ 黄金数据采集失败: {e}")
            raise
    
    def _get_ticker_data(self, symbol: str, name: str) -> Optional[Dict]:
        """获取单个 ticker 数据"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 获取历史数据
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
                
            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest
            
            # 获取更多信息
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': name,
                'close': round(float(latest['Close']), 2),
                'open': round(float(latest['Open']), 2),
                'high': round(float(latest['High']), 2),
                'low': round(float(latest['Low']), 2),
                'volume': int(latest['Volume']),
                'change': round(float(latest['Close']) - float(prev['Close']), 2),
                'change_pct': round((float(latest['Close']) - float(prev['Close'])) / float(prev['Close']) * 100, 2),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow'),
                'market_cap': info.get('marketCap'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取 {symbol} 数据失败: {e}")
            return None
    
    def _calculate_correlation(self, data: Dict) -> Dict:
        """计算黄金与美元指数的关联性"""
        futures = data.get('futures', {}).get('GC=F', {})
        dxy = data.get('dxy', {})
        
        if not futures or not dxy:
            return {'gold_dxy_correlation': 'N/A', 'interpretation': '数据不足'}
            
        gold_change = futures.get('change_pct', 0)
        dxy_change = dxy.get('change_pct', 0)
        
        # 简单的反向关系判断
        if gold_change > 0 and dxy_change < 0:
            relation = "负相关 (美元跌黄金涨)"
        elif gold_change < 0 and dxy_change > 0:
            relation = "负相关 (美元涨黄金跌)"
        else:
            relation = "正相关或无明显关系"
            
        return {
            'gold_dxy_correlation': relation,
            'interpretation': '典型负相关关系' if '负相关' in relation else '需进一步观察'
        }
    
    def _calculate_summary(self, data: Dict) -> Dict:
        """计算市场摘要"""
        futures = data.get('futures', {}).get('GC=F', {})
        
        if not futures:
            return {'mood': '未知'}
            
        change_pct = futures.get('change_pct', 0)
        
        if change_pct > 1:
            mood = '强势上涨'
        elif change_pct > 0:
            mood = '温和上涨'
        elif change_pct > -1:
            mood = '温和下跌'
        else:
            mood = '弱势下跌'
            
        return {
            'mood': mood,
            'change_pct': change_pct,
            'price_level': '高位' if futures.get('close', 0) > 2000 else '中位' if futures.get('close', 0) > 1800 else '低位'
        }
