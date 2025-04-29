import threading
from confluent_kafka import Consumer
import configparser
import time

'''
Multiple threads in the same consumer group will split the message consumption (assuming there are multiple partitions in the topic).
If you want independent consumption (each consumer consumes all messages) then each consumer should be in its own consumer group.

We want to split consumption across two threads, one for each partition in the topic. The idea behind this is to increase throughput
by running multiple consumers in parallel. I'll test the throughput with one thread versus two threads to see if there is a pronounced effect.
It could be the case that no substantial improvement is observed since the message volume is too low.
'''
def consume_messages():
    start_time = time.time_ns()
    config = configparser.ConfigParser()
    config.read("Config/config.properties")
    bootstrap_servers = config['DEFAULT']['bootstrap.servers']
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'consumer-group1',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'true'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['test_topic'])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg:
                print(f"Thread {threading.current_thread().name}: {msg.value().decode('utf-8')}")
    finally:
        consumer.close()

def main():
    start_time = time.time_ns() 
    
    num_threads = 2
    consumer_threads = []
    for i in range(num_threads):
        consumer_thread = threading.Thread(target=consume_messages)
        consumer_thread.start()
        consumer_threads.append(consumer_thread)

    for thread in consumer_threads:
        thread.join()

    end_time = time.time_ns()
    print(f"Total execution time: {end_time - start_time} nanoseconds")




if __name__ == '__main__':
    main()




