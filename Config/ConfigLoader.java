package Config;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

public class ConfigLoader {

    /**
     * Eager creation of ConfigLoader to avoid thread synchronization overhead
     */
    private static ConfigLoader instance = new ConfigLoader();
    private Properties properties;

    public static ConfigLoader getInstance() {
        return instance;
    }

    private ConfigLoader() {
        this.properties = properties;
        try (FileInputStream input = new FileInputStream("config.properties")) {
            properties.load(input);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public String getProperty(String propertyKey) {
        try {
            return properties.getProperty(propertyKey);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    } 
}

