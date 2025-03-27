package KafkaTesting;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.RecordMetadata;

import com.google.gson.Gson;
import com.google.gson.JsonElement;

import Config.ConfigLoader;
import java.util.Properties;
import java.util.HashMap;
import java.util.Map;

public class KafkaTest {

    public static void main(String[] args) {
        publishToTestTopic();
    }

    public static void publishToTestTopic() {
        try {
            ConfigLoader configLoaderInstance = ConfigLoader.getInstance();
            Map<String, Object> kafkaProperties = new HashMap<>();
            kafkaProperties.put("bootstrap.servers", configLoaderInstance.getProperty("bootstrap.servers"));
            kafkaProperties.put("key.serializer", configLoaderInstance.getProperty("key.serializer"));
            kafkaProperties.put("value.serializer", configLoaderInstance.getProperty("value.serializer"));
            KafkaProducer<String, String> producer = new KafkaProducer<>(kafkaProperties);
            
            String topic = "test_topic";
            String data = "stock";
            String data2 = "testmessage";
            ProducerRecord<String, String> record = new ProducerRecord<String, String>(topic, data, data2);
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
                        System.out.printf("Sent message with key=%s value=%s to partition=%d offset=%d%n",
                                data, data2, metadata.partition(), metadata.offset());
                    } else {
                        System.err.println("Error sending message: " + exception.getMessage());
                    }
                    
                }
            });
            producer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
