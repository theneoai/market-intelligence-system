# 市场情报分析系统 (Market Intelligence System)

## 系统架构

```
市场情报系统/
├── 📊 数据采集层 (Data Collection)
│   ├── A股数据采集
│   ├── 黄金期货数据采集
│   ├── 数字货币数据采集
│   └── 国债数据采集
│
├── 🧠 分析引擎 (Analysis Engine)
│   ├── 市场情绪分析
│   ├── 价格异常检测
│   ├── 趋势预测模型
│   └── 相关性分析
│
├── 🚨 监控预警 (Monitoring & Alerts)
│   ├── 实时监控
│   ├── 异常预警
│   └── 趋势变化通知
│
└── 📈 可视化展示 (Visualization)
    ├── 实时看板
    ├── 分析报告
    └── 预测图表
```

## 功能模块

### 1. A股市场分析
- 个股基本面分析 (使用现有 skill)
- 行业板块轮动监控
- 北向资金流向追踪
- 龙虎榜数据分析
- 融资融券余额监控

### 2. 黄金期货分析
- COMEX/LME 黄金期货价格
- 美元指数关联分析
- 黄金ETF持仓变化
- 央行购金数据

### 3. 数字货币分析
- BTC/ETH 等主流币种价格
- 交易所资金流动
- 链上数据分析
- 恐慌贪婪指数

### 4. 国债分析
- 中美利差监控
- 国债收益率曲线
- 利率期限结构
- 通胀预期分析

### 5. 市场情绪分析
- 新闻情绪 NLP 分析
- 社交媒体情绪
- 搜索指数趋势
- 波动率指数 (VIX)

### 6. 异常检测
- 价格波动异常
- 成交量异常
- 相关性断裂
- 技术指标背离

### 7. 趋势预测
- 机器学习模型
- 时间序列分析
- 多因子模型
- 市场情绪加权

## 技术栈

- **语言**: Python 3.12
- **数据采集**: tushare, yfinance, ccxt
- **分析**: pandas, numpy, scipy, scikit-learn
- **可视化**: matplotlib, plotly, streamlit
- **数据库**: sqlite (本地), PostgreSQL (可选)
- **API**: FastAPI (数据服务)

## 数据源

| 市场 | 数据源 |
|------|--------|
| A股 | Tushare, AkShare |
| 黄金 | Yahoo Finance, 金十数据 |
| 数字货币 | Binance API, CoinGecko |
| 国债 | 中国债券信息网, FRED |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API Key:

```bash
cp .env.example .env
```

编辑 `.env` 文件:
```
TUSHARE_TOKEN=your_tushare_token_here
BINANCE_API_KEY=your_binance_api_key
FRED_API_KEY=your_fred_api_key
```

### 3. 快速测试

验证所有模块正常工作:

```bash
python test_modules.py
```

### 4. 运行系统

**单次运行模式:**
```bash
python main.py --mode once
```

**持续监控模式:**
```bash
python main.py --mode continuous
```

**启动可视化看板:**
```bash
python main.py --mode dashboard
```

## 项目结构

```
market-intelligence-system/
├── config/
│   └── config.yaml          # 系统配置
├── src/
│   ├── data_collection/     # 数据采集模块
│   │   ├── a_share_collector.py
│   │   ├── gold_collector.py
│   │   ├── crypto_collector.py
│   │   └── bond_collector.py
│   ├── analysis/            # 分析引擎
│   │   ├── sentiment_analyzer.py
│   │   ├── anomaly_detector.py
│   │   └── trend_predictor.py
│   ├── monitoring/          # 实时监控
│   │   └── real_time_monitor.py
│   └── visualization/       # 可视化
│       └── dashboard.py
├── data/                    # 数据存储
├── logs/                    # 日志文件
├── main.py                  # 主入口
└── test_modules.py          # 测试脚本
```

## 使用 opencode 开发

opencode 将帮助我们:
1. 生成项目代码结构
2. 编写核心分析算法
3. 实现数据采集模块
4. 创建可视化看板
5. 编写测试用例
