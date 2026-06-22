import time

from adafruit_blinka.microcontroller.generic_linux.spi import SPI

import neopixel_spi

import busio

import board

import subprocess

import spidev

class LinuxSPI:
    def __init__(self, bus, device=0):
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._locked = False
        self.frequency = 6400000

    def try_lock(self):
        if self._locked:
            return False
        self._locked = True
        return True

    def unlock(self):
        self._locked = False

    def configure(self, *, baudrate=6400000, polarity=0, phase=0, bits=8):
        self.frequency = baudrate
        self._spi.max_speed_hz = baudrate
        self._spi.mode = (polarity << 1) | phase
        self._spi.bits_per_word = bits

    def write(self, buf, start=0, end=None):
        if end is None:
            end = len(buf)
        data = buf[start:end]
        if hasattr(self._spi, "writebytes2"):
            self._spi.writebytes2(data)
        else:
            self._spi.writebytes(list(data))

cpp_proc=subprocess.Popen(
    ["/home/iresx/powergrid_demo/USB-RELAY(SourceCodeProjet2)/build/usbrelay"],
    stdin=subprocess.PIPE,
    text=True
)
current_time = time.monotonic()

start_time = time.monotonic()

LED_COUNT_MAIN = 30

LED_COUNT_BACKUP = 30

spi_main = LinuxSPI(0, 0)    # /dev/spidev10.0 GPIO PIN 10
spi_backup = LinuxSPI(3, 0)   # /dev/spidev3.0 GPIO PIN 6

main_branch = neopixel_spi.NeoPixel_SPI(
    spi_main,
    LED_COUNT_MAIN,
    brightness=0.5,
    auto_write=True,
    pixel_order=neopixel_spi.RGB
)

backup_branch = neopixel_spi.NeoPixel_SPI(
    spi_backup,
    LED_COUNT_BACKUP,
    brightness=0.5,
    auto_write=True,
    pixel_order=neopixel_spi.RGB
)


BPP = 3 
# Bytes per pixel. 3 for RGB and 4 for RGBW pixels
# in class NeoPixel it's set to 3 as default 
# we're using ws2812B which only support RGB channel
# the order of the pixel color is also variable
# in class NeoPixel it's set to RGB when bpp is 3 as default
# between 0-1

# the color channal is in "RGB" order


#global helper variables
current_relay_state= None
flow_pos_main = 0
last_update_main = time.monotonic()


flow_pos_backup = 0
last_update_backup = time.monotonic()


def flow_main(strip, color, tail=5, period_ms=40):
    global flow_pos_main, last_update_main, now_main

    now_main = time.monotonic()

    if now_main - last_update_main < period_ms / 1000:
        return

    last_update_main = now_main

    strip.fill((0,0,0))

    for i in range(tail):
        idx = (flow_pos_main - i) % LED_COUNT_MAIN
        brightness = (tail - i) / tail

        strip[idx] = (
            int(color[0] * brightness),
            int(color[1] * brightness),
            int(color[2] * brightness)
        )
    strip.show()

    flow_pos_main = (flow_pos_main + 1) % LED_COUNT_MAIN


def flow_backup(strip, color, tail=5, period_ms=40):
    global flow_pos_backup, last_update_backup

    now_backup = time.monotonic()

    if now_backup - last_update_backup < period_ms / 1000:
        return

    last_update_backup = now_backup

    strip.fill((0,0,0))

    for i in range(tail):
        idx = (flow_pos_backup - i) % LED_COUNT_BACKUP

        brightness = (tail - i) / tail

        strip[idx] = (
            int(color[0] * brightness),
            int(color[1] * brightness),
            int(color[2] * brightness)
        )

    strip.show()

    flow_pos_backup = (flow_pos_backup + 1) % LED_COUNT_BACKUP


def set_relay(state):
    global current_relay_state

    if state == current_relay_state:
        return

    cpp_proc.stdin.write(state + "\n")
    cpp_proc.stdin.flush()

    current_relay_state = state

    print(f"Relay -> {state}")




cpp_proc.stdin.write("y\n")
cpp_proc.stdin.flush()
print("starting event")



while True:
    timer=current_time-start_time
    ##timer is in secs
    if(timer<12.375):
        #MAIN 440kV: NORMAL(G)
        #BACKUP 220kV: NORMAL(G)
        #LOAD:NORMAL(G)
        flow_main(main_branch, (255, 0, 0))
        flow_backup(backup_branch, (255, 0, 0))
        set_relay("d")
    elif(timer<17.25):
        #MAIN 440kV:DISTURBED(Y)
        #BACKUP 220kV:NORMAL(G)
        #LOAD:NORMAL(G)
        flow_main(main_branch,(255 ,255 ,0))
        flow_backup(backup_branch, (255, 0, 0))
        set_relay("d")
    elif(timer<18.5):
        #MAIN 440kV: TRIPPED(R)
        #BACKUP 220kV: NORMAL-HIGH PRESSURE(G)
        #LOAD:ALARMING(Y)
        main_branch.fill((0, 255, 0))
        flow_backup(backup_branch,(255,0,0),period_ms=15)
        set_relay("y")        
    elif(timer<22.5):
        #MAIN 440kV: TRIPPED(R)
        #BACKUP 220kV: DISTRUBED-HIGH PRESSURE(Y)
        #LOAD:ALARMING(Y)
        main_branch.fill((0, 255, 0))
        flow_backup(backup_branch,(255,255,0),period_ms=15)
        set_relay("y")   
    elif(timer<26.125):
        #MAIN 440kV:TRIPPED(R)
        #BACKUP 220kV:TRIPPED(R)
        #LOAD:NO POWER(R)
        main_branch.fill((0, 255, 0))
        backup_branch.fill((0, 255, 0))
        set_relay("r") 
    elif(timer<30.5):
        #MAIN 440kV: DISTURBED-HIGH PRESSURE(Y)
        #BACKUP 220kV:TRIPPED(R)
        #LOAD:ALARMING(Y)
        flow_main(main_branch,(255, 255 ,0),period_ms=15)
        backup_branch.fill((0, 255, 0))
        set_relay("y")
    elif(timer<31.875):
        #MAIN 440kV:NORMAL-HIGH PRESSURE(G)
        #BACKUP 220kV: TRIPPED(R)
        #LOAD:ALARMING(Y)
        flow_main(main_branch,(255, 0 ,0),period_ms=15)
        backup_branch.fill((0, 255, 0))
        set_relay("y")
    elif(timer<32.875):
        #MAIN 440kV:NORMAL(G)
        #BACKUP 220kV:DISTURBED(Y)
        #LOAD:ALARMING(Y)
        flow_main(main_branch,(255, 0 ,0))
        flow_backup(backup_branch,(255,255,0))
        set_relay("d")
    elif(timer<37.5):
        #MAIN 440kV:NORMAL(G)
        #BACKUP 220kV:NORMAL(G)
        #LOAD:NORMAL(G)
        flow_main(main_branch,(255, 0 ,0))
        flow_backup(backup_branch,(255,0,0))
        set_relay("d")
    else:
        start_time=time.monotonic()
    current_time= time.monotonic()
    time.sleep(0.001)
