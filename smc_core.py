import numpy as np
import pandas as pd

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def detect_luxalgo_structure(df: pd.DataFrame, size: int = 5) -> pd.DataFrame:
    """
    Chuyển đổi chính xác hàm leg(size) và getCurrentStructure của LuxAlgo.
    Lưu ý: Pivot tại index [i - size] chỉ được xác nhận tại thời điểm [i] để tránh repaint.
    """
    df = df.copy()
    n = len(df)
    leg = np.zeros(n, dtype=int)
    
    highs = df['high'].values
    lows = df['low'].values
    
    # Tính toán leg(size) giống Pine Script:
    # newLegHigh = high[size] > ta.highest(size)
    # newLegLow  = low[size]  < ta.lowest(size)
    for i in range(size, n):
        window_high = np.max(highs[i - size + 1 : i + 1])
        window_low = np.min(lows[i - size + 1 : i + 1])
        
        if highs[i - size] > window_high:
            leg[i] = 0  # Bearish leg bắt đầu (tạo đỉnh)
        elif lows[i - size] < window_low:
            leg[i] = 1  # Bullish leg bắt đầu (tạo đáy)
        else:
            leg[i] = leg[i - 1]
            
    df['leg'] = leg
    df['new_pivot'] = df['leg'] != df['leg'].shift(1)
    df['pivot_low_confirmed'] = df['new_pivot'] & (df['leg'] == 1)
    df['pivot_high_confirmed'] = df['new_pivot'] & (df['leg'] == 0)
    
    # Giá trị thực tế của đỉnh/đáy nằm ở nến [i - size]
    df['confirmed_low_price'] = np.where(df['pivot_low_confirmed'], df['low'].shift(size), np.nan)
    df['confirmed_low_idx'] = np.where(df['pivot_low_confirmed'], df.index.shift(size) if isinstance(df.index, pd.RangeIndex) else np.arange(n) - size, np.nan)
    
    df['confirmed_high_price'] = np.where(df['pivot_high_confirmed'], df['high'].shift(size), np.nan)
    df['confirmed_high_idx'] = np.where(df['pivot_high_confirmed'], np.arange(n) - size, np.nan)
    
    return df

def analyze_htf_smc(df_4h: pd.DataFrame, swing_size: int = 10, internal_size: int = 3) -> pd.DataFrame:
    """
    Phân tích 4 yêu cầu trên khung HTF-4H:
    1. Cấu trúc: Bull, Bear, Sideway (Tích lũy / Phân phối)
    2. Xác nhận đỉnh/đáy qua việc quét IDM (Internal Swing)
    3. Xác định OB (kèm FVG, Volume > 1.5x trung bình, vị trí Premium/Discount)
    4. Xác định vùng thanh khoản đối diện (BSL / SSL)
    """
    df = df_4h.copy()
    df['atr'] = calculate_atr(df, 14)
    df['vol_ma'] = df['volume'].rolling(10).mean()
    df['high_volume'] = df['volume'] > (df['vol_ma'] * 1.5) # Volume lớn hơn 50% nến kế bên
    
    # Tính cấu trúc Swing (chính) và Internal (dùng làm IDM)
    swing_df = detect_luxalgo_structure(df, size=swing_size)
    internal_df = detect_luxalgo_structure(df, size=internal_size)
    
    df['swing_high'] = swing_df['confirmed_high_price']
    df['swing_low'] = swing_df['confirmed_low_price']
    df['internal_high'] = internal_df['confirmed_high_price']
    df['internal_low'] = internal_df['confirmed_low_price']
    
    # FVG Detection (Bullish & Bearish)
    df['bull_fvg'] = df['low'] > df['high'].shift(2)
    df['bear_fvg'] = df['high'] < df['low'].shift(2)
    
    # Lưu trạng thái cấu trúc theo từng nến
    trends = []
    wyckoff_phases = []
    active_obs = [] # Danh sách OB hợp lệ tại thời điểm i
    
    current_trend = 'SIDEWAY'
    last_sh, prev_sh = np.nan, np.nan
    last_sl, prev_sl = np.nan, np.nan
    last_idm_high, last_idm_low = np.nan, np.nan
    idm_swept = False
    
    current_ob = None # Dict lưu OB mạnh hiện tại
    
    for i in range(len(df)):
        row = df.iloc[i]
        
        # Cập nhật Internal Structure (IDM)
        if not np.isnan(row['internal_high']):
            last_idm_high = row['internal_high']
        if not np.isnan(row['internal_low']):
            last_idm_low = row['internal_low']
            
        # Cập nhật Swing Structure
        if not np.isnan(row['swing_high']):
            prev_sh = last_sh
            last_sh = row['swing_high']
            idm_swept = False # Reset trạng thái quét IDM khi có đỉnh mới
            
        if not np.isnan(row['swing_low']):
            prev_sl = last_sl
            last_sl = row['swing_low']
            idm_swept = False

        # 1. Xác định xu hướng (Bull / Bear / Sideway)
        if not np.isnan(last_sh) and not np.isnan(prev_sh) and not np.isnan(last_sl) and not np.isnan(prev_sl):
            if last_sh > prev_sh and last_sl > prev_sl:
                current_trend = 'BULL'
            elif last_sh < prev_sh and last_sl < prev_sl:
                current_trend = 'BEAR'
            else:
                current_trend = 'SIDEWAY'
                
        # Phân loại Sideway: Tích lũy (Accumulation) hay Phân phối (Distribution)
        phase = 'NONE'
        if current_trend == 'SIDEWAY' and not np.isnan(last_sh) and not np.isnan(last_sl):
            mid_range = (last_sh + last_sl) / 2
            # Nếu giá giữ trên 50% biên độ kèm volume tăng ở đáy -> Tích lũy, ngược lại -> Phân phối
            if row['close'] < mid_range and row['high_volume']:
                phase = 'ACCUMULATION'
            elif row['close'] > mid_range and row['high_volume']:
                phase = 'DISTRIBUTION'
                
        # 2. Kiểm tra quét IDM để xác nhận đỉnh/đáy
        if current_trend == 'BULL' and not np.isnan(last_idm_low):
            if row['low'] < last_idm_low:
                idm_swept = True # Giá hồi về quét IDM -> Đỉnh last_sh chính thức được xác nhận
        elif current_trend == 'BEAR' and not np.isnan(last_idm_high):
            if row['high'] > last_idm_high:
                idm_swept = True # Giá hồi lên quét IDM -> Đáy last_sl chính thức được xác nhận

        # 3. Tìm OB mạnh (sau khi quét IDM, có FVG, Volume > 50%, nằm vùng Discount/Premium)
        if idm_swept and i >= 2 and not np.isnan(last_sh) and not np.isnan(last_sl):
            equilibrium = (last_sh + last_sl) / 2
            
            # Tìm Bullish OB (Nằm vùng rẻ Discount < Equilibrium)
            if current_trend == 'BULL' and row['bull_fvg'] and df.iloc[i-1]['high_volume']:
                ob_candle = df.iloc[i-2]
                if ob_candle['high'] < equilibrium:
                    current_ob = {
                        'type': 'BULL_OB',
                        'top': ob_candle['high'],
                        'bottom': ob_candle['low'],
                        'tp_target': last_sh, # BSL đối diện
                        'created_idx': i,
                        'atr': row['atr']
                    }
                    
            # Tìm Bearish OB (Nằm vùng mắc Premium > Equilibrium)
            elif current_trend == 'BEAR' and row['bear_fvg'] and df.iloc[i-1]['high_volume']:
                ob_candle = df.iloc[i-2]
                if ob_candle['low'] > equilibrium:
                    current_ob = {
                        'type': 'BEAR_OB',
                        'top': ob_candle['high'],
                        'bottom': ob_candle['low'],
                        'tp_target': last_sl, # SSL đối diện
                        'created_idx': i,
                        'atr': row['atr']
                    }
                    
        # Vô hiệu hóa OB nếu giá đóng cửa xuyên thủng hoàn toàn
        if current_ob is not None:
            if current_ob['type'] == 'BULL_OB' and row['close'] < current_ob['bottom']:
                current_ob = None
            elif current_ob['type'] == 'BEAR_OB' and row['close'] > current_ob['top']:
                current_ob = None

        trends.append(current_trend)
        wyckoff_phases.append(phase)
        active_obs.append(current_ob.copy() if current_ob else None)
        
    df['htf_trend'] = trends
    df['wyckoff_phase'] = wyckoff_phases
    df['active_ob'] = active_obs
    return df
