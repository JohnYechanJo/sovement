import schedule
import random
import csv
import sched
import time
import datetime

index=1
f=open("data_list.csv","w+")
f.close()

def data_get_distance():
    msg=random.randrange(0, 10)
    return msg

def data_get_temperature():
    temp=random.randrange(50, 100)
    return temp

def data_get_humidity():
    humid=random.randrange(0, 10)
    return humid

############################################################

header = ["index", "distance", "temperature", "humidity"]
f=open("data_list.csv","a", newline="")
wr=csv.writer(f)
wr.writerow(["index","distance","temperature","humidity","time"])
f.close()
def data_stack():
    global index
    stack_time = int(time.time())
    date_time = datetime.datetime.fromtimestamp(stack_time)
    msg=data_get_distance()
    temp=data_get_temperature()
    humid=data_get_humidity()
    f=open("data_list.csv","a", newline="")
    wr=csv.writer(f)
    wr.writerow([index,msg,temp,humid,date_time])
    f.close()
    if (temp>=70): #온도 데이터 70도 이상으로 측정 시
        #30초 후에 온도 받은 것이 temp_new
        time.sleep(10)
        fire_time = int(time.time())
        fire_date_time = datetime.datetime.fromtimestamp(fire_time)
        temp_new=data_get_temperature()
        if(temp_new>=70):
            #data_stack_temperature(temp_i, temp_new)
            f=open("data_list.csv","a", newline="")
            wr=csv.writer(f)
            wr.writerow(["*",msg,temp_new,humid,fire_date_time])
            f.close()
            #화재가 발생했다고 판단->네트워크 모듈로 통신
            print("화재 발생!")
        else:
            f=open("data_list.csv","a", newline="")
            wr=csv.writer(f)
            wr.writerow(["*",msg,temp_new,humid,fire_date_time])
            f.close()
    index=index+1
    
# step3.running cycle settings
schedule.every(15).seconds.do (data_stack)

# step4.starting the schedule
while True:
    schedule.run_pending()
    time.sleep(1)
   