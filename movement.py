import struct
import threading
import sys

class MovementSensor:
    def __init__(self,input_dev,sys_iface):
        self.input_dev = input_dev
        self.sys_iface = sys_iface
    def set_sample_rate(self,rate):
        h = open(self.sys_iface+"/sample_rate",'w')
        h.write(str(rate))
        h.write("\n")
        h.close()
    def get_sample_rate(self):
        h = open(self.sys_iface+"/sample_rate",'r')
        rate = int(h.read().strip())
        h.close()
        return rate
    def open(self):
        return MovementSource(self.input_dev)

class MovementSource:
    def __init__(self,fn):
        self.ifile = open(fn,'rb')
        self.x = 0
        self.y = 0
        self.z = 0
    def __iter__(self):
        return self
    def next(self):
        while True:
            buf = self.ifile.read(16)
            if not buf:
                raise StopIteration()
            (time1,time2, type, code, value) = struct.unpack('iihhi',buf)
            if type==2 or type==3:
                if code==0:
                    self.x = value
                elif code==1:
                    self.y = value
                elif code==2:
                    self.z = value
            elif type==0 and code==0:
                secs = float(time1) + float(time2)/1000000.0
                return (secs,self.x,self.y,self.z)
    def __del__(self):
        self.ifile.close()

accelerator1 = MovementSensor("/dev/input/event2","/sys/class/i2c-adapter/i2c-0/0-0073/spi_s3c24xx_gpio.0/spi3.0")
accelerator2 = MovementSensor("/dev/input/event3","/sys/class/i2c-adapter/i2c-0/0-0073/spi_s3c24xx_gpio.0/spi3.1")


class MovementReader(threading.Thread):
    def __init__(self,fn):
        threading.Thread.__init__(self)
        self.src1 = accelerator1.open()
        self.src2 = accelerator2.open()
        self.trg = open(fn,'w')
        self.running = False
    def run(self):
        self.running = True
        while self.running:
            (t1,x1,y1,z1) = self.src1.next()
            (t2,x2,y2,z2) = self.src2.next()
            self.trg.write("%f\t%d\t%d\t%d\t%d\t%d\t%d\n" % (t1, x1, x2, y1, y2, z1, z2))
    def stop(self):
        self.running = False
        
        
