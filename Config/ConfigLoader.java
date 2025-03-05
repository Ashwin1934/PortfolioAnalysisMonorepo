package Config;

import java.io.FileInputStream;
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
        this.properties = new Properties();
        try (FileInputStream input = new FileInputStream("Config/config.properties")) {
            properties.load(input);
        } catch (Exception e) { // FileNotFound or IOExceptions
            e.printStackTrace();
        }
    }

    public String getProperty(String propertyKey) {
        try {
            if (properties != null) {
                return properties.getProperty(propertyKey);
            }
            return null;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    } 
}

