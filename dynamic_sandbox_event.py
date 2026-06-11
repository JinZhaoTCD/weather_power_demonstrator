import time

import board

import neopixel

import subprocess

cpp_proc=subprocess.Popen(
    ["/home/maya/Desktop/USB-RELAY(SourceCodeProjet2)/build/usbrelay"],
    stdin=subprocess.PIPE,
    text=True
)
start_time = time.monotonic()
current_time = time.monotonic()
PIN_MAIN = board.D18
LED_COUNT_MAIN = 60

PIN_BACKUP = board.D21
LED_COUNT_BACKUP = 30
BPP = 3 
# Bytes per pixel. 3 for RGB and 4 for RGBW pixels
# in class NeoPixel it's set to 3 as default 
# we're using ws2812B which only support RGB channel
COLOR_CHANNEL = neopixel.RGB 
# the order of the pixel color is also variable
# in class NeoPixel it's set to RGB when bpp is 3 as default
# between 0-1

# the color channal is in "GRB" order
main_branch = neopixel.NeoPixel( 
    PIN_MAIN, LED_COUNT_MAIN, brightness = 0.2, auto_write=True, pixel_order = COLOR_CHANNEL
    )
backup_branch = neopixel.NeoPixel( 
    PIN_BACKUP ,LED_COUNT_BACKUP , brightness = 0.2, auto_write=True, pixel_order = COLOR_CHANNEL
    )


#global helper variables
current_relay_state= None
flow_pos_main = 1
last_update_main = 0

flow_pos_backup = 1
last_update_backup = 0

def flow_main(strip, color, tail=5, period_ms=30):
    global flow_pos_main, last_update_main

    now = time.monotonic()

    if now - last_update_main < period_ms / 1000:
        return

    last_update_main = now

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


def flow_backup(strip, color, tail=5, period_ms=30):
    global flow_pos_backup, last_update_backup

    now = time.monotonic()

    if now - last_update_backup < period_ms / 1000:
        return

    last_update_backup = now

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