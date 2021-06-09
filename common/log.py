import datetime
import common.CTime1000 as tm

ROOT_LOG = '/data/media/0/videos/'


global_alertTextMsg1 = ''
global_alertTextMsg2 = ''



def printf1( txt ):
    global global_alertTextMsg1
    global_alertTextMsg1 = txt

def printf2( txt ):
    global global_alertTextMsg2
    global_alertTextMsg2 = txt    

class Loger:
    debug_step_latch = 0   # debug
    debug_step_data = 0  # debug 

    def __init__(self, txt_msg="defualt", time_val = 0. ):
        self.name = txt_msg
        self.nTime = time_val * 0.001
        self.old_txt = ""
        self.debug_Timer = 0
        self.Timer1 = tm.CTime1000("LOG")

    def __del__(self):
        print( "{} - Loger class delete".format( self.name ))



    def add( self, txt ):
        if self.Timer1.endTime():
           self.Timer1.startTime( self.nTime )

           if txt == self.old_txt:
               pass
           else:
                self.old_txt = txt
                now = datetime.datetime.now()
                cur_date = "{}{}{}".format(now.year, now.month, now.day )
                cur_time = "{}:{}:{}:{}".format(  now.hour, now.minute, now.second, now.microsecond ) 

                log_data = "{}-{} {}\r\n".format( cur_date, cur_time , txt) 
                #print( log_data )
                try:
                    path_file_name = ROOT_LOG + cur_date + '-' + self.name + ".txt"
                    with open( path_file_name, "a") as file:
                        file.write( log_data )
                except:
                    print("file open error file name:", path_file_name)
                    pass
                finally:  # try end 
                    pass       




