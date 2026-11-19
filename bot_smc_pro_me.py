import ccxt
import pandas as pd
import numpy as np
import logging
import os
import json

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SMCCryptoBot:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        # Khởi tạo kết nối sàn (Mặc định Binance Futures)
        self.exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.secret,
            'options': {'defaultType': 'future'}
        })
        if self.testnet:
            self.exchange.set_sandbox_mode(True)

    def load_config(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = json.load(f)
                self.symbol = config.get('symbol', 'BTC/USDT:USDT')
                self.risk_pct = config.get('risk_pct', 0.01)
                self.api_key = os.getenv('BINANCE_API_KEY', config.get('api_key', ''))
                self.secret = os.getenv('BINANCE_SECRET', config.get('secret', ''))
                self.testnet = config.get('testnet', True)
        else:
            # Fallback mặc định
            self.symbol = 'BTC/USDT:USDT'
            self.risk_pct = 0.01
            self.api_key = ''
            self.secret = ''
            self.testnet = True

    def fetch_ohlcv(self, timeframe, limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logging.error(f"Lỗi tải dữ liệu {timeframe}: {e}")
            return None

    def calculate_atr(self, df, period=14):
        df['tr'] = np.maximum(df['high'] - df['low'], 
                              np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                         abs(df['low'] - df['close'].shift(1))))
        df['atr'] = df['tr'].rolling(window=period).mean()
        return df

    # ==========================================
    # [BƯỚC 1: HTF Bias] --> Khung 4H
    # ==========================================
    def step_1_htf_bias(self):
        df = self.fetch_ohlcv('4h', limit=50)
        if df is None: return "NEUTRAL", None

        # Logic: Xác định BOS qua đỉnh/đáy 20 nến gần nhất
        recent_high = df['high'].iloc[-20:-1].max()
        recent_low = df['low'].iloc[-20:-1].min()
        current_close = df['close'].iloc[-1]

        bias = "NEUTRAL"
        if current_close > recent_high:
            bias = "BULLISH"
        elif current_close < recent_low:
            bias = "BEARISH"
            
        logging.info(f"[Bước 1 - HTF Bias 4H]: Xu hướng hiện tại là {bias}")
        return bias, df

    # ==========================================
    # [BƯỚC 2: POI Selection] --> Lọc Order Block chuẩn hóa
    # ==========================================
    def step_2_poi_selection(self, df_4h, bias):
        if bias == "NEUTRAL": return None

        # 1. Tính ATR và Volume SMA cho khung 4H
        df_4h = self.calculate_atr(df_4h, period=14)
        df_4h['vol_ma'] = df_4h['volume'].rolling(20).mean()
        
        poi_zone = None
        # Duyệt từ quá khứ gần về xa (trừ 3 nến cuối để đủ không gian xét nến sau)
        for i in range(len(df_4h) - 3, 5, -1):
            if bias == "BULLISH":
                # Điều kiện 1: Tìm nến giảm (đỏ) cuối cùng trước đợt tăng
                is_red_candle = df_4h['close'].iloc[i] < df_4h['open'].iloc[i]
                
                # Điều kiện 2: Thân nến bứt phá (nến i+1) > 1.5 * ATR_14
                breakout_body = abs(df_4h['close'].iloc[i+1] - df_4h['open'].iloc[i+1])
                atr_val = df_4h['atr'].iloc[i+1]
                is_large_body = breakout_body > (1.5 * atr_val) if not pd.isna(atr_val) else True
                
                # Điều kiện 3: Khối lượng nến bứt phá > 1.5 * SMA(Volume, 20)
                is_high_volume = df_4h['volume'].iloc[i+1] > df_4h['vol_ma'].iloc[i+1] * 1.5
                
                # Điều kiện 4: Phải có Fair Value Gap (FVG) xuất hiện ngay sau OB
                # (Đối với xu hướng tăng: Đáy của nến i+2 phải nằm cao hơn Đỉnh của nến i)
                has_fvg = df_4h['low'].iloc[i+2] > df_4h['high'].iloc[i]
                
                # Nếu thỏa mãn toàn bộ các bộ lọc định lượng khắt khe
                if is_red_candle and is_large_body and is_high_volume and has_fvg:
                    # Tinh chỉnh vùng vào lệnh: Lấy Midpoint (50%) của cây nến OB
                    ob_high = df_4h['high'].iloc[i]
                    ob_low = df_4h['low'].iloc[i]
                    poi_zone = ob_low + (ob_high - ob_low) * 0.5
                    logging.info(f"[Bước 2]: Đã tìm thấy OB chuẩn hóa tại index {i} thỏa mãn ATR, Volume & FVG.")
                    break
        
        logging.info(f"[Bước 2 - POI Selection]: Vùng POI được xác định tại mức giá: {poi_zone}")
        return poi_zone


    # ==========================================
    # [BƯỚC 3: LTF Trigger] --> Khung 15m (Chờ ChoCH)
    # ==========================================
    def step_3_ltf_trigger(self, poi_zone):
        if not poi_zone: return False, None

        df_15m = self.fetch_ohlcv('15m', limit=50)
        df_15m = self.calculate_atr(df_15m, period=14)
        
        # 1. Tính toán SMA Volume cho khung 15m (20 chu kỳ)
        df_15m['vol_ma_15m'] = df_15m['volume'].rolling(20).mean()
        
        current_price = df_15m['close'].iloc[-1]
        atr_buffer = df_15m['atr'].iloc[-1] * 0.5

        # Kiểm tra xem giá hiện tại có đang nằm trong vùng POI 4H không
        in_poi_zone = abs(current_price - poi_zone) <= atr_buffer

        if in_poi_zone:
            logging.info("[Bước 3]: Giá đã chạm vùng POI 4H. Đang quét tín hiệu ChoCH khung 15m kèm Volume...")
            
            # Lấy đỉnh gần nhất của 10 nến trước đó (bỏ qua cây nến hiện tại đang chạy)
            recent_swing_high = df_15m['high'].iloc[-11:-1].max()
            
            # Điều kiện 1: Giá đóng cửa (Close) phải vượt qua đỉnh cũ
            confirmed_close = df_15m['close'].iloc[-1]
            
            # Điều kiện 2: Phải có Fair Value Gap (FVG) xuất hiện ở khung 15m
            has_ltf_fvg = df_15m['low'].iloc[-1] > df_15m['high'].iloc[-3]
            
            # Điều kiện 3 (MỚI): Khối lượng giao dịch của cây nến phá vỡ > 1.5 lần trung bình 20 phiên
            breakout_volume = df_15m['volume'].iloc[-1]
            avg_volume = df_15m['vol_ma_15m'].iloc[-1]
            has_high_volume = breakout_volume > (avg_volume * 1.5) if not pd.isna(avg_volume) else True

            # Tổng hợp tất cả các bộ lọc khắt khe
            if confirmed_close > recent_swing_high and has_ltf_fvg and has_high_volume:
                logging.info("[Bước 3]: Phát hiện ChoCH khung 15m HOÀN HẢO (Close > Swing High + FVG + Volume bùng nổ > 1.5x). Sẵn sàng vào lệnh.")
                return True, df_15m
        
        return False, None


    # ==========================================
    # [BƯỚC 4: Execution] --> Vào lệnh Limit + SL (ATR Buffer)
    # ==========================================
    def step_4_execution(self, df_15m):
        current_price = df_15m['close'].iloc[-1]
        atr = df_15m['atr'].iloc[-1]
        
        # Đặt Stop Loss cách Swing Low gần nhất trừ đi ATR Buffer
        swing_low = df_15m['low'].iloc[-10:].min()
        stop_loss = swing_low - (atr * 0.8)
        
        risk_distance = current_price - stop_loss
        if risk_distance <= 0: return # Bảo vệ lỗi toán học

        # Tính toán khối lượng lệnh dựa trên tài khoản
        try:
            balance = self.exchange.fetch_balance()['USDT']['free']
            risk_amount = balance * self.risk_pct
            position_size = risk_amount / risk_distance
            
            logging.info(f"[Bước 4 - Execution]: Đặt lệnh MUA tại {current_price} | SL: {stop_loss} | Khối lượng: {position_size:.4f}")
            # Thực tế: self.exchange.create_order(...)
        except Exception as e:
            logging.error(f"Lỗi tính toán thực thi lệnh: {e}")

  # ==========================================
    # [BƯỚC 5: Management] --> TP1 (Chốt 1 phần + Dời SL về Entry) & TP2
    # ==========================================
    def step_5_management(self):
        try:
            # Lấy danh sách vị thế đang mở trên sàn
            positions = self.exchange.fetch_positions()
            for pos in positions:
                if pos['symbol'] == self.symbol and float(pos['contracts']) > 0:
                    entry_price = float(pos['entryPrice'])
                    current_price = float(pos['markPrice'])
                    size = float(pos['contracts'])
                    
                    # Tính khoảng cách lợi nhuận hiện tại so với giá vào lệnh
                    profit_distance = current_price - entry_price
                    
                    # Giả sử đặt TP1 tại 1:2 R đối với khoảng cách rủi ro ban đầu (ví dụ: tăng 1.5% giá)
                    # Logic quản trị tự động:
                    if profit_distance >= (entry_price * 0.015): # Đạt mức TP1 cấu trúc
                        logging.info("[Bước 5 - Management]: Giá đạt TP1. Tiến hành chốt 50% vị thế và dời SL về Breakeven.")
                        
                        # 1. Chốt 50% khối lượng
                        half_size = size / 2
                        # self.exchange.create_order(self.symbol, 'market', 'sell', half_size, params={'reduceOnly': True})
                        
                        # 2. Dời Stop Loss về đúng giá vào lệnh (Breakeven) để không bao giờ lỗ
                        # self.exchange.edit_stop_loss(...) 
                        
        except Exception as e:
            logging.error(f"Lỗi ở bước quản lý vị thế (Step 5): {e}")

    def run(self):
        logging.info("--- BẮT ĐẦU CHU KỲ PHÂN TÍCH SMC/ICT ---")
        bias, df_4h = self.step_1_htf_bias()
        poi_zone = self.step_2_poi_selection(df_4h, bias)
        triggered, df_15m = self.step_3_ltf_trigger(poi_zone)
        
        if triggered:
            self.step_4_execution(df_15m)
        
        self.step_5_management()

if __name__ == "__main__":
    bot = SMCCryptoBot()
    bot.run()
