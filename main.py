import socket
import re
from machine import Pin

def set_pin(num,value):
    pin = Pin(num,Pin.OUT)
    if value:
        pin.on()
    else:
        pin.off()

def get_pin(num):
    pin = Pin(num)
    return pin.value()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

def parse_req(req):
    try:
        match = re.search('^GET\s+(.*)\s+HTTP/1.1.*$',req)
        if match:
            return match.group(1)
        else:
            print('not doing other req now')
            return ""
    except:
        print('parsing error!')
        return ""

def route_req(req_url):
    try:
        if req_url == "/":
            return "OK"
        elif req_url.startswith("/get"):
            params = re.search("/get/([0-9]+)",req_url)
            pin_num = int(params.group(1))
            value = "off" if get_pin(pin_num) == 1 else "on"
            return "pin %d set to %s" % (pin_num,value)
        elif req_url.startswith("/pin"):
            params = re.search("/pin/([0-9]+)/(.*)",req_url)
            pin_num = int(params.group(1))
            value = not (params.group(2) == "on")
            set_pin(pin_num,value)
            return "pin %d set to %s" % (pin_num, value)
        else:
            return 'not found'  
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
    response = route_req(req)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    print(response)
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()