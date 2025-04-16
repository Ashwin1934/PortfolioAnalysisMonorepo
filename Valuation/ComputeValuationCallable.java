package Valuation;

import KafkaPublishing.KafkaMessagePublisher;
import SocketTesting.OptimizedUDPServer;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.concurrent.Callable;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;



public class ComputeValuationCallable implements Callable<String> {

    private static final Logger logger = LoggerFactory.getLogger(ComputeValuationCallable.class);
    private final Gson gson = new Gson();
    private JsonObject jsonData;
    private int messageNumber;
    private final double PE_NO_GROWTH = 7;
    private final double GROWTH_RATE_COEFFICIENT = 1.5;
    private final double BOND_YIELD_CONSTANT = 4.4;
    private final double TWENTY_YEAR_CORPORATE_BOND_YIELD = 5.32; // as of Feb 2025
    // private final KafkaMessagePublisher publisher;

    public ComputeValuationCallable(String jsonData, int messageNumber) {
        this.jsonData = getJsonObject(jsonData);
        this.messageNumber = messageNumber;
        // this.publisher = KafkaMessagePublisher.getInstance();
    }

    @Override
    public String call() {
        try {
            String ticker = jsonData.get("ticker").getAsString();
            // System.out.println("Message " + messageNumber + " for ticker: " + ticker + " handled by thread: " + Thread.currentThread().getName());
            logger.info("Message for ticker: {} handled by thread: {}", ticker, Thread.currentThread().getName());

            // relevant data for computation
            double ttmEPS = jsonData.get("ttm_eps").getAsDouble();
            double oneYearGrowthProjection = 0;
            double longTermGrowthProjection = 0;
            try {
                oneYearGrowthProjection = jsonData.get("1yg").getAsDouble();
                longTermGrowthProjection = jsonData.get("LTG").getAsDouble();
            } catch (Exception e) { // NumberFormatException or UnsupportedOperationException
                e.printStackTrace();
            }


            // valuation 
            // TODO compute valuation with revenue growth as the projection as well
            double numerator = ttmEPS * (PE_NO_GROWTH + (GROWTH_RATE_COEFFICIENT * oneYearGrowthProjection)) * BOND_YIELD_CONSTANT;
            double denominator = TWENTY_YEAR_CORPORATE_BOND_YIELD;
            double valuation = numerator / denominator;
            //System.out.println("Valuation for ticker: " + ticker + ": " + valuation);
            logger.info("Valuation for ticker: {}: {}",ticker, valuation);

            // add the valuation to the existing JSONObject and send that to the message queue
            jsonData.add("Valuation", this.gson.toJsonTree(valuation));
            return jsonData.toString();
            // jsonData.toString();
            // KafkaMessagePublisher.getInstance().publishMessage(jsonData.toString(), ticker, messageNumber);
            //this.publisher.publishMessage(jsonData.toString(), messageNumber);
            //System.out.println("ComputeValuation: message " + messageNumber + " processed by KafkaMessagePublisher for: " + ticker);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "Empty string";
    }

    public JsonObject getJsonObject(String data) {
        try {
            JsonObject jsonObject = this.gson.fromJson(data, JsonObject.class);
            return jsonObject;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }


}
