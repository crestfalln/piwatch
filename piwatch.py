import RPi.GPIO as gpio
import gpiozero
import datetime
import time
import os


# Global Variables
TRIG = 4
ECHO = 17
state = 0
writeDir = "/var/www/html/"
waitTime = 30
trigDist = 100


# Functions
def getDist():
    time.sleep(0.001)
    gpio.output(TRIG, True)
    time.sleep(0.00001)
    gpio.output(TRIG, False)
    debugTime = time.time()
    while gpio.input(ECHO) == 0:
        pulse_start = time.time()
        if(pulse_start - debugTime > 2):
            raise gpiozero.BadWaitTime("Took too long for pulse to echo")
    debugTime = time.time()
    while gpio.input(ECHO) == 1:
        pulse_end = time.time()
        if(pulse_start - debugTime > 2):
            raise gpiozero.BadWaitTime("Took too long for pulse to echo")
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print(distance)
    return distance


def trigAlert(dist):
    if(dist <= trigDist):
        return True
    else:
        return False


def mkdir(di):
    if (not os.path.exists(di)):
        os.makedirs(di)

def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(TRIG, gpio.OUT)
    gpio.setup(ECHO, gpio.IN)
    gpio.output(TRIG, False)
    time.sleep(0.5)

def reset():
    gpio.cleanup()
    init()


init()

# Main logic
gpioprob = 0
while True:
    start = time.time()
    end = time.time()
    wait = 6
    try:
        for x in range(3):
            while(trigAlert(getDist())):
                time.sleep(0.5)
                end = time.time()
        gpioprob = 0
        timeElasped = end - start
        timeElasped = round(timeElasped)
        if(timeElasped >= wait):
            print(timeElasped)
            nTime = time.strftime("%I:%M%p")
            nYear = time.strftime("Year %Y")
            nMonth = time.strftime("%B")
            nDate = time.strftime("%d - %a")
            startStr = time.strftime("%I:%M:%S%p", time.localtime(start))
            endStr = time.strftime("%I:%M:%S%p", time.localtime(end))

            fileDir = writeDir  + nYear + "/" + nMonth + "/" + nDate + "/"
            fileName = startStr + ".txt"

            print(fileDir + fileName)
            mkdir(fileDir)            
            file = open(fileDir + fileName , "w")
            file.write(startStr + " to " + endStr + "\n")
            file.write("Total Time Taken: " + str(datetime.timedelta(seconds=timeElasped)))
            file.close()
    except KeyboardInterrupt:
            break
    except :
        if not gpioprob:
            gpioprob = 1
            reset()
        else:
            reset()
            file = open(writeDir+"PROBLEM PLEASE CHECK WIRES AND RESET THE BOARD" , "w")
            file.close()


gpio.cleanup()
