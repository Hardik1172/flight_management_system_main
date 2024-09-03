from confluent_kafka import Producer, Consumer
import json

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_message():
    producer = Producer({'bootstrap.servers': 'localhost:9092'})
    producer.produce('test_topic', key='key', value=json.dumps({'test': 'message'}), callback=delivery_report)
    producer.flush()

def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['test_topic'])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            print(f'Received message: {msg.value().decode("utf-8")}')
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'produce':
        produce_message()
    elif len(sys.argv) > 1 and sys.argv[1] == 'consume':
        consume_messages()
    else:
        print("Usage: python test_kafka.py [produce|consume]")