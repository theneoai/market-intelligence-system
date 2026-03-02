#!/usr/bin/env python3
"""
市场情报分析系统 - 快速测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.anomaly_detector import AnomalyDetector
from analysis.trend_predictor import TrendPredictor


async def test_analyzers():
    """测试分析引擎"""
    print("=" * 50)
    print("🧪 市场情报分析系统 - 模块测试")
    print("=" * 50)
    
    # 模拟数据
    mock_data = {
        'indices': {
            'shanghai': {'change_pct': 2.5, 'close': 3050},
            'shenzhen': {'change_pct': 1.8, 'close': 9800}
        },
        'market_summary': {'market_mood': '乐观'}
    }
    
    # 1. 测试情绪分析
    print("\n1️⃣ 情绪分析模块")
    sentiment = SentimentAnalyzer()
    result = await sentiment.analyze('a_share', mock_data)
    print(f"   ✅ 情绪得分: {result['score']}")
    print(f"   ✅ 情绪状态: {result['mood']}")
    
    # 2. 测试异常检测
    print("\n2️⃣ 异常检测模块")
    detector = AnomalyDetector()
    anomalies = await detector.detect('a_share', mock_data)
    print(f"   ✅ 发现异常: {len(anomalies)} 个")
    for a in anomalies:
        print(f"      - {a['description']}")
    
    # 3. 测试趋势预测
    print("\n3️⃣ 趋势预测模块")
    predictor = TrendPredictor()
    trend = await predictor.predict('a_share', mock_data)
    print(f"   ✅ 趋势方向: {trend.get('direction', '未知')}")
    print(f"   ✅ 置信度: {trend.get('confidence', 0):.2f}")
    
    print("\n" + "=" * 50)
    print("✅ 所有模块测试通过!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_analyzers())
