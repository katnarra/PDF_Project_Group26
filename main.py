from machine import Pin, PWM, RTC
import ntptime
import network
import asyncio
import time

SSID = "123"
PASS = "passwordXd"
sensor = Pin(4, Pin.IN)
led1 = Pin(3, Pin.OUT)
led2 = Pin(2, Pin.OUT)
motor = PWM(Pin(5))
minHour = 8
maxHour = 18

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
        # pray to god this doesn't suddendly decide to change since the ip address
        # is hard coded to the Android application
        # net.ifconfig(('192.168.240.169', '255.255.255.0', '192.168.240.63', '1.1.1.1'))
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
    shouldActivate = minHour <= hour <= maxHour
    print(f"min\tcur\tmax")
    print(f"{minHour}\t{hour}\t{maxHour}")
    print(f"Proceed: {shouldActivate}")
    return shouldActivate
    
def start():
    connectWIFI()
    ntptime.settime()
    motor.freq(50)
    handleTurn(2300)
    setupServer()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(displayIpAddressUsingLeds())
    loop.run_forever()

def displayIpAddressUsingLeds():
    # we were having problems with getting a predictable
    # local ip from the pi. as such the way we're going to
    # handle the issue is:
    # 1. let the network give us whichever address it wants
    # 2. make the pi print it out by lighting up the leds
    # i wouldn't call this a hack since this is way worse but
    # this will have to do.
    ip = network.WLAN(network.STA_IF).ifconfig()[0].split(".")
    first = "0"*(3-len(ip[2]))+ip[2]
    last  = "0"*(3-len(ip[3]))+ip[3]
    while True:
        for i in range(3):
            for k in range(int(first[i])):
                led1.high()
                await asyncio.sleep(0.5)
                led1.low()
                await asyncio.sleep(0.5)
            await asyncio.sleep(1)
        for i in range(3):
            for k in range(int(last[i])):
                led2.high()
                await asyncio.sleep(0.5)
                led2.low()
                await asyncio.sleep(0.5)
            await asyncio.sleep(1)
def setupServer():
    server = asyncio.start_server(handleServer, "0.0.0.0", 80)
    asyncio.create_task(server)

def main():
    activations = 0
    while True:
        while withinHours():
            covered = "Not covered" if (sensor.value() == 1) else "Covered"
            print(f"Sensor: {covered}")
            if sensor.value() == 0:
                handleTurn(activations % 2)
                activations += 1
            await asyncio.sleep(10)
        else:
            await asyncio.sleep(60)

start()
