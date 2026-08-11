/**
 * Wrapper for the Adafruit_GFX library to provide LCD functionality
 * for displaying bearing and other information.
 */

#pragma once
#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <Adafruit_SPITFT.h>


class LCD {
public:
    /**
     * @brief Constructor
     * @param width Screen width in pixels
     * @param height Screen height in pixels
     */
    LCD(int width, int height);

    /**
     * @brief Initialize the display, set rotations, and draw static UI elements 
     * (borders, labels).
     */
    void begin();

    /**
     * @brief The main update loop for the UI. Call this only when data changes.
     * 
     * @param bearingDegrees Calculated Angle of Arrival (0.0 - 359.9)
     * @param freqMHz Current Tuned Frequency (e.g., 433.0)
     * @param magnitude Magnitude/RSSI - for signal strength
     * @param systemState Current status string (e.g., "SCAN", "LOCK", "CALIB")
     */
    void updateDashboard(float bearingDegrees, float freqMHz, float magnitude, String systemState);

    /**
     * @brief Displays a visual warning.
     */
    void showAlert(String errorMessage);

private:
    Adafruit_ST7789 _tft;
    int _width;
    int _height;
    int _centerX;
    int _centerY;
    
    float _lastBearing;
    float _lastFreq;
    String _lastState;

    // Graphics Configuration
    const int COMPASS_RADIUS = 40;
    const uint16_t COLOR_BG = 0x0000;   // Black
    const uint16_t COLOR_TEXT = 0xFFFF; // White
    const uint16_t COLOR_ACCENT = 0x07E0; // Green

    // Internal Helpers
    void drawCompassFace();
    void drawBearingNeedle(float angle, uint16_t color);
    void clearOldValue(int x, int y, int w, int h);
};
