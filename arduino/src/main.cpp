#include "Arduino.h"
#include "Wire.h"
#include <Adafruit_INA219.h>
#include <SPI.h>
#include <TimerOne.h>


#define USE_RAW_MEASUREMENTS

#define READ_MEASUREMENT_INTERVAL_US (1000)
#define REFRESH_LCD_DISPLAY_RATE (100)

#ifndef USE_RAW_MEASUREMENTS
#include <LiquidCrystal.h>
#endif


static Adafruit_INA219 ina219;

// debug pin for osci
static int debug_pin = 8;

#define MEASUREMENTS_PER_SECOND ((1000) / (READ_MEASUREMENT_INTERVAL_US / 1000))

#if ((READ_MEASUREMENT_INTERVAL_US < 1000) || (READ_MEASUREMENT_INTERVAL_US > 255000))
#error Interval must be between 1000 and 255000000
#endif


#ifndef USE_RAW_MEASUREMENTS

static LiquidCrystal lcd(12, 11, 5, 4, 3, 2 );
static uint8_t refresh_lcd_display = 1;

static float shuntvoltage = 0;
static float busvoltage = 0;
static float current_mA = 0;
static float loadvoltage = 0;
static float power = 0;

static float shuntvoltage_prev = 0;
static float busvoltage_prev = 0;
static float current_mA_prev = 0;
static float loadvoltage_prev = 0;
static float power_prev = 0;

#else

static int16_t busvoltage = 0;
static int16_t current_mA = 0;
static int16_t power = 0;

static int16_t busvoltage_prev = 0;
static int16_t current_mA_prev = 0;
static int16_t power_prev = 0;

#endif

static volatile uint8_t trigger_read = 0;

static uint8_t transmit_buf[8];

static volatile uint8_t recv_byte_trigger = false;
static volatile int recv_byte;


#ifndef USE_RAW_MEASUREMENTS
static void read_measurement_pretty() {
  digitalWrite(debug_pin, HIGH);
  float shuntvoltage_read = ina219.getShuntVoltage_mV();
  float busvoltage_read = ina219.getBusVoltage_V();
  float current_mA_read = ina219.getCurrent_mA();
  float loadvoltage_read = busvoltage + (shuntvoltage / 1000);
  float power_read = ina219.getPower_mW();
  digitalWrite(debug_pin, LOW);

  shuntvoltage = shuntvoltage_read;
  busvoltage = busvoltage_read;
  current_mA = current_mA_read;
  loadvoltage = loadvoltage_read;
  power = power_read;
}
#endif

#ifdef USE_RAW_MEASUREMENTS
static void read_measurement() {
  //int16_t shuntvoltage_read = ina219.getShuntVoltage_raw();
  int16_t busvoltage_read = ina219.getBusVoltage_raw();
  int16_t current_mA_read = ina219.getCurrent_raw();
  //int16_t loadvoltage_read = busvoltage + (shuntvoltage / 1000);
  int16_t power_read = ina219.getPower_raw();

  busvoltage_prev = busvoltage;
  busvoltage = busvoltage_read;

  current_mA_prev = current_mA;
  current_mA = current_mA_read;

  power_prev = power;
  power = power_read;
}
#endif


static void tmr_measure_callback() {
  trigger_read = 1;
}

void setup()
{
  Serial.begin(115200);

  pinMode(debug_pin, OUTPUT);
  digitalWrite(debug_pin, LOW);

  transmit_buf[0] = (uint8_t) ('D');
  transmit_buf[7] = (uint8_t) ('\n');

  // Initialize the INA219.
  // By default the initialization will use the largest range (32V, 2A).  However
  // you can call a setCalibration function to change this range (see comments).
  ina219.begin();
  // To use a slightly lower 32V, 1A range (higher precision on amps):
  //ina219.setCalibration_32V_1A();
  // Or to use a lower 16V, 400mA range (higher precision on volts and amps):
  ina219.setCalibration_16V_400mA();

  Timer1.initialize(READ_MEASUREMENT_INTERVAL_US);

#ifndef USE_RAW_MEASUREMENTS
  lcd.backlight();
  lcd.begin(16,2);               // initialize the lcd
#endif

  Serial.println("Measuring voltage and current with INA219 ...");
}


static void send_data_over_serial() {
    transmit_buf[1] = (uint8_t) (busvoltage >> 8);
    transmit_buf[2] = (uint8_t) (busvoltage && 0xFF);

    //transmit_buf[3] = (uint8_t) (shuntvoltage >> 8);
    //transmit_buf[4] = (uint8_t) (shuntvoltage && 0xFF);

    transmit_buf[3] = (uint8_t) (current_mA >> 8);
    transmit_buf[4] = (uint8_t) (current_mA && 0xFF);

    transmit_buf[5] = (uint8_t) (power >> 8);
    transmit_buf[6] = (uint8_t) (power && 0xFF);

    Serial.write(transmit_buf, 8);
}

#ifndef USE_RAW_MEASUREMENTS
static void send_data_over_serial_pretty() {
  Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
  Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
  Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
  Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
  Serial.println("");
}
#endif

#ifndef USE_RAW_MEASUREMENTS
static void show_values_lcd() {

    lcd.clear();
    lcd.home ();                   // go home

    lcd.print(busvoltage);
    lcd.print(" V ");
    lcd.print(current_mA);
    lcd.print(" mA");

    lcd.setCursor ( 0, 1 );        // go to the next line

    lcd.print(power);
    lcd.print(" mW ");
    lcd.print(shuntvoltage);
    lcd.print(" mV");
}
#endif

static void start(void)
{
    Timer1.attachInterrupt(tmr_measure_callback);
}

static void stop(void)
{
    Timer1.stop();
    Timer1.restart();
}

void serialEvent(){
  recv_byte = Serial.read();
  recv_byte_trigger = true;
}

void loop()
{

  if (trigger_read == 1) {
    trigger_read = 0;
    digitalWrite(debug_pin, HIGH);

#ifndef USE_RAW_MEASUREMENTS
    read_measurement_pretty();

    if (refresh_lcd_display == REFRESH_LCD_DISPLAY_RATE) {
      show_values_lcd();
      refresh_lcd_display = 1;
    } else {
      refresh_lcd_display++;
    }
#else
    read_measurement();
    send_data_over_serial();
#endif

    digitalWrite(debug_pin, LOW);
  }


  if (recv_byte_trigger == true) {
    if (recv_byte == 'S') {
      // start
      start();

      Serial.print("SACK\n");
    } else if (recv_byte == 'P') {
      // stop
      stop();

      Serial.print("PACK\n");
    }

    recv_byte_trigger = false;
  }

  //delay(500);
}
