#include <SPI.h>
#include <Ethernet.h>
#include <LiquidCrystal.h>

// Dirección MAC para el shield Ethernet
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFF, 0xEE};

// Dirección IP del servidor
IPAddress server(192, 168, 0, 4); // Dirección IP del servidor

EthernetClient client;

// Inicializa la pantalla LCD con los números de los pines a los que están conectados
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600);
  
  // Configura la pantalla LCD con 16 columnas y 2 filas
  lcd.begin(16, 2);
  
  // Muestra un mensaje inicial en la pantalla LCD
  lcd.print("Inicializando...");

  // Inicializa la conexión Ethernet con DHCP
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    lcd.clear();
    lcd.print("Error Ethernet");
    while (true);
  }
  delay(1000);

  // Imprime la dirección IP asignada al Arduino en la pantalla LCD
  lcd.clear();
  lcd.print("IP: ");
  lcd.print(Ethernet.localIP());

  pinMode(A0, INPUT); // Sensor MQ2 conectado al pin analógico A0
}

void loop() {
  int sensorValue = analogRead(A0); // Lee el valor del sensor MQ2 desde la salida analógica
  Serial.print("Valor del Sensor: ");
  Serial.println(sensorValue);

  // Muestra el valor del sensor en la pantalla LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sensor Value:");
  lcd.setCursor(0, 1);
  lcd.print(sensorValue);

  // Muestra el mensaje "Enviando datos..." en la pantalla LCD
  lcd.setCursor(0, 1);
  lcd.print("Enviando datos...");

  // Intenta conectarse al servidor
  if (client.connect(server, 8000)) { // Puerto donde se ejecuta el servidor Flask
    Serial.println("Conexión al servidor exitosa");
    client.print("GET /saveData?value=");
    client.print(sensorValue); // Enviar el valor del sensor al servidor
    client.println(" HTTP/1.1");
    client.print("Host: ");
    client.println(server); // Añade la dirección IP del servidor en la cabecera Host
    client.println("Connection: close");
    client.println();
    client.stop();
    // Muestra el mensaje de éxito en la pantalla LCD
    lcd.setCursor(0, 1);
    lcd.print("Datos enviados ");
  } else {
    Serial.println("Error de conexión");
    // Muestra un mensaje de error en la pantalla LCD
    lcd.clear();
    lcd.print("Error Conexion");
  }
  
  delay(6000); // Espera 6 segundos antes de enviar el siguiente dato
}
