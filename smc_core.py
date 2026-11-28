from __future__ import annotations
# smc mới chỉ định ngĩa
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd


class TrendState(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAY = "SIDEWAY"
    UNKNOWN = "UNKNOWN"


class SidewayType(str, Enum):
    NONE = "NONE"
    ACCUMULATION = "ACCUMULATION"   # Quy ước cá nhân: vùng thấp / discount (mặc định <= 0.36)
    DISTRIBUTION = "DISTRIBUTION"   # Quy ước cá nhân: vùng cao / premium (mặc định >= 0.65)


class StructureEventType(str, Enum):
    BOS_BULL = "BOS_BULL"
    BOS_BEAR = "BOS_BEAR"
    CHOCH_BULL = "CHOCH_BULL"
    CHOCH_BEAR = "CHOCH_BEAR"


@dataclass
class SwingPoint:
    idx: int
    confirmed_idx: int
    kind: str             # "HIGH" hoặc "LOW"
    price: float
    label: str = ""       # "HH", "HL", "LH", "LL"


@dataclass
class StructureEvent:
    event_idx: int
    event_type: StructureEventType
    broken_swing: SwingPoint
    break_price: float


@dataclass
class ValidPullbackIDM:
    direction: str          # "BULL" hoặc "BEAR"
    level: float
    formed_idx: int
    retrace_size: float = 0.0
    atr_at_form: float = 0.0
    swept: bool = False
    swept_idx: int | None = None


@dataclass
class LiquidityZone:
    kind: str               # "EQH", "EQL", "SWING_HIGH", "SWING_LOW"
    price: float
    formed_idx: int
    member_indices: list[int]
    swept: bool = False
    swept_idx: int | None = None


@dataclass
class ZoneOB:
    direction: str          # "BULL" hoặc "BEAR"
    role: str               # "OB" hoặc "OB_EX"
    candle_idx: int
    top: float
    bottom: float
    impulse_origin_idx: int


def compute_atr(df: pd.DataFrame, period: int = 14) -> np.ndarray:
    """Tính ATR dùng chung cho toàn bộ module."""
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    closes = df["close"].to_numpy(dtype=float)
    prev_closes = np.roll(closes, 1)

    tr = np.maximum(
        highs - lows,
        np.maximum(np.abs(highs - prev_closes), np.abs(lows - prev_closes)),
    )
    if len(tr) > 0:
        tr[0] = highs[0] - lows[0]
    return pd.Series(tr, index=df.index).rolling(period, min_periods=1).mean().to_numpy()


def is_valid_idm(retrace_size: float, atr_val: float, min_atr_mult: float = 0.6) -> bool:
    """Lọc nhiễu: nhịp hồi/IDM hợp lệ khi đạt độ lớn tối thiểu theo ATR."""
    return atr_val > 0 and retrace_size >= (min_atr_mult * atr_val)


def detect_confirmed_swings(df: pd.DataFrame, k: int = 2) -> list[SwingPoint]:
    """
    Duyệt từ trái -> phải (0 -> N-1).
    Swing tại pivot = i - k chỉ được xác nhận tại nến i (tránh look-ahead).
    """
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    swings: list[SwingPoint] = []

    if len(df) < 2 * k + 1:
        return swings

    for i in range(2 * k, len(df)):
        pivot = i - k
        if highs[pivot] > np.max(highs[pivot - k : pivot]) and highs[pivot] >= np.max(highs[pivot + 1 : i + 1]):
            swings.append(SwingPoint(idx=pivot, confirmed_idx=i, kind="HIGH", price=float(highs[pivot])))
        if lows[pivot] < np.min(lows[pivot - k : pivot]) and lows[pivot] <= np.min(lows[pivot + 1 : i + 1]):
            swings.append(SwingPoint(idx=pivot, confirmed_idx=i, kind="LOW", price=float(lows[pivot])))

    swings.sort(key=lambda s: (s.confirmed_idx, s.idx))

    last_high: float | None = None
    last_low: float | None = None
    for sw in swings:
        if sw.kind == "HIGH":
            if last_high is not None:
                sw.label = "HH" if sw.price > last_high else "LH"
            last_high = sw.price
        else:
            if last_low is not None:
                sw.label = "HL" if sw.price > last_low else "LL"
            last_low = sw.price

    return swings


def classify_range_position(
    df: pd.DataFrame,
    current_idx: int,
    window: int = 50,
    discount_max: float = 0.36,
    premium_min: float = 0.65,
) -> tuple[SidewayType, float]:
    """Đánh giá vị trí giá đóng cửa trong biên độ [current_idx - window + 1 .. current_idx]."""
    start_idx = max(0, current_idx - window + 1)
    sub = df.iloc[start_idx : current_idx + 1]
    r_high = float(sub["high"].max())
    r_low = float(sub["low"].min())
    close_price = float(df["close"].iloc[current_idx])

    if r_high <= r_low:
        return SidewayType.NONE, 0.5

    pos = (close_price - r_low) / (r_high - r_low)
    if pos <= discount_max:
        return SidewayType.ACCUMULATION, pos
    if pos >= premium_min:
        return SidewayType.DISTRIBUTION, pos
    return SidewayType.NONE, pos


def detect_eq_zones(
    df: pd.DataFrame,
    swings: list[SwingPoint],
    atr: np.ndarray,
    tol_atr_mult: float = 0.1,
) -> list[LiquidityZone]:
    """Tìm cụm EQH / EQL theo độ lệch <= tol_atr_mult * ATR."""
    zones: list[LiquidityZone] = []
    last_h: SwingPoint | None = None
    last_l: SwingPoint | None = None

    for sw in swings:
        tol = tol_atr_mult * float(atr[sw.idx])
        if sw.kind == "HIGH":
            if last_h is not None and abs(sw.price - last_h.price) <= tol:
                zones.append(
                    LiquidityZone(
                        kind="EQH",
                        price=(sw.price + last_h.price) / 2.0,
                        formed_idx=sw.idx,
                        member_indices=[last_h.idx, sw.idx],
                    )
                )
            last_h = sw
        else:
            if last_l is not None and abs(sw.price - last_l.price) <= tol:
                zones.append(
                    LiquidityZone(
                        kind="EQL",
                        price=(sw.price + last_l.price) / 2.0,
                        formed_idx=sw.idx,
                        member_indices=[last_l.idx, sw.idx],
                    )
                )
            last_l = sw

    return zones


def track_structure_and_liquidity(
    df: pd.DataFrame,
    swings: list[SwingPoint],
    zones: list[LiquidityZone],
    atr: np.ndarray,
    min_idm_atr_mult: float = 0.6,
) -> tuple[list[StructureEvent], list[ValidPullbackIDM], list[LiquidityZone], TrendState]:
    """
    Duyệt từ trái -> phải (0 -> N-1): cập nhật LQ Sweep, BOS/CHOCH, IDM hợp lệ và Trend.
    """
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    closes = df["close"].to_numpy(dtype=float)

    swings_by_confirm: dict[int, list[SwingPoint]] = {}
    for sw in swings:
        swings_by_confirm.setdefault(sw.confirmed_idx, []).append(sw)

    last_conf_h: SwingPoint | None = None
    last_conf_l: SwingPoint | None = None
    broken_ids: set[int] = set()

    trend = TrendState.UNKNOWN
    events: list[StructureEvent] = []
    idms: list[ValidPullbackIDM] = []
    active_idm: ValidPullbackIDM | None = None

    for i in range(len(df)):
        # 1. Liquidity Sweep
        for z in zones:
            if not z.swept and i > z.formed_idx:
                if z.kind in ("EQH", "SWING_HIGH") and highs[i] > z.price and closes[i] < z.price:
                    z.swept, z.swept_idx = True, i
                elif z.kind in ("EQL", "SWING_LOW") and lows[i] < z.price and closes[i] > z.price:
                    z.swept, z.swept_idx = True, i

        # 2. Swing được xác nhận tại nến i -> tạo IDM hợp lệ nếu đủ độ lớn
        for sw in swings_by_confirm.get(i, []):
            atr_val = float(atr[sw.idx])
            if sw.kind == "HIGH":
                if last_conf_l is not None and trend == TrendState.BEARISH:
                    retrace = abs(sw.price - float(lows[last_conf_l.idx]))
                    if is_valid_idm(retrace, atr_val, min_idm_atr_mult):
                        active_idm = ValidPullbackIDM("BEAR", sw.price, sw.idx, retrace, atr_val)
                        idms.append(active_idm)
                last_conf_h = sw
            else:
                if last_conf_h is not None and trend == TrendState.BULLISH:
                    retrace = abs(float(highs[last_conf_h.idx]) - sw.price)
                    if is_valid_idm(retrace, atr_val, min_idm_atr_mult):
                        active_idm = ValidPullbackIDM("BULL", sw.price, sw.idx, retrace, atr_val)
                        idms.append(active_idm)
                last_conf_l = sw

        # 3. Kiểm tra quét IDM
        if active_idm is not None and not active_idm.swept:
            if active_idm.direction == "BULL" and lows[i] < active_idm.level:
                active_idm.swept, active_idm.swept_idx = True, i
            elif active_idm.direction == "BEAR" and highs[i] > active_idm.level:
                active_idm.swept, active_idm.swept_idx = True, i

        # 4. BOS / CHOCH bằng giá đóng cửa
        c = float(closes[i])
        if last_conf_h is not None and id(last_conf_h) not in broken_ids and c > last_conf_h.price:
            broken_ids.add(id(last_conf_h))
            ev_type = StructureEventType.CHOCH_BULL if trend == TrendState.BEARISH else StructureEventType.BOS_BULL
            trend = TrendState.BULLISH
            events.append(StructureEvent(i, ev_type, last_conf_h, c))

        if last_conf_l is not None and id(last_conf_l) not in broken_ids and c < last_conf_l.price:
            broken_ids.add(id(last_conf_l))
            ev_type = StructureEventType.CHOCH_BEAR if trend == TrendState.BULLISH else StructureEventType.BOS_BEAR
            trend = TrendState.BEARISH
            events.append(StructureEvent(i, ev_type, last_conf_l, c))

    return events, idms, zones, trend


def find_origin_and_obs_backward(
    df: pd.DataFrame,
    current_idx: int,
    direction: str,
    swing_indices: list[int],
    max_candle_steps: int = 10,
    max_lookback_bars: int = 150,
) -> tuple[ZoneOB | None, ZoneOB | None]:
    """
    Quét từ phải -> trái (current_idx lùi về quá khứ) để lấy OB và OB_EX.
    """
    opens = df["open"].to_numpy(dtype=float)
    closes = df["close"].to_numpy(dtype=float)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)

    def _pick_opposing_candle(origin_idx: int) -> int | None:
        low_bound = max(0, origin_idx - max_candle_steps)
        for j in range(origin_idx, low_bound - 1, -1):
            if direction == "BULL" and closes[j] < opens[j]:
                return j
            if direction == "BEAR" and closes[j] > opens[j]:
                return j
        return None

    min_bar = max(0, current_idx - max_lookback_bars)
    past_origins = sorted([idx for idx in swing_indices if min_bar <= idx < current_idx])
    if not past_origins:
        return None, None

    nearest_ob: ZoneOB | None = None
    latest_origin = past_origins[-1]
    ob_idx = _pick_opposing_candle(latest_origin)
    if ob_idx is not None:
        nearest_ob = ZoneOB(direction, "OB", ob_idx, float(highs[ob_idx]), float(lows[ob_idx]), latest_origin)

    extreme_ob: ZoneOB | None = None
    for origin_idx in past_origins:
        ex_idx = _pick_opposing_candle(origin_idx)
        if ex_idx is not None:
            extreme_ob = ZoneOB(direction, "OB_EX", ex_idx, float(highs[ex_idx]), float(lows[ex_idx]), origin_idx)
            break

    return nearest_ob, extreme_ob
