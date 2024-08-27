from concurrent.futures import ThreadPoolExecutor
import  requests
import json as json
from time import sleep
from kafka import  kafkaProducer

def serializer(message):
    return json.dumps(message).encode('utf-8')
prodcuder = KafkaProducer(
    s
)

response = requests.get("https://www.dropbox.com/s/iwcpg1oo59i4yrn/exfoCustosTest%20%283%29.json?dl=1")
json_data = json.loads(response.content)

servers = json_data['servers']
services = json_data['services']

ip_to_name = {server['ip']: service ['name'] for service in service }
debug = True
with ThreadPoolExecuter (max_workers = 16) as executor:
    future_results = []
    for server in servers:
        for client in server['clients']:
            future = executor.submit(flatten_record , server, client)
            future_results.append(future)

     for future in future_results:
         flat_record = future.result()
         if debug:
             print(f"Sending record to Kafka Stream: {json.loads(flat_record)}")
             data = json.load(flat_record)
             print(data["timestamp"])
             producer.send('mec-xdr', flat_record)
             producer.flush()

def main():
    while True:
        get_push_records()
        sleep(2)

if __name__ == "main":
    main()

