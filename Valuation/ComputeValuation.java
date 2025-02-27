package Valuation;

import com.google.gson.Gson;
import com.google.gson.JsonObject;


public class ComputeValuation implements Runnable {

    private JsonObject jsonData;
    private int messageNumber;

    public ComputeValuation(String jsonData, int messageNumber) {
        this.jsonData = getJsonObject(jsonData);
        this.messageNumber = messageNumber;
    }

    @Override
    public void run() {
        System.out.println("Message " + messageNumber + " handled by thread: " + Thread.currentThread().getName());
        System.out.println(jsonData.get("ticker").getAsString());
        System.out.println(jsonData.get("price").getAsDouble());
        System.out.println(jsonData.get("ttm_eps").getAsDouble());
        System.out.println(jsonData.get("price_tgt").getAsDouble());
    }

    public JsonObject getJsonObject(String data) {
        try {
            Gson gson = new Gson();
            JsonObject jsonObject = gson.fromJson(data, JsonObject.class);
            return jsonObject;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }


}