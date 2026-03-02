"""
A股数据采集模块
使用 akshare / tushare 获取A股数据
"""

import asyncio
import akshare as ak
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger


class AShareCollector:
    """A股数据采集器"""
    
    def __init__(self):
        self.name = "A股"
        self.data_cache = {}
        
    async def collect(self) -> Dict:
        """采集A股数据"""
        logger.info("📈 采集A股数据...")
        
        try:
            # 在异步环境中运行同步的akshare
            loop = asyncio.get_event_loop()
            
            # 上证指数
            sh_index = await loop.run_in_executor(
                None, self._get_index_data, "sh000001"
            )
            
            # 深证成指
            sz_index = await loop.run_in_executor(
                None, self._get_index_data, "sz399001"
            )
            
            # 创业板指
            cy_index = await loop.run_in_executor(
                None, self._get_index_data, "sz399006"
            )
            
            # 涨跌停统计
            zdt = await loop.run_in_executor(None, ak.stock_zt_pool_em)
            
            # 北向资金
            north_money = await loop.run_in_executor(None, ak.stock_hsgt_hist_em)
            
            # 行业板块
            sectors = await loop.run_in_executor(None, ak.stock_sector_spot)
            
            # 龙虎榜
            lhb = await loop.run_in_executor(None, ak.stock_lhb_ggtj_em)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'indices': {
                    'shanghai': sh_index,
                    'shenzhen': sz_index,
                    'chinext': cy_index
                },
                'zt_pool': zdt.to_dict() if zdt is not None else None,
                'north_money': north_money.to_dict() if north_money is not None else None,
                'sectors': sectors.to_dict() if sectors is not None else None,
                'lhb': lhb.to_dict() if lhb is not None else None,
                'market_summary': self._calculate_summary(sh_index, sz_index, cy_index)
            }
            
            logger.success(f"✅ A股数据采集完成 - 涨停: {len(zdt) if zdt is not None else 0} 家")
            return data
            
        except Exception as e:
            logger.error(f"❌ A股数据采集失败: {e}")
            raise
    
    def _get_index_data(self, symbol: str) -> Dict:
        """获取指数数据"""
        try:
            # 获取最近5天的数据
            df = ak.index_zh_a_hist(symbol=symbol, period="daily", 
                                   start_date=(datetime.now() - timedelta(days=5)).strftime("%Y%m%d"),
                                   end_date=datetime.now().strftime("%Y%m%d"))
            
            if df is None or df.empty:
                return None
                
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            return {
                'symbol': symbol,
                'name': self._get_index_name(symbol),
                'close': float(latest['收盘']),
                'open': float(latest['开盘']),
                'high': float(latest['最高']),
                'low': float(latest['最低']),
                'change': float(latest['收盘']) - float(prev['收盘']),
                'change_pct': round((float(latest['收盘']) - float(prev['收盘'])) / float(prev['收盘']) * 100, 2),
                'volume': int(latest['成交量']),
                'amount': float(latest['成交额']),
                'date': latest['日期']
            }
        except Exception as e:
            logger.error(f"获取指数 {symbol} 数据失败: {e}")
            return None
    
    def _get_index_name(self, symbol: str) -> str:
        """获取指数名称"""
        names = {
            "sh000001": "上证指数",
            "sz399001": "深证成指", 
            "sz399006": "创业板指",
            "sh000016": "上证50",
            "sh000300": "沪深300"
        }
        return names.get(symbol, symbol)
    
    def _calculate_summary(self, sh, sz, cy) -> Dict:
        """计算市场汇总数据"""
        indices_up = 0
        indices_down = 0
        
        for idx in [sh, sz, cy]:
            if idx and 'change_pct' in idx:
                if idx['change_pct'] > 0:
                    indices_up += 1
                elif idx['change_pct'] < 0:
                    indices_down += 1
                    
        return {
            'indices_up': indices_up,
            'indices_down': indices_down,
            'market_mood': '乐观' if indices_up > indices_down else '谨慎' if indices_up < indices_down else '平衡'
        }
    
    async def get_stock_fundamentals(self, symbol: str) -> Optional[Dict]:
        """获取个股基本面数据"""
        try:
            loop = asyncio.get_event_loop()
            
            # 财务指标
            finance = await loop.run_in_executor(
                None, ak.stock_financial_report_sina, symbol
            )
            
            # 估值指标
            valuation = await loop.run_in_executor(
                None, ak.stock_a_pe, symbol
            )
            
            return {
                'finance': finance.to_dict() if finance is not None else None,
                'valuation': valuation.to_dict() if valuation is not None else None
            }
        except Exception as e:
            logger.error(f"获取 {symbol} 基本面数据失败: {e}")
            return None
