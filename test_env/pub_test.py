import paho.mqtt.client as paho
broker="192.168.7.85"
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass
client1= paho.Client("control")                           #create client object
client1.on_publish = on_publish  
client1.username_pw_set("admin", "12345678")                        #assign function to callback
client1.connect(broker,port)                                 #establish connection
ret= client1.publish(topic="test",payload="ccccccc",qos=0)   
print(ret)
