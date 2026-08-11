#pragma once

#include <rf_switch.h>
#include <lmx2572_lo.h>
#include <ads131_adc.h>

#include <lcd.h>

namespace HAL::RF
{
    // TODO: correct pin assignments
    RFSwitch rfSwitchChan0(10, 11);
    RFSwitch rfSwitchChan1(12, 13);
    LMX2572 lo0(9, 8);
    LMX2572 lo1(4, 3);
    Ads131m04 adc(7, 6, 5);
}


namespace HAL::DIGITAL
{
    LCD lcdDisplay(240, 240);
}