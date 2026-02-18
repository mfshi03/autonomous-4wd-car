import cv2
import numpy as np
import time
from camera import Camera
from motor import Ordinary_Car
from servo import Servo

def get_red_area(cam):
    """Captures a frame and returns the area of the largest red object."""
    frame_bytes = cam.get_frame()
    nparr = np.frombuffer(frame_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return 0

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Define red range
    mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255])) + \
           cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        return cv2.contourArea(max(contours, key=cv2.contourArea))
    return 0

def main():
    car = Ordinary_Car()
    mount = Servo()
    cam = Camera(stream_size=(400, 300))
    cam.start_stream()
    step_interval = 30 # Your original 10-degree increments
    smooth_delay = 0.01 # Delay between individual degree movements
    settle_time = 0.2   # Time to wait before taking a picture
    current_angle = 0 # Assuming we start at 0

    try:
        while True:
            print("Scanning 0 to 180...")
            best_angle = 0
            max_area = 0


            for target_angle in range(0, 181, step_interval):
                # Move from current_angle to target_angle 1 degree at a time
                print(f"At angle {target_angle}")
                mount.move_servo_slow('0', target_angle)

                # Give the camera a moment to stabilize
                time.sleep(settle_time)

                # Check for the red object
                area = get_red_area(cam)
                if area > max_area:
                    print(f"Found RED at {target_angle} degrees!")
                    max_area = area
                    best_angle = target_angle

            if max_area > 500:
                print("FOUND RED > 500 px")

            # # 2. DECIDE: If enough red is found (threshold 500)
            # if max_area > 500:
            #     print(f"Target found at {best_angle} degrees. Rotating car...")

            #     # 3. ACT: Rotate chassis toward the best_angle
            #     # Logic: If angle < 90, target is to the right. If > 90, to the left.
            #     # Adjust sleep time based on your car's turn speed.
            #     if best_angle < 80:
            #         car.set_motor_model(2000, 2000, -2000, -2000) # Spin Right
            #         time.sleep(abs(90 - best_angle) / 60) # Rough estimate for turn time
            #     elif best_angle > 100:
            #         car.set_motor_model(-2000, -2000, 2000, 2000) # Spin Left
            #         time.sleep(abs(90 - best_angle) / 60)

            #     car.set_motor_model(0, 0, 0, 0) # Stop rotating

            #     # 4. RESET: Pan camera mount back to center (90)
            #     print("Resetting camera mount to center.")
            #     mount.set_servo_pwm('0', 90)
            #     time.sleep(0.5)

            #     # Move closer to the target now that we face it
            #     car.set_motor_model(1800, 1800, 1800, 1800) # Forward
            #     time.sleep(1)
            #     car.set_motor_model(0, 0, 0, 0)
            # else:
            #     print("No red target found in scan.")
            #     time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        car.close()
        cam.close()

if __name__ == "__main__":
    main()