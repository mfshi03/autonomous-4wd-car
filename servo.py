import time
from pca9685 import PCA9685

class Servo:
    def __init__(self):
        self.pwm_frequency = 50
        self.initial_pulse = 1500
        self.pwm_channel_map = {
            '0': 8,
            '1': 9,
            '2': 10,
            '3': 11,
            '4': 12,
            '5': 13,
            '6': 14,
            '7': 15
        }
        self.pwm_servo = PCA9685(0x40, debug=False)
        self.pwm_servo.set_pwm_freq(self.pwm_frequency)
        for channel in self.pwm_channel_map.values():
            self.pwm_servo.set_servo_pulse(channel, self.initial_pulse)
        self.current_angle = {ch: 90 for ch in self.pwm_channel_map}


    def set_servo_pwm(self, channel: str, angle: int, error: int = 10) -> None:
        angle = int(angle)
        if channel not in self.pwm_channel_map:
            raise ValueError(f"Invalid channel: {channel}. Valid channels are {list(self.pwm_channel_map.keys())}.")
        pulse = 2500 - int((angle + error) / 0.09) if channel == '0' else 500 + int((angle + error) / 0.09)
        self.pwm_servo.set_servo_pulse(self.pwm_channel_map[channel], pulse)
        self.current_angle[channel] = angle

    def move_servo_slow(self, channel, end_angle, step=1, delay=0.02):
        start_angle = self.current_angle[channel]
        direction = 1 if end_angle > start_angle else -1

        for angle in range(start_angle, end_angle, direction * step):
            self.set_servo_pwm(channel, angle)
            time.sleep(delay)

        self.set_servo_pwm(channel, end_angle)



# Main program logic follows:
if __name__ == '__main__':
    print("Now servos will rotate to 90 degree.")
    print("If they have already been at 90 degree, nothing will be observed.")
    print("Please keep the program running when installing the servos.")
    print("After that, you can press ctrl-C to end the program.")


    pwm_servo = Servo()

    try:
        print("Move to 0")
        pwm_servo.move_servo_slow('0', 0)
        time.sleep(3)
        print("Move to 90")
        pwm_servo.move_servo_slow('0', 90)
        time.sleep(3)
        print("Move to 180")
        pwm_servo.move_servo_slow('0', 180)

    except KeyboardInterrupt:
        print("\nEnd of program")