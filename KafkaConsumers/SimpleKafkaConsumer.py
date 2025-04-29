from kafka import KafkaConsumer
import asyncio
import threading
import configparser
import time

'''
Important Notes
Consumer Group Behavior:
If the consumer group (group_id) has already committed offsets for this topic, the consumer will start from the last committed offset, even if auto_offset_reset is set to 'earliest'.

To ignore committed offsets and start fresh, you can:
Use a unique group_id for your consumer.
Manually reset the offsets (e.g., using kafka-consumer-groups.sh).

Idempotency:
Ensure that processing each message multiple times does not cause issues, as starting from the beginning will re-process old messages.

Performance:
Reading from the beginning can be time-consuming if the topic has a large backlog of messages.

Execution times:

'''

async def test_async_function(message):
    try:
        print(f"Handling message {message}: with {threading.current_thread()}") # async io runs single threaded event loop; unlike WebFlux/Project Reactor which has a thread pool running the event loop
        # still running with main thread ^^
    except Exception as e:
        print(e)

def main():
    try:
        start_time = time.time_ns()
        config = configparser.ConfigParser()
        config.read("Config/config.properties")
        bootstrap_servers = config['DEFAULT']['bootstrap.servers']
        # one thread per consumer, not thread safe. Generally one consumer thread per partition; we only have 1 partition.
        consumer = KafkaConsumer(
            "test_topic",
            bootstrap_servers = bootstrap_servers,
            auto_offset_reset = 'earliest', #starts from the earliest message IF NO COMMITTED OFFSETS ARE FOUND
            #enable_auto_commit = True, #ensures we regularly commit the last message we consumed,
            group_id = 'group2'
        )

        print("starting consumption")
        for message in consumer: # blocks and processes messages as they come in
            print(f"Received message: {message.value.decode('utf-8')}")
            # async io runs single threaded event loop; unlike WebFlux/Project Reactor which has a thread pool running the event loop
            asyncio.run(test_async_function(message=message)) 

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        consumer.close()
        print("Consumer closed.")
        end_time = time.time_ns()
        print(f"Total execution time: {end_time - start_time} nanoseconds")

if __name__ == "__main__":
    main()