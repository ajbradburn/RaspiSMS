import time 
import serial
import RPi.GPIO as GPIO

ser = serial.Serial(
  port='/dev/serial0',
  baudrate = 9600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)
print('Serial Initialized, let us send.');

# This com delay should vary based upon the baud.
COM_DELAY = 1 / 1000000 * 4000
enable_pin = 18

number = "4072438744"
text = "This is a test message from python." 

def init():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(enable_pin, GPIO.OUT)

#GPIO.output(enable_pin, 1/0)

def destruct():
  GPIO.cleanup()

def com_error():
  print('Error communicating with the SIM800L Module.\n');
  exit()

def sendSms(number, text):
  print('Sending text.')
  writeSerial("AT+CMGF=1\r\n");
  readSerial("OK\r\n")
  print('Initiated connection.')

  writeSerial("AT+CMGS=\"" + number + "\"\r\n" + text + "\r\n");
  readSerial("> ")
  print('Message transmitted.')

  writeSerial(chr(26))

def prepareForSMSReceive():
  writeSerial("AT+CMGF=1\r\n")
  #readSerial("OK\r\n")
  print(readSerial())

  writeSerial("AT+CNMI=2,1,0,0,0\r\n")
  readSerial("OK\r\n")

  return True

  # This function is used to monitor for unsolicited SMS notifications.
  # Alternatively, you can simply request all messages at your convenience.
def checkForSMS():
  # Received string: \r\n+CMTI: "[SM|ME]",1\r\n
  if ser.in_waiting == 0:
    return False

  match_string = "+CMTI:"

  response = ser.read_until(b'\r\n', 100)
  response = response.decode('ascii')

  match_index = response.find(match_string)
  if match_index == -1:
    return False

  return response[match_index + len(match_string)::].strip()

def readUnreadMessages():
  writeSerial("AT+CMGL=\"ALL\",0\n")
  print(readSerial())

def readSerial(termination_string = "", timeout = 10000000):
  print('-')
  end = getMTime() + timeout
  buffer = ""

  while getMTime() < end:
    buffer = buffer + ser.read(10).decode('ascii')
    if buffer.find(termination_string) != -1:
      print('Found')
      break

  print('|')
  if termination_string != "" and getMTime() > end:
    com_error()

  response = {
    'timeout':None,
    'response':buffer
    }

  if getMTime() < end:
    response['timeout'] = False
  else:
    response['timeout'] = True

  return response

def getMTime():
  return time.time_ns() / 1000

def writeSerial(string):
  print('.')
  ser.write(string.encode())

# Program

sendSms(number, text)

ser.close()

#run = True
#timeout = 100000 * 1000
#endtime = getMTime() + timeout
#while run:
#  response = checkForSMS()
#  if response:
#    print(response);
#  if getMTime() > endtime:
#    break

#prepareForSMSReceive()
#readUnreadMessages()
#writeSerial("AT+CMGD=?\n")
#print(readSerail())
