import os
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

def plot_trade_setup(df_4h: pd.DataFrame, df_15m: pd.DataFrame, trade: pd.Series, output_dir: str = "charts"):
    os.makedirs(output_dir, exist_ok=True)
    tid = trade['trade_id']
    entry_time = pd.to_datetime(trade['entry_time'])
    exit_time = pd.to_datetime(trade['exit_time'])
    
    # 1. Vẽ khung HTF 4H (lấy 40 nến trước entry và 10 nến sau exit)
    sub_4h = df_4h.loc[entry_time - pd.Timedelta(days=7) : exit_time + pd.Timedelta(days=2)].copy()
    if len(sub_4h) > 5:
        path_4h = os.path.join(output_dir, f"trade_{tid}_4h.png")
        hlines_4h = dict(
            hlines=[trade['ob_top'], trade['ob_bottom'], trade['tp']],
            colors=['blue', 'blue', 'green'],
            linestyle=['--', '--', '-'],
            linewidths=[1, 1, 1.5]
        )
        mpf.plot(
            sub_4h,
            type='candle',
            style='charles',
            title=f"Trade #{tid} ({trade['side']}) - HTF 4H Context | Result: {trade['status']}",
            hlines=hlines_4h,
            volume=True,
            savefig=dict(fname=path_4h, dpi=120, bbox_inches='tight')
        )
        plt.close('all')

    # 2. Vẽ khung LTF 15m (lấy 30 nến trước entry đến 10 nến sau exit)
    sub_15m = df_15m.loc[entry_time - pd.Timedelta(hours=8) : exit_time + pd.Timedelta(hours=3)].copy()
    if len(sub_15m) > 5:
        path_15m = os.path.join(output_dir, f"trade_{tid}_15m.png")
        
        # Đánh dấu điểm Entry và Exit trên biểu đồ 15m
        entry_marker = [trade['entry_price'] if idx == entry_time else float('nan') for idx in sub_15m.index]
        exit_marker = [trade['exit_price'] if idx == exit_time else float('nan') for idx in sub_15m.index]
        
        apds = [
            mpf.make_addplot(entry_marker, type='scatter', markersize=100, marker='^' if trade['side']=='LONG' else 'v', color='blue'),
            mpf.make_addplot(exit_marker, type='scatter', markersize=100, marker='X', color='green' if trade['status']=='WIN' else 'red')
        ]
        
        hlines_15m = dict(
            hlines=[trade['entry_price'], trade['sl'], trade['tp']],
            colors=['blue', 'red', 'green'],
            linestyle=['-', '--', '--'],
            linewidths=[1.2, 1.2, 1.2]
        )
        mpf.plot(
            sub_15m,
            type='candle',
            style='charles',
            title=f"Trade #{tid} ({trade['side']}) - LTF 15m Entry/SL/TP (RR: 1:{trade['rr']})",
            hlines=hlines_15m,
            addplot=apds,
            volume=True,
            savefig=dict(fname=path_15m, dpi=120, bbox_inches='tight')
        )
        plt.close('all')
