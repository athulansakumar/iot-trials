import socket
import re
from machine import Pin

def led(on):
    led = Pin(2,Pin.OUT)
    if on:
        led.off()
    else:
        led.on()

def relay(num,on):
    if num == 1:
        relay = Pin(4,Pin.OUT)
    elif num == 2:
        relay = Pin(0,Pin.OUT)
    if on:
        relay.off()
    else:
        relay.on()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

def parse_req(req):
    try:
        match = re.search('^GET\s+(.*)\s+HTTP/1.1.*$',req)
        if match:
            return match.group(1).split('/')
        else:
            print('not doing other req now')
            return []
    except:
        print('parsing error!')
        return []

def route_req(req):
    try:
        if req[1] == 'led':
            led(req[2] == 'on')
            return 'led is turned '+ req[2]
        elif req[1] == 'relay':
            relay(int(req[2]),req[3] == 'on') 
            return 'relay '+req[2]+' is turned '+ req[3]
        return 'nothing happened'
    except:
        print('error while routing!')
        return 'error while routing!'

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    data = str(cl.recv(100),'utf8')
    req = parse_req(data)
    print(req)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    response = route_req(req)
    print(response)
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()