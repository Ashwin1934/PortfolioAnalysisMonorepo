package SocketTesting;

import Config.ConfigLoader;
import KafkaPublishing.KafkaMessagePublisher;
import Valuation.ComputeValuation;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public class UDPServer {

    private static final int UDP_PORT = Integer.parseInt(ConfigLoader.getInstance().getProperty("udp_server.port"));
    private static final int NUM_PROCESSORS = Runtime.getRuntime().availableProcessors();
    private static AtomicBoolean continuePolling = new AtomicBoolean(true);
    private static AtomicInteger messagesConsumed = new AtomicInteger(0);
    private static final ScheduledExecutorService scheduledExecutorService = Executors.newScheduledThreadPool(1);


    public static void main(String[] args) {
        shutdownUDPServerAfterSetDuration(1);
        launchUDPServer();

    }

    static void launchUDPServer() {
        long startTime = System.currentTimeMillis();
        System.out.println("Start time MS: " + startTime);
        System.out.println("UDP server up and listening on 127.0.0.1: " + UDP_PORT);
        try {

            ExecutorService executorService = launchExecutorService(NUM_PROCESSORS); // Test with just 1 thread
            List<Future<?>> futures = new ArrayList<>();

            DatagramChannel channel = DatagramChannel.open();
            channel.bind(new InetSocketAddress("localhost", UDP_PORT));
            channel.configureBlocking(false);
            ByteBuffer buffer = ByteBuffer.allocate(200);

            while (continuePolling.get()) {
                try {
                    /**
                     * Switched from DatagramSocket to DatagramChannel for the non-blocking capabilities of DatagramChannel.
                     * DatagramSocket receive() method blocks until a packet is received or error is encountered.
                     * This breaks the ScheduledExecutorService logic which tries to reset the boolean value.
                     */
                    SocketAddress senderAddress = channel.receive(buffer); // returns data if available right away otherwise null
                    if (senderAddress != null) {
                        buffer.flip();
                        byte[] data = new byte[buffer.remaining()];
                        buffer.get(data);

                        messagesConsumed.incrementAndGet();

                        System.out.println("Received message number " + messagesConsumed.get() + " from "+ senderAddress);
                        // CompletableFuture.runAsync(
                        //     new ComputeValuation(new String(data), messagesConsumed.get())
                        // ); // note this is currently running with built in thread pool
                        CompletableFuture.runAsync(
                            new ComputeValuation(new String(data), messagesConsumed.get()),
                            executorService
                        ); // run with 8 threads

                        buffer.clear();
                    } else {
                        // no data received
                        // System.out.println("No data received");
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }

            }
            System.out.println("Messages consumed: " + messagesConsumed.get());

            /**
             * Initiate shutdown of sockets and executors.
             */
            System.out.println("DatagramChannel closed.");
            channel.close();
            System.out.println("Executor Service shutdown");
            executorService.shutdown();
            System.out.println("Scheduled Executor Service shutdown.");
            scheduledExecutorService.shutdown();
            KafkaMessagePublisher.getInstance().shutdownKafkaProducer();

        } catch(Exception e) {
            e.printStackTrace();
        }
    }

    private static ExecutorService launchExecutorService(int numThreads) {
        try {
            return Executors.newFixedThreadPool(numThreads);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            
        }
        return null;
    }

    private static void shutdownUDPServerAfterSetDuration(int minutes) {
        System.out.println("Entered shutdownUDPServerAfterSetDuration.");
        scheduledExecutorService.schedule(() -> {
            // shut down the executorService after x minutes, all work should be done now
            continuePolling.set(false);
            System.out.println("UDP Server down after " + minutes + " minutes.");
        }, minutes, TimeUnit.MINUTES);
    }
}