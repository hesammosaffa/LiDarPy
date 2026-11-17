# UDPSend.py
import socket
import struct
import threading
import time

class UDPSender:
    def __init__(self, plc_ip="192.168.109.1", plc_port=5000, my_ip="192.168.109.201", interval=0.01):
        self.PLC_IP = plc_ip
        self.PLC_PORT = plc_port
        self.MY_IP = my_ip
        self.SEND_INTERVAL = interval

        self.data = {
            "ID1": 100,
            "Pan_SetPos": 0.0, "Pan_Vel": 8000, "Pan_Acc": 40, "Pan_Dec": 40, "Pan_InitVal": 0.0,
            "Tilt_SetPos": 0.0, "Tilt_Vel": 8000, "Tilt_Acc": 40, "Tilt_Dec": 40, "Tilt_InitVal": 0.0,
            "Fire_Rate": 1, "R_Spare101": 0.0, "R_Spare102": 0.0, "R_Spare103": 0.0, "R_Spare104": 0.0,
            "Fire_Time": 200, "Control_Mode": 1,
            "Fire": [0]*16, "PB": [0,0,0,0,0,0,0,0], "ExtraBits": [0]*8, "ID2": 999
        }

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_error = None  

        try:
            self.sock.bind((self.MY_IP, 0))
            print(f"UDP Sender bound to {self.MY_IP}")
        except OSError as e:
            self.bind_error = f"Bind failed: {e}"
            print(self.bind_error)
            

        self.running = False
        self.thread = None

    def bits_to_byte(self, bits):
        value = 0
        for i, bit in enumerate(bits):
            value |= (bit & 1) << i
        return value.to_bytes(1, 'little')

    def update_position(self, pan_setpos, tilt_setpos,pan_vel,tilt_vel):
        self.data["Pan_SetPos"] = round(float(pan_setpos), 6)
        self.data["Tilt_SetPos"] = round(float(tilt_setpos), 6)
        self.data["Pan_Vel"] = round(float(pan_vel), 6)
        self.data["Tilt_Vel"] = round(float(tilt_vel), 6)

    #  -----------  cam_on---------------
    def cam_on(self, state):
        self.data["ExtraBits"][0] = 1 if state else 0    
    #  -----------  cam_off---------------
    def cam_off(self, state):
        self.data["ExtraBits"][1] = 1 if state else 0
    
    
    #  ----------- PB---------------
    def set_pb_ServoOn(self, state):
        self.data["PB"][0] = 1 if state else 0    

    def set_pb_ServoOff(self, state):
        self.data["PB"][1] = 1 if state else 0

    def set_pb_home(self, state):
        self.data["PB"][2] = 1 if state else 0    

    def set_pb_auto(self, state):
        self.data["PB"][6] = 1 if state else 0

    def set_pb_man(self, state):
        self.data["PB"][7] = 1 if state else 0

    #  ----------- PB---------------
    def Fire_Reset(self, state):
        self.data["Fire"][0] = 1 if state else 0 

    def Fire_Gun1(self, state):
        self.data["Fire"][1] = 1 if state else 0 

    #  ----------- PB---------------
    def Fire_Gun2(self, state):
        self.data["Fire"][2] = 1 if state else 0

    def Fire_Gun3(self, state):
        self.data["Fire"][3] = 1 if state else 0     

    def Fire1(self, state):
        self.data["Fire"][4] = 1 if state else 0   

    def Firing_Mode(self, state):
        self.data["Fire"][5] = 1 if state else 0

    def shooting_Number(self, number):

        self.data["Fire"][8:16] = [(number >> i) & 1 for i in range(8)]      

    def _send_loop(self):
        fmt = "<H15fIB"
        while self.running:
            try:
                #print(self.data)
                numeric_values = [
                    self.data["ID1"], self.data["Pan_SetPos"], self.data["Pan_Vel"], self.data["Pan_Acc"],
                    self.data["Pan_Dec"], self.data["Pan_InitVal"], self.data["Tilt_SetPos"], self.data["Tilt_Vel"],
                    self.data["Tilt_Acc"], self.data["Tilt_Dec"], self.data["Tilt_InitVal"], self.data["Fire_Rate"],
                    self.data["R_Spare101"], self.data["R_Spare102"], self.data["R_Spare103"], self.data["R_Spare104"],
                    self.data["Fire_Time"], self.data["Control_Mode"]
                ]

                packet = struct.pack(fmt, *numeric_values)
                packet += self.bits_to_byte(self.data["Fire"][:8])
                packet += self.bits_to_byte(self.data["Fire"][8:16])
                packet += self.bits_to_byte(self.data["PB"])
                packet += self.bits_to_byte(self.data["ExtraBits"])
                packet += struct.pack("<H", self.data["ID2"])
                

                #
                if self.bind_error is None:
                    self.sock.sendto(packet, (self.PLC_IP, self.PLC_PORT))
                # 

            except Exception as e:
                print(f"UDP Send Error: {e}")
            time.sleep(self.SEND_INTERVAL)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._send_loop, daemon=True)
            self.thread.start()
            print("UDP Sender thread started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        try:
            self.sock.close()
        except:
            pass
        print("UDP Sender stopped.")