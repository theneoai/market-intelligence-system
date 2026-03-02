"""
国债数据采集模块
使用 FRED API / 中国债券信息网
"""

import asyncio
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger


class BondCollector:
    """国债数据采集器"""
    
    def __init__(self):
        self.name = "国债"
        self.fred_url = "https://api.stlouisfed.org/fred"
        
    async def collect(self) -> Dict:
        """采集国债数据"""
        logger.info("📜 采集国债数据...")
        
        try:
            loop = asyncio.get_event_loop()
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'us_treasury': {},
                'china_bond': {},
                'yield_curve': {},
                'spread': {},
                'market_summary': {}
            }
            
            # 美国国债收益率 (使用 FRED API，需要 API Key)
            # 这里使用示例数据或备用数据源
            us_data = await loop.run_in_executor(
                None, self._get_us_treasury_yield
            )
            data['us_treasury'] = us_data
            
            # 中国国债收益率 (使用示例数据)
            china_data = await loop.run_in_executor(
                None, self._get_china_bond_yield
            )
            data['china_bond'] = china_data
            
            # 计算利差
            data['spread'] = self._calculate_spread(data)
            
            # 收益率曲线
            data['yield_curve'] = self._analyze_yield_curve(data)
            
            # 市场摘要
            data['market_summary'] = self._calculate_summary(data)
            
            us_10y = us_data.get('10y', {}).get('rate', 'N/A')
            logger.success(f"✅ 国债数据采集完成 - 美债10Y: {us_10y}%")
            return data
            
        except Exception as e:
            logger.error(f"❌ 国债数据采集失败: {e}")
            raise
    
    def _get_us_treasury_yield(self) -> Dict:
        """获取美国国债收益率"""
        try:
            # 使用模拟数据（实际生产需要 FRED API Key）
            # 访问 https://www.tradingview.com/chart/?symbol=TVC:US10Y 等获取实时数据
            
            # 这里使用简化的模拟数据
            return {
                '2y': {'rate': 4.25, 'change': 0.02, 'name': '2年期'},
                '5y': {'rate': 4.15, 'change': 0.03, 'name': '5年期'},
                '10y': {'rate': 4.05, 'change': 0.04, 'name': '10年期'},
                '30y': {'rate': 4.25, 'change': 0.05, 'name': '30年期'},
                'source': '模拟数据 (实际需 FRED API)',
                'note': '请配置 FRED API Key 获取实时数据'
            }
        except Exception as e:
            logger.error(f"获取美债数据失败: {e}")
            return {}
    
    def _get_china_bond_yield(self) -> Dict:
        """获取中国国债收益率"""
        try:
            # 中国国债收益率参考
            return {
                '1y': {'rate': 1.60, 'change': -0.01, 'name': '1年期'},
                '5y': {'rate': 2.10, 'change': -0.02, 'name': '5年期'},
                '10y': {'rate': 2.25, 'change': -0.03, 'name': '10年期'},
                '30y': {'rate': 2.45, 'change': -0.04, 'name': '30年期'},
                'source': '参考数据'
            }
        except Exception as e:
            logger.error(f"获取中债数据失败: {e}")
            return {}
    
    def _calculate_spread(self, data: Dict) -> Dict:
        """计算中美利差"""
        us_10y = data.get('us_treasury', {}).get('10y', {}).get('rate', 0)
        cn_10y = data.get('china_bond', {}).get('10y', {}).get('rate', 0)
        
        spread = us_10y - cn_10y
        
        return {
            'us_cn_10y_spread': round(spread, 2),
            'interpretation': 
                '美元强势' if spread > 1.5 else 
                '美元中性' if spread > 0.5 else 
                '美元弱势'
        }
    
    def _analyze_yield_curve(self, data: Dict) -> Dict:
        """分析收益率曲线"""
        us_data = data.get('us_treasury', {})
        
        if not us_data:
            return {'shape': '未知'}
            
        short_rate = us_data.get('2y', {}).get('rate', 0)
        long_rate = us_data.get('10y', {}).get('rate', 0)
        
        spread = long_rate - short_rate
        
        if spread > 0.5:
            shape = '陡峭 (正常)'
            signal = '经济扩张'
        elif spread > 0:
            shape = '平坦'
            signal = '经济放缓'
        else:
            shape = '倒挂 (警惕)'
            signal = '经济衰退风险'
            
        return {
            'shape': shape,
            '10y_2y_spread': round(spread, 2),
            'signal': signal
        }
    
    def _calculate_summary(self, data: Dict) -> Dict:
        """计算市场摘要"""
        us_10y = data.get('us_treasury', {}).get('10y', {}).get('rate', 0)
        spread = data.get('spread', {}).get('us_cn_10y_spread', 0)
        curve = data.get('yield_curve', {}).get('shape', '')
        
        return {
            'us_rate_level': '高位' if us_10y > 4 else '中位' if us_10y > 3 else '低位',
            'cn_rate_level': '高位' if data.get('china_bond', {}).get('10y', {}).get('rate', 0) > 3 else '低位',
            'curve_signal': '警惕' if '倒挂' in curve else '正常',
            'fx_implication': '美元偏强' if spread > 1 else '人民币偏强' if spread < 0.5 else '平衡'
        }
