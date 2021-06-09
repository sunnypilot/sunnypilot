


class MoveAvg():
    def __init__(self):
        self.skip_timer = 0
        self.data_cnt = 0
        self.data_sum = 0
        self.data_avg = 0
        self.data_steer = []

    def __del__(self):
        self.data_steer.clear()        

    def get_data(self, steer_angle_dest, max_cnt ):
        self.data_steer.append( steer_angle_dest )
        self.data_cnt += 1

        delta = self.data_cnt - max_cnt
        if self.data_cnt > max_cnt:
            self.data_cnt = max_cnt

            if delta > 0:
                del self.data_steer[:delta]
            else:
                self.data_steer.pop(0)


        self.data_sum = 0
        for enum in self.data_steer:
            #print( enum )
            self.data_sum += enum

        self.data_avg = self.data_sum / self.data_cnt
        return  self.data_avg



    def get_min(self, steer_angle_dest, max_cnt ):
        self.data_steer.append( steer_angle_dest )
        self.data_cnt += 1

        delta = self.data_cnt - max_cnt
        if self.data_cnt > max_cnt:
            self.data_cnt = max_cnt

            if delta > 0:
                del self.data_steer[:delta]
            else:
                self.data_steer.pop(0)


        data_min = 255
        for enum in self.data_steer:
            if data_min > enum:
                data_min = enum


        return  data_min