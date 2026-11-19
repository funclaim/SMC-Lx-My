import os
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

def plot_trade_setup(df_4h: pd.DataFrame, df_ltf: pd.DataFrame, trade: pd.Series, output_dir: str = "charts"):
    os.makedirs(output_dir, exist_ok=True)
    tid = trade['trade_id']
    entry_time = pd.to_datetime(trade['entry_time'])
    exit_time = pd.to_datetime(trade['exit_time'])
    
    # 1. BIỂU ĐỒ HTF 4H (Tô bóng vùng OB 4H và FVG 4H)
    sub_4h = df_4h.loc[entry_time - pd.Timedelta(days=10) : exit_time + pd.Timedelta(days=3)].copy()
    if len(sub_4h) > 5:
        path_4h = os.path.join(output_dir, f"trade_{tid}_4h.png")
        fig, axes = mpf.plot(
            sub_4h,
            type='candle',
            style='charles',
            title=f"Trade #{tid} ({trade['side']}) - HTF 4H Zones | Status: {trade['status']} ({trade['pnl_r']}R)",
            volume=True,
            returnfig=True
        )
        ax_main = axes[0]
        # Tô bóng vùng OB 4H (Màu xanh dương nhạt)
        ax_main.axhspan(trade['ob_bottom'], trade['ob_top'], color='#2962FF', alpha=0.18, label='HTF 4H OB')
        # Tô bóng vùng FVG 4H (Màu vàng cam nhạt)
        if trade['fvg_top'] != trade['ob_top']:
            ax_main.axhspan(trade['fvg_bottom'], trade['fvg_top'], color='#FF9800', alpha=0.15, label='HTF 4H FVG')
        # Đường TP đối diện
        ax_main.axhline(trade['tp'], color='#00C853', linestyle='--', linewidth=1.2, label='TP Target')
        ax_main.legend(loc='upper left', fontsize=8)
        
        fig.savefig(path_4h, dpi=130, bbox_inches='tight')
        plt.close(fig)

    # 2. BIỂU ĐỒ LTF (Tô bóng vùng Limit OB LTF, vùng Risk/Reward và đánh dấu Entry/Exit)
    sub_ltf = df_ltf.loc[entry_time - pd.Timedelta(hours=24) : exit_time + pd.Timedelta(hours=8)].copy()
    if len(sub_ltf) > 5:
        path_ltf = os.path.join(output_dir, f"trade_{tid}_ltf.png")
        
        entry_marker = [trade['entry_price'] if idx == entry_time else float('nan') for idx in sub_ltf.index]
        exit_marker = [trade['exit_price'] if idx == exit_time else float('nan') for idx in sub_ltf.index]
        
        apds = [
            mpf.make_addplot(entry_marker, type='scatter', markersize=110, marker='^' if trade['side']=='LONG' else 'v', color='#2962FF'),
            mpf.make_addplot(exit_marker, type='scatter', markersize=110, marker='X', color='#00C853' if trade['status']=='WIN' else '#D50000')
        ]
        
        fig, axes = mpf.plot(
            sub_ltf,
            type='candle',
            style='charles',
            title=f"Trade #{tid} ({trade['side']}) - LTF Limit Entry & Zone Shading (RR 1:{trade['rr']})",
            addplot=apds,
            volume=True,
            returnfig=True
        )
        ax_main = axes[0]
        
        # Tô bóng vùng Extreme OB LTF nơi đặt Limit
        ax_main.axhspan(trade['ltf_ob_bottom'], trade['ltf_ob_top'], color='#AA00FF', alpha=0.20, label='LTF Limit OB Zone')
        # Tô bóng vùng Stop Loss (Màu đỏ nhạt)
        ax_main.axhspan(min(trade['entry_price'], trade['sl']), max(trade['entry_price'], trade['sl']), color='#D50000', alpha=0.10, label='Risk Zone (SL)')
        # Tô bóng vùng Take Profit (Màu xanh lá nhạt)
        ax_main.axhspan(min(trade['entry_price'], trade['tp']), max(trade['entry_price'], trade['tp']), color='#00C853', alpha=0.10, label='Reward Zone (TP)')
        
        ax_main.axhline(trade['entry_price'], color='#2962FF', linestyle='-', linewidth=1.0)
        ax_main.axhline(trade['sl'], color='#D50000', linestyle='--', linewidth=1.0)
        ax_main.axhline(trade['tp'], color='#00C853', linestyle='--', linewidth=1.0)
        ax_main.legend(loc='upper left', fontsize=8)
        
        fig.savefig(path_ltf, dpi=130, bbox_inches='tight')
        plt.close(fig)
