// RF Switch (BSW6440) - Controls RF signal routing

#pragma once
#include <Arduino.h>

class RFSwitch {
private:
    int _ctrlPin1;
    int _ctrlPin2;
public:
    RFSwitch(int controlPin1, int controlPin2);

    /**
     * @brief Initialize control pins
    */
    void begin();

    /**
     * @brief Set the RF switch path
     * 
     * @param path Path selection (0, 1, or 2)
    */
    void setPath(int path);
};