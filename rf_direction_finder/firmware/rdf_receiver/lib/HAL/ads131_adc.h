/**
 * Driver for ADS131M04
 * Derived from TI sample code and datasheet.
 */

#pragma once

#include <Arduino.h>
#include <SPI.h>

// Configuration
constexpr uint8_t ADS_CHANNEL_COUNT = 4;
constexpr uint8_t ADS_BYTES_PER_WORD = 3; // 24-bit mode

// SPI Command Definitions (Opcodes)
namespace AdsOp {
    // No Operation. Used to clock out data without altering device state.
    constexpr uint16_t NO_OP    = 0x0000; 

    // Software Reset. Resets all registers to default values.
    constexpr uint16_t RESET    = 0x0011; 

    // Read Register. Logical OR with register address (bits 7-13).
    constexpr uint16_t RREG     = 0xA000; 

    // Write Register. Logical OR with register address (bits 7-13).
    constexpr uint16_t WREG     = 0x6000; 

    // Lock SPI Interface. Prevents register writes.
    constexpr uint16_t LOCK     = 0x0555; 

    // Unlock SPI Interface. Enables register writes.
    constexpr uint16_t UNLOCK   = 0x0655; 
}

// Register Map Addresses
namespace AdsReg {
    // Device ID (Read-Only). Contains Family ID and Channel Count.
    constexpr uint8_t ID            = 0x00; 

    // Status Register. Global status (DRDY state, Clock/Reset faults, CRC errors).
    constexpr uint8_t STATUS        = 0x01; 

    // Mode Register. Configures Data Word length (24-bit), CRC enable, and DRDY format.
    constexpr uint8_t MODE          = 0x02; 

    // Clock Register. Sets Oversampling Ratio (OSR), Power Mode, and Channel Enables.
    constexpr uint8_t CLOCK         = 0x03; 

    // Gain Register 1. Sets PGA Gain (1-128) for Channels 0-3.
    constexpr uint8_t GAIN1         = 0x04; 
    
    // Configuration Register. Global Chop (DC offset removal) and diagnostic current sources.
    constexpr uint8_t CFG           = 0x06; 

    // High Threshold (MSB). Upper limit for analog diagnostic comparators.
    constexpr uint8_t THRSHLD_MSB   = 0x07; 

    // High Threshold (LSB). Lower 8 bits for analog diagnostic comparators.
    constexpr uint8_t THRSHLD_LSB   = 0x08; 

    // Channel 0 Configuration. MUX selection (Input/Short/Test) and Phase Delay settings.
    constexpr uint8_t CH0_CFG       = 0x09; 

    // Channel 0 Offset Calibration (MSB). Upper 16 bits of 24-bit offset subtraction value.
    constexpr uint8_t CH0_OCAL_MSB  = 0x0A; 

    // Channel 0 Offset Calibration (LSB). Lower 8 bits of offset subtraction value.
    constexpr uint8_t CH0_OCAL_LSB  = 0x0B; 

    // Channel 0 Gain Calibration (MSB). Upper 16 bits of gain scaling factor.
    constexpr uint8_t CH0_GCAL_MSB  = 0x0C; 

    // Channel 0 Gain Calibration (LSB). Lower 8 bits of gain scaling factor.
    constexpr uint8_t CH0_GCAL_LSB  = 0x0D; 
}

// Default Configurations
namespace AdsDefaults {
    // RX_CRC_EN=0, WLENGTH=24bit, DRDY_FMT=Pulse
    constexpr uint16_t MODE  = 0x0510;
    // OSR=1024, PWR=HR, All Ch Enabled
    constexpr uint16_t CLOCK = 0x0F0E; 
}

struct adc_channel_data {
    uint16_t status;
    int32_t channel[ADS_CHANNEL_COUNT];
    uint16_t crc; // Only populated if RX_CRC_EN is set
};

class Ads131m04 {
public:
    Ads131m04(int csPin, int drdyPin, int rstPin, SPIClass *spiBus = &SPI);

    // Init SPI and verify Device ID (0x2xxx)
    bool begin();

    // Blocking read triggered by DRDY. Populates data struct.
    bool readData(adc_channel_data *data);

    uint16_t readRegister(uint8_t address);
    void writeRegister(uint8_t address, uint16_t value);
    
    // Pulses hardware reset and sends RESET opcode
    void resetDevice();
    
    // Register cache mirroring device state
    uint16_t registerMap[64];

private:
    const int _cs;
    const int _drdy;
    const int _rst;
    SPIClass *_spi;
    SPISettings _spiSettings;

    // Helpers
    static uint16_t combineBytes(uint8_t upper, uint8_t lower);
    static uint8_t upperByte(uint16_t val);
    static uint8_t lowerByte(uint16_t val);
    static int32_t signExtend24(const uint8_t *data);
    
    uint16_t sendCommand(uint16_t opcode);
};

