# Báo Cáo Backtest SMC Pro MTF - CEX_BTCUSD_1h

## 1. Cấu hình tham số hệ thống

- **Dữ liệu đầu vào:** `data/CEX_BTCUSD_1h.csv` (LTF: 1H -> HTF: 4H)
- **Cơ chế vào lệnh:** Limit tại Extreme OB/FVG sau CHoCH
- **Bộ lọc phiên Killzones (London/NY):** `TẮT`
- **Quản lý vốn Break-even (1.5R / BOS):** `BẬT`

## 2. Thống kê hiệu suất tổng quan

| Chỉ số | Giá trị |
| :--- | :--- |
| **Tổng số lệnh đã khớp** | 49 |
| **Thắng (WIN)** | 6 |
| **Hòa vốn (Break-Even)** | 32 |
| **Thua (LOSS)** | 11 |
| **Tỷ lệ thắng (Winrate)** | 12.24% |
| **Tổng lợi nhuận ròng (R)** | **+12.81R** |
| **Tỷ lệ R:R trung bình** | 1:3.87 |

## 3. Chi tiết lệnh & Biểu đồ phân tích Zone Shading

### Lệnh #1 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2016-09-12 03:00:00+00:00` | **Khớp Limit:** `2016-09-12 04:00:00+00:00` | **Đóng lệnh:** `2016-09-12 05:00:00+00:00`
- **Entry Limit:** `627.4052` | **SL:** `627.4052` | **TP:** `669.0637` | **RR:** `1:3.0`
- **Vùng OB 4H:** `614.4 - 615.0` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 1 4H](charts/trade_1_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 1 LTF](charts/trade_1_ltf.png)

---

### Lệnh #2 — SHORT | Kết quả: **WIN (+4.97R)**
- **Tín hiệu CHoCH:** `2017-03-16 03:00:00+00:00` | **Khớp Limit:** `2017-03-16 04:00:00+00:00` | **Đóng lệnh:** `2017-03-17 03:00:00+00:00`
- **Entry Limit:** `1262.2304` | **SL:** `1262.2304` | **TP:** `1147.0` | **RR:** `1:4.97`
- **Vùng OB 4H:** `1240.9704 - 1271.5012` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 2 4H](charts/trade_2_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 2 LTF](charts/trade_2_ltf.png)

---

### Lệnh #3 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2017-05-17 21:00:00+00:00` | **Khớp Limit:** `2017-05-17 23:00:00+00:00` | **Đóng lệnh:** `2017-05-18 16:00:00+00:00`
- **Entry Limit:** `1875.2508` | **SL:** `1904.7077` | **TP:** `1406.432` | **RR:** `1:15.92`
- **Vùng OB 4H:** `1850.1001 - 1893.0792` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 3 4H](charts/trade_3_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 3 LTF](charts/trade_3_ltf.png)

---

### Lệnh #4 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2018-04-18 16:00:00+00:00` | **Khớp Limit:** `2018-04-18 17:00:00+00:00` | **Đóng lệnh:** `2018-04-18 20:00:00+00:00`
- **Entry Limit:** `8088.5` | **SL:** `8088.5` | **TP:** `8754.305` | **RR:** `1:3.0`
- **Vùng OB 4H:** `7910.5 - 8000.0` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 4 4H](charts/trade_4_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 4 LTF](charts/trade_4_ltf.png)

---

### Lệnh #5 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2018-06-06 16:00:00+00:00` | **Khớp Limit:** `2018-06-06 20:00:00+00:00` | **Đóng lệnh:** `2018-06-08 04:00:00+00:00`
- **Entry Limit:** `7645.7` | **SL:** `7645.7` | **TP:** `7156.0` | **RR:** `1:4.25`
- **Vùng OB 4H:** `7650.1 - 7739.9` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 5 4H](charts/trade_5_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 5 LTF](charts/trade_5_ltf.png)

---

### Lệnh #6 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2018-06-08 08:00:00+00:00` | **Khớp Limit:** `2018-06-08 09:00:00+00:00` | **Đóng lệnh:** `2018-06-08 16:00:00+00:00`
- **Entry Limit:** `7640.0` | **SL:** `7640.0` | **TP:** `7156.0` | **RR:** `1:4.01`
- **Vùng OB 4H:** `7650.1 - 7739.9` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 6 4H](charts/trade_6_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 6 LTF](charts/trade_6_ltf.png)

---

### Lệnh #7 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2018-06-09 13:00:00+00:00` | **Khớp Limit:** `2018-06-09 20:00:00+00:00` | **Đóng lệnh:** `2018-06-09 23:00:00+00:00`
- **Entry Limit:** `7645.0` | **SL:** `7645.0` | **TP:** `7156.0` | **RR:** `1:4.22`
- **Vùng OB 4H:** `7650.1 - 7739.9` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 7 4H](charts/trade_7_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 7 LTF](charts/trade_7_ltf.png)

---

### Lệnh #8 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2019-01-25 15:00:00+00:00` | **Khớp Limit:** `2019-01-25 16:00:00+00:00` | **Đóng lệnh:** `2019-01-25 18:00:00+00:00`
- **Entry Limit:** `3599.0` | **SL:** `3599.0` | **TP:** `3880.2179` | **RR:** `1:3.0`
- **Vùng OB 4H:** `3517.7 - 3586.3` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 8 4H](charts/trade_8_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 8 LTF](charts/trade_8_ltf.png)

---

### Lệnh #9 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2019-01-27 20:00:00+00:00` | **Khớp Limit:** `2019-01-27 21:00:00+00:00` | **Đóng lệnh:** `2019-01-27 22:00:00+00:00`
- **Entry Limit:** `3610.8` | **SL:** `3610.8` | **TP:** `3927.4179` | **RR:** `1:3.0`
- **Vùng OB 4H:** `3517.7 - 3586.3` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 9 4H](charts/trade_9_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 9 LTF](charts/trade_9_ltf.png)

---

### Lệnh #10 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2019-02-23 04:00:00+00:00` | **Khớp Limit:** `2019-02-23 10:00:00+00:00` | **Đóng lệnh:** `2019-02-23 17:00:00+00:00`
- **Entry Limit:** `3955.7` | **SL:** `3992.445` | **TP:** `3658.6` | **RR:** `1:8.09`
- **Vùng OB 4H:** `3957.7 - 3978.9` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 10 4H](charts/trade_10_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 10 LTF](charts/trade_10_ltf.png)

---

### Lệnh #11 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2020-06-18 20:00:00+00:00` | **Khớp Limit:** `2020-06-18 23:00:00+00:00` | **Đóng lệnh:** `2020-06-19 09:00:00+00:00`
- **Entry Limit:** `9409.4` | **SL:** `9409.4` | **TP:** `8908.5` | **RR:** `1:3.29`
- **Vùng OB 4H:** `9475.7 - 9523.1` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 11 4H](charts/trade_11_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 11 LTF](charts/trade_11_ltf.png)

---

### Lệnh #12 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2020-07-15 19:00:00+00:00` | **Khớp Limit:** `2020-07-15 20:00:00+00:00` | **Đóng lệnh:** `2020-07-16 06:00:00+00:00`
- **Entry Limit:** `9230.0` | **SL:** `9230.0` | **TP:** `8768.5786` | **RR:** `1:3.0`
- **Vùng OB 4H:** `9309.8 - 9364.5` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 12 4H](charts/trade_12_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 12 LTF](charts/trade_12_ltf.png)

---

### Lệnh #13 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2020-08-31 20:00:00+00:00` | **Khớp Limit:** `2020-08-31 21:00:00+00:00` | **Đóng lệnh:** `2020-08-31 22:00:00+00:00`
- **Entry Limit:** `11717.1` | **SL:** `11717.1` | **TP:** `11358.2079` | **RR:** `1:3.0`
- **Vùng OB 4H:** `11690.9 - 11804.5` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 13 4H](charts/trade_13_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 13 LTF](charts/trade_13_ltf.png)

---

### Lệnh #14 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2020-09-01 01:00:00+00:00` | **Khớp Limit:** `2020-09-01 02:00:00+00:00` | **Đóng lệnh:** `2020-09-01 06:00:00+00:00`
- **Entry Limit:** `11669.7` | **SL:** `11836.7307` | **TP:** `11168.6079` | **RR:** `1:3.0`
- **Vùng OB 4H:** `11690.9 - 11804.5` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 14 4H](charts/trade_14_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 14 LTF](charts/trade_14_ltf.png)

---

### Lệnh #15 — LONG | Kết quả: **WIN (+3.00R)**
- **Tín hiệu CHoCH:** `2020-10-18 23:00:00+00:00` | **Khớp Limit:** `2020-10-19 00:00:00+00:00` | **Đóng lệnh:** `2020-10-21 03:00:00+00:00`
- **Entry Limit:** `11486.7` | **SL:** `11486.7` | **TP:** `12150.4993` | **RR:** `1:3.0`
- **Vùng OB 4H:** `11298.5 - 11438.8` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 15 4H](charts/trade_15_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 15 LTF](charts/trade_15_ltf.png)

---

### Lệnh #16 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2021-07-17 09:00:00+00:00` | **Khớp Limit:** `2021-07-17 10:00:00+00:00` | **Đóng lệnh:** `2021-07-18 00:00:00+00:00`
- **Entry Limit:** `31581.2` | **SL:** `31581.2` | **TP:** `34616.9` | **RR:** `1:4.94`
- **Vùng OB 4H:** `31111.6 - 31761.9` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 16 4H](charts/trade_16_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 16 LTF](charts/trade_16_ltf.png)

---

### Lệnh #17 — LONG | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2021-07-18 21:00:00+00:00` | **Khớp Limit:** `2021-07-18 22:00:00+00:00` | **Đóng lệnh:** `2021-07-19 12:00:00+00:00`
- **Entry Limit:** `31698.8` | **SL:** `30966.2007` | **TP:** `34616.9` | **RR:** `1:3.98`
- **Vùng OB 4H:** `31111.6 - 31761.9` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 17 4H](charts/trade_17_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 17 LTF](charts/trade_17_ltf.png)

---

### Lệnh #18 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2021-09-02 14:00:00+00:00` | **Khớp Limit:** `2021-09-02 21:00:00+00:00` | **Đóng lệnh:** `2021-09-03 08:00:00+00:00`
- **Entry Limit:** `49834.7` | **SL:** `49834.7` | **TP:** `44000.1` | **RR:** `1:6.79`
- **Vùng OB 4H:** `50100.5 - 50483.9` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 18 4H](charts/trade_18_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 18 LTF](charts/trade_18_ltf.png)

---

### Lệnh #19 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-01-14 10:00:00+00:00` | **Khớp Limit:** `2022-01-14 14:00:00+00:00` | **Đóng lệnh:** `2022-01-15 12:00:00+00:00`
- **Entry Limit:** `42467.3` | **SL:** `42467.3` | **TP:** `36122.8979` | **RR:** `1:3.0`
- **Vùng OB 4H:** `42940.2 - 44379.5` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 19 4H](charts/trade_19_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 19 LTF](charts/trade_19_ltf.png)

---

### Lệnh #20 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-01-17 03:00:00+00:00` | **Khớp Limit:** `2022-01-17 07:00:00+00:00` | **Đóng lệnh:** `2022-01-20 14:00:00+00:00`
- **Entry Limit:** `42900.0` | **SL:** `42900.0` | **TP:** `37853.6979` | **RR:** `1:3.0`
- **Vùng OB 4H:** `42940.2 - 44379.5` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 20 4H](charts/trade_20_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 20 LTF](charts/trade_20_ltf.png)

---

### Lệnh #21 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-04-26 09:00:00+00:00` | **Khớp Limit:** `2022-04-26 10:00:00+00:00` | **Đóng lệnh:** `2022-04-26 12:00:00+00:00`
- **Entry Limit:** `40400.1` | **SL:** `40400.1` | **TP:** `38600.0` | **RR:** `1:3.05`
- **Vùng OB 4H:** `40240.7 - 40778.6` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 21 4H](charts/trade_21_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 21 LTF](charts/trade_21_ltf.png)

---

### Lệnh #22 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-06-10 00:00:00+00:00` | **Khớp Limit:** `2022-06-10 03:00:00+00:00` | **Đóng lệnh:** `2022-06-10 08:00:00+00:00`
- **Entry Limit:** `30023.1` | **SL:** `30023.1` | **TP:** `24945.1264` | **RR:** `1:3.0`
- **Vùng OB 4H:** `31276.4 - 31566.0` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 22 4H](charts/trade_22_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 22 LTF](charts/trade_22_ltf.png)

---

### Lệnh #23 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-07-02 12:00:00+00:00` | **Khớp Limit:** `2022-07-02 13:00:00+00:00` | **Đóng lệnh:** `2022-07-02 14:00:00+00:00`
- **Entry Limit:** `19282.3` | **SL:** `19282.3` | **TP:** `21865.0` | **RR:** `1:4.86`
- **Vùng OB 4H:** `18900.0 - 19302.6` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 23 4H](charts/trade_23_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 23 LTF](charts/trade_23_ltf.png)

---

### Lệnh #24 — LONG | Kết quả: **WIN (+5.47R)**
- **Tín hiệu CHoCH:** `2022-07-03 19:00:00+00:00` | **Khớp Limit:** `2022-07-04 01:00:00+00:00` | **Đóng lệnh:** `2022-07-08 01:00:00+00:00`
- **Entry Limit:** `19231.8` | **SL:** `19231.8` | **TP:** `21865.0` | **RR:** `1:5.47`
- **Vùng OB 4H:** `18900.0 - 19302.6` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 24 4H](charts/trade_24_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 24 LTF](charts/trade_24_ltf.png)

---

### Lệnh #25 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-07-08 02:00:00+00:00` | **Khớp Limit:** `2022-07-08 08:00:00+00:00` | **Đóng lệnh:** `2022-07-09 17:00:00+00:00`
- **Entry Limit:** `21762.1` | **SL:** `21762.1` | **TP:** `30796.5871` | **RR:** `1:3.0`
- **Vùng OB 4H:** `18900.0 - 19302.6` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 25 4H](charts/trade_25_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 25 LTF](charts/trade_25_ltf.png)

---

### Lệnh #26 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-07-13 23:00:00+00:00` | **Khớp Limit:** `2022-07-14 06:00:00+00:00` | **Đóng lệnh:** `2022-07-14 15:00:00+00:00`
- **Entry Limit:** `19979.0` | **SL:** `19979.0` | **TP:** `23664.1871` | **RR:** `1:3.0`
- **Vùng OB 4H:** `18900.0 - 19302.6` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 26 4H](charts/trade_26_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 26 LTF](charts/trade_26_ltf.png)

---

### Lệnh #27 — LONG | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2022-08-18 09:00:00+00:00` | **Khớp Limit:** `2022-08-18 14:00:00+00:00` | **Đóng lệnh:** `2022-08-19 01:00:00+00:00`
- **Entry Limit:** `23465.8` | **SL:** `22867.8529` | **TP:** `25259.6414` | **RR:** `1:3.0`
- **Vùng OB 4H:** `22979.8 - 23237.5` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 27 4H](charts/trade_27_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 27 LTF](charts/trade_27_ltf.png)

---

### Lệnh #28 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-09-01 23:00:00+00:00` | **Khớp Limit:** `2022-09-02 00:00:00+00:00` | **Đóng lệnh:** `2022-09-02 03:00:00+00:00`
- **Entry Limit:** `20161.0` | **SL:** `20161.0` | **TP:** `21950.7` | **RR:** `1:3.94`
- **Vùng OB 4H:** `19785.7 - 19938.7` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 28 4H](charts/trade_28_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 28 LTF](charts/trade_28_ltf.png)

---

### Lệnh #29 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-09-23 10:00:00+00:00` | **Khớp Limit:** `2022-09-23 13:00:00+00:00` | **Đóng lệnh:** `2022-09-23 22:00:00+00:00`
- **Entry Limit:** `19075.0` | **SL:** `19075.0` | **TP:** `17468.0586` | **RR:** `1:3.0`
- **Vùng OB 4H:** `19126.8 - 19472.6` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 29 4H](charts/trade_29_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 29 LTF](charts/trade_29_ltf.png)

---

### Lệnh #30 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2022-09-24 07:00:00+00:00` | **Khớp Limit:** `2022-09-24 12:00:00+00:00` | **Đóng lệnh:** `2022-09-24 21:00:00+00:00`
- **Entry Limit:** `19130.4` | **SL:** `19130.4` | **TP:** `17689.6586` | **RR:** `1:3.0`
- **Vùng OB 4H:** `19126.8 - 19472.6` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 30 4H](charts/trade_30_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 30 LTF](charts/trade_30_ltf.png)

---

### Lệnh #31 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2022-09-25 21:00:00+00:00` | **Khớp Limit:** `2022-09-26 00:00:00+00:00` | **Đóng lệnh:** `2022-09-27 01:00:00+00:00`
- **Entry Limit:** `18910.7` | **SL:** `19610.6471` | **TP:** `16810.8586` | **RR:** `1:3.0`
- **Vùng OB 4H:** `19126.8 - 19472.6` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 31 4H](charts/trade_31_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 31 LTF](charts/trade_31_ltf.png)

---

### Lệnh #32 — LONG | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2022-10-09 11:00:00+00:00` | **Khớp Limit:** `2022-10-09 19:00:00+00:00` | **Đóng lệnh:** `2022-10-10 22:00:00+00:00`
- **Entry Limit:** `19445.0` | **SL:** `19121.3114` | **TP:** `20416.0657` | **RR:** `1:3.0`
- **Vùng OB 4H:** `19180.0 - 19507.0` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 32 4H](charts/trade_32_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 32 LTF](charts/trade_32_ltf.png)

---

### Lệnh #33 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2022-12-03 22:00:00+00:00` | **Khớp Limit:** `2022-12-04 00:00:00+00:00` | **Đóng lệnh:** `2022-12-04 18:00:00+00:00`
- **Entry Limit:** `16972.4` | **SL:** `17185.75` | **TP:** `16044.3` | **RR:** `1:4.35`
- **Vùng OB 4H:** `17068.1 - 17133.4` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 33 4H](charts/trade_33_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 33 LTF](charts/trade_33_ltf.png)

---

### Lệnh #34 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-02-18 07:00:00+00:00` | **Khớp Limit:** `2023-02-18 12:00:00+00:00` | **Đóng lệnh:** `2023-02-19 08:00:00+00:00`
- **Entry Limit:** `24618.3` | **SL:** `24618.3` | **TP:** `21351.8` | **RR:** `1:4.74`
- **Vùng OB 4H:** `24648.4 - 25154.1` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 34 4H](charts/trade_34_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 34 LTF](charts/trade_34_ltf.png)

---

### Lệnh #35 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-02-21 13:00:00+00:00` | **Khớp Limit:** `2023-02-21 14:00:00+00:00` | **Đóng lệnh:** `2023-02-21 15:00:00+00:00`
- **Entry Limit:** `24658.3` | **SL:** `24658.3` | **TP:** `21351.8` | **RR:** `1:5.1`
- **Vùng OB 4H:** `24648.4 - 25154.1` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 35 4H](charts/trade_35_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 35 LTF](charts/trade_35_ltf.png)

---

### Lệnh #36 — SHORT | Kết quả: **WIN (+4.37R)**
- **Tín hiệu CHoCH:** `2023-02-21 21:00:00+00:00` | **Khớp Limit:** `2023-02-21 23:00:00+00:00` | **Đóng lệnh:** `2023-03-09 18:00:00+00:00`
- **Entry Limit:** `24570.8` | **SL:** `24570.8` | **TP:** `21351.8` | **RR:** `1:4.37`
- **Vùng OB 4H:** `24648.4 - 25154.1` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 36 4H](charts/trade_36_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 36 LTF](charts/trade_36_ltf.png)

---

### Lệnh #37 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2023-04-10 13:00:00+00:00` | **Khớp Limit:** `2023-04-10 15:00:00+00:00` | **Đóng lệnh:** `2023-04-10 16:00:00+00:00`
- **Entry Limit:** `28381.6` | **SL:** `28757.22` | **TP:** `27254.74` | **RR:** `1:3.0`
- **Vùng OB 4H:** `28508.7 - 28650.0` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 37 4H](charts/trade_37_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 37 LTF](charts/trade_37_ltf.png)

---

### Lệnh #38 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-04-28 13:00:00+00:00` | **Khớp Limit:** `2023-04-28 14:00:00+00:00` | **Đóng lệnh:** `2023-04-28 19:00:00+00:00`
- **Entry Limit:** `29337.9` | **SL:** `29337.9` | **TP:** `26913.4221` | **RR:** `1:3.0`
- **Vùng OB 4H:** `29078.4 - 30005.4` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 38 4H](charts/trade_38_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 38 LTF](charts/trade_38_ltf.png)

---

### Lệnh #39 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-04-30 01:00:00+00:00` | **Khớp Limit:** `2023-04-30 04:00:00+00:00` | **Đóng lệnh:** `2023-05-01 01:00:00+00:00`
- **Entry Limit:** `29263.6` | **SL:** `29263.6` | **TP:** `26616.2221` | **RR:** `1:3.0`
- **Vùng OB 4H:** `29078.4 - 30005.4` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 39 4H](charts/trade_39_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 39 LTF](charts/trade_39_ltf.png)

---

### Lệnh #40 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-05-04 12:00:00+00:00` | **Khớp Limit:** `2023-05-04 13:00:00+00:00` | **Đóng lệnh:** `2023-05-05 01:00:00+00:00`
- **Entry Limit:** `29143.0` | **SL:** `29143.0` | **TP:** `26133.8221` | **RR:** `1:3.0`
- **Vùng OB 4H:** `29078.4 - 30005.4` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 40 4H](charts/trade_40_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 40 LTF](charts/trade_40_ltf.png)

---

### Lệnh #41 — SHORT | Kết quả: **WIN (+3.00R)**
- **Tín hiệu CHoCH:** `2023-05-06 14:00:00+00:00` | **Khớp Limit:** `2023-05-07 01:00:00+00:00` | **Đóng lệnh:** `2023-05-12 06:00:00+00:00`
- **Entry Limit:** `29194.3` | **SL:** `29194.3` | **TP:** `26339.0221` | **RR:** `1:3.0`
- **Vùng OB 4H:** `29078.4 - 30005.4` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 41 4H](charts/trade_41_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 41 LTF](charts/trade_41_ltf.png)

---

### Lệnh #42 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-05-12 07:00:00+00:00` | **Khớp Limit:** `2023-05-12 09:00:00+00:00` | **Đóng lệnh:** `2023-05-14 00:00:00+00:00`
- **Entry Limit:** `26446.6` | **SL:** `26446.6` | **TP:** `17223.4429` | **RR:** `1:3.0`
- **Vùng OB 4H:** `29270.0 - 29431.2` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 42 4H](charts/trade_42_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 42 LTF](charts/trade_42_ltf.png)

---

### Lệnh #43 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-05-19 12:00:00+00:00` | **Khớp Limit:** `2023-05-19 14:00:00+00:00` | **Đóng lệnh:** `2023-05-21 12:00:00+00:00`
- **Entry Limit:** `26925.2` | **SL:** `26925.2` | **TP:** `27909.2729` | **RR:** `1:3.0`
- **Vùng OB 4H:** `26663.6 - 26859.9` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 43 4H](charts/trade_43_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 43 LTF](charts/trade_43_ltf.png)

---

### Lệnh #44 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2023-05-22 13:00:00+00:00` | **Khớp Limit:** `2023-05-22 17:00:00+00:00` | **Đóng lệnh:** `2023-05-24 03:00:00+00:00`
- **Entry Limit:** `26868.9` | **SL:** `26868.9` | **TP:** `27707.7` | **RR:** `1:3.09`
- **Vùng OB 4H:** `26663.6 - 26859.9` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 44 4H](charts/trade_44_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 44 LTF](charts/trade_44_ltf.png)

---

### Lệnh #45 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2024-01-07 23:00:00+00:00` | **Khớp Limit:** `2024-01-08 06:00:00+00:00` | **Đóng lệnh:** `2024-01-08 18:00:00+00:00`
- **Entry Limit:** `44146.4` | **SL:** `45720.1136` | **TP:** `39425.2593` | **RR:** `1:3.0`
- **Vùng OB 4H:** `43786.6 - 45450.0` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 45 4H](charts/trade_45_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 45 LTF](charts/trade_45_ltf.png)

---

### Lệnh #46 — LONG | Kết quả: **WIN (+3.00R)**
- **Tín hiệu CHoCH:** `2024-09-13 18:00:00+00:00` | **Khớp Limit:** `2024-09-16 13:00:00+00:00` | **Đóng lệnh:** `2024-11-11 19:00:00+00:00`
- **Entry Limit:** `58269.0` | **SL:** `58269.0` | **TP:** `85753.9714` | **RR:** `1:3.0`
- **Vùng OB 4H:** `49660.2 - 53185.6` (Cấu trúc 4H: `BULL`)

#### Khung cấu trúc HTF 4H
![Trade 46 4H](charts/trade_46_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 46 LTF](charts/trade_46_ltf.png)

---

### Lệnh #47 — SHORT | Kết quả: **LOSS (-1.00R)**
- **Tín hiệu CHoCH:** `2025-08-08 15:00:00+00:00` | **Khớp Limit:** `2025-08-08 17:00:00+00:00` | **Đóng lệnh:** `2025-08-10 15:00:00+00:00`
- **Entry Limit:** `116625.0` | **SL:** `118802.0729` | **TP:** `110093.7814` | **RR:** `1:3.0`
- **Vùng OB 4H:** `117898.3 - 118523.3` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 47 4H](charts/trade_47_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 47 LTF](charts/trade_47_ltf.png)

---

### Lệnh #48 — LONG | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2026-02-20 22:00:00+00:00` | **Khớp Limit:** `2026-02-21 00:00:00+00:00` | **Đóng lệnh:** `2026-02-22 13:00:00+00:00`
- **Entry Limit:** `67785.6` | **SL:** `67785.6` | **TP:** `74132.8693` | **RR:** `1:3.0`
- **Vùng OB 4H:** `66135.6 - 67160.6` (Cấu trúc 4H: `BEAR`)

#### Khung cấu trúc HTF 4H
![Trade 48 4H](charts/trade_48_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 48 LTF](charts/trade_48_ltf.png)

---

### Lệnh #49 — SHORT | Kết quả: **BE (+0.00R)**
- **Tín hiệu CHoCH:** `2026-03-01 16:00:00+00:00` | **Khớp Limit:** `2026-03-02 01:00:00+00:00` | **Đóng lệnh:** `2026-03-02 14:00:00+00:00`
- **Entry Limit:** `66783.5` | **SL:** `66783.5` | **TP:** `59534.1221` | **RR:** `1:3.0`
- **Vùng OB 4H:** `67810.6 - 68660.6` (Cấu trúc 4H: `SIDEWAY`)

#### Khung cấu trúc HTF 4H
![Trade 49 4H](charts/trade_49_4h.png)

#### Khung vào lệnh Limit LTF
![Trade 49 LTF](charts/trade_49_ltf.png)

---
