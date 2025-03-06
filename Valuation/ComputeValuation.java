package Valuation;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.ietf.jgss.GSSContext;


public class ComputeValuation implements Runnable {

    private final Gson gson = new Gson();
    private JsonObject jsonData;
    private int messageNumber;
    private final double PE_NO_GROWTH = 7;
    private final double GROWTH_RATE_COEFFICIENT = 1.5;
    private final double BOND_YIELD_CONSTANT = 4.4;
    private final double TWENTY_YEAR_CORPORATE_BOND_YIELD = 5.32; // as of Feb 2025

    public ComputeValuation(String jsonData, int messageNumber) {
        this.jsonData = getJsonObject(jsonData);
        this.messageNumber = messageNumber;
    }

    @Override
    public void run() {
        try {
            String ticker = jsonData.get("ticker").getAsString();
            System.out.println("Message " + messageNumber + " for ticker: " + ticker + " handled by thread: " + Thread.currentThread().getName());
            
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
            double numerator = ttmEPS * (PE_NO_GROWTH + (GROWTH_RATE_COEFFICIENT * oneYearGrowthProjection)) + BOND_YIELD_CONSTANT;
            double denominator = TWENTY_YEAR_CORPORATE_BOND_YIELD;
            double valuation = numerator / denominator;
            System.out.println("Valuation for ticker: " + ticker + ": " + valuation);

            // add the valuation to the existing JSONObject and send that to the message queue
            jsonData.add("Valuation", this.gson.toJsonTree(valuation));
        } catch (Exception e) {
            e.printStackTrace();
        }
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