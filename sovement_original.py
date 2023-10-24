import schedule
import time
import random
import csv

f1=open("distance.csv","w+")
f1.close()
f2=open("temperature.csv","w+")
f2.close()
f3=open("humidity.csv","w+")
f3.close()

def data_get_distance():
    msg=random.randrange(0, 10)
    return msg

def data_get_temperature():
    temp=random.randrange(0, 100)
    return temp

def data_get_humidity():
    humid=random.randrange(0, 10)
    return humid

def data_stack_distance(msg_i, msg):
    f1=open("distance.csv","a", newline="")
    wr1=csv.writer(f1)
    wr1.writerow([msg_i,msg])
    f1.close()

def data_stack_temperature(temp_i, temp): 
    f2=open("temperature.csv","a", newline="")
    wr2=csv.writer(f2)
    wr2.writerow([temp_i,temp])
    f2.close()

def data_stack_humidity(humid_i, humid):
    f3=open("humidity.csv","a", newline="")
    wr3=csv.writer(f3)
    wr3.writerow([humid_i,humid])
    f3.close()
        
# step3.running cycle settings
schedule.every(10).minutes.do (data_stack_distance)
schedule.every(10).minutes.do (data_stack_temperature)
schedule.every(10).minutes.do (data_stack_humidity)

start_num=1
msg_i=start_num
temp_i=start_num
humid_i=start_num
    
# step4.starting the schedule
while True:

    msg=data_get_distance() #거리 데이터 10분마다 받기
    data_stack_distance(msg_i, msg)
    msg_i=msg_i+1
    
    temp=data_get_temperature() #온도 데이터 10분마다 받기
    data_stack_temperature(temp_i, temp)
    while True:
        temp_i=temp_i+1
        if (temp>=70): #온도 데이터 70도 이상으로 측정 시
            schedule.every(30).seconds.do (data_get_temperature) #30초마다 측정
            temp_new=data_get_temperature()
            if(temp_new>=70):
                data_stack_temperature(temp_i, temp_new)
                #화재가 발생했다고 판단->네트워크 모듈로 통신
                print("화재 발생!")
                break
            else:
                data_stack_temperature(temp_i, temp_new)
                break
        else:
            break        
    humid=data_get_humidity()
    data_stack_humidity(humid_i, humid)
    humid_i=humid_i+1