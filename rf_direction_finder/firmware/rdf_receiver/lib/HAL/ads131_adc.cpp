/**
 * ads131_adc.cpp
 */

#include <ads131_adc.h>

constexpr uint32_t SPI_SPEED = 4000000; // 4 Mhz. Max 25MHz

Ads131m04::Ads131m04(int csPin, int drdyPin, int rstPin, SPIClass *spiBus) 
    : _cs(csPin), _drdy(drdyPin), _rst(rstPin), _spi(spiBus) {
    _spiSettings = SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE1);
}

bool Ads131m04::begin() {
    pinMode(_cs, OUTPUT);
    pinMode(_drdy, INPUT);
    pinMode(_rst, OUTPUT);
    
    digitalWrite(_cs, HIGH);
    digitalWrite(_rst, HIGH);

    _spi->begin();

    resetDevice();

    // Verify family ID and channel count (0x04)
    uint16_t id = readRegister(AdsReg::ID);
    return ((id >> 8) == 0x24);
}

void Ads131m04::resetDevice() {
    // Hardware pulse (tSRLRST > 1ms)
    digitalWrite(_rst, LOW);
    delayMicroseconds(50);
    digitalWrite(_rst, HIGH);
    delay(2); 

    // Software reset to clear internal filters
    sendCommand(AdsOp::RESET);
    delay(2);
}

uint16_t Ads131m04::readRegister(uint8_t address) {
    // Frame 1: Request | Frame 2: Response
    uint16_t opcode = AdsOp::RREG | (static_cast<uint16_t>(address) << 7);
    
    sendCommand(opcode);
    uint16_t value = sendCommand(AdsOp::NO_OP);
    
    registerMap[address] = value;
    return value;
}

void Ads131m04::writeRegister(uint8_t address, uint16_t value) {
    uint16_t opcode = AdsOp::WREG | (static_cast<uint16_t>(address) << 7);
    
    // Full frame transaction required to maintain sync
    uint8_t txData[6] = {
        upperByte(opcode), lowerByte(opcode), 0x00,
        upperByte(value),  lowerByte(value),  0x00
    };
    uint8_t rxData[6]; // Dummy rx

    _spi->beginTransaction(_spiSettings);
    digitalWrite(_cs, LOW);
    _spi->transferBytes(txData, rxData, 6);
    digitalWrite(_cs, HIGH);
    _spi->endTransaction();

    registerMap[address] = value;
}

bool Ads131m04::readData(adc_channel_data *data) {
    if (!data) return false;

    // Payload: status + 4 channels. Each word is 3 bytes (24-bit)
    constexpr size_t TOTAL_BYTES = (1 + ADS_CHANNEL_COUNT) * ADS_BYTES_PER_WORD;
    
    uint8_t rx[TOTAL_BYTES];
    // Use NULL opcode to clock out data
    uint8_t tx[TOTAL_BYTES] = {0}; 

    _spi->beginTransaction(_spiSettings);
    digitalWrite(_cs, LOW);
    _spi->transferBytes(tx, rx, TOTAL_BYTES);
    digitalWrite(_cs, HIGH);
    _spi->endTransaction();

    data->status = combineBytes(rx[0], rx[1]);

    for (int i = 0; i < ADS_CHANNEL_COUNT; i++) {
        size_t offset = (i + 1) * ADS_BYTES_PER_WORD;
        data->channel[i] = signExtend24(&rx[offset]);
    }
    
    return true; 
}

uint16_t Ads131m04::sendCommand(uint16_t opcode) {
    uint8_t tx[3] = { upperByte(opcode), lowerByte(opcode), 0x00 };
    uint8_t rx[3];
    
    _spi->beginTransaction(_spiSettings);
    digitalWrite(_cs, LOW);
    _spi->transferBytes(tx, rx, 3);
    digitalWrite(_cs, HIGH);
    _spi->endTransaction();
    
    return combineBytes(rx[0], rx[1]);
}


int32_t Ads131m04::signExtend24(const uint8_t *data) {
    int32_t val = (static_cast<int32_t>(data[0]) << 24) | 
                  (static_cast<int32_t>(data[1]) << 16) | 
                  (static_cast<int32_t>(data[2]) << 8);
    return (val >> 8);
}

uint16_t Ads131m04::combineBytes(uint8_t upper, uint8_t lower) {
    return (static_cast<uint16_t>(upper) << 8) | lower;
}

uint8_t Ads131m04::upperByte(uint16_t val) {
    return static_cast<uint8_t>((val >> 8) & 0xFF);
}

uint8_t Ads131m04::lowerByte(uint16_t val) {
    return static_cast<uint8_t>(val & 0xFF);
}