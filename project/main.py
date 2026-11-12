import network
import urequests
import time
from machine import I2C, Pin
import ssd1306

# 1. Wi-Fi Credentials
WIFI_SSID = "Zubair"
WIFI_PASS = "753812221"

# 2. Firebase URL (matches the /esp32/users.json path)
FIREBASE_URL = "https://proto-cbb4e-default-rtdb.asia-southeast1.firebasedatabase.app/esp32/users.json"

# 3. Initialize OLED (SCK -> GPIO 22, SDA -> GPIO 21)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def show_message(line1, line2="", line3=""):
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 22)
    oled.text(line3, 0, 44)
    oled.show()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        show_message("Connecting WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
    show_message("WiFi Connected!", wlan.ifconfig()[0])
    time.sleep(1)

connect_wifi()

while True:
    try:
        response = urequests.get(FIREBASE_URL)
        data = response.json()
        response.close()

        if data and isinstance(data, dict):
            # Convert Firebase dictionary of push-IDs into a list of user records
            users = list(data.values())
            total = len(users)

            # Roll through every stored user on the OLED
            for index, user in enumerate(users):
                name = str(user.get("name", "No Name"))
                reg = str(user.get("regNumber", "No Reg"))

                # Slide-in roll effect from right to left
                for x_offset in range(128, -1, -16):
                    oled.fill(0)
                    oled.text("User {}/{}".format(index + 1, total), 0, 0)
                    oled.text(name, x_offset, 24)
                    oled.text(reg, x_offset, 44)
                    oled.show()
                    time.sleep(0.03)

                # Pause 3 seconds so the user can be read clearly
                time.sleep(3)
        else:
            show_message("No users found", "Submit on web")
            time.sleep(3)

    except Exception as e:
        show_message("Fetch Error", "Retrying...")
        time.sleep(3)
