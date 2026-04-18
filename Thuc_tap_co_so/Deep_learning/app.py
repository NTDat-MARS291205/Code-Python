from flask import Flask, render_template, request
import numpy as np
import joblib
import json
import os

app = Flask(__name__)

# Lấy đường dẫn thư mục hiện tại của file app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model và các file cần thiết
model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))
job_encoder = joblib.load(os.path.join(BASE_DIR, "job_encoder.pkl"))
label_encoder = joblib.load(os.path.join(BASE_DIR, "label_encoder.pkl"))

# Load file guide với encoding UTF-8 (tránh lỗi UnicodeDecodeError)
with open(os.path.join(BASE_DIR, "kb_healthGuide.json"), "r", encoding="utf-8") as f:
    guide = json.load(f)


# Trang chủ
@app.route('/')
def home():
    return render_template("index.html")


# Xử lý dự đoán
@app.route('/predict', methods=['POST'])
def predict():

    job = request.form['job']
    age = float(request.form['age'])
    height = float(request.form['height'])
    weight = float(request.form['weight'])

    # encode job
    job_encoded = job_encoder.transform([job])[0]

    # tạo input cho model
    X = np.array([[job_encoded, age, height, weight]])
    X = scaler.transform(X)

    # dự đoán
    pred = model.predict(X)

    # decode label
    label = label_encoder.inverse_transform(pred)[0]

    # lấy guide tương ứng
    health = guide.get(label, "No guide available")

    return render_template(
        "index.html",
        result=label,
        guide=health
    )


# chạy web
if __name__ == "__main__":
    app.run(debug=True)