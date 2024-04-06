from machine import Pin, PWM, RTC
import ntptime
import network
import asyncio
import time

SSID = "******"
PASS = "******"
sensor = Pin(4, Pin.IN)
motor = PWM(Pin(3))
minHour = 0
maxHour = 12

def webpage(minHour, maxHour):
    html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Server</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <form action="./minInc">
                    <input type="submit" value="min++" />
                </form>
                <form action="./minDec">
                    <input type="submit" value="min--" />
                </form>
                <form action="./maxInc">
                    <input type="submit" value="max++" />
                </form>
                <form action="./maxDec">
                    <input type="submit" value="max--" />
                </form>
                <p>minHour: {minHour}</p>
                <p>maxHour: {maxHour}</p>
            </body>
        </html>
    """
    return str(html)

async def handleServer(reader, writer):
    global minHour, maxHour
    request_line = await reader.readline()
    while await reader.readline() != b"\r\n":
        pass
    request = str(request_line, 'utf-8').split()[1]
    if request == '/minInc?':
        minHour += 1
    elif request == '/minDec?':
        minHour -= 1
    elif request == '/maxInc?':
        maxHour += 1
    elif request == '/maxDec?':
        maxHour -= 1
    response = webpage(minHour, maxHour)  
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    
def turn(start, end, increment):
    for position in range(start, end, increment):
        motor.duty_u16(position)
        time.sleep(0.001)
        
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
    hour = rtc.datetime()[4]
    print(minHour, "<=", hour, "<=", maxHour)
    return minHour <= hour <= maxHour
    
def start():
    connectWIFI()
    ntptime.settime()
    motor.freq(50)
    print("-> 0   Degrees")
    motor.duty_u16(1144)
    setupServer()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

def setupServer():
    server = asyncio.start_server(handleServer, "0.0.0.0", 80)
    asyncio.create_task(server)

def main():
    activations = 0
    while True:
        while withinHours():
            print("Sensor:", sensor.value())
            if sensor.value() == 0:
                if activations % 2 == 0:
                    print("-> 180 Degrees")
                    turn(1144, 7600, 5)
                else:
                    print("-> 0   Degrees")
                    turn(7600, 1144, -5)
                activations += 1
            await asyncio.sleep(15)
        else:
            await asyncio.sleep(15)

start()
