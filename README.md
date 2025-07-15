# 🤖 RCute Robot - Emotion-Aware AI Robot Framework

Một hệ thống robot cảm xúc mini điều hướng được, tích hợp:
- Wake word
- Speech-to-text (cloud)
- ChatGPT / trợ lý hội thoại
- Emotion engine (dựa vào hội thoại + hành vi)
- Cloud TTS
- Điều khiển servo, motor, sonar tránh vật cản
- Giao diện cảm xúc OLED / màn nhỏ
- Giao tiếp WebSocket/Web API

---

## 🧠 Mục tiêu hệ thống

- Robot tương tác bằng lời nói
- Có cảm xúc và biểu cảm theo tình huống
- Có thể quay về trạm sạc khi cần
- Có thể mở rộng thêm module (camera, map, theo dõi,...)

---

## 📁 Cấu trúc project

```bash
rcute-robot/
├── main/                  # Vòng lặp chính, asyncio orchestrator
├── domain/                # Logic trung tâm: RobotAssistant, trạng thái, router
├── services/              # Các dịch vụ AI: STT, TTS, ChatGPT, Emotion
├── hardware/              # Giao tiếp phần cứng: Servo, Motor, Sonar, OLED
├── interface/             # Web UI (Sanic + WebSocket)
├── config/                # Cấu hình JSON (GPIO, servo, emotion,...)
├── assets/                # Icon biểu cảm, âm thanh,...
├── scripts/               # Autostart, benchmark, tiện ích CLI
├── tests/                 # Unit test
└── requirements.txt
```


## ✅ Tiến độ thực hiện

### 📅 Tiến độ ngày 2025-07-15

#### 📁 Cấu hình hệ thống

- Đã tạo file `hardware_config.json` trong thư mục `config/`, định nghĩa đầy đủ các chân phần cứng bao gồm: `touch`, `ir`, `motor`, `servo`, `screen`, `sonar`.
- Xây dựng class `HardwareConfig` trong `hardware_config.py` để load file JSON và truy cập từng thành phần bằng các thuộc tính như:  
  `config.servo_config`, `config.motor_pins`, `config.ir_pins`,...

#### ⚙️ Module phần cứng

- **Hoàn thành module `servo_controller.py`:**
  - Tạo class `ServoKit` quản lý toàn bộ kênh servo của PCA9685.
  - Tạo class `Servo` hỗ trợ điều chỉnh góc, pulse, relax servo.
  - Chuẩn hóa theo PEP8, bổ sung chú thích rõ ràng.

- **Hoàn thành module `sonar_sensor.py`:**
  - Điều khiển cảm biến khoảng cách VL53L0X qua I2C.
  - Tự động đọc giá trị trong một luồng riêng (thread).
  - Hỗ trợ callback `when_in_range` và `when_out_of_range`.

#### 🧠 Cấu trúc & định hướng

- Hoàn thiện sơ đồ tổ chức dự án `rcute-robot`:
  - Phân chia rõ ràng các module theo nhiệm vụ (`main/`, `domain/`, `services/`, `hardware/`, `interface/`,...).
  - Tổ chức chuẩn theo mô hình hướng đối tượng (OOP), dễ mở rộng.

- Định hướng sử dụng `asyncio` làm nền để chạy song song:
  - Vòng lặp chính `robot_loop`
  - Server web `Sanic` xử lý WebSocket hoặc REST

- Cập nhật `README.md`:
  - Mô tả mục tiêu, cấu trúc project, phần cứng hỗ trợ, tiến độ hiện tại và kế hoạch tiếp theo.
