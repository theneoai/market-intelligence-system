"""
Streamlit 可视化看板
交互式市场数据展示
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


class Dashboard:
    """可视化看板"""
    
    def __init__(self):
        self.title = "市场情报分析看板"
        
    def run(self):
        """运行看板"""
        st.set_page_config(
            page_title=self.title,
            page_icon="📊",
            layout="wide"
        )
        
        st.title(f"📊 {self.title}")
        st.markdown(f"*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        # 侧边栏
        with st.sidebar:
            st.header("控制面板")
            market = st.selectbox(
                "选择市场",
                ["全部", "A股", "黄金", "数字货币", "国债"]
            )
            
            st.divider()
            st.markdown("### 快速操作")
            if st.button("🔄 刷新数据"):
                st.rerun()
                
        # 主要内容区域
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="上证指数",
                value="3,200.00",
                delta="+1.2%"
            )
            
        with col2:
            st.metric(
                label="黄金价格",
                value="$2,050.00",
                delta="+0.5%"
            )
            
        with col3:
            st.metric(
                label="比特币",
                value="$65,000",
                delta="-2.1%"
            )
            
        with col4:
            st.metric(
                label="美债10Y",
                value="4.05%",
                delta="+0.04%"
            )
            
        # 情绪指标
        st.divider()
        st.subheader("🎭 市场情绪")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.progress(70, text="A股: 乐观")
        with col2:
            st.progress(65, text="黄金: 看涨")
        with col3:
            st.progress(45, text="数字货币: 中性")
        with col4:
            st.progress(30, text="国债: 谨慎")
            
        # 异常预警
        st.divider()
        st.subheader("🚨 异常预警")
        
        with st.expander("查看预警详情"):
            st.warning("⚠️ 上证指数暴涨 5.2% - 需关注")
            st.info("ℹ️ 收益率曲线倒挂 - 经济衰退风险")
            
        # 图表区域
        st.divider()
        st.subheader("📈 市场走势")
        
        # 创建示例图表
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('上证指数', '黄金价格', '比特币', '美债收益率'),
            vertical_spacing=0.1
        )
        
        # 示例数据
        import numpy as np
        x = np.arange(30)
        
        fig.add_trace(
            go.Scatter(x=x, y=np.cumsum(np.random.randn(30)) + 3200, name='上证指数'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=x, y=np.cumsum(np.random.randn(30) * 5) + 2050, name='黄金'),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=x, y=np.cumsum(np.random.randn(30) * 100) + 65000, name='BTC'),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=x, y=np.cumsum(np.random.randn(30) * 0.02) + 4.05, name='美债10Y'),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # 趋势预测
        st.divider()
        st.subheader("🔮 趋势预测")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info("**A股**\n方向: 上涨\n置信度: 70%\n建议: 适度参与")
        with col2:
            st.info("**黄金**\n方向: 看涨\n置信度: 65%\n建议: 关注美元")
        with col3:
            st.info("**数字货币**\n方向: 震荡\n置信度: 60%\n建议: 高抛低吸")
        with col4:
            st.info("**国债**\n方向: 收益率下行\n置信度: 75%\n建议: 配置价值")


if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
