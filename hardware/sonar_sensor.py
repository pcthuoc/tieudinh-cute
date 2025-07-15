import time
import threading
import board
import busio
import adafruit_vl53l0x

class SonarSensor:
    """
    Cảm biến khoảng cách VL53L0X sử dụng I2C.
    Tự động cập nhật giá trị trong luồng riêng.
    Hỗ trợ gắn callback khi có vật thể đến gần hoặc rời đi.
    """

    def __init__(self, max_distance=0.5, threshold_distance=0.1, interval=0.2):
        """
        max_distance: khoảng cách tối đa (m) → sẽ giới hạn readings
        threshold_distance: ngưỡng để kích hoạt callback (m)
        interval: thời gian giữa 2 lần đọc (giây)
        """
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl53l0x.VL53L0X(self.i2c)

        self.max_distance = max_distance * 1000  # chuyển sang mm
        self.threshold_distance = threshold_distance * 1000  # mm
        self.interval = interval

        self._distance = self.max_distance
        self._last_distance = self.max_distance

        self.when_in_range = None   # callback khi có vật đến gần
        self.when_out_of_range = None  # callback khi vật rời đi

        self._run_flag = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def __del__(self):
        self.close()

    def close(self):
        """Dừng luồng đọc cảm biến."""
        self._run_flag = False
        self._thread.join(timeout=3)

    def _run_loop(self):
        """Luồng riêng đọc cảm biến định kỳ"""
        while self._run_flag:
            time.sleep(self.interval)
            self._update_distance()

    def _update_distance(self):
        """Đọc dữ liệu cảm biến và xử lý sự kiện nếu vượt ngưỡng"""
        try:
            distance = self.sensor.range  # mm
        except Exception as e:
            print("Sonar sensor error:", e)
            return

        self._last_distance = self._distance
        self._distance = min(distance, self.max_distance)

        # Khi vượt ngưỡng từ gần → xa
        if self._distance > self.threshold_distance >= self._last_distance:
            if self.when_out_of_range:
                self.when_out_of_range()

        # Khi vượt ngưỡng từ xa → gần
        elif self._distance < self.threshold_distance <= self._last_distance:
            if self.when_in_range:
                self.when_in_range()

    @property
    def distance(self):
        """Trả về khoảng cách gần nhất đo được (mm)"""
        return self._distance
