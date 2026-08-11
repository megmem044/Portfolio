// LMX2572 Local Oscillator (LO) - Frequency synthesis for RF receiver

#pragma once

#include <Arduino.h>
#include <SPI.h>

class LMX2572 {
private:
    int _csPin;
    int _lockPin; // MUXOUT pin for lock detection
    SPIClass *_spi;
    
    /**
     * @brief helper to send 24-bit data (Reg Addr + Data)
     * 
    */
    void writeRegister(uint8_t reg, uint16_t data);

    // Registers (LMX2572 Specific)
    static constexpr uint8_t REG_R0   = 0;   // Reset & Calibration
    static constexpr uint8_t REG_R36  = 36;  // PLL_N (Integer part)
    static constexpr uint8_t REG_R37  = 37;  // PFD_DLY, MASH_ORDER
    static constexpr uint8_t REG_R38  = 38;  // PLL_DEN (Denominator MSB)
    static constexpr uint8_t REG_R39  = 39;  // PLL_DEN (Denominator LSB)
    static constexpr uint8_t REG_R42  = 42;  // PLL_NUM (Numerator MSB)
    static constexpr uint8_t REG_R43  = 43;  // PLL_NUM (Numerator LSB)
    static constexpr uint8_t REG_R73  = 73;  // Channel Divider (OUT_DIV)
    static constexpr uint8_t REG_R75  = 75;  // VCO Divider

    static constexpr uint32_t INIT_MAP[] = {
        0x7D0820, // R125
        0x7C0000, // R124
        0x7B0000, // R123
        0x7A0000, // R122
        0x790000, // R121
        0x780000, // R120
        0x770000, // R119
        0x760000, // R118
        0x750000, // R117
        0x740000, // R116
        0x730000, // R115
        0x727802, // R114
        0x710000, // R113
        0x700000, // R112
        0x6F0000, // R111
        0x6E0000, // R110
        0x6D0000, // R109
        0x6C0000, // R108
        0x6B0000, // R107
        0x6A0007, // R106
        0x694440, // R105
        0x682710, // R104
        0x670000, // R103
        0x660000, // R102
        0x650000, // R101
        0x642710, // R100
	    0x630000, // R99
	    0x620000, // R98
	    0x610000, // R97
	    0x600000, // R96
	    0x5F0000, // R95
	    0x5E0000, // R94
	    0x5D0000, // R93
	    0x5C0000, // R92
	    0x5B0000, // R91
	    0x5A0000, // R90
	    0x590000, // R89
	    0x580000, // R88
	    0x570000, // R87
	    0x560000, // R86
	    0x55D800, // R85
	    0x540001, // R84
	    0x530000, // R83
	    0x522800, // R82
	    0x510000, // R81
	    0x50CCCC, // R80
	    0x4F004C, // R79
	    0x4E027F, // R78
	    0x4D0000, // R77
	    0x4C000C, // R76
	    0x4B0840, // R75
	    0x4A0000, // R74
	    0x49003F, // R73
	    0x480001, // R72
	    0x470081, // R71
	    0x46C350, // R70
	    0x450000, // R69
	    0x4403E8, // R68
	    0x430000, // R67
	    0x4201F4, // R66
	    0x410000, // R65
	    0x401388, // R64
	    0x3F0000, // R63
	    0x3E00AF, // R62
	    0x3D00A8, // R61
	    0x3C03E8, // R60
	    0x3B0001, // R59
	    0x3A9001, // R58
	    0x390020, // R57
	    0x380000, // R56
	    0x370000, // R55
	    0x360000, // R54
	    0x350000, // R53
	    0x340421, // R52
	    0x330080, // R51
	    0x320080, // R50
	    0x314180, // R49
	    0x3003E0, // R48
	    0x2F0300, // R47
	    0x2E07F0, // R46
	    0x2DC604, // R45
	    0x2C0423, // R44
	    0x2B40DA, // R43
	    0x2A8DA7, // R42
	    0x290000, // R41
	    0x280000, // R40
	    0x27AAAA, // R39
	    0x26AAAA, // R38
	    0x250305, // R37
	    0x240056, // R36
	    0x230004, // R35
	    0x220010, // R34
	    0x211E01, // R33
	    0x2005BF, // R32
	    0x1FC3E6, // R31
	    0x1E0CA6, // R30
	    0x1D0000, // R29
	    0x1C0488, // R28
	    0x1B0002, // R27
	    0x1A0808, // R26
	    0x190624, // R25
	    0x18071A, // R24
	    0x17007C, // R23
	    0x160001, // R22
	    0x150409, // R21
	    0x144848, // R20
	    0x1327B7, // R19
	    0x120064, // R18
	    0x110089, // R17
	    0x100080, // R16
	    0x0F060E, // R15
	    0x0E1820, // R14
	    0x0D4000, // R13
	    0x0C5001, // R12
	    0x0BB018, // R11
	    0x0A10F8, // R10
	    0x090004, // R9
	    0x082000, // R8
	    0x0700B2, // R7
	    0x06C802, // R6
	    0x0530C8, // R5
	    0x040A43, // R4
	    0x030782, // R3
	    0x020500, // R2
	    0x010808, // R1
	    0x00209C  // R0
    };

public:
    static constexpr float REF_FREQ_MHZ = 40.0f;
    static constexpr uint32_t SPI_SPEED = 10000000;


    LMX2572(int csPin, int lockPin = -1, SPIClass *spiInterface = &SPI);

    /**
     * @brief Initialize SPI and LO settings
     */
    void begin();
    
    /**
     * @brief Set output frequency
     * 
     * @param targetFreqMHz Desired frequency in MHz
     * @return actual frequency achieved (due to fractional resolution)
     */
    double setFrequency(double targetFreqMHz);

    /**
     * @brief Load a register map from an array
     *
     * @param regMap Pointer to array of 32-bit register values (exported from TICs Pro)
     * @param len Number of registers in the array
    */
    void loadMap(
        const uint32_t* regMap = INIT_MAP,
        size_t len = sizeof(INIT_MAP)/sizeof(INIT_MAP[0])
    );
    
    /**
     * @brief Check if the LO is locked
     * 
     * @return true if locked, false otherwise
     */
    bool isLocked();
};
