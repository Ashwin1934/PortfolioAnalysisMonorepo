from kafka import KafkaConsumer
import asyncio
import threading
import os
from concurrent.futures import ThreadPoolExecutor
import time


def publish_function(message):
    # TODO add google sheets publishing here, perhaps add a new object
    # see if we should publish all at once or batches, vs publish each message
    try:
        print(f"Handling message with thread: {threading.current_thread()}")
    except Exception as e:
        print(e)

def consume_messages(number_of_threads):
    try:
        start_time = time.time()
        print(f"Start time: {start_time}")
        # one thread per consumer, not thread safe. Generally one consumer thread per partition; we only have 1 partition.
        consumer = KafkaConsumer(
            "test_topic",
            bootstrap_servers = 'localhost:9092',
            auto_offset_reset = 'earliest'
        )

        executor = ThreadPoolExecutor(max_workers=number_of_threads)
        for message in consumer:  # blocks and processes messages as they come in
            print(f"Received message: {message.value.decode('utf-8')}")
            executor.submit(publish_function, message.value.decode('utf-8'))
            
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        consumer.close()
        executor.shutdown() # alternatively can use the 'with' keyword to manage/close resources
        print("Consumer closed.")
        end_time = time.time()
        print(f"End Time: {end_time}")


def main():
    num_processors = os.cpu_count()
    consume_messages(num_processors)
    return 0


if __name__ == "__main__":
    main()