# Development Phases

**Last updated: August 15, 2026**

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

## Phase 12: Add Focused Directed Tests

Files:

- `verification/uvm/fifo_full_sequence.sv`
- `verification/uvm/fifo_full_test.sv`
- `verification/uvm/parallel_routing_sequence.sv`
- `verification/uvm/parallel_routing_test.sv`
- `verification/uvm/reset_during_traffic_sequence.sv`
- `verification/uvm/reset_during_traffic_test.sv`

Three focused tests were added for important switch behaviors. The FIFO-full test blocks one output and fills all input queues to exercise backpressure. The parallel-routing test sends four simultaneous packets to four different outputs. The reset-during-traffic test buffers packets, resets the switch, and then sends new traffic to check clean recovery.

The simulation top now calls `run_test()` without hardcoding a class, allowing each test to be selected with the UVM command-line test-name option.

## Phase 13: Compile and Run with Questa

Questa-Altera FPGA Starter Edition compiled the complete RTL and UVM environment with zero errors and zero warnings. Initial compilation exposed reserved-keyword variable names and a UVM subscriber method-signature mismatch; both were corrected without changing test intent.

The first base-test run exposed a scoreboard modeling defect. The model removed accepted packets while it was still checking other outputs in the same cycle, allowing a newly exposed packet to appear too early in the prediction. Output checking was changed to use one pre-clock state for all four outputs, followed by a separate state-update pass.

After the correction, all five tests completed with zero UVM errors and zero UVM fatals:

- Base pseudo-random traffic
- Repeated output contention
- FIFO saturation and backpressure
- Four-way parallel routing
- Reset during buffered traffic

The Starter license does not include the `svverification` feature needed for constrained randomization and covergroup execution. Procedural `$urandom` stimulus is used locally, and simulations run with `-nocvg`. The functional coverage model remains implemented for future execution with a suitable advanced-verification license.

Two representative waveforms provide visual evidence alongside the zero-error UVM reports and automated scoreboard checks:

- `waves/contention_waveform.png` records sustained contention for Output 0 across the full 515 ns test.
- `waves/fifo_full_backpressure_waveform.png` shows queue saturation, input backpressure, and recovery as stored packets drain.

## Current Limitations

- Questa run and regression scripts are not yet implemented.
- Functional coverage has not been executed because the Starter license lacks the required advanced-verification feature.
- Coverage for explicit arbitration-winner history can be expanded.
- Additional directed testing is needed for prolonged output stalls.
- Coverage goals and regression pass criteria still need to be documented.

## Next Phases

The long-term goal is an FPGA-ready packet-switch subsystem with a software-visible control path. The existing switch remains the datapath. New work will be added around it in small stages.

### Stage 1: Stronger Verification

1. Add SystemVerilog assertions for FIFO limits, one-hot grants, correct routing, stable stalled outputs, and clean reset behavior.
2. Add arbitration fairness and end-of-test checks.
3. Add a prolonged-output-stall test.
4. Write a verification matrix that links requirements to tests, assertions, coverage, and results.
5. Run functional coverage when a suitable simulator license is available and record any remaining coverage gaps.

### Stage 2: Repeatable Automation

1. Add a Python regression command that can choose tests, seeds, iteration counts, verbosity, and waveform output.
2. Save failing seeds and produce a short pass/fail summary.
3. Add hardware-focused CI for lint, RTL simulation, formal checks, and synthesis with free tools where possible.

### Stage 3: Software-Visible Control

1. Add a simple AXI4-Lite or APB register interface.
2. Add registers for port enable controls, packet counters, stall counters, FIFO occupancy, error status, and counter reset.
3. Add a UVM register model and bus agent to verify reset values, read/write rules, reserved bits, counters, and control effects.
4. Write a small C/C++ driver that configures ports, reads status, and clears counters.

### Stage 4: Formal, Synthesis, and Performance

1. Formally check the FIFO and round-robin selector first because they are small and have clear rules.
2. Make packet width and FIFO depth easy to configure, then test several configurations.
3. Run synthesis and report logic use, registers, memory, timing, and maximum clock speed.
4. Measure throughput, latency, fairness, and behavior under contention and backpressure.
5. Use an FPGA board for a final hardware demonstration if one is available.

These stages describe planned work. The current implementation ends at Phase 13 above.
