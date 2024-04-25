from machine import Pin, PWM, RTC
from time import sleep
import ntptime
import network

SSID="123"
PASS="passwordXd"
sensor = Pin(4, Pin.IN)
led1 = Pin(3, Pin.OUT)
led2 = Pin(2, Pin.OUT)
motor = PWM(Pin(5))
minHour = 8
maxHour = 22

def turn(start, end, increment):
    for position in range(start, end, increment):
        motor.duty_u16(position)
        sleep(0.001)
        
def handleTurn(pos):
    if (pos == 0):
        print(f"0\t-> 180\tDegrees")
        turn(1144, 7700, 5)
    elif (pos == 1):
        print(f"180\t-> 0\tDegrees")
        turn(7600, 2300, -5)
    else:
        print(f"Rotate to {pos}")
        motor.duty_u16(pos)
        
def connectWIFI():
    net = network.WLAN(network.STA_IF)
    if not net.isconnected():
        net.active(True)
        print('Connecting...')
        net.connect(SSID, PASS)
        while not net.isconnected():
            pass
    print('Connection successful')
    print(net.ifconfig())

def withinHours():
    rtc = RTC()
    # hour = rtc.datetime()[4] # pfft don't need none of that nonsense
    # my homies prefer THIS:
    hour = int(ntptime.time() / 3600 % 24 + 3)
    shouldActivate = minHour < hour < maxHour
    print(f"min\tcur\tmax")
    print(f"{minHour}\t{hour}\t{maxHour}")
    print(f"Proceed: {shouldActivate}")
    return shouldActivate

def main():
    activations = 0
    while True:
        while withinHours():
            led1.high()
            covered = "Not covered" if (sensor.value() == 1) else "Covered"
            print(f"Sensor: {covered}")
            if sensor.value() == 0:
                led2.high()
                handleTurn(activations % 2)
                activations += 1
            led2.low()
            sleep(5)
        else:
            led1.low()
            sleep(60)

def start():
    connectWIFI()
    ntptime.settime()
    motor.freq(50)
    handleTurn(2300)
    main()

start()
