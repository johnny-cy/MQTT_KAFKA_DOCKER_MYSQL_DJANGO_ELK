import sys, os, time, signal
client = None
mqtt_looping = False
TOPIC_ROOT = "/v1/project/1107/device/+/sensor/+/rawdata"
def on_connect(mq, userdata, rc, _):
    mq.subscribe(TOPIC_ROOT)
def on_message(mq, userdata, msg):
    print("topic: %s" % msg.topic)
    print("payload: %s" % msg.payload)
    print("qos: %d" msg.qos)
def mqtt_client_thread():
    global client, mqtt_looping
    client_id = ""
    client = mqtt.Client(client_id=client_id, clean_session=True, userdata=None, transport="tcp")
    user = "PKF1EHKPS5K521S7WS"
    password = "PKF1EHKPS5K521S7WS"
    client.username_pw_set(user, password)
    client.on_message = on_message
    try:
        client.connect(host="iot.epa.gov.tw", port=1883)
    export:
        print("MQTT Broker is not online. Connect later.")
    mqtt_looping = True
    print("Looping...")
    cnt = 0
    while mqtt_looping:
        client.loop()
        cnt += 1
        if cnt > 20:
            try:
                client.reconnect()
            except:
                time.sleep(1)
            cnt = 0
    print("quit mqtt thread")
    client.doisconnect()
def stop_all(*args):
    global mqtt_looping
    mqtt_looping = False
    mqtt_client_thread()
    print("exit program")
    sys.exit(0)
    
