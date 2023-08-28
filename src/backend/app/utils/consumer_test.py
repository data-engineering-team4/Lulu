from confluent_kafka import Consumer, KafkaError

# 카프카 컨슈머 설정
config = {
    "bootstrap.servers": "",
    "group.id": "your_group_id",
    "auto.offset.reset": "earliest",
}
consumer = Consumer(config)

# 구독할 토픽 설정
consumer.subscribe(["testfastapi"])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        print(f"Received message: {msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
