# ESP32 Manual Water Command Integration

This backend now supports a device command flow for ESP32 devices so the mobile app can trigger real pump actions.

## New IoT Endpoints

- `POST /api/iot/commands/`
  - Create a manual device command by `device_id` or `plant_id`
  - Example body:
    ```json
    {
      "plant_id": 1,
      "command_type": "water",
      "duration_seconds": 5,
      "notes": "Manual water button"
    }
    ```

- `GET /api/iot/commands/{device_id}/`
  - ESP32 polls this endpoint to fetch pending commands.
  - Returns an array of pending commands.

- `POST /api/iot/commands/{command_id}/ack/`
  - ESP32 calls this after executing the command.

## Recommended ESP32 behavior

1. Periodically poll `/api/iot/commands/{device_id}/`.
2. If a pending command is returned, execute it.
3. For `command_type == "water"`, enable the pump relay for `duration_seconds`.
4. After execution, POST an acknowledgment to `/api/iot/commands/{command_id}/ack/`.

## Example Arduino sketch logic

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const String backendBase = "http://192.168.1.10:8001/api";
const String deviceId = "esp32-plant-01";
const int relayPin = 26;

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // relay off if active low
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    checkDeviceCommands();
  }
  delay(10000);
}

void checkDeviceCommands() {
  HTTPClient http;
  String url = backendBase + "/iot/commands/" + deviceId + "/";
  http.begin(url);
  int httpCode = http.GET();
  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);
    if (doc.is<JsonArray>()) {
      for (JsonObject cmd : doc.as<JsonArray>()) {
        String commandType = cmd["command_type"].as<String>();
        int commandId = cmd["id"].as<int>();
        int duration = cmd["duration_seconds"].as<int>();
        if (commandType == "water") {
          runPump(duration);
          acknowledgeCommand(commandId);
        }
      }
    }
  }
  http.end();
}

void runPump(int durationSeconds) {
  digitalWrite(relayPin, LOW);
  delay(durationSeconds * 1000);
  digitalWrite(relayPin, HIGH);
}

void acknowledgeCommand(int commandId) {
  HTTPClient http;
  String url = backendBase + "/iot/commands/" + String(commandId) + "/ack/";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST("{}");
  http.end();
}
```

### Note on Backend Host

When cloning this repository or running the ESP32 on a different machine, set `backendBase` to your backend host's LAN IP address:

```cpp
const String backendBase = "http://<YOUR_BACKEND_IP>:8001/api";
```

Do not use `localhost` from the ESP32 unless the backend is running on the same device as the ESP32.

## Notes

- The mobile manual water button now creates a backend command if the plant is linked to an ESP32 device.
- If the plant is not linked to a device, the button still updates watering history locally but cannot trigger physical hardware.
- Adjust `duration_seconds` to suit your pump and irrigation setup.
