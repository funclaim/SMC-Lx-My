import pandas as pd
from smc_core import analyze_htf_smc
from strategy_mtf import run_mtf_strategy
from chart_plotter import plot_trade_setup

def generate_summary_markdown(trades_df: pd.DataFrame, output_file: str = "backtest_summary.md"):
    total_trades = len(trades_df)
    if total_trades == 0:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Báo cáo Backtest SMC MTF (4H -> 15m)\n\nKhông có lệnh nào thỏa mãn điều kiện vào lệnh.\n")
        return

    wins = trades_df[trades_df['status'] == 'WIN']
    losses = trades_df[trades_df['status'] == 'LOSS']
    win_rate = (len(wins) / total_trades) * 100
    net_r = trades_df['pnl_r'].sum()
    avg_rr = trades_df['rr'].mean()

    md_lines = [
        "# Báo Cáo Tổng Hợp Backtest SMC Đa Khung Thời Gian (4H -> 15m)\n",
        "## 1. Thống kê hiệu suất tổng quan\n",
        f"- **Tổng số lệnh:** {total_trades}",
        f"- **Số lệnh thắng (WIN):** {len(wins)}",
        f"- **Số lệnh thua (LOSS):** {len(losses)}",
        f"- **Tỷ lệ thắng (Winrate):** {win_rate:.2f}%",
        f"- **Tổng lợi nhuận ròng (R):** {net_r:.2f}R",
        f"- **Tỷ lệ Risk:Reward trung bình:** 1:{avg_rr:.2f}\n",
        "## 2. Chi tiết từng lệnh & Hình ảnh phân tích\n"
    ]

    for _, row in trades_df.iterrows():
        tid = row['trade_id']
        md_lines.extend([
            f"### Lệnh #{tid} - {row['side']} ({row['status']})",
            f"- **Thời gian vào lệnh:** {row['entry_time']} | **Thoát lệnh:** {row['exit_time']}",
            f"- **Entry:** `{row['entry_price']}` | **SL:** `{row['sl']}` | **TP:** `{row['tp']}` | **Kết quả:** `{row['pnl_r']}R`",
            f"- **Vùng OB 4H:** `{row['ob_bottom']} - {row['ob_top']}` (Cấu trúc 4H: {row['htf_trend']})\n",
            f"#### Biểu đồ khung HTF 4H",
            f"![Trade {tid} 4H](charts/trade_{tid}_4h.png)\n",
            f"#### Biểu đồ điểm vào lệnh LTF 15m",
            f"![Trade {tid} 15m](charts/trade_{tid}_15m.png)\n",
            "---\n"
        ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

def main():
    # Đọc dữ liệu 15m (cột yêu cầu: timestamp, open, high, low, close, volume)
    df_15m = pd.read_csv("data/btcusdt_15m.csv", parse_dates=['timestamp'], index_col='timestamp')
    
    # Resample từ 15m lên 4H để đồng bộ dữ liệu chính xác
    df_4h = df_15m.resample('4h').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    print("1. Đang phân tích cấu trúc SMC khung 4H...")
    df_4h_analyzed = analyze_htf_smc(df_4h, swing_size=10, internal_size=3)

    print("2. Đang chạy mô phỏng vào lệnh khung 15m...")
    trades_df = run_mtf_strategy(df_4h_analyzed, df_15m, risk_reward_min=3.0)

    # Xuất kết quả CSV
    trades_df.to_csv("backtest_results.csv", index=False)
    print(f"3. Đã lưu {len(trades_df)} lệnh vào backtest_results.csv")

    # Vẽ biểu đồ cho từng lệnh
    print("4. Đang xuất hình ảnh biểu đồ 4H và 15m...")
    for _, trade in trades_df.iterrows():
        plot_trade_setup(df_4h_analyzed, df_15m, trade, output_dir="charts")

    # Xuất báo cáo Markdown
    generate_summary_markdown(trades_df, output_file="backtest_summary.md")
    print("5. Hoàn tất! Kiểm tra file backtest_summary.md để xem chi tiết.")

if __name__ == "__main__":
    main()
