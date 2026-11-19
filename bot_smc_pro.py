import os
import argparse
import pandas as pd
from smc_core import analyze_htf_smc
from strategy_mtf import run_mtf_strategy
from chart_plotter import plot_trade_setup

def load_and_clean_csv(filepath: str) -> pd.DataFrame:
    """
    Tự động nhận diện cột thời gian (time, timestamp, date, datetime) từ file CEX_*.csv
    """
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower() for c in df.columns]
    
    time_col = next((c for c in ['timestamp', 'time', 'date', 'datetime'] if c in df.columns), None)
    if time_col is None:
        raise ValueError(f"Không tìm thấy cột thời gian trong file {filepath}. Các cột hiện có: {df.columns.tolist()}")
        
    # Chuyển đổi thời gian (hỗ trợ cả dạng Unix timestamp giây/ms và dạng chuỗi ngày)
    if pd.api.types.is_numeric_dtype(df[time_col]):
        unit = 'ms' if df[time_col].iloc[0] > 1e11 else 's'
        df[time_col] = pd.to_datetime(df[time_col], unit=unit, utc=True)
    else:
        df[time_col] = pd.to_datetime(df[time_col], utc=True)
        
    df.set_index(time_col, inplace=True)
    df.sort_index(inplace=True)
    
    # Đảm bảo đủ cột volume nếu file CSV thiếu
    if 'volume' not in df.columns:
        df['volume'] = 1000.0
        
    return df[['open', 'high', 'low', 'close', 'volume']].dropna()

def generate_summary_markdown(trades_df: pd.DataFrame, symbol: str, config: dict, output_file: str = "backtest_summary.md"):
    total_trades = len(trades_df)
    md_lines = [
        f"# Báo Cáo Backtest SMC Pro MTF - {symbol}\n",
        "## 1. Cấu hình tham số hệ thống\n",
        f"- **Dữ liệu đầu vào:** `{config['data_file']}` (LTF: 1H -> HTF: 4H)",
        f"- **Cơ chế vào lệnh:** Limit tại Extreme OB/FVG sau CHoCH",
        f"- **Bộ lọc phiên Killzones (London/NY):** `{'BẬT' if config['use_killzones'] else 'TẮT'}`",
        f"- **Quản lý vốn Break-even (1.5R / BOS):** `{'BẬT' if config['use_breakeven'] else 'TẮT'}`\n"
    ]

    if total_trades == 0:
        md_lines.append("> **Kết quả:** Không có lệnh nào khớp trong giai đoạn dữ liệu này.\n")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        return

    wins = trades_df[trades_df['status'] == 'WIN']
    losses = trades_df[trades_df['status'] == 'LOSS']
    bes = trades_df[trades_df['status'] == 'BE']
    
    win_rate = (len(wins) / total_trades) * 100
    net_r = trades_df['pnl_r'].sum()
    avg_rr = trades_df['rr'].mean()

    md_lines.extend([
        "## 2. Thống kê hiệu suất tổng quan\n",
        "| Chỉ số | Giá trị |",
        "| :--- | :--- |",
        f"| **Tổng số lệnh đã khớp** | {total_trades} |",
        f"| **Thắng (WIN)** | {len(wins)} |",
        f"| **Hòa vốn (Break-Even)** | {len(bes)} |",
        f"| **Thua (LOSS)** | {len(losses)} |",
        f"| **Tỷ lệ thắng (Winrate)** | {win_rate:.2f}% |",
        f"| **Tổng lợi nhuận ròng (R)** | **{net_r:+.2f}R** |",
        f"| **Tỷ lệ R:R trung bình** | 1:{avg_rr:.2f} |\n",
        "## 3. Chi tiết lệnh & Biểu đồ phân tích Zone Shading\n"
    ])

    for _, row in trades_df.iterrows():
        tid = row['trade_id']
        md_lines.extend([
            f"### Lệnh #{tid} — {row['side']} | Kết quả: **{row['status']} ({row['pnl_r']:+.2f}R)**",
            f"- **Tín hiệu CHoCH:** `{row['signal_time']}` | **Khớp Limit:** `{row['entry_time']}` | **Đóng lệnh:** `{row['exit_time']}`",
            f"- **Entry Limit:** `{row['entry_price']}` | **SL:** `{row['sl']}` | **TP:** `{row['tp']}` | **RR:** `1:{row['rr']}`",
            f"- **Vùng OB 4H:** `{row['ob_bottom']} - {row['ob_top']}` (Cấu trúc 4H: `{row['htf_trend']}`)\n",
            f"#### Khung cấu trúc HTF 4H",
            f"![Trade {tid} 4H](charts/trade_{tid}_4h.png)\n",
            f"#### Khung vào lệnh Limit LTF",
            f"![Trade {tid} LTF](charts/trade_{tid}_ltf.png)\n",
            "---\n"
        ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

def main():
    parser = argparse.ArgumentParser(description="Chạy Backtest SMC Pro MTF")
    parser.add_argument("--data", type=str, default="data/CEX_BTCUSD_1h.csv", help="Đường dẫn file CSV dữ liệu")
    parser.add_argument("--killzones", action="store_true", help="Bật bộ lọc phiên London/NY")
    parser.add_argument("--no-killzones", dest="killzones", action="store_false", help="Tắt bộ lọc phiên")
    parser.set_defaults(killzones=True)
    parser.add_argument("--breakeven", action="store_true", help="Bật dời SL hòa vốn")
    parser.add_argument("--no-breakeven", dest="breakeven", action="store_false", help="Tắt dời SL hòa vốn")
    parser.set_defaults(breakeven=True)
    args = parser.parse_args()

    symbol = os.path.basename(args.data).split('.')[0]
    print(f"[*] Đang tải dữ liệu từ {args.data}...")
    df_ltf = load_and_clean_csv(args.data)

    # Tổng hợp dữ liệu lên khung 4H
    df_4h = df_ltf.resample('4h').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    print("[*] Đang phân tích cấu trúc SMC khung HTF 4H...")
    df_4h_analyzed = analyze_htf_smc(df_4h, swing_size=8, internal_size=3)

    print(f"[*] Đang mô phỏng chiến lược Limit MTF (Killzones={args.killzones}, BreakEven={args.breakeven})...")
    trades_df = run_mtf_strategy(
        df_4h_analyzed,
        df_ltf,
        risk_reward_min=3.0,
        use_killzones=args.killzones,
        use_breakeven=args.breakeven
    )

    trades_df.to_csv("backtest_results.csv", index=False)
    print(f"[*] Đã lưu {len(trades_df)} lệnh vào backtest_results.csv")

    print("[*] Đang vẽ biểu đồ Zone Shading cho từng lệnh...")
    for _, trade in trades_df.iterrows():
        plot_trade_setup(df_4h_analyzed, df_ltf, trade, output_dir="charts")

    config = {
        'data_file': args.data,
        'use_killzones': args.killzones,
        'use_breakeven': args.breakeven
    }
    generate_summary_markdown(trades_df, symbol=symbol, config=config, output_file="backtest_summary.md")
    print("[*] Hoàn tất! Kiểm tra backtest_summary.md và thư mục charts/.")

if __name__ == "__main__":
    main()
