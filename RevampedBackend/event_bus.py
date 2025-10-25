'''
Custom event bus used to facilitate multiple consomers of valuation results (db insertion and under valued check)
## The Flow:
```
Thread Pool Thread 1 ──┐
Thread Pool Thread 2 ──┤
Thread Pool Thread 3 ──┼──> event_bus.publish_from_thread(result, loop)
Thread Pool Thread N ──┘
                        │
                        ↓
            loop.call_soon_threadsafe()
                        │
                        ↓
              ┌─────────────────┐
              │  Event Loop     │
              │  Thread         │
              │                 │
              │  • db_handler   │
              │  • alert_handler│
              │  • queue_consumer│
              └─────────────────┘
Alternatives considered:
- PyPubSub, similar to Guava EventBus in Spring/Java, but we don't need the complexity plus its not async aware
- Kafka also too heavy for this use case

'''
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

class AsyncEventBus:    
    def __init__(self):
        self.subscribers = []
        logger.info("AsyncEventBus initialized")

    # registration of subscribers; each subscriber has a callback that fires when the eventbus receives an item
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        logger.info(f"Subscriber {subscriber.__name__} registered")

    def publish_from_thread(self, item, loop, context=None):
        # threads hand off to the main event loop
        logger.info(f"Publishing item {item} from thread to event bus")
        for subscriber in self.subscribers:
            loop.call_soon_threadsafe(subscriber, item, context)