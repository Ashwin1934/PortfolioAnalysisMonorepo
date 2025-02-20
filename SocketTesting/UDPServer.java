package SocketTesting;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.List;
import java.util.ArrayList;

public class UDPServer {

    private static String UDP_IP = "127.0.0.1";
    private static int UDP_PORT = 5005;
    private static int num_processors = Runtime.getRuntime().availableProcessors();
    private static AtomicBoolean continue_polling = new AtomicBoolean(true);


    public static void main(String[] args) {
        shutdownUDPServerAfterSetDuration(1);
        launchUDPServer();

    }

    static void launchUDPServer() {
        System.out.println("UDP server up and listening on 127.0.0.1:5005");
        try {

            ExecutorService executorService = launchExecutorService(num_processors);
            List<Future<?>> futures = new ArrayList<>();

            DatagramSocket socket = new DatagramSocket(UDP_PORT);
            socket.setSoTimeout(1000);
            byte[] buffer = new byte[200]; // todo configurable number 

            while (continue_polling.get()) {
                try {
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    
                    socket.receive(packet); // this blocks until a datagram packet is received or an error is encountered

                    InetAddress address = packet.getAddress();
                    int receivedPort = packet.getPort();
                    String data = new String(packet.getData(), 0, packet.getLength());

                    System.out.println("Received message:" + data + "from " + address + ":" + receivedPort);
                    Future<?> future = executorService.submit(new Runnable() {
                        @Override
                        public void run() {
                            System.out.println("thread" + Thread.currentThread().getName());
                            System.out.println("Received message:" + data + "from " + address + ":" + receivedPort);
                        }
                    });
                    futures.add(future);
                    future.get(); // try this out, I feel it may block the process...
                } catch (SocketTimeoutException e) {

                }

            }
            System.out.println("UDP Socket closed.");
            socket.close();
            

            System.out.println("Executor Service shutdown");
            executorService.shutdown();

            for (Future<?> f: futures) {
                f.get();
            }
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
        scheduledExecutorService.schedule(new Runnable() {
            @Override
            public void run() {
                // shut down the executorService after 5 minutes, all work should be done now
                continue_polling.set(false);
                System.out.println("UDP Server down after 5 minutes.");
            }
        }, minutes, TimeUnit.MINUTES);
        scheduledExecutorService.shutdown();
        System.out.println("Scheduled Executor Service shutdown.");
    }
}