import serial
from serial.tools import list_ports
import keyboard
import datetime
import pyperclip
import threading
import sys

class read_temps:
    def __init__(self,filename,**args):
        
        self.output=filename
        
        if 'id_file' in args:
            id_file=args['id_file']
        else:
            id_file=r"Z:\Software\Arduino_Code\Temperature_Recording\thermocouple_id.txt"
        self.devicekey={}
        with open(id_file,'r') as file:
            for line in file:
                try:
                    self.devicekey[line.split()[0]]=int(line.split()[1])
                except IndexError:
                    pass
        
        #opens serial connection            
        self.s=serial.Serial()
        if 'com' in args:
            self.s.port=args['com']
        else:
            ports=list_ports.comports()
            for port,desc,hiwd in ports:
                if ' '.join(desc.split()[:3])=='USB Serial Device':
                    self.s.port=port
        if 'baudrate' in args:
            self.s.baudrate=args['baudrate']
        else:
            self.s.baudrate=9600
        self.s.open()
        
        while True:
            line=self.s.readline().decode('utf-8').split()
            try:
                if line[0]=='Initialization':
                    self.devicecount=int(line[-1])
                    break
            except IndexError:
                pass
            
        self.current_temps=[]
        self.deviceaddress=[]
        while len(self.deviceaddress)<self.devicecount:
            line=self.s.readline().decode('utf-8').split()
            try:
                if line[0]=='Device':
                    self.deviceaddress.append(line[-1])
                    self.current_temps.append(0.0)
            except IndexError:
                pass
        
        if 'print_file' in args:
            print_file=args['print_file']
        else:
            print_file=r"Z:\Software\Arduino_Code\Temperature_Recording\print_order.txt"
        self.print_order=[]
        with open(print_file,'r') as file:
            for line in file:
                if len(line.split())==0:
                    self.print_order.append(0)
                else:
                    self.print_order.append(line.split()[0])
        
        with open(self.output,'w+') as output:
            output.write('start time is: '+str(datetime.datetime.now())+'\n')
            output.write('device count is: '+str(self.devicecount)+'\n')
            output.write('device addresses are:')
            for i in self.deviceaddress:
                output.write(' '+str(i))
                output.write('\ndevice names are:')
                output.write(' '+str(self.devicekey[i]))
            output.write('\n')
            output.flush()
        
        t=threading.Thread(target=self.temp_recorder)
        t.daemon=True
        t.start()
        print('temps are being recorded ')
        
    def temp_recorder(self):
        device_counter=0
        self.is_recording=True
        with open(self.output, 'a') as output:
            while not keyboard.is_pressed('escape'): 
                if not self.is_recording:
                    break
                line=self.s.readline().decode('utf-8').split()
                try:
                    if line[0]=='Devices':
                        output.write('\n'+str(datetime.datetime.now()))
                        device_counter=0
                    elif line[0]=='Temperature':
                        output.write(' '+str('{:0<8}'.format(float(line[-1]))))
                        self.current_temps[device_counter]=float(line[-1])
                        device_counter+=1
                except IndexError:
                    pass
                if device_counter==self.devicecount:
                    output.flush()
                    device_counter=0
        self.s.close()
        self.is_recording=False
        
    def check_temps(self):
        print('timestamp:  '+str(datetime.datetime.now())+'\n')
        print('device numbers and temps:\n')
        i=0
        j=0
        tempvar=[]
        for i in self.print_order:
            if i==0:
                print('')
                tempvar.append('\n')
            else:
                for j in range(self.devicecount):
                    if self.devicekey[self.deviceaddress[j]]==int(i):
                        print(str(i+'\t'+str(self.current_temps[j])+'\n'))
                        tempvar.append(str(self.current_temps[j])+'\n')
                        break
        pyperclip.copy(''.join(tempvar))
                
def serial_tester(com_port):
    serial1=serial.Serial()
    serial1.port=com_port
    serial1.baudrate=9600
    serial1.open()
    while not keyboard.is_pressed('escape'):
        line=serial1.readline().decode('utf-8')
        print(line)
    serial1.close()
   
def temp_reader(filename):
    with open(filename, 'r') as file:
        for i in range(3):
            line=file.readline().split()
        devicenames=line
        times=[]
        temps=[[] for i in range(len(devicenames))]
        while True:
            line=file.readline().split()
            if not line:
                break
            if len(line)==devicenames+2:
                times.append(datetime.datetime.strptime(' '.join(line[0:1]),'%Y-%m-%d %H:%M:%S.%f'))
                for i in range(2,len(line)):
                    temps[i-2].append(line[i])

    return times,temps,devicenames