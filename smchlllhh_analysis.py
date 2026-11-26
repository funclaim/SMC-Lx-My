import numpy as np
import pandas as pd
from config import SWING_SIZE, EQ_THRESHOLD, RR_RATIO

MIN_CHECKLIST_SCORE = 75
VOL_MULT = 1.5   # volume nến phá CHoCH >= VOL_MULT x TB 20 nến trước
VOL_N = 20
STATS = None             # backtest gán dict để đếm phễu; live để None
REQUIRE_HTF_BOS = True   # hồi sau: chỉ đánh khi HTF đã BOS
CHOCH_BODY_ATR = 0.5   # thân nến phá CHoCH >= N*ATR
SWEEP_CLEAR_ATR = 3.0   # không còn swing chưa quét trong N*ATR sau đỉnh/đáy quét


# ---------------------------------------------------------------- helpers
def _hit(stage, key):
    if STATS is not None:
        STATS.setdefault(stage, set()).add(key)


def _swings(h, l, size):
    """Swing high/low (NaN nếu không phải swing). Tương đương vòng for cũ."""
    w = 2 * size + 1
    hs = pd.Series(h).rolling(w, center=True).max().values
    ls = pd.Series(l).rolling(w, center=True).min().values
    return np.where(h == hs, h, np.nan), np.where(l == ls, l, np.nan)


def nearest_liquidity(idxs, vals, suf, entry, step, short):
    """Swing chưa bị quét, gần entry nhất, ở phía đối diện."""
    best = None
    for k, v in zip(idxs, vals):
        if k + 1 > step:
            continue
        if short:  # swing low dưới entry, chưa bị thủng
            if v < entry and suf[k + 1] >= v and (best is None or v > best):
                best = v
        else:      # swing high trên entry, chưa bị vượt
            if v > entry and suf[k + 1] <= v and (best is None or v < best):
                best = v
    return best


def has_liquidity_ahead(idxs, vals, suf, level, dist, step, short):
    """Còn swing chưa quét trong `dist` phía sau đỉnh (SHORT) / đáy (LONG) quét?"""
    for k, v in zip(idxs, vals):
        if k + 1 > step:
            continue
        if short:
            if level < v <= level + dist and suf[k + 1] <= v:
                return True
        else:
            if level - dist <= v < level and suf[k + 1] >= v:
                return True
    return False


def idm_chain(bos_idxs, bos_vals, idm_idxs, idm_vals, closes, i, start_w, short):
    """Chuỗi IDM của cấu trúc trước nến i (đi tuần tự theo swing).
    short=True : cấu trúc TĂNG (bos = swing high, idm = swing low) - dùng cho kèo SHORT đảo chiều.
    short=False: cấu trúc GIẢM (bos = swing low, idm = swing high).
    Đáy đầu tiên sau đỉnh = IDM; đóng cửa vượt đỉnh (BOS) rồi tạo đáy CAO hơn = IDM mới;
    đáy thấp hơn IDM = cấu trúc gãy, dựng lại. Trả về ((idx, level), n_bos) hoặc (None, 0)
    nếu chưa có IDM hoặc IDM đã bị đóng cửa phá trước nến i."""
    sg = 1.0 if short else -1.0
    c = sg * closes
    sw = sorted([(k, sg * v, 0) for k, v in zip(bos_idxs, bos_vals) if start_w <= k < i - 2] +
                [(k, sg * v, 1) for k, v in zip(idm_idxs, idm_vals) if start_w <= k < i - 2])
    idm = ref = last_high = None      # idm=(idx,val); ref = đỉnh mà IDM hồi về từ đó
    n_bos = 0
    for k, v, kind in sw:
        if kind == 0:
            last_high = (k, v)
            continue
        if last_high is None:         # đáy phải đứng sau một đỉnh
            continue
        if idm is None:
            idm, ref, n_bos = (k, v), last_high, 0
        elif v < idm[1]:              # đáy thấp hơn IDM: cấu trúc gãy
            idm = ref = last_high = None
            n_bos = 0
        elif k > idm[0] and (c[idm[0] + 1:k] > ref[1]).any():   # BOS rồi đáy cao hơn
            idm, ref, n_bos = (k, v), last_high, n_bos + 1
    if idm is None or (c[idm[0] + 1:i] < idm[1]).any():
        return None, 0
    return (idm[0], sg * idm[1]), n_bos


def find_idm(bos_idxs, bos_vals, idm_idxs, idm_vals, closes, i, start_w, short):
    """IDM hiện hành (idx, level) hoặc None. Xem idm_chain."""
    return idm_chain(bos_idxs, bos_vals, idm_idxs, idm_vals, closes, i, start_w, short)[0]


def valid_choch_break(opens, highs, lows, closes, b, atr, step, lvl, short):
    """Phá thật: nến thân mạnh đóng gần cực trị (không rút râu) và nến sau giữ được mức."""
    rng = highs[b] - lows[b]
    body = abs(closes[b] - opens[b])
    if rng <= 0 or body < CHOCH_BODY_ATR * atr or body < 0.5 * rng:
        return False
    if b + 1 > step:          # chưa có nến xác nhận giữ mức
        return False
    if short:
        return (closes[b] < opens[b] and closes[b] <= lows[b] + 0.35 * rng
                and closes[b + 1] < lvl)
    return (closes[b] > opens[b] and closes[b] >= highs[b] - 0.35 * rng
            and closes[b + 1] > lvl)


def choch_volume_ok(vol, b_pos, n=None, mult=None):
    """Nến phá CHoCH phải có volume lớn hơn trung bình n nến trước."""
    n = VOL_N if n is None else n
    mult = VOL_MULT if mult is None else mult
    if b_pos < n or np.isnan(vol[b_pos]):
        return False
    return vol[b_pos] >= mult * vol[b_pos - n:b_pos].mean()


def fvg_reaction(lows, highs, closes, b_pos, step, fvg_bot, fvg_top, short):
    """('FVG', j) | ('OB', None) | ('WAIT', None)
    LONG : râu tới >= 50% FVG và đóng trên mép trên -> FVG; đóng dưới mép dưới -> OB.
    SHORT: râu tới >= 50% FVG và đóng dưới mép dưới -> FVG; đóng trên mép trên -> OB.
    """
    mid = (fvg_bot + fvg_top) / 2
    for j in range(b_pos + 1, step + 1):
        if not short:
            if closes[j] < fvg_bot:
                return 'OB', None
            if lows[j] <= mid and closes[j] > fvg_top:
                return 'FVG', j
        else:
            if closes[j] > fvg_top:
                return 'OB', None
            if highs[j] >= mid and closes[j] < fvg_bot:
                return 'FVG', j
    return 'WAIT', None


# ---------------------------------------------------------------- HTF
def analyze_htf_context_and_poi(df_htf, current_low, current_high, size=SWING_SIZE):
    if len(df_htf) < size * 2 + 5:
        return 'NEUTRAL', {'has_bos': False, 'mid_4h': 0.0, 'touched_poi': False}

    highs_arr, lows_arr = df_htf['high'].values, df_htf['low'].values
    closes = df_htf['close'].values
    sh, sl = _swings(highs_arr, lows_arr, size)

    # chỉ dùng swing đã xác nhận (bỏ `size` nến cuối)
    highs = sh[:-size][~np.isnan(sh[:-size])]
    lows = sl[:-size][~np.isnan(sl[:-size])]
    if len(highs) < 2 or len(lows) < 2:
        return 'NEUTRAL', {'has_bos': False, 'mid_4h': 0.0, 'touched_poi': False}

    last_close = closes[-1]
    mid_4h = float((highs[-1] + lows[-1]) / 2.0)

    trend, has_bos = 'NEUTRAL', False
    if last_close > highs[-1]:
        trend, has_bos = 'BULLISH', True
    elif highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        trend, has_bos = 'BULLISH', False
    elif last_close < lows[-1]:
        trend, has_bos = 'BEARISH', True
    elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        trend, has_bos = 'BEARISH', False

    if trend == 'NEUTRAL':
        return 'NEUTRAL', {'has_bos': False, 'mid_4h': mid_4h, 'touched_poi': False}

    # Vùng 4H POI (OB + FVG) chưa bị phá & giá hiện tại đã chạm vùng
    suf_min = np.minimum.accumulate(closes[::-1])[::-1]
    suf_max = np.maximum.accumulate(closes[::-1])[::-1]
    touched_poi = False
    for i in range(2, len(df_htf) - 2):
        if trend == 'BULLISH' and lows_arr[i + 2] > highs_arr[i]:
            p_top, p_bottom = lows_arr[i + 2], lows_arr[i]
            if suf_min[i + 2] >= p_bottom and current_low <= p_top and current_high >= p_bottom:
                touched_poi = True
                break
        elif trend == 'BEARISH' and highs_arr[i + 2] < lows_arr[i]:
            p_top, p_bottom = highs_arr[i], highs_arr[i + 2]
            if suf_max[i + 2] <= p_top and current_high >= p_bottom and current_low <= p_top:
                touched_poi = True
                break

    return trend, {'has_bos': has_bos, 'mid_4h': mid_4h, 'touched_poi': touched_poi}


# ---------------------------------------------------------------- checklist
def evaluate_smc_checklist(htf_info, entry, is_eq, fvg_size, atr, direction, rr):
    htf_bos_pts = 20 if htf_info.get('has_bos') else 10
    mid_4h = htf_info.get('mid_4h', 0.0)
    in_zone = (direction == 'LONG' and entry < mid_4h) or (direction == 'SHORT' and entry > mid_4h)
    htf_liq_pts = 10 if (mid_4h > 0 and in_zone) else 4
    sweep_pts = 15 if is_eq else 10
    choch_pts = 10
    fvg_pts = 20 if fvg_size >= (0.4 * atr) else 12
    entry_sl_pts = 15
    rr_pts = 10 if rr >= 2.0 else 0
    total = htf_bos_pts + htf_liq_pts + sweep_pts + choch_pts + fvg_pts + entry_sl_pts + rr_pts
    detail = f"HTF:{htf_bos_pts+htf_liq_pts}/30 | LTF:{sweep_pts+choch_pts+fvg_pts}/45 | Setup:{entry_sl_pts+rr_pts}/25"
    return total, detail


# ---------------------------------------------------------------- LTF
def find_sweep_ob_setups(df, trend, htf_info):
    setups = []
    if (trend not in ['BULLISH', 'BEARISH'] or not htf_info.get('touched_poi')
            or (REQUIRE_HTF_BOS and not htf_info.get('has_bos')) or len(df) < 60):
        return setups

    highs_arr, lows_arr = df['high'].values, df['low'].values
    closes_arr, opens_arr = df['close'].values, df['open'].values
    atrs_arr, times_arr = df['atr'].values, df.index
    vols_arr = df['volume'].values

    sh, sl = _swings(highs_arr, lows_arr, 2)
    lh_idxs = [k for k in np.where(~np.isnan(sh))[0] if k >= 2]
    ll_idxs = [k for k in np.where(~np.isnan(sl))[0] if k >= 2]
    lh_vals = [highs_arr[k] for k in lh_idxs]
    ll_vals = [lows_arr[k] for k in ll_idxs]

    suf_min = np.minimum.accumulate(lows_arr[::-1])[::-1]
    suf_max = np.maximum.accumulate(highs_arr[::-1])[::-1]

    import bisect
    step = len(df) - 1
    start_w = max(0, step - 60)

    for i in range(max(10, step - 25), step - 3):
        if np.isnan(atrs_arr[i]):
            continue
        atr, ob_time = atrs_arr[i], str(times_arr[i])

        # ------------------------------------------------ SHORT
        if trend == 'BEARISH' and closes_arr[i] > opens_arr[i]:
            fvg_size = lows_arr[i] - highs_arr[i + 2]
            ob_top, ob_bottom = highs_arr[i], lows_arr[i]
            if fvg_size >= (0.15 * atr):
                l_pos, r_pos = bisect.bisect_left(lh_idxs, start_w), bisect.bisect_left(lh_idxs, i - 1)
                _hit('1_ob_fvg', 'S' + ob_time)
                p_hi = [x for x in range(l_pos, r_pos) if lh_vals[x] < ob_top]
                p_highs = [lh_vals[x] for x in p_hi]
                if len(p_highs) >= 2:
                    _hit('2_hai_swing', 'S' + ob_time)
                    h1, h2 = p_highs[-2], p_highs[-1]
                    lq_level, sweep_high = max(h1, h2), max(highs_arr[i], highs_arr[i + 1])
                    if sweep_high > lq_level:
                        _hit('3_quet_tho', 'S' + ob_time)
                    if (sweep_high > lq_level
                            and closes_arr[i if highs_arr[i] >= highs_arr[i + 1] else i + 1] <= lq_level
                            and not has_liquidity_ahead(lh_idxs, lh_vals, suf_max, sweep_high,
                                                        SWEEP_CLEAR_ATR * atr, step, True)):
                        _hit('4_quet_ro_rang', 'S' + ob_time)
                        idm = find_idm(lh_idxs, lh_vals, ll_idxs, ll_vals, closes_arr, i, start_w, True)
                        if idm is None:
                            continue
                        choch_idx, choch_lvl = idm
                        _hit('5_co_idm', 'S' + ob_time)
                        fut_closes = closes_arr[i + 2: step + 1]
                        if fut_closes.min() < choch_lvl and fut_closes.max() <= sweep_high:
                            first_b = int(np.argmax(fut_closes < choch_lvl))
                            if first_b <= 12:
                                b_pos = i + 2 + first_b
                                _hit('6_dong_pha_idm_trong12', 'S' + ob_time)
                                if not valid_choch_break(opens_arr, highs_arr, lows_arr, closes_arr, b_pos, atr, step, choch_lvl, True):
                                    continue
                                _hit('7_pha_that', 'S' + ob_time)
                                if not choch_volume_ok(vols_arr, b_pos):
                                    continue
                                _hit('8_volume_ok', 'S' + ob_time)
                                # fvg_bot = highs[i+2], fvg_top = lows[i]
                                mode, j = fvg_reaction(lows_arr, highs_arr, closes_arr, b_pos, step,
                                                       highs_arr[i + 2], lows_arr[i], True)
                                if mode == 'FVG' and j < step:
                                    continue  # đã kích hoạt từ trước
                                after_highs = highs_arr[b_pos + 1: step + 1]
                                if mode == 'FVG' or len(after_highs) == 0 or after_highs.max() < ob_bottom:
                                    _hit('9_entry_hop_le', 'S' + ob_time)
                                    if mode == 'FVG':
                                        entry = closes_arr[j]
                                        sl_p = max(highs_arr[j], sweep_high) + 0.2 * atr
                                    else:
                                        entry = ob_bottom
                                        sl_p = sweep_high + 0.2 * atr
                                    tp = nearest_liquidity(ll_idxs, ll_vals, suf_min, entry, step, True)
                                    if tp is None:
                                        continue
                                    _hit('10_co_tp', 'S' + ob_time)
                                    rr = (entry - tp) / (sl_p - entry)
                                    if rr < RR_RATIO:
                                        continue
                                    _hit('11_rr_dat', 'S' + ob_time)
                                    is_eq = abs(h1 - h2) <= EQ_THRESHOLD * atr
                                    score, detail = evaluate_smc_checklist(htf_info, entry, is_eq, fvg_size, atr, 'SHORT', rr)
                                    if score >= MIN_CHECKLIST_SCORE:
                                        _hit('12_du_diem', 'S' + ob_time)
                                        setups.append({
                                            'direction': 'SHORT', 'index': i, 'ob_time': ob_time,
                                            'score': score, 'checklist': detail,
                                            'ob_top': ob_top, 'ob_bottom': ob_bottom,
                                            'entry': round(entry, 6), 'sl': round(sl_p, 6), 'tp': round(tp, 6),
                                            'rr': round(rr, 2), 'entry_mode': mode, 'htf_mode': 'AFTER',
                                            'lq_level': lq_level,
                                            'lq_type': 'EQH Sweep' if is_eq else 'LQ Sweep',
                                            'choch_level': choch_lvl, 'choch_start_idx': choch_idx,
                                            'choch_break_idx': b_pos
                                        })

        # ------------------------------------------------ LONG
        elif trend == 'BULLISH' and closes_arr[i] < opens_arr[i]:
            fvg_size = lows_arr[i + 2] - highs_arr[i]
            ob_top, ob_bottom = highs_arr[i], lows_arr[i]
            if fvg_size >= (0.15 * atr):
                l_pos, r_pos = bisect.bisect_left(ll_idxs, start_w), bisect.bisect_left(ll_idxs, i - 1)
                _hit('1_ob_fvg', 'L' + ob_time)
                p_lo = [x for x in range(l_pos, r_pos) if ll_vals[x] > ob_bottom]
                p_lows = [ll_vals[x] for x in p_lo]
                if len(p_lows) >= 2:
                    _hit('2_hai_swing', 'L' + ob_time)
                    l1, l2 = p_lows[-2], p_lows[-1]
                    lq_level, sweep_low = min(l1, l2), min(lows_arr[i], lows_arr[i + 1])
                    if sweep_low < lq_level:
                        _hit('3_quet_tho', 'L' + ob_time)
                    if (sweep_low < lq_level
                            and closes_arr[i if lows_arr[i] <= lows_arr[i + 1] else i + 1] >= lq_level
                            and not has_liquidity_ahead(ll_idxs, ll_vals, suf_min, sweep_low,
                                                        SWEEP_CLEAR_ATR * atr, step, False)):
                        _hit('4_quet_ro_rang', 'L' + ob_time)
                        idm = find_idm(ll_idxs, ll_vals, lh_idxs, lh_vals, closes_arr, i, start_w, False)
                        if idm is None:
                            continue
                        choch_idx, choch_lvl = idm
                        _hit('5_co_idm', 'L' + ob_time)
                        fut_closes = closes_arr[i + 2: step + 1]
                        if fut_closes.max() > choch_lvl and fut_closes.min() >= sweep_low:
                            first_b = int(np.argmax(fut_closes > choch_lvl))
                            if first_b <= 12:
                                b_pos = i + 2 + first_b
                                _hit('6_dong_pha_idm_trong12', 'L' + ob_time)
                                if not valid_choch_break(opens_arr, highs_arr, lows_arr, closes_arr, b_pos, atr, step, choch_lvl, False):
                                    continue
                                _hit('7_pha_that', 'L' + ob_time)
                                if not choch_volume_ok(vols_arr, b_pos):
                                    continue
                                _hit('8_volume_ok', 'L' + ob_time)
                                # fvg_bot = highs[i], fvg_top = lows[i+2]
                                mode, j = fvg_reaction(lows_arr, highs_arr, closes_arr, b_pos, step,
                                                       highs_arr[i], lows_arr[i + 2], False)
                                if mode == 'FVG' and j < step:
                                    continue  # đã kích hoạt từ trước
                                after_lows = lows_arr[b_pos + 1: step + 1]
                                if mode == 'FVG' or len(after_lows) == 0 or after_lows.min() > ob_top:
                                    _hit('9_entry_hop_le', 'L' + ob_time)
                                    if mode == 'FVG':
                                        entry = closes_arr[j]
                                        sl_p = min(lows_arr[j], sweep_low) - 0.2 * atr
                                    else:
                                        entry = ob_top
                                        sl_p = sweep_low - 0.2 * atr
                                    tp = nearest_liquidity(lh_idxs, lh_vals, suf_max, entry, step, False)
                                    if tp is None:
                                        continue
                                    _hit('10_co_tp', 'L' + ob_time)
                                    rr = (tp - entry) / (entry - sl_p)
                                    if rr < RR_RATIO:
                                        continue
                                    _hit('11_rr_dat', 'L' + ob_time)
                                    is_eq = abs(l1 - l2) <= EQ_THRESHOLD * atr
                                    score, detail = evaluate_smc_checklist(htf_info, entry, is_eq, fvg_size, atr, 'LONG', rr)
                                    if score >= MIN_CHECKLIST_SCORE:
                                        _hit('12_du_diem', 'L' + ob_time)
                                        setups.append({
                                            'direction': 'LONG', 'index': i, 'ob_time': ob_time,
                                            'score': score, 'checklist': detail,
                                            'ob_top': ob_top, 'ob_bottom': ob_bottom,
                                            'entry': round(entry, 6), 'sl': round(sl_p, 6), 'tp': round(tp, 6),
                                            'rr': round(rr, 2), 'entry_mode': mode, 'htf_mode': 'AFTER',
                                            'lq_level': lq_level,
                                            'lq_type': 'EQL Sweep' if is_eq else 'LQ Sweep',
                                            'choch_level': choch_lvl, 'choch_start_idx': choch_idx,
                                            'choch_break_idx': b_pos
                                        })

    if not setups:
        return []
    # Ưu tiên duy nhất Extreme OB (cao nhất cho SHORT, thấp nhất cho LONG)
    extreme = max(setups, key=lambda x: x['ob_top']) if trend == 'BEARISH' else min(setups, key=lambda x: x['ob_bottom'])
    return [extreme]


# ---------------------------------------------------------------- TREND (thuận sóng chính LTF)
def find_trend_setups(df, trend):
    """Kèo thuận sóng chính LTF: giá quét IDM (râu thủng) rồi nến đóng cửa lại ngoài IDM -> vào tại close.
    BULLISH -> LONG: cấu trúc tăng đã có BOS + đáy cao hơn; IDM = đáy cao hơn gần nhất.
    BEARISH -> SHORT: đối xứng. SL ngoài râu quét (+0.2 ATR), TP = swing chưa quét gần nhất, R:R >= RR_RATIO.
    Chỉ báo ở nến vừa đóng (step). Lọc HTF (POI/BOS) để bên gọi quyết định."""
    if trend not in ('BULLISH', 'BEARISH') or len(df) < 60:
        return []
    highs, lows, closes = df['high'].values, df['low'].values, df['close'].values
    atr = df['atr'].values[-1]
    if np.isnan(atr):
        return []
    step = len(df) - 1
    start_w = max(0, step - 60)
    sh, sl = _swings(highs, lows, 2)
    lh_idxs = [k for k in np.where(~np.isnan(sh))[0] if k >= 2]
    ll_idxs = [k for k in np.where(~np.isnan(sl))[0] if k >= 2]
    lh_vals = [highs[k] for k in lh_idxs]
    ll_vals = [lows[k] for k in ll_idxs]

    long = trend == 'BULLISH'
    key = ('L' if long else 'S') + str(df.index[step])
    if long:
        idm, n_bos = idm_chain(lh_idxs, lh_vals, ll_idxs, ll_vals, closes, step, start_w, True)
    else:
        idm, n_bos = idm_chain(ll_idxs, ll_vals, lh_idxs, lh_vals, closes, step, start_w, False)
    if idm is None or n_bos < 1:
        return []
    _hit('T1_idm_sau_bos', key)
    lvl = idm[1]
    if not ((lows[step] < lvl) if long else (highs[step] > lvl)):
        return []
    _hit('T2_quet_idm', key)
    if not ((closes[step] > lvl) if long else (closes[step] < lvl)):
        return []
    _hit('T3_dong_cua_lai', key)

    entry = closes[step]
    if long:
        sl_p = lows[step] - 0.2 * atr
        suf = np.maximum.accumulate(highs[::-1])[::-1]
        tp = nearest_liquidity(lh_idxs, lh_vals, suf, entry, step, False)
        rr = None if tp is None else (tp - entry) / (entry - sl_p)
    else:
        sl_p = highs[step] + 0.2 * atr
        suf = np.minimum.accumulate(lows[::-1])[::-1]
        tp = nearest_liquidity(ll_idxs, ll_vals, suf, entry, step, True)
        rr = None if tp is None else (entry - tp) / (sl_p - entry)
    if tp is None:
        return []
    _hit('T4_co_tp', key)
    if rr < RR_RATIO:
        return []
    _hit('T5_rr_dat', key)
    return [{'direction': 'LONG' if long else 'SHORT', 'mode': 'TREND',
             'sweep_time': str(df.index[step]), 'entry': round(entry, 6),
             'sl': round(sl_p, 6), 'tp': round(tp, 6), 'rr': round(rr, 2),
             'idm': lvl, 'n_bos': n_bos}]
