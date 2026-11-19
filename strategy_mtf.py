import pandas as pd
import numpy as np
from smc_core import detect_luxalgo_structure

def run_mtf_strategy(df_4h: pd.DataFrame, df_15m: pd.DataFrame, risk_reward_min: float = 3.0) -> pd.DataFrame:
    """
    Kết hợp khung 4H và 15m:
    - Chờ giá 15m chạm vùng Active OB của 4H
    - Xác nhận CHoCH trên 15m cùng hướng với 4H
    - Entry tại vùng CHoCH, SL = mép ngoài OB 4H +/- 0.3 * ATR_4H
    - TP = max(1:3 RR, thanh khoản đối diện BSL/SSL)
    """
    df_15m = detect_luxalgo_structure(df_15m, size=4)
    
    # Map dữ liệu 4H sang 15m (dùng shift(1) trên 4H để đảm bảo nến 4H đã đóng cửa hoàn toàn)
    df_4h_shifted = df_4h[['htf_trend', 'wyckoff_phase', 'active_ob']].shift(1)
    df_merged = pd.merge_asof(
        df_15m.sort_index(),
        df_4h_shifted.sort_index(),
        left_index=True,
        right_index=True,
        direction='backward'
    )
    
    trades = []
    in_position = False
    current_trade = None
    
    last_ltf_high = np.nan
    last_ltf_low = np.nan
    in_htf_ob = False
    
    for i in range(len(df_merged)):
        row = df_merged.iloc[i]
        timestamp = df_merged.index[i]
        
        # Cập nhật đỉnh/đáy LTF 15m
        if not np.isnan(row['confirmed_high_price']):
            last_ltf_high = row['confirmed_high_price']
        if not np.isnan(row['confirmed_low_price']):
            last_ltf_low = row['confirmed_low_price']
            
        # Quản lý lệnh đang mở
        if in_position and current_trade is not None:
            if current_trade['side'] == 'LONG':
                if row['low'] <= current_trade['sl']:
                    current_trade['exit_time'] = timestamp
                    current_trade['exit_price'] = current_trade['sl']
                    current_trade['pnl_r'] = -1.0
                    current_trade['status'] = 'LOSS'
                    trades.append(current_trade)
                    in_position = False
                elif row['high'] >= current_trade['tp']:
                    current_trade['exit_time'] = timestamp
                    current_trade['exit_price'] = current_trade['tp']
                    current_trade['pnl_r'] = current_trade['rr']
                    current_trade['status'] = 'WIN'
                    trades.append(current_trade)
                    in_position = False
            elif current_trade['side'] == 'SHORT':
                if row['high'] >= current_trade['sl']:
                    current_trade['exit_time'] = timestamp
                    current_trade['exit_price'] = current_trade['sl']
                    current_trade['pnl_r'] = -1.0
                    current_trade['status'] = 'LOSS'
                    trades.append(current_trade)
                    in_position = False
                elif row['low'] <= current_trade['tp']:
                    current_trade['exit_time'] = timestamp
                    current_trade['exit_price'] = current_trade['tp']
                    current_trade['pnl_r'] = current_trade['rr']
                    current_trade['status'] = 'WIN'
                    trades.append(current_trade)
                    in_position = False
            continue

        # Kiểm tra điều kiện tìm lệnh mới
        ob = row['active_ob']
        if ob is None or not isinstance(ob, dict):
            in_htf_ob = False
            continue
            
        # 4. Kiểm tra giá đã chạm vào vùng OB 4H chưa
        if ob['type'] == 'BULL_OB':
            if row['low'] <= ob['top'] and row['high'] >= ob['bottom']:
                in_htf_ob = True
                
            # LTF 1. Xác nhận CHoCH tăng trên 15m (giá đóng cửa phá qua đỉnh LTF gần nhất)
            if in_htf_ob and not np.isnan(last_ltf_high) and row['close'] > last_ltf_high:
                entry = row['close']
                sl = ob['bottom'] - (0.3 * ob['atr'])
                risk = entry - sl
                if risk <= 0:
                    continue
                    
                # TP tối thiểu 1:3 hoặc đỉnh thanh khoản đối diện
                tp_min = entry + (risk * risk_reward_min)
                tp = max(tp_min, ob['tp_target'])
                rr = (tp - entry) / risk
                
                current_trade = {
                    'trade_id': len(trades) + 1,
                    'side': 'LONG',
                    'entry_time': timestamp,
                    'entry_price': round(entry, 4),
                    'sl': round(sl, 4),
                    'tp': round(tp, 4),
                    'rr': round(rr, 2),
                    'ob_top': ob['top'],
                    'ob_bottom': ob['bottom'],
                    'htf_trend': row['htf_trend']
                }
                in_position = True
                in_htf_ob = False

        elif ob['type'] == 'BEAR_OB':
            if row['high'] >= ob['bottom'] and row['low'] <= ob['top']:
                in_htf_ob = True
                
            # LTF 1. Xác nhận CHoCH giảm trên 15m (giá đóng cửa phá qua đáy LTF gần nhất)
            if in_htf_ob and not np.isnan(last_ltf_low) and row['close'] < last_ltf_low:
                entry = row['close']
                sl = ob['top'] + (0.3 * ob['atr'])
                risk = sl - entry
                if risk <= 0:
                    continue
                    
                tp_min = entry - (risk * risk_reward_min)
                tp = min(tp_min, ob['tp_target'])
                rr = (entry - tp) / risk
                
                current_trade = {
                    'trade_id': len(trades) + 1,
                    'side': 'SHORT',
                    'entry_time': timestamp,
                    'entry_price': round(entry, 4),
                    'sl': round(sl, 4),
                    'tp': round(tp, 4),
                    'rr': round(rr, 2),
                    'ob_top': ob['top'],
                    'ob_bottom': ob['bottom'],
                    'htf_trend': row['htf_trend']
                }
                in_position = True
                in_htf_ob = False

    return pd.DataFrame(trades)
