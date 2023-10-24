import schedule
import random
import csv
import sched
import time
import datetime

f1=open("distance.csv","w+")
f1.close()
f2=open("temperature.csv","w+")
f2.close()
f3=open("humidity.csv","w+")
f3.close()

start_num=1
msg_i=start_num
temp_i=start_num
humid_i=start_num 


def data_get_distance():
    msg=random.randrange(0, 10)
    return msg

def data_get_temperature():
    temp=random.randrange(0, 100)
    return temp

def data_get_humidity():
    humid=random.randrange(0, 10)
    return humid

############################################################

def data_stack_distance():
    global msg_i
    msg_time = int(time.time())
    msg_date_time = datetime.datetime.fromtimestamp(msg_time)
    msg=data_get_distance() #거리 데이터 10분마다 받기
    f1=open("distance.csv","a", newline="")
    wr1=csv.writer(f1)
    wr1.writerow([msg_i,msg,msg_date_time])
    f1.close()
    msg_i=msg_i+1
    print("스케줄 실행중")

def data_stack_temperature():
    global temp_i
    temp_time = int(time.time())
    temp_date_time = datetime.datetime.fromtimestamp(temp_time)
    temp=data_get_temperature() #온도 데이터 10분마다 받기
    f2=open("temperature.csv","a", newline="")
    wr2=csv.writer(f2)
    wr2.writerow([temp_i,temp,temp_date_time])
    f2.close()
    if (temp>=70): #온도 데이터 70도 이상으로 측정 시
        #30초 후에 온도 받은 것이 temp_new
        time.sleep(10)
        temp_fire_time = int(time.time())
        temp_fire_date_time = datetime.datetime.fromtimestamp(temp_fire_time)
        temp_new=data_get_temperature()
        if(temp_new>=70):
            #data_stack_temperature(temp_i, temp_new)
            f2=open("temperature.csv","a", newline="")
            wr2=csv.writer(f2)
            wr2.writerow([temp_i,temp_new,temp_fire_date_time])
            f2.close()
            #화재가 발생했다고 판단->네트워크 모듈로 통신
            print("화재 발생!")
        else:
            f2=open("temperature.csv","a", newline="")
            wr2=csv.writer(f2)
            wr2.writerow([temp_i,temp_new,temp_fire_date_time])
            f2.close()   
    temp_i=temp_i+1
            
def data_stack_humidity():
    global humid_i
    humid_time = int(time.time())
    humid_date_time = datetime.datetime.fromtimestamp(humid_time)
    humid=data_get_humidity()
    f3=open("humidity.csv","a", newline="")
    wr3=csv.writer(f3)
    wr3.writerow([humid_i,humid,humid_date_time])
    f3.close()
    humid_i=humid_i+1
    
# step3.running cycle settings
schedule.every(15).seconds.do (data_stack_distance)
schedule.every(15).seconds.do (data_stack_temperature)
schedule.every(15).seconds.do (data_stack_humidity)

# step4.starting the schedule
while True:
    schedule.run_pending()
    time.sleep(1)
   