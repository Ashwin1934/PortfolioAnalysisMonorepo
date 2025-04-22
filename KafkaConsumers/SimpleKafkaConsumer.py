from kafka import KafkaConsumer
import asyncio
import threading

async def test_async_function(message):
    try:
        print(f"Handling message {message}: with {threading.current_thread()}") # async io runs single threaded event loop; unlike WebFlux/Project Reactor which has a thread pool running the event loop
    except Exception as e:
        print(e)

def main():
    try:
        # one thread per consumer, not thread safe. Generally one consumer thread per partition; we only have 1 partition.
        consumer = KafkaConsumer(
            "test_topic",
            bootstrap_servers = 'localhost:9092',
            auto_offset_reset = 'earliest'
        )

        for message in consumer: # blocks and processes messages as they come in
            print(f"Received message: {message.value.decode('utf-8')}")
            # async io runs single threaded event loop; unlike WebFlux/Project Reactor which has a thread pool running the event loop
            asyncio.run(test_async_function(message=message)) 

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        consumer.close()
        print("Consumer closed.")

if __name__ == "__main__":
    main()