# ============================================================
#   CHUONG 3: DU DOAN GIA CO PHIEU VOI RNN — KAGGLE NOTEBOOK
#   Dataset: Tesla Stock Price Data (2000-2025)
#   Dataset path: kaggle.com/datasets/taimoor888/tesla-stock-price-data-2000-2025
#   Bai toan: Dung 60 ngay truoc -> du doan gia dong cua ngay tiep theo
# ============================================================

# -- BUOC 1: IMPORT THU VIEN
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error, r2_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
from tensorflow.keras.callbacks import (ModelCheckpoint, EarlyStopping,
                                        ReduceLROnPlateau)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
print("Thu vien da san sang!")

# -- BUOC 2: KIEM TRA VA DOC DATASET
files = glob.glob('/kaggle/input/**/*.csv', recursive=True)
print("\nCac file CSV tim thay:")
for f in files:
    print(f"  {f}")

# File co 3 dong header rac -> skiprows=3
df = pd.read_csv(files[0], skiprows=3, header=None,
                 names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

df = df.sort_values('Date').reset_index(drop=True)

for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna().reset_index(drop=True)

print(f"\nShape : {df.shape}")
print(f"Tu    : {df['Date'].min().date()}  ->  {df['Date'].max().date()}")
print(df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].head())

# -- BUOC 3: TIEN XU LY
close_prices = df['Close'].values.reshape(-1, 1)
print(f"\nSo ngay giao dich : {len(close_prices)}")
print(f"Gia min : {close_prices.min():.2f} | Gia max : {close_prices.max():.2f}")

plt.figure(figsize=(14, 4))
plt.plot(df['Date'], close_prices, color='red', linewidth=1)
plt.title('Gia dong cua Tesla (2000-2025)')
plt.xlabel('Nam')
plt.ylabel('Gia (USD)')
plt.tight_layout()
plt.savefig('/kaggle/working/tesla_full_price.png', dpi=150)
plt.show()

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(close_prices)

# -- BUOC 4: TAO SEQUENCES
LOOK_BACK = 60

def create_sequences(data, look_back=60):
    X, Y = [], []
    for i in range(look_back, len(data)):
        X.append(data[i - look_back:i, 0])
        Y.append(data[i, 0])
    return np.array(X), np.array(Y)

X, Y = create_sequences(scaled_data, LOOK_BACK)
X = X.reshape(X.shape[0], X.shape[1], 1)

split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
Y_train, Y_test = Y[:split], Y[split:]

print(f"\nX_train : {X_train.shape} | Y_train : {Y_train.shape}")
print(f"X_test  : {X_test.shape}  | Y_test  : {Y_test.shape}")

# -- BUOC 5: XAY DUNG MODEL RNN
# SimpleRNN — kien truc tuong duong LSTM de so sanh cong bang
# LSTM dung 128 + 64 units -> RNN dung 128 + 64 units
def get_rnn_model():
    model = Sequential([
        # RNN layer 1 — 128 units
        SimpleRNN(128, return_sequences=True, input_shape=(LOOK_BACK, 1),
                  activation='tanh'),
        Dropout(0.3),

        # RNN layer 2 — 64 units
        SimpleRNN(64, return_sequences=False, activation='tanh'),
        Dropout(0.3),

        # Output layer
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_absolute_error',
                  metrics=['mae'])
    return model

rnn_model = get_rnn_model()
rnn_model.summary()

# -- BUOC 6: CALLBACKS
best_weights_path = '/kaggle/working/best_rnn_weights.weights.h5'

callbacks = [
    ModelCheckpoint(best_weights_path,
                    monitor='val_loss', verbose=1,
                    save_best_only=True, save_weights_only=True, mode='min'),
    EarlyStopping(monitor='val_loss', patience=10,
                  restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                      patience=5, verbose=1, min_lr=1e-7)
]

# -- BUOC 7: TRAIN MODEL
print("\nBat dau training RNN...\n")
history = rnn_model.fit(
    X_train, Y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.1,
    callbacks=callbacks,
    verbose=1
)

# -- BUOC 8: DU DOAN
rnn_model.load_weights(best_weights_path)

Y_train_pred_scaled = rnn_model.predict(X_train, verbose=0)
Y_test_pred_scaled  = rnn_model.predict(X_test,  verbose=0)

Y_train_pred = scaler.inverse_transform(Y_train_pred_scaled)
Y_test_pred  = scaler.inverse_transform(Y_test_pred_scaled)
Y_train_true = scaler.inverse_transform(Y_train.reshape(-1, 1))
Y_test_true  = scaler.inverse_transform(Y_test.reshape(-1, 1))

# -- BUOC 9: DANH GIA MODEL
def print_metrics(y_true, y_pred, label):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae  = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    r2   = r2_score(y_true, y_pred)
    print(f"\n{'='*45}")
    print(f"KET QUA DANH GIA - {label}")
    print(f"{'='*45}")
    print(f"  RMSE : {rmse:.4f}")
    print(f"  MAE  : {mae:.4f}")
    print(f"  MAPE : {mape:.2f}%")
    print(f"  R2   : {r2:.4f}  ({'Tot' if r2 > 0.9 else 'Trung binh'})")
    print(f"{'='*45}")
    return {'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'R2': r2}

train_metrics = print_metrics(Y_train_true, Y_train_pred, "TAP TRAIN (RNN)")
test_metrics  = print_metrics(Y_test_true,  Y_test_pred,  "TAP TEST  (RNN)")

# -- BUOC 10: DU DOAN GIA NGAY TIEP THEO
last_60 = scaled_data[-LOOK_BACK:]
x_next  = last_60.reshape(1, LOOK_BACK, 1)

next_pred_scaled = rnn_model.predict(x_next, verbose=0)
next_pred_price  = scaler.inverse_transform(next_pred_scaled)[0][0]

next_date         = df['Date'].iloc[-1] + pd.Timedelta(days=1)
actual_last_price = df['Close'].iloc[-1]

print(f"\n{'='*45}")
print(f"DU DOAN GIA NGAY TIEP THEO (RNN)")
print(f"{'='*45}")
print(f"  Ngay cuoi dataset : {df['Date'].iloc[-1].date()}")
print(f"  Gia dong cua thuc : ${actual_last_price:.2f}")
print(f"  Ngay du doan      : {next_date.date()}")
print(f"  Gia du doan       : ${next_pred_price:.2f}")
diff = next_pred_price - actual_last_price
print(f"  Chenh lech        : {'tang' if diff > 0 else 'giam'} ${abs(diff):.2f}")
print(f"{'='*45}")

# -- BUOC 11: VE DO THI
train_dates = df['Date'].iloc[LOOK_BACK:split + LOOK_BACK]
test_dates  = df['Date'].iloc[split + LOOK_BACK:]

fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# 1. Toan bo: thuc te vs du doan
axes[0, 0].plot(df['Date'],  close_prices,  label='Gia thuc te',     color='red',    linewidth=1.5)
axes[0, 0].plot(train_dates, Y_train_pred,  label='Du doan (train)', color='green',  linestyle='--')
axes[0, 0].plot(test_dates,  Y_test_pred,   label='Du doan (test)',  color='blue',   linestyle='--')
axes[0, 0].scatter([next_date], [next_pred_price],
                   color='orange', zorder=5, s=80,
                   label=f'Ngay tiep theo: ${next_pred_price:.2f}')
axes[0, 0].set_title('RNN - Du doan vs Thuc te (Train + Test)')
axes[0, 0].set_xlabel('Thoi gian')
axes[0, 0].set_ylabel('Gia (USD)')
axes[0, 0].legend()
axes[0, 0].grid(True)

# 2. Zoom test set
axes[0, 1].plot(test_dates, Y_test_true, label='Gia thuc te', color='steelblue', linewidth=2)
axes[0, 1].plot(test_dates, Y_test_pred, label='Gia du doan', color='seagreen',  linestyle='--')
axes[0, 1].set_title('RNN - Zoom Test Set')
axes[0, 1].set_xlabel('Thoi gian')
axes[0, 1].set_ylabel('Gia (USD)')
axes[0, 1].legend()
axes[0, 1].grid(True)

# 3. Loss
axes[1, 0].plot(history.history['loss'],     'b-o', label='Train Loss', markersize=4)
axes[1, 0].plot(history.history['val_loss'], 'r-o', label='Val Loss',   markersize=4)
axes[1, 0].set_title('Loss qua cac epoch')
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].set_ylabel('MAE Loss')
axes[1, 0].legend()
axes[1, 0].grid(True)

# 4. MAE
axes[1, 1].plot(history.history['mae'],     'b-o', label='Train MAE', markersize=4)
axes[1, 1].plot(history.history['val_mae'], 'r-o', label='Val MAE',   markersize=4)
axes[1, 1].set_title('MAE qua cac epoch')
axes[1, 1].set_xlabel('Epoch')
axes[1, 1].set_ylabel('MAE')
axes[1, 1].legend()
axes[1, 1].grid(True)

plt.suptitle('RNN - Du doan gia co phieu Tesla (2000-2025)',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('/kaggle/working/rnn_results.png', dpi=150)
plt.show()
print("Do thi RNN da duoc luu!")

# -- BUOC 12: BANG SO SANH RNN vs LSTM
# Dien ket qua LSTM cua ban vao day de so sanh
# (lay tu output cua notebook LSTM truoc do)
print(f"\n{'='*55}")
print(f"BANG SO SANH: RNN vs LSTM (TAP TEST)")
print(f"{'='*55}")
print(f"  {'Chi so':<10} {'RNN':>12} {'LSTM':>12} {'Tot hon'}")
print(f"  {'-'*50}")

# Ket qua RNN (tu bien test_metrics)
rnn_rmse = test_metrics['RMSE']
rnn_mae  = test_metrics['MAE']
rnn_mape = test_metrics['MAPE']
rnn_r2   = test_metrics['R2']

# Placeholder LSTM — thay bang ket qua thuc te cua ban
lstm_rmse = 0.0  # <- dien ket qua LSTM vao day
lstm_mae  = 0.0
lstm_mape = 0.0
lstm_r2   = 0.0

print(f"  {'RMSE':<10} {rnn_rmse:>12.4f} {lstm_rmse:>12.4f}  {'RNN' if rnn_rmse < lstm_rmse else 'LSTM'}")
print(f"  {'MAE':<10} {rnn_mae:>12.4f}  {lstm_mae:>12.4f}  {'RNN' if rnn_mae  < lstm_mae  else 'LSTM'}")
print(f"  {'MAPE(%)':<10} {rnn_mape:>11.2f}% {lstm_mape:>11.2f}%  {'RNN' if rnn_mape < lstm_mape else 'LSTM'}")
print(f"  {'R2':<10} {rnn_r2:>12.4f} {lstm_r2:>12.4f}  {'RNN' if rnn_r2   > lstm_r2   else 'LSTM'}")
print(f"{'='*55}")
print("  (Dien ket qua LSTM thuc te vao cac bien lstm_* de so sanh)")

# -- BUOC 13: LUU MODEL
rnn_model.save('/kaggle/working/rnn_stock_model.h5')
print("\nModel RNN da duoc luu: /kaggle/working/rnn_stock_model.h5")
print("-> Vao tab Output de tai file ve may!")