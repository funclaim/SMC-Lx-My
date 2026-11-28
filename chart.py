from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import requests

from smc_core import (
    StructureEventType,
    TrendState,
    classify_range_position,
    compute_atr,
    detect_confirmed_swings,
    detect_eq_zones,
    find_origin_and_obs_backward,
    track_structure_and_liquidity,
)


def fetch_okx_candles(
    inst_id: str = "BTC-USDT",
    bar: str = "4H",
    limit: int = 200,
) -> pd.DataFrame:
    """
    Lấy dữ liệu nến OHLCV từ OKX (mới nhất đứng đầu -> đảo ngược để sắp xếp Trái -> Phải).
    """
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": inst_id, "bar": bar, "limit": str(limit)}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    if payload.get("code") != "0" or not payload.get("data"):
        raise RuntimeError(f"Lỗi dữ liệu OKX: {payload}")

    # OKX trả về: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
    raw = payload["data"][::-1]  # Đảo thành Trái -> Phải (cũ -> mới)
    df = pd.DataFrame(
        raw,
        columns=["ts", "open", "high", "low", "close", "vol", "vol_ccy", "vol_quote", "confirm"],
    )
    df["timestamp"] = pd.to_datetime(df["ts"].astype(np.int64), unit="ms", utc=True).dt.tz_convert("Asia/Ho_Chi_Minh")
    for col in ["open", "high", "low", "close", "vol"]:
        df[col] = df[col].astype(float)

    df = df.set_index("timestamp").drop(columns=["ts", "vol_ccy", "vol_quote", "confirm"])
    return df


def plot_candlesticks(ax: plt.Axes, df: pd.DataFrame) -> None:
    """Vẽ nến Nhật cơ bản theo chỉ số vị trí 0..N-1 (Trái -> Phải)."""
    opens = df["open"].to_numpy()
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    closes = df["close"].to_numpy()

    for i in range(len(df)):
        is_up = closes[i] >= opens[i]
        color = "#26a69a" if is_up else "#ef5350"
        # Râu nến
        ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1.0, zorder=2)
        # Thân nến
        body_low = min(opens[i], closes[i])
        body_high = max(opens[i], closes[i])
        height = max(body_high - body_low, (highs[i] - lows[i]) * 0.02)
        rect = Rectangle(
            (i - 0.32, body_low),
            width=0.64,
            height=height,
            facecolor=color,
            edgecolor=color,
            linewidth=0.8,
            zorder=3,
        )
        ax.add_patch(rect)


def draw_smc_chart(df: pd.DataFrame, k: int = 2, title: str = "BTC-USDT 4H - SMC/ICT") -> None:
    """Chạy smc_core và vẽ toàn bộ cấu trúc + vùng OB/OB_EX + BOS/CHOCH + IDM + EQH/EQL."""
    n = len(df)
    last_idx = n - 1
    atr = compute_atr(df, period=14)
    swings = detect_confirmed_swings(df, k=k)
    eq_zones = detect_eq_zones(df, swings, atr=atr, tol_atr_mult=0.1)
    events, idms, zones, trend = track_structure_and_liquidity(
        df, swings=swings, zones=eq_zones, atr=atr, min_idm_atr_mult=0.6
    )
    sw_type, range_pos = classify_range_position(df, current_idx=last_idx, window=50)

    # Truy vấn OB & OB_EX từ phải -> trái (tính từ nến cuối cùng)
    swing_indices = [s.idx for s in swings]
    bull_ob, bull_ob_ex = find_origin_and_obs_backward(df, last_idx, "BULL", swing_indices)
    bear_ob, bear_ob_ex = find_origin_and_obs_backward(df, last_idx, "BEAR", swing_indices)

    fig, ax = plt.subplots(figsize=(15, 8))
    plot_candlesticks(ax, df)

    # 1. Tô màu các vùng OB và OB_EX (kéo dài từ candle_idx tới nến cuối)
    ob_styles = [
        (bull_ob, "#00e676", 0.16, "--", "BULL OB"),
        (bull_ob_ex, "#00c853", 0.26, "-", "BULL OB_EX"),
        (bear_ob, "#ff5252", 0.16, "--", "BEAR OB"),
        (bear_ob_ex, "#d50000", 0.26, "-", "BEAR OB_EX"),
    ]
    for ob, color, alpha, ls, label in ob_styles:
        if ob is None:
            continue
        width = max(1, last_idx - ob.candle_idx)
        height = max(ob.top - ob.bottom, 1e-6)
        rect = Rectangle(
            (ob.candle_idx, ob.bottom),
            width=width,
            height=height,
            facecolor=color,
            alpha=alpha,
            edgecolor=color,
            linestyle=ls,
            linewidth=1.3,
            zorder=1,
        )
        ax.add_patch(rect)
        ax.text(
            ob.candle_idx + 0.5,
            ob.top,
            f"{label} (#{ob.candle_idx})",
            color=color,
            fontsize=8,
            fontweight="bold",
            va="bottom",
        )

    # 2. Vẽ nhãn Swing (HH, HL, LH, LL)
    for sw in swings:
        if not sw.label:
            continue
        is_high = sw.kind == "HIGH"
        y_pos = sw.price * (1.0015 if is_high else 0.9985)
        ax.text(
            sw.idx,
            y_pos,
            sw.label,
            color="#1565c0" if is_high else "#6a1b9a",
            fontsize=7.5,
            fontweight="bold",
            ha="center",
            va="bottom" if is_high else "top",
            zorder=4,
        )

    # 3. Vẽ đường & nhãn BOS / CHOCH
    for ev in events:
        is_bull = ev.event_type in (StructureEventType.BOS_BULL, StructureEventType.CHOCH_BULL)
        is_choch = ev.event_type in (StructureEventType.CHOCH_BULL, StructureEventType.CHOCH_BEAR)
        ev_color = "#2e7d32" if is_bull else "#c62828"
        ax.hlines(
            y=ev.broken_swing.price,
            xmin=ev.broken_swing.idx,
            xmax=ev.event_idx,
            colors=ev_color,
            linestyles=":" if is_choch else "-.",
            linewidth=1.4,
            zorder=4,
        )
        ax.text(
            ev.event_idx,
            ev.broken_swing.price,
            f" {ev.event_type.value}",
            color=ev_color,
            fontsize=8,
            fontweight="bold",
            va="bottom" if is_bull else "top",
            zorder=5,
        )

    # 4. Vẽ mốc IDM hợp lệ
    for idm in idms:
        end_x = idm.swept_idx if idm.swept and idm.swept_idx is not None else last_idx
        ax.hlines(
            y=idm.level,
            xmin=idm.formed_idx,
            xmax=end_x,
            colors="#ff8f00",
            linestyles="--",
            linewidth=1.1,
            zorder=4,
        )
        tag = "IDM (swept)" if idm.swept else "IDM"
        ax.text(idm.formed_idx, idm.level, f" {tag}", color="#ef6c00", fontsize=7.5, va="center", zorder=5)

    # 5. Vẽ EQH / EQL và đánh dấu LQ Sweep
    for z in zones:
        if z.kind not in ("EQH", "EQL"):
            continue
        end_x = z.swept_idx if z.swept and z.swept_idx is not None else last_idx
        ax.hlines(
            y=z.price,
            xmin=z.formed_idx,
            xmax=end_x,
            colors="#00838f",
            linestyles="-",
            linewidth=1.1,
            alpha=0.85,
            zorder=4,
        )
        lbl = f"{z.kind} [SWEEP]" if z.swept else z.kind
        ax.text(z.formed_idx, z.price, f" {lbl}", color="#006064", fontsize=7.5, va="center", zorder=5)

    # Trục thời gian gọn gàng
    step = max(1, n // 10)
    tick_positions = list(range(0, n, step))
    tick_labels = [df.index[idx].strftime("%m-%d %H:%M") for idx in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=25, ha="right", fontsize=8.5)

    ax.set_title(
        f"{title} | Trend: {trend.value} | RangePos(50): {range_pos:.2f} ({sw_type.value}) | Nến: {n}",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_ylabel("Price (USDT)")
    ax.grid(True, linestyle="--", alpha=0.25)
    plt.tight_layout()
    plt.savefig("btc_4h_smc.png", dpi=650)
    plt.show()


if __name__ == "__main__":
    df_btc_4h = fetch_okx_candles(inst_id="BTC-USDT", bar="4H", limit=200)
    draw_smc_chart(df_btc_4h, k=2, title="OKX BTC-USDT 4H")
