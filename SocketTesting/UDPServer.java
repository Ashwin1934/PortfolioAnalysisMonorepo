package SocketTesting;

import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class UDPServer {

    private static int UDP_PORT = 5005;
    private static final int numProcessors = Runtime.getRuntime().availableProcessors();
    private static AtomicBoolean continuePolling = new AtomicBoolean(true);


    public static void main(String[] args) {
        shutdownUDPServerAfterSetDuration(15);
        launchUDPServer();

    }

    static void launchUDPServer() {
        System.out.println("UDP server up and listening on 127.0.0.1:5005");
        try {

            ExecutorService executorService = launchExecutorService(numProcessors);
            List<Future<?>> futures = new ArrayList<>();

            DatagramChannel channel = DatagramChannel.open();
            channel.bind(new InetSocketAddress(UDP_PORT));
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

                        System.out.println("Received message from "+ senderAddress + ":" + new String(data));

                        buffer.clear();
                    } else {
                        // no data received
                        System.out.println("No data received");
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }

            }
            System.out.println("DatagramChannel closed.");
            channel.close();
            

            System.out.println("Executor Service shutdown");
            executorService.shutdown();

            // for (Future<?> f: futures) {
            //     f.get();
            // }
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
        // surround with try catch, poll the datagram socket, 
        ScheduledExecutorService scheduledExecutorService = Executors.newScheduledThreadPool(1);
        scheduledExecutorService.schedule(() -> {
            // shut down the executorService after x minutes, all work should be done now
            continuePolling.set(false);
            System.out.println("UDP Server down after " + minutes + " minutes.");
        }, minutes, TimeUnit.MINUTES);
        scheduledExecutorService.shutdown();
        System.out.println("Scheduled Executor Service shutdown.");
    }
}