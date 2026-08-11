// LMX2572 Local Oscillator (LO) - Frequency synthesis for RF receiver

#include <lmx2572_lo.h>

LMX2572::LMX2572(int csPin, int lockPin, SPIClass *spiInterface) 
    : _csPin(csPin), _lockPin(lockPin), _spi(spiInterface) {
}

void LMX2572::begin() {
    pinMode(_csPin, OUTPUT);
    digitalWrite(_csPin, HIGH);
    
    if (_lockPin >= 0) {
        pinMode(_lockPin, INPUT);
    }

    _spi->begin(); 
}

void LMX2572::writeRegister(uint8_t reg, uint16_t data) {
    // LMX2572 format: 1 bit R/W (0=Write), 7 bit Reg Addr, 16 bit Data
    
    uint8_t byte1 = (reg & 0x7F); // R/W bit is 0 for write
    uint8_t byte2 = (data >> 8) & 0xFF;
    uint8_t byte3 = data & 0xFF;

    _spi->beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE0));
    digitalWrite(_csPin, LOW);
    
    _spi->transfer(byte1);
    _spi->transfer(byte2);
    _spi->transfer(byte3);
    
    digitalWrite(_csPin, HIGH);
    _spi->endTransaction();
}

void LMX2572::loadMap(const uint32_t* regMap, size_t len) {
    // Write in reverse order (highest register first), R0 last.
    // Array already ordered in reverse order.
    for (int i = 0; i < len; i++) {
        uint32_t val = regMap[i];
        uint8_t reg = (val >> 16) & 0x7F;
        uint16_t data = val & 0xFFFF;
        writeRegister(reg, data);
    }
}

double LMX2572::setFrequency(double targetFreqMHz) {
    // Calculate Output Divider (CHDIV)
    // VCO Range: 3200 to 6400 MHz
    
    // VCO limits
    constexpr double VCO_MIN = 3200.0;
    constexpr double VCO_MAX = 6400.0;
    
    uint8_t outDiv = 0; 
    int divVal = 2; 
    
    // Find valid divider
    while ( (targetFreqMHz * divVal) < VCO_MIN ) {
        divVal += 2;
        if (divVal > 192) return 0.0; // Error: Frequency too low
    }
    
    double vcoFreq = targetFreqMHz * divVal;
    if (vcoFreq > VCO_MAX) return 0.0; // Error: Frequency too high

    // Write Output Divider
    writeRegister(REG_R73, divVal); 

    // Calculate PLL Feedback
    // f_vco = f_osc * (PLL_N + NUM / DEN)
    double n_full = vcoFreq / REF_FREQ_MHZ;
    uint16_t N = (uint16_t)n_full;
    
    double fraction = n_full - N;
    constexpr uint32_t DEN = 1000000;
    uint32_t NUM = (uint32_t)(fraction * DEN);
    
    // Write PLL Registers
    writeRegister(REG_R36, N);
    
    writeRegister(REG_R38, (DEN >> 16) & 0xFFFF);
    writeRegister(REG_R39, DEN & 0xFFFF);
    
    writeRegister(REG_R42, (NUM >> 16) & 0xFFFF);
    writeRegister(REG_R43, NUM & 0xFFFF);

    // Trigger Calibration (R0)
    // Writes generic R0 config. Verify specific bits with TICS Pro!
    writeRegister(REG_R0, 0x2418); 

    return (REF_FREQ_MHZ * (N + (double)NUM/DEN)) / divVal;
}

bool LMX2572::isLocked() {
    if (_lockPin == -1) return false;
    return digitalRead(_lockPin) == HIGH; 
}