#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上证指数日K线图生成脚本
"""

import akshare as ak
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import os
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def generate_kline_chart(output_path, days=60):
    """
    生成上证指数日K线图
    
    Args:
        output_path: 输出图片路径
        days: 显示的交易日数量，默认60个交易日
    """
    try:
        print(f"正在获取上证指数数据...")
        
        # 获取上证指数日K线数据
        # 使用stock_zh_index_hist_csindex接口
        df = ak.stock_zh_index_hist_csindex(symbol='000001')
        
        # 打印列名调试
        print(f"数据列名: {df.columns.tolist()}")
        
        # 重命名列（中文名称）
        df = df.rename(columns={'日期': 'date', '开盘': 'open', '收盘': 'close', 
                                '最高': 'high', '最低': 'low', '成交量': 'volume'})
        
        # 按日期排序
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 取最近N个交易日
        df = df.tail(days)
        
        print(f"获取到 {len(df)} 个交易日数据")
        print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]},
                                        facecolor='white')
        
        # 设置标题
        fig.suptitle(f'上证指数日K线图\n{df["date"].min().strftime("%Y-%m-%d")} 至 {df["date"].max().strftime("%Y-%m-%d")}', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # 绘制K线图
        for idx, row in df.iterrows():
            date = row['date']
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']
            
            # 判断涨跌
            if close_price >= open_price:
                color = '#ff4757'  # 红色上涨
            else:
                color = '#2ed573'  # 绿色下跌
            
            # 绘制实体
            ax1.bar(date, close_price - open_price, bottom=open_price, 
                   width=0.6, color=color, edgecolor=color)
            
            # 绘制上下影线
            ax1.plot([date, date], [low_price, high_price], 
                    color=color, linewidth=1)
        
        # 设置K线图样式
        ax1.set_ylabel('指数点位', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_facecolor('#fafafa')
        
        # 添加均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        ax1.plot(df['date'], df['ma5'], label='MA5', color='#ffa502', linewidth=1.5, alpha=0.8)
        ax1.plot(df['date'], df['ma10'], label='MA10', color='#3742fa', linewidth=1.5, alpha=0.8)
        ax1.plot(df['date'], df['ma20'], label='MA20', color='#2f3542', linewidth=1.5, alpha=0.8)
        
        ax1.legend(loc='upper left', fontsize=10)
        
        # 标注最新价格
        latest = df.iloc[-1]
        ax1.axhline(y=latest['close'], color='#ff6b81', linestyle='--', alpha=0.5, linewidth=1)
        ax1.text(df['date'].iloc[-1], latest['close'], f" {latest['close']:.2f}", 
                fontsize=11, fontweight='bold', color='#ff6b81', va='center')
        
        # 绘制成交量
        colors = ['#ff4757' if df.iloc[i]['close'] >= df.iloc[i]['open'] else '#2ed573' 
                  for i in range(len(df))]
        ax2.bar(df['date'], df['volume'] / 1e8, width=0.6, color=colors, alpha=0.7)
        
        ax2.set_ylabel('成交量（亿）', fontsize=12, fontweight='bold')
        ax2.set_xlabel('日期', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_facecolor('#fafafa')
        
        # 设置日期格式
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 添加数据来源
        fig.text(0.99, 0.01, '数据来源: akshare', fontsize=9, 
                color='gray', ha='right', va='bottom', alpha=0.7)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        print(f"K线图已保存至: {output_path}")
        
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"生成K线图时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import pandas as pd
    
    # 从命令行参数获取输出路径
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "kline.png"
    
    # 生成K线图
    success = generate_kline_chart(output_path, days=60)
    
    if success:
        print("K线图生成成功！")
        sys.exit(0)
    else:
        print("K线图生成失败！")
        sys.exit(1)
