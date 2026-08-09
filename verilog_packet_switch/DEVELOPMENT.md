# Development Phases

This document records how the 4-port packet switch has been built so far. The work is divided into small phases so each design decision and verification layer can be reviewed independently.

## Phase 1: Define the Project

The project began with four inputs, four outputs, a fixed-width packet, and a 2-bit destination stored in the packet's upper bits. Ready/valid handshakes were chosen so senders and receivers can pause safely without losing data.

The design was split into four understandable RTL responsibilities:

- Store packets waiting at each input.
- Decode the destination of each front packet.
- Select fairly when inputs compete for an output.
- Connect all components and external handshakes.

## Phase 2: Build the Input Packet Queue

File: `rtl/input_packet_queue.v`

A synchronous FIFO was implemented for each input. It contains packet memory, read and write positions, and an occupancy count. Full and empty flags reject unsafe pushes and pops. Simultaneous push and pop operations leave the occupancy unchanged.

The pointers wrap after the final storage slot, making the memory operate as a circular queue.

## Phase 3: Build Fair Output Selection

File: `rtl/fair_output_selector.v`

A four-request round-robin selector was implemented for one output. Its combinational logic grants the first active request starting from the saved priority. The grant is one-hot, meaning at most one input wins.

Priority changes only after the receiving output accepts a transfer. This preserves fairness when an output applies backpressure.

## Phase 4: Decode Packet Destinations

File: `rtl/packet_destination_decoder.v`

The decoder reads the upper two bits of the front packet and creates a one-hot request for Outputs 0 through 3. An empty input queue generates no request.

## Phase 5: Integrate the Complete Switch

File: `rtl/packet_switch.v`

The top-level RTL instantiates:

- Four input packet queues
- Four destination decoders
- Four fair output selectors

Requests are transposed so every output selector sees requests from all four inputs. A granted packet is presented using ready/valid flow control and leaves its input queue only after the output accepts it.

## Phase 6: Check RTL Elaboration

Icarus Verilog 12.0 was installed as a free RTL tool. All four Verilog modules successfully passed Verilog-2005 parsing and top-level elaboration. This confirms structural consistency but does not replace functional simulation.

## Phase 7: Define Verification Interfaces and Parameters

Files:

- `verification/interfaces/packet_switch_interface.sv`
- `verification/uvm/parameters_pkg.sv`

The complete-switch interface groups all ready/valid channels and defines separate driver, monitor, and DUT views. Clocking blocks establish when verification components drive and sample signals.

A parameter package shares packet width, port count, FIFO depth, and destination width across the UVM environment.

## Phase 8: Build the UVM Data Path

Files:

- `verification/uvm/transaction.sv`
- `verification/uvm/sequencer.sv`
- `verification/uvm/driver.sv`
- `verification/uvm/monitor.sv`
- `verification/uvm/agent.sv`

The transaction stores randomized stimulus and observed DUT signals. The sequencer sends transactions to the driver, which applies them through the interface. The monitor samples every cycle and publishes snapshots. The agent constructs and connects these components.

## Phase 9: Add the Reference-Model Scoreboard

File: `verification/uvm/scoreboard.sv`

The scoreboard models four expected input queues and one round-robin priority per output. It records accepted input packets, predicts each output winner, checks output validity and packet data, removes accepted packets, and advances modeled priority.

The model checks routing, ordering, data integrity, handshake behavior, and round-robin decisions independently from the RTL implementation.

## Phase 10: Add Functional Coverage

File: `verification/uvm/coverage.sv`

The coverage subscriber currently measures:

- Every input-to-destination route
- Input handshake and backpressure states per port
- Output handshake and backpressure states per port
- Simultaneous accepted input and output counts
- Reset asserted and deasserted states
- Entering and leaving reset

The monitor publishes the same observations to both the scoreboard and coverage component.

## Phase 11: Build Tests and Simulation Structure

Files:

- `verification/uvm/environment.sv`
- `verification/uvm/sequence.sv`
- `verification/uvm/contention_sequence.sv`
- `verification/uvm/test.sv`
- `verification/uvm/contention_test.sv`
- `verification/uvm/verification_pkg.sv`
- `verification/top.sv`
- `verification/files.f`

The base sequence resets the switch, generates randomized traffic, and drains queued packets. The contention sequence repeatedly sends all four inputs to Output 0 using unique packet tags. Separate UVM tests start each sequence.

The simulation top generates the clock, connects the interface and DUT, provides virtual interfaces through the UVM configuration database, and starts the selected test. The file list records compilation dependencies.

## Current Limitations

- The UVM source has not yet been compiled with Questa.
- Questa run and regression scripts are not yet implemented.
- Coverage for explicit arbitration-winner history can be expanded.
- Additional directed tests are needed for FIFO saturation, prolonged output stalls, independent parallel routes, and reset during traffic.
- Coverage goals and regression pass criteria still need to be documented.

## Next Phases

1. Allow command-line UVM test selection.
2. Add FIFO-full and backpressure-focused sequences.
3. Add parallel-routing and reset-during-traffic tests.
4. Add arbitration fairness coverage and end-of-test checks.
5. Compile with Questa and correct any simulator-specific issues.
6. Add Windows-friendly run and regression commands.
7. Record coverage results and representative waveforms.
