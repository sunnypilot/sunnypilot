
import time
import datetime

class CTime1000:
    def __init__(self, txt_msg="time", end_time = 0 ):
        self.name = txt_msg
        self.start_time = self.get_mmsec()
        self.end_time = self.start_time + end_time
        self.old_txt = ""
        self.debug_Timer = 0
        self.pre_second = 0
        self.sample_cnt = 0
        self.sample_val = 0

    def __del__(self):
        print( "{} - class delete".format( self.name ))

    def get_mmsec( self ):
        cur_time = time.time() * 0.001
        return cur_time

    def get_time(self):
        cur_time = self.get_mmsec()
        delta_time = self.end_time - cur_time

        return delta_time


    def startTime(self, end_time ):
        self.start_time = self.get_mmsec()
        self.end_time = self.start_time + end_time

    def endTime(self, end_time = -1):
        ret_code = False
        if  end_time > 0:
            self.end_time = self.start_time + end_time

        cur_time = self.get_mmsec()
        delta_time = self.end_time - cur_time
        if delta_time < 0.:
              ret_code = True

        return  ret_code

    def sampleTime(self):
        self.sample_cnt += 1
        now = datetime.datetime.now()
        if now.second != self.pre_second:
            self.pre_second = now.second
            self.sample_val = self.sample_cnt
            self.sample_cnt = 0

        return  self.sample_val




