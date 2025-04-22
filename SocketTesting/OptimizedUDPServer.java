package SocketTesting;

import Config.ConfigLoader;
import KafkaPublishing.KafkaMessagePublisher;
import Valuation.ComputeValuation;
import Valuation.ComputeValuationCallable;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.UUID;

public class OptimizedUDPServer {

    private static final Logger logger = LoggerFactory.getLogger(OptimizedUDPServer.class);
    private static final int UDP_PORT = Integer.parseInt(ConfigLoader.getInstance().getProperty("udp_server.port"));
    private static final int NUM_PROCESSORS = Runtime.getRuntime().availableProcessors();
    private static AtomicBoolean continuePolling = new AtomicBoolean(true);
    private static AtomicInteger messagesConsumed = new AtomicInteger(0);
    private static AtomicInteger messagesSent = new AtomicInteger(0);
    private static KafkaProducer<String, String> kafkaProducer = createKafkaProducer();
    private static final ExecutorService computeExecutorService = launchExecutorService(NUM_PROCESSORS);
    private static final ExecutorService ioExecutorService = launchExecutorService(NUM_PROCESSORS * 2);


    public static void main(String[] args) {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutdown signal received. Stopping server...");
            computeExecutorService.shutdown();
            ioExecutorService.shutdown();
            shutdownUDPServer();
        }));
        launchUDPServer();
    }

    static void launchUDPServer() {
        long startTime = System.currentTimeMillis();
        logger.info("Start time MS: {}", startTime);
        logger.info("UDP server up and listening on 127.0.0.1: {}", UDP_PORT);

        try {
            DatagramChannel channel = DatagramChannel.open();
            channel.bind(new InetSocketAddress("localhost", UDP_PORT));
            channel.configureBlocking(false);

            while (continuePolling.get()) {
                try {
                    ByteBuffer buffer = ByteBuffer.allocate(200);
                    SocketAddress senderAddress = channel.receive(buffer); // returns data if available right away otherwise null
                    if (senderAddress != null) {
                        buffer.flip();
                        byte[] dataCopy = new byte[buffer.remaining()];
                        buffer.get(dataCopy);

                        logger.info("Received message from {}", senderAddress);
                        CompletableFuture.runAsync(() -> processMessageAsync(dataCopy), computeExecutorService);
                        logger.info("Message getting processed asynchronously for {}", senderAddress);

                        buffer.clear();
                    }
                } catch (Exception e) {
                    logger.error("Error in UDP server loop", e);
                }
            }
            channel.close();
            logger.info("DatagramChannel closed.");
        } catch (Exception e) {
            logger.error("Error in launchUDPServer", e);
        }
    }

    private static ExecutorService launchExecutorService(int numThreads) {
        try {
            return Executors.newFixedThreadPool(numThreads);
        } catch (Exception e) {
            logger.error("Error creating ExecutorService", e);
        }
        return null;
    }

    private static void shutdownUDPServer() {
        logger.info("Shutting down UDP Server.");
        continuePolling.set(false);
        logger.info("UDP Server down.");
    }

    private static KafkaProducer<String, String> createKafkaProducer() {
        ConfigLoader configLoaderInstance = ConfigLoader.getInstance();
        Map<String, Object> kafkaProperties = new HashMap<>();

        kafkaProperties.put("bootstrap.servers", configLoaderInstance.getProperty("bootstrap.servers"));
        kafkaProperties.put("key.serializer", configLoaderInstance.getProperty("key.serializer"));
        kafkaProperties.put("value.serializer", configLoaderInstance.getProperty("value.serializer"));
        kafkaProperties.put("retries", 0);
        kafkaProperties.put("request.timeout.ms", 50);
        kafkaProperties.put("delivery.timeout.ms", 300);
        kafkaProperties.put("max.block.ms", 300); // Reduce the timeout for metadata fetch to 100ms
        kafkaProperties.put("max.in.flight.requests.per.connection", 10);

        return new KafkaProducer<>(kafkaProperties);
    }

    /**
     * This is executed in a new thread as per the CompletableFuture runAsync invocation of this method.
     * @param message
     */
    private static void processMessageAsync(byte[] message) {
        CompletableFuture<String> valuation = CompletableFuture.supplyAsync(
            () -> new ComputeValuationCallable(new String(message), messagesConsumed.get()).call(),
            computeExecutorService
        );

        valuation.thenAcceptAsync(valuationString -> {
            /** the valuation computation doesn't take long but in case anything else is added to the valuation process, we will use thenAcceptAsync
             * to simulate a nonblocking approach
             */
            int messageNumber = messagesSent.incrementAndGet();
            logger.info("Valuation for message {}: {} sent by thread: {}", messageNumber, valuationString, Thread.currentThread().getName());
            ProducerRecord<String, String> record = new ProducerRecord<>("test_topic", UUID.randomUUID().toString(), valuationString);
            kafkaProducer.send(record, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    long currentTimeMillis = System.currentTimeMillis();
                    if (exception == null) {
                        logger.info("Sent message number={} at currentTimeMS={} with value={} to partition={} offset={}",
                                messageNumber, currentTimeMillis, valuationString, metadata.partition(), metadata.offset());
                    } else {
                        logger.error("Error sending message {} at currentTimeMS {}: {}", messageNumber, currentTimeMillis, exception.getMessage());
                    }   
                }
            });
        }, ioExecutorService);
    }
}
