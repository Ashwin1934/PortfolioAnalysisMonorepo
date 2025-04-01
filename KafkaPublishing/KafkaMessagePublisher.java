package KafkaPublishing;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;

import Config.ConfigLoader;

public class KafkaMessagePublisher {

    private static KafkaMessagePublisher kafkaMessagePublisher = new KafkaMessagePublisher();
    Map<String, Object> kafkaProperties = new HashMap<>();
    private final KafkaProducer<String, String> producer;
    private String topicName;



    public static KafkaMessagePublisher getInstance() {
        // if (kafkaMessagePublisher == null) {
        //     kafkaMessagePublisher = new KafkaMessagePublisher();
        // }
        return kafkaMessagePublisher;
    }
    
    private KafkaMessagePublisher() {
        System.out.println("Creating kafka publisher");
        ConfigLoader configLoaderInstance = ConfigLoader.getInstance();
        kafkaProperties.put("bootstrap.servers", configLoaderInstance.getProperty("bootstrap.servers"));
        kafkaProperties.put("key.serializer", configLoaderInstance.getProperty("key.serializer"));
        kafkaProperties.put("value.serializer", configLoaderInstance.getProperty("value.serializer"));
        /**
         * Limit the number of retries to 1, otherwise it waits 60000 ms or 1 min before resending.
         * Default number of retries is 2147483647, constrained by timeout of 60000ms I believe.
         * Without this the producer was shutting down with the scheduled executor after 1 min and send() 
         * was still running.
         * 
         */
        kafkaProperties.put("retries", 1); 
        kafkaProperties.put("request.timeout.ms", 50);
        kafkaProperties.put("delivery.timeout.ms", 100);
        /**
         * Note, the above configs did nothing to deter the error message:
         * "Error sending message: Topic test_topic not present in metadata after 60000 ms"
         * I was still getting this despite the configs, and this comes from a metadata fetch call.
         * To explicityly change how long we want to wait for metadata call, we add this property:
         * kafkaProperties.put("max.block.ms", 100);
         */
        kafkaProperties.put("max.block.ms", 100); // Reduce the timeout for metadata fetch to 100ms
        
        this.topicName = configLoaderInstance.getProperty("topic");
        this.producer = new KafkaProducer<>(kafkaProperties);
    }

    public void publishMessage(String jsonData, String ticker, int messageNumber) {
        // no locking needed but multiple threads will access
        System.out.println("Publishing kafka message: " + messageNumber + " for ticker: " + ticker);
        try {
            ProducerRecord<String, String> record = new ProducerRecord<String, String>(topicName, "key", "value"); 
             /**
             * Asynchronously send a record to a topic and invoke the provided callback when the send has been acknowledged.
             * The send is asynchronous and this method will return immediately once the record has been stored in the buffer of records waiting to be sent.
             * This allows sending many records in parallel without blocking to wait for the response after each one.
             */ 
            this.producer.send(record, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    long currentTimeMillis = System.currentTimeMillis();
                    // TODO Auto-generated method stub
                    if (exception == null) {
                        System.out.printf("Sent message number=%d at currentTimeMS=%d with value=%s to partition=%d offset=%d%n",
                                messageNumber, currentTimeMillis, jsonData, metadata.partition(), metadata.offset());
                    } else {
                        System.err.println("Error sending message " + messageNumber + " for ticker " + ticker + " at currentTimeMS " + currentTimeMillis + ": " + exception.getMessage());
                    }   
                }
                
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void shutdownKafkaProducer() {
        producer.close();
        System.out.println("KafkaMessagePublisher shutdown");
    }






}


