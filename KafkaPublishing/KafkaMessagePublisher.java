package KafkaPublishing;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;

import Config.ConfigLoader;

public class KafkaMessagePublisher {

    public static KafkaMessagePublisher kafkaMessagePublisher = new KafkaMessagePublisher();
    Map<String, Object> kafkaProperties = new HashMap<>();
    private KafkaProducer<String, String> producer;
    private String topicName;



    public static KafkaMessagePublisher getInstance() {
        // if (kafkaMessagePublisher == null) {
        //     kafkaMessagePublisher = new KafkaMessagePublisher();
        // }
        System.out.println("KafkaMessagePublisher instance fetched");
        return kafkaMessagePublisher;
    }
    
    private KafkaMessagePublisher() {
        ConfigLoader configLoaderInstance = ConfigLoader.getInstance();
        kafkaProperties.put("bootstrap.servers", configLoaderInstance.getProperty("bootstrap.servers"));
        kafkaProperties.put("key.serializer", configLoaderInstance.getProperty("key.serializer"));
        kafkaProperties.put("value.serializer", configLoaderInstance.getProperty("value.serializer"));
        topicName = configLoaderInstance.getProperty("topic");
        producer = new KafkaProducer<>(kafkaProperties);
    }

    public static void publishMessage(String jsonData) {
        // no locking needed but multiple threads will access
        System.out.println("Publishing kafka message");
        try {
            ProducerRecord<String> record = new ProducerRecord<String>(topicName, jsonData); 
             /**
             * Asynchronously send a record to a topic and invoke the provided callback when the send has been acknowledged.
             * The send is asynchronous and this method will return immediately once the record has been stored in the buffer of records waiting to be sent.
             * This allows sending many records in parallel without blocking to wait for the response after each one.
             */ 
            producer.send(record, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    // TODO Auto-generated method stub
                    if (exception == null) {
                        System.out.printf("Sent message with value=%s to partition=%d offset=%d%n",
                                jsonData, metadata.partition(), metadata.offset());
                    } else {
                        System.err.println("Error sending message: " + exception.getMessage());
                    }   
                }
                
            })
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void shutdownKafkaProducer() {
        producer.close();
    }






}


