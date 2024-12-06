#include <Arduino.h>
#include <LovyanGFX.hpp>
#include <Wire.h>
#include "aurebesh_font.h"

// Power control pins
#define BATT_PWR_PIN 10      // Battery power control pin
#define TFT_BL 45            // Backlight control
#define PWR_EN 46            // Power enable pin
#define I2C_SDA 17           // I2C data pin for power management
#define I2C_SCL 18           // I2C clock pin for power management

class LGFX : public lgfx::LGFX_Device
{
    lgfx::Panel_ST7796 _panel_instance;
    lgfx::Bus_Parallel8 _bus_instance;

public:
    LGFX(void)
    {
        {
            auto cfg = _bus_instance.config();
            cfg.port = 0;
            cfg.freq_write = 40000000;
            cfg.pin_wr = 47;
            cfg.pin_rd = -1;
            cfg.pin_rs = 0;
            cfg.pin_d0 = 9;
            cfg.pin_d1 = 46;
            cfg.pin_d2 = 3;
            cfg.pin_d3 = 8;
            cfg.pin_d4 = 18;
            cfg.pin_d5 = 17;
            cfg.pin_d6 = 16;
            cfg.pin_d7 = 15;
            _bus_instance.config(cfg);
            _panel_instance.setBus(&_bus_instance);
        }

        {
            auto cfg = _panel_instance.config();
            cfg.pin_cs = -1;
            cfg.pin_rst = 4;
            cfg.pin_busy = -1;
            cfg.memory_width = 480;
            cfg.memory_height = 480;
            cfg.panel_width = 480;
            cfg.panel_height = 480;
            cfg.offset_x = 0;
            cfg.offset_y = 0;
            cfg.offset_rotation = 0;
            cfg.dummy_read_pixel = 8;
            cfg.dummy_read_bits = 1;
            cfg.readable = true;
            cfg.invert = true;
            cfg.rgb_order = false;
            cfg.dlen_16bit = false;
            cfg.bus_shared = true;
            _panel_instance.config(cfg);
        }
        setPanel(&_panel_instance);
    }
};

LGFX lcd;

// Display constants
const int TFT_WIDTH = 480;
const int CENTER = 240;
const int TEXT_LINES[4][2] = {{60, 280}, {70, 320}, {88, 360}, {140, 400}};

// Colors
#define COLOR_TACTICAL_BLUE 0x24FF
#define COLOR_GREEN 0x07E0
#define COLOR_RED 0xF800
#define COLOR_ORANGE 0xFD20
#define COLOR_YELLOW 0xFFE0
#define COLOR_WHITE 0xFFFF
#define COLOR_BLACK 0x0000

// Tactical Objects (scaled up for 480x480)
const int arcs[5][4] = {
    {300, 380, 60, 0},
    {300, 380, 60, 0},
    {55, 240, 60, 0},
    {55, 90, 90, 0},
    {180, 380, 90, 0}
};

const int angleLines[6][4] = {
    {CENTER + 32, CENTER + 36, 134, 55},
    {CENTER + 42, CENTER + 18, 134, 15},
    {CENTER + 42, CENTER - 18, 134, 345},
    {CENTER + 24, CENTER - 36, 134, 295},
    {CENTER - 24, CENTER - 36, 134, 240},
    {CENTER - 38, CENTER - 18, 134, 200}
};

// Timer structure
typedef struct {
    unsigned long time_start;
    unsigned long durationMs;
} Timer;

void drawLineAtAngle(int x, int y, int length, double angle, uint16_t color) {
    double radians = angle * PI / 180.0;
    int x2 = x + length * cos(radians);
    int y2 = y + length * sin(radians);
    lcd.drawLine(x, y, x2, y2, color);
}

void drawCircleCentered(int r, boolean filled, int increaseWidth, uint16_t color) {
    if (filled) {
        lcd.fillCircle(CENTER, CENTER, r, color);
    } else {
        for (int i = -increaseWidth; i <= increaseWidth; i++) {
            lcd.drawCircle(CENTER, CENTER, r + i, color);
        }
    }
}

void drawArc(int start_degree, int end_degree, int r, uint16_t color) {
    for (int i = start_degree; i <= end_degree; i++) {
        float radian = i * PI / 180.0;
        int x = CENTER + r * cos(radian);
        int y = CENTER + r * sin(radian);
        lcd.drawPixel(x, y, color);
    }
}

void bootTacticalDisplay() {
    // Draw central elements
    drawCircleCentered(CENTER - 34, false, 6, COLOR_TACTICAL_BLUE);
    drawCircleCentered(30, false, 2, COLOR_TACTICAL_BLUE);
    delay(200);

    // Draw arcs
    for (int i = 0; i < 5; i++) {
        for (int j = -arcs[i][3]; j <= arcs[i][3]; j++) {
            drawArc(arcs[i][0], arcs[i][1], arcs[i][2] + j, COLOR_TACTICAL_BLUE);
        }
    }

    // Draw angle lines
    for (int i = 0; i < 6; i++) {
        drawLineAtAngle(angleLines[i][0], angleLines[i][1], 
                       angleLines[i][2], angleLines[i][3], 
                       COLOR_TACTICAL_BLUE);
    }

    // Draw crosshairs
    lcd.drawLine(CENTER, 0, CENTER, TFT_WIDTH, COLOR_TACTICAL_BLUE);
    lcd.drawLine(0, CENTER, TFT_WIDTH, CENTER, COLOR_TACTICAL_BLUE);
}

void initPower() {
    // Initialize I2C for power management
    Wire.begin(I2C_SDA, I2C_SCL);
    
    // Configure power control pins
    pinMode(BATT_PWR_PIN, OUTPUT);
    pinMode(PWR_EN, OUTPUT);
    pinMode(TFT_BL, OUTPUT);
    
    // Enable main power
    digitalWrite(PWR_EN, HIGH);
    delay(100);  // Wait for power to stabilize
    
    // Enable USB/Battery power path
    digitalWrite(BATT_PWR_PIN, HIGH);
    delay(100);
    
    // Enable display backlight
    digitalWrite(TFT_BL, HIGH);
    
    delay(200);  // Give everything time to stabilize
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Starting ESP32-S3 Display");
    
    Serial.println("Initializing power...");
    initPower();
    
    Serial.println("Initializing display...");
    lcd.init();
    Serial.println("Setting rotation...");
    lcd.setRotation(0);
    Serial.println("Setting brightness...");
    lcd.setBrightness(255);  // Maximum brightness
    Serial.println("Filling screen...");
    lcd.fillScreen(COLOR_BLACK);
    
    Serial.println("Booting tactical display...");
    bootTacticalDisplay();
    Serial.println("Setup complete!");
}

void loop() {
    // Add animation effects here
    delay(100);
}
