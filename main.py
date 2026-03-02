#!/usr/bin/env python3
"""
市场情报分析系统 - 主入口
Market Intelligence System Main Entry

功能：
- 多市场数据采集 (A股/黄金/数字货币/国债)
- 情绪分析 & 异常检测 & 趋势预测
- 实时监控 & 预警
- 可视化看板
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from loguru import logger

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_collection.a_share_collector import AShareCollector
from data_collection.gold_collector import GoldCollector
from data_collection.crypto_collector import CryptoCollector
from data_collection.bond_collector import BondCollector
from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.anomaly_detector import AnomalyDetector
from analysis.trend_predictor import TrendPredictor
from monitoring.real_time_monitor import RealTimeMonitor
from visualization.dashboard import Dashboard


class MarketIntelligenceSystem:
    """市场情报分析系统主类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化系统"""
        self.config_path = config_path
        self.collectors = {}
        self.analyzers = {}
        self.monitor = None
        self.dashboard = None
        
        logger.info("🚀 市场情报分析系统初始化中...")
        self._init_collectors()
        self._init_analyzers()
        
    def _init_collectors(self):
        """初始化数据采集器"""
        logger.info("📊 初始化数据采集模块...")
        
        self.collectors = {
            'a_share': AShareCollector(),
            'gold': GoldCollector(),
            'crypto': CryptoCollector(),
            'bond': BondCollector()
        }
        
    def _init_analyzers(self):
        """初始化分析引擎"""
        logger.info("🧠 初始化分析引擎...")
        
        self.analyzers = {
            'sentiment': SentimentAnalyzer(),
            'anomaly': AnomalyDetector(),
            'trend': TrendPredictor()
        }
        
    async def collect_all_data(self):
        """采集所有市场数据"""
        logger.info("📥 开始采集全市场数据...")
        
        tasks = []
        for name, collector in self.collectors.items():
            task = asyncio.create_task(
                self._collect_with_retry(name, collector),
                name=f"collect_{name}"
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for name, result in zip(self.collectors.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"❌ {name} 数据采集失败: {result}")
                data[name] = None
            else:
                logger.success(f"✅ {name} 数据采集完成")
                data[name] = result
                
        return data
    
    async def _collect_with_retry(self, name: str, collector, max_retry=3):
        """带重试的数据采集"""
        for attempt in range(max_retry):
            try:
                return await collector.collect()
            except Exception as e:
                if attempt == max_retry - 1:
                    raise
                logger.warning(f"⚠️ {name} 采集失败，第{attempt+1}次重试...")
                await asyncio.sleep(2 ** attempt)
                
    async def analyze_data(self, data: dict):
        """分析数据"""
        logger.info("🔍 开始数据分析...")
        
        analysis_results = {}
        
        # 情绪分析
        for market, market_data in data.items():
            if market_data is not None:
                sentiment = await self.analyzers['sentiment'].analyze(market, market_data)
                analysis_results[f"{market}_sentiment"] = sentiment
                
        # 异常检测
        for market, market_data in data.items():
            if market_data is not None:
                anomalies = await self.analyzers['anomaly'].detect(market, market_data)
                analysis_results[f"{market}_anomalies"] = anomalies
                
        # 趋势预测
        for market, market_data in data.items():
            if market_data is not None:
                trend = await self.analyzers['trend'].predict(market, market_data)
                analysis_results[f"{market}_trend"] = trend
                
        return analysis_results
    
    def start_monitoring(self):
        """启动实时监控"""
        logger.info("👁️ 启动实时监控系统...")
        self.monitor = RealTimeMonitor(self.collectors, self.analyzers)
        self.monitor.start()
        
    def start_dashboard(self):
        """启动可视化看板"""
        logger.info("📈 启动可视化看板...")
        self.dashboard = Dashboard()
        self.dashboard.run()
        
    async def run_once(self):
        """运行一次完整流程"""
        logger.info("=" * 50)
        logger.info("🎯 市场情报分析系统 - 单次运行模式")
        logger.info("=" * 50)
        
        # 1. 采集数据
        data = await self.collect_all_data()
        
        # 2. 分析数据
        analysis = await self.analyze_data(data)
        
        # 3. 生成报告
        self._generate_report(data, analysis)
        
        return data, analysis
    
    def _generate_report(self, data: dict, analysis: dict):
        """生成分析报告"""
        logger.info("📝 生成分析报告...")
        
        report = []
        report.append("\n" + "=" * 60)
        report.append("📊 市场情报分析报告")
        report.append("=" * 60)
        
        for market in ['a_share', 'gold', 'crypto', 'bond']:
            report.append(f"\n【{market.upper()}】")
            
            if f"{market}_sentiment" in analysis:
                sentiment = analysis[f"{market}_sentiment"]
                report.append(f"  情绪: {sentiment.get('score', 'N/A')}")
                
            if f"{market}_trend" in analysis:
                trend = analysis[f"{market}_trend"]
                report.append(f"  趋势: {trend.get('direction', 'N/A')}")
                
            if f"{market}_anomalies" in analysis:
                anomalies = analysis[f"{market}_anomalies"]
                if anomalies:
                    report.append(f"  ⚠️ 异常: {len(anomalies)} 个")
                    
        report.append("\n" + "=" * 60)
        
        report_text = "\n".join(report)
        logger.info(report_text)
        
        # 保存报告
        report_path = Path("data/reports")
        report_path.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"report_{timestamp}.txt"
        
        report_file.write_text(report_text, encoding='utf-8')
        logger.info(f"📄 报告已保存: {report_file}")
        
    def run_continuous(self):
        """持续运行模式"""
        logger.info("🔄 启动持续监控模式...")
        self.start_monitoring()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="市场情报分析系统")
    parser.add_argument(
        "--mode", 
        choices=['once', 'continuous', 'dashboard'],
        default='once',
        help='运行模式: once=单次, continuous=持续监控, dashboard=只看板'
    )
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = MarketIntelligenceSystem(config_path=args.config)
    
    if args.mode == 'once':
        await system.run_once()
    elif args.mode == 'continuous':
        system.run_continuous()
    elif args.mode == 'dashboard':
        system.start_dashboard()


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/market_intelligence.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG"
    )
    
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # 运行主程序
    asyncio.run(main())
