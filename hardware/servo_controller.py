import board
from adafruit_pca9685 import PCA9685

# Bộ điều khiển servo qua PCA9685, quản lý toàn bộ 16 kênh
class ServoKit:
    def __init__(self, *, channels, freq, i2c=None, address=0x40, reference_clock_speed=25000000):
        if channels not in [8, 16]:
            raise ValueError("servo_channels must be 8 or 16!")

        self._servo_instances = [None] * channels
        self._num_channels = channels

        if i2c is None:
            i2c = board.I2C()

        self._pca = PCA9685(i2c, address=address, reference_clock_speed=reference_clock_speed)
        self._pca.frequency = freq

        self._servo = _ServoManager(self)

    @property
    def servo(self):
        # Truy cập qua: servo_kit.servo[0]
        return self._servo


# Bộ quản lý truy cập từng kênh servo cụ thể (dạng mảng)
class _ServoManager:
    def __init__(self, kit: ServoKit):
        self._kit = kit

    def __getitem__(self, channel):
        if channel >= self._kit._num_channels or channel < 0:
            raise ValueError(f"Servo channel must be 0 to {self._kit._num_channels - 1}!")

        servo = self._kit._servo_instances[channel]

        if servo is None:
            pwm_channel = self._kit._pca.channels[channel]
            servo = Servo(pwm_channel)
            self._kit._servo_instances[channel] = servo
            return servo

        if isinstance(servo, Servo):
            return servo

        raise ValueError(f"Channel {channel} is already in use.")


# Lớp điều khiển một servo duy nhất: góc, tỷ lệ xung, relax,...
class Servo:
    def __init__(self, pwm_out, *, start_angle=0, end_angle=180, min_pulse=750, max_pulse=2250):
        self._pwm_out = pwm_out
        self._last_fraction = None

        self.set_pulse_width_range(min_pulse, max_pulse)
        self.set_actuation_range(start_angle, end_angle)

    def set_actuation_range(self, start_angle, end_angle):
        """Gán dải góc hoạt động: ví dụ 0–180 độ"""
        self._start_angle = start_angle
        self._end_angle = end_angle
        self._angle_range = end_angle - start_angle

    def set_pulse_width_range(self, min_pulse=750, max_pulse=2250):
        """Thiết lập khoảng xung PWM theo micro giây"""
        self._min_pulse = min_pulse
        self._max_pulse = max_pulse

        self._min_duty = int((min_pulse * self._pwm_out.frequency) / 1_000_000 * 0xFFFF)
        max_duty = int((max_pulse * self._pwm_out.frequency) / 1_000_000 * 0xFFFF)
        self._duty_range = max_duty - self._min_duty

    @property
    def channel(self):
        return self._pwm_out._index

    @property
    def min_pulse(self):
        return self._min_pulse

    @property
    def max_pulse(self):
        return self._max_pulse

    @property
    def fraction(self):
        """Trả về vị trí servo dưới dạng tỉ lệ 0.0–1.0"""
        if self._pwm_out.duty_cycle == 0 and self._min_duty != 0:
            return self._last_fraction
        return (self._pwm_out.duty_cycle - self._min_duty) / self._duty_range

    @fraction.setter
    def fraction(self, value):
        if value is None:
            self._pwm_out.duty_cycle = 0
            self._last_fraction = None
            return
        if not 0.0 <= value <= 1.0:
            raise ValueError("Fraction must be between 0.0 and 1.0")
        self._pwm_out.duty_cycle = self._min_duty + int(value * self._duty_range)

    @property
    def angle(self):
        """Trả về góc hiện tại của servo (None nếu đang relax)"""
        if self.fraction is None:
            return None
        return self._angle_range * self.fraction + self._start_angle

    @angle.setter
    def angle(self, new_angle):
        """Thiết lập góc servo, nằm trong khoảng khai báo"""
        if new_angle is None:
            self.fraction = None
            return
        if self._start_angle <= new_angle <= self._end_angle or self._start_angle >= new_angle >= self._end_angle:
            self.fraction = (new_angle - self._start_angle) / self._angle_range
        else:
            raise ValueError("Angle out of range")

    def relax(self):
        """Tạm ngắt servo, không gửi tín hiệu (duty = 0)"""
        self._last_fraction = self.fraction
        self._pwm_out.duty_cycle = 0
