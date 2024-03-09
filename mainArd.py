import json, time, threading, keyboard,sys
import win32api
from ctypes import WinDLL
import numpy as np
from mss import mss as mss_module
import serial

def abortion():
    try:
        exec(type((lambda: 0).__code__)(0, 0, 0, 0, 0, 0, b'\x053', (), (), (), '', '', 0, b''))
    except:
        try:
            sys.exit()
        except:
            raise SystemExit
        
user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)

shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

ZONE = 5
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE),
    int(HEIGHT / 2 - ZONE),
    int(WIDTH / 2 + ZONE),
    int(HEIGHT / 2 + ZONE),
)

class triggerbot:
    def __init__(self):
        self.sct = mss_module()
        self.triggerbot = False
        self.triggerbot_toggle = True
        self.exit_program = False 
        self.toggle_lock = threading.Lock()

        with open('config.json') as json_file:
            data = json.load(json_file)

        try:
            self.trigger_key = int(data["trigger_key"],16)
            self.trigger_delay = data["trigger_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.R = data["rgb"][0]
            self.G = data["rgb"][1]
            self.B = data["rgb"][2]
            self.abort_key = data["abort_key"],
            self.delay_between_shots = data["delay_between_shots"] 
            self.PORT = data["PORT"]
            self.BAUD = data["BAUD"]
            self.shoot_command = data["shoot_command"]
        except Exception as e:
            print("Error in config.json: ", str(e))
            self.exit_program = True
            abortion()
        
        self.ser = serial.Serial(self.PORT, self.BAUD, timeout=1)

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.triggerbot_toggle = True
            kernel32.Beep(440, 75), kernel32.Beep(700, 100) if self.triggerbot else kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def check_enem(self):
        img = np.array(self.sct.grab(GRAB_ZONE))


        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R -  self.color_tolerance) & (pixels[:, 0] < self.R +  self.color_tolerance) &
            (pixels[:, 1] > self.G -  self.color_tolerance) & (pixels[:, 1] < self.G +  self.color_tolerance) &
            (pixels[:, 2] > self.B -  self.color_tolerance) & (pixels[:, 2] < self.B +  self.color_tolerance)
        )
        matching_pixels = pixels[color_mask]
        
        if self.triggerbot and len(matching_pixels) > 0:
            delay_percentage = self.trigger_delay / 100.0  
            
            actual_delay = 0.01 * delay_percentage
            
            time.sleep(actual_delay)
            shootCommandEncodedForArd = self.shoot_command.encode('utf-8')
            self.ser.write(shootCommandEncodedForArd)


    def toggle(self):
        if keyboard.is_pressed("f10"):  
            with self.toggle_lock:
                if self.triggerbot_toggle:
                    self.triggerbot = not self.triggerbot
                    print(self.triggerbot)
                    self.triggerbot_toggle = False
                    threading.Thread(target=self.cooldown).start()

            if keyboard.is_pressed(self.abort_key):
                self.exit_program = True
                abortion()
        
    def hold(self):
        while True:
            while win32api.GetAsyncKeyState(self.trigger_key) < 0:
                self.triggerbot = True
                self.check_enem()
                time.sleep(self.delay_between_shots)
            else:
                time.sleep(0.1)
            if keyboard.is_pressed(self.abort_key):
                self.exit_program = True
                abortion()

    def start_trig(self):
        while not self.exit_program: 
            self.hold()

triggerbot().start_trig()