import cv2
import numpy as np
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
from camera import Camera
from motor import Ordinary_Car
from servo import Servo

class RobotApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Initialize Hardware
        self.car = Ordinary_Car()
        self.mount = Servo()
        self.cam = Camera(stream_size=(400, 300))
        self.cam.start_stream()

        # UI Elements
        self.label_video = tk.Label(window)
        self.label_video.pack(padx=10, pady=10)
        
        self.status_text = tk.StringVar(value="Status: Initializing...")
        self.label_status = tk.Label(window, textvariable=self.status_text, font=("Helvetica", 12))
        self.label_status.pack(pady=5)

        self.btn_quit = tk.Button(window, text="Stop & Exit", command=self.on_closing, bg="red", fg="white")
        self.btn_quit.pack(pady=10)

        # State variables
        self.current_frame = None
        self.running = True

        # Start Threads
        self.logic_thread = threading.Thread(target=self.robot_logic, daemon=True)
        self.logic_thread.start()
        
        # Start GUI Update Loop
        self.update_gui()

    def get_processed_frame(self):
        """Captures frame, finds red area, and draws a circle on it for the GUI."""
        frame_bytes = self.cam.get_frame()
        nparr = np.frombuffer(frame_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return 0, None

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255])) + \
               cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        area = 0
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)
            # Draw a green outline around the red object for the GUI
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, f"Red Area: {int(area)}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return area, img

    def robot_logic(self):
        """The background thread that controls the physical robot movements."""
        step_interval = 30
        settle_time = 0.2

        try:
            while self.running:
                self.status_text.set("Status: Scanning 0-180...")
                max_area = 0
                best_angle = 90

                for target_angle in range(0, 181, step_interval):
                    if not self.running: break
                    
                    self.mount.move_servo_slow('0', target_angle)
                    time.sleep(settle_time)

                    area, img = self.get_processed_frame()
                    self.current_frame = img # Update the frame shared with GUI

                    if area > max_area:
                        max_area = area
                        best_angle = target_angle
                        self.status_text.set(f"Target found at {best_angle}°")

                if max_area > 500:
                    self.status_text.set(f"LOCKED! Turning to {best_angle}°")
                    # Put your car movement logic here (same as your original code)
                    time.sleep(1) 
                else:
                    self.status_text.set("Status: No target found. Resting...")
                    time.sleep(1)

        except Exception as e:
            print(f"Logic Error: {e}")

    def update_gui(self):
        """Updates the Tkinter label with the latest frame at ~30 FPS."""
        if self.current_frame is not None:
            # Convert BGR (OpenCV) to RGB (Tkinter)
            img_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            
            self.label_video.imgtk = img_tk
            self.label_video.configure(image=img_tk)
        
        if self.running:
            self.window.after(30, self.update_gui)

    def on_closing(self):
        """Safely shuts down motors and camera."""
        print("Shutting down...")
        self.running = False
        self.car.set_motor_model(0,0,0,0)
        self.car.close()
        self.cam.close()
        self.window.destroy()

# --- Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root, "Robot Red-Object Tracker")
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()