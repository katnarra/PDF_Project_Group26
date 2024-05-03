
from machine import Pin, PWM
from time import sleep
import usocket
import ntptime
import network

SSID = "123"
PASS = "passwordXd"
sensor = Pin(4, Pin.IN)
led1 = Pin(3, Pin.OUT)
led2 = Pin(2, Pin.OUT)
motor = PWM(Pin(5))
minHour = 8
maxHour = 20

def turn(start, end, increment):
    for position in range(start, end, increment):
        motor.duty_u16(position)
        sleep(0.001)

def handleTurn(pos):
    if (pos == 0):
        print("\n0   -> 180 Degrees")
        turn(2300, 7700, 1)
    elif (pos == 1):
        print("\n180 -> 0   Degrees")
        turn(7700, 2300, -1)

def connectWIFI():
    print("\nConnecting...")
    net = network.WLAN(network.STA_IF)
    net.active(True)
    net.connect(SSID, PASS)
    while not net.isconnected():
        sleep(1)
    print()
    print(net.ifconfig())

def withinHours():
    hour = int(ntptime.time() / 3600 % 24 + 3)
    print("\nStart\t   Current\t   End")
    print(f"{minHour}:00\t<= {hour}:00\t<= {maxHour}:00")
    return minHour <= hour <= maxHour

def main(connection):
    activations = 0
    while True:
        if withinHours():
            led1.high()
            led2.low()
            if sensor.value() == 0:
                led2.high()
                connection.send(b'sus')
                handleTurn(activations % 2)
                activations += 1
            sleep(5)
        else:
            led1.low()
            led2.low()
            sleep(60*60)

def setTime():
    while True:
        try:
            ntptime.settime()
            e = None
        except ETIMEDOUT as e:
            pass
        if e:
            print("\nSyncing the clock failed, retrying...")
            sleep(1)
        else:
            break

def createSocket():
    socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    socket.bind(('', 8888))
    socket.listen(5)
    print("\nWaiting for the client to connect...")
    connection, address = socket.accept()
    return connection

def start():
    connectWIFI()
    setTime()
    motor.freq(50)
    connection = createSocket()
    main(connection)

start()
