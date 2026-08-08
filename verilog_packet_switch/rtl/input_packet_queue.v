module input_packet_queue #(
    parameter PACKET_WIDTH = 16, // Number of bits in one packet
    parameter FIFO_DEPTH   = 4   // Maximum number of packets the FIFO can hold
) (
    input                         clk,             // Clock that controls all FIFO operations
    input                         reset,           // Clears the FIFO on the next rising clock edge

    // Packet coming INTO the FIFO
    input                         push_packet,     // Requests that a packet be added to the FIFO
    input      [PACKET_WIDTH-1:0] incoming_packet, // Packet to store when a push is accepted

    // Packet leaving the FIFO
    input                         pop_packet,      // Requests removal of the oldest packet
    output     [PACKET_WIDTH-1:0] front_packet,    // Oldest packet currently stored in the FIFO

    // FIFO status
    output                        fifo_full,       // High when no more packets can be stored
    output                        fifo_empty       // High when no packets are stored
);

    // -------------------------------------------------------------------------
    // Calculate how many bits are needed for pointers/counters
    // -------------------------------------------------------------------------
    function integer bits_needed;
        input integer value;     // Number of different values that must be represented
        integer remaining;       // Temporary value shifted while counting required bits
        begin
            bits_needed = 0;
            remaining = value - 1;

            while (remaining > 0) begin
                bits_needed = bits_needed + 1;
                remaining = remaining >> 1;
            end
        end
    endfunction


    localparam INDEX_WIDTH = bits_needed(FIFO_DEPTH);     // Bits needed to select a storage slot
    localparam COUNT_WIDTH = bits_needed(FIFO_DEPTH + 1); // Bits needed to count from 0 to FIFO_DEPTH


    // -------------------------------------------------------------------------
    // FIFO storage
    // -------------------------------------------------------------------------

    // Actual packet storage
    reg [PACKET_WIDTH-1:0] fifo_storage [0:FIFO_DEPTH-1]; // Memory containing the queued packets

    // Points to the packet that should leave next
    reg [INDEX_WIDTH-1:0] front_index; // Storage slot containing the oldest packet

    // Points to where the next incoming packet should be stored
    reg [INDEX_WIDTH-1:0] next_free_index; // Storage slot used by the next accepted push

    // Number of packets currently inside the FIFO
    reg [COUNT_WIDTH-1:0] packets_stored; // Current number of packets inside the FIFO


    // -------------------------------------------------------------------------
    // FIFO status
    // -------------------------------------------------------------------------

    assign fifo_empty = (packets_stored == 0);
    assign fifo_full  = (packets_stored == FIFO_DEPTH);


    // A write actually happens only if:
    // someone wants to push AND there is space
    wire push_happens = push_packet && !fifo_full; // High when a requested push is accepted

    // A read actually happens only if:
    // someone wants to pop AND there is a packet available
    wire pop_happens = pop_packet && !fifo_empty; // High when a requested pop is accepted


    // -------------------------------------------------------------------------
    // Make the oldest packet visible to the router
    // -------------------------------------------------------------------------

    assign front_packet = fifo_storage[front_index];


    // -------------------------------------------------------------------------
    // FIFO operation
    // -------------------------------------------------------------------------

    always @(posedge clk) begin

        // Reset FIFO to empty
        if (reset) begin
            front_index     <= 0;
            next_free_index <= 0;
            packets_stored  <= 0;
        end

        else begin

            // -------------------------------------------------------------
            // Add a new packet
            // -------------------------------------------------------------
            if (push_happens) begin

                fifo_storage[next_free_index] <= incoming_packet;

                // Move to next storage location
                if (next_free_index == FIFO_DEPTH - 1)
                    next_free_index <= 0;
                else
                    next_free_index <= next_free_index + 1'b1;
            end


            // -------------------------------------------------------------
            // Remove the packet at the front
            // -------------------------------------------------------------
            if (pop_happens) begin

                // Move front to the next packet
                if (front_index == FIFO_DEPTH - 1)
                    front_index <= 0;
                else
                    front_index <= front_index + 1'b1;
            end


            // -------------------------------------------------------------
            // Update number of packets stored
            // -------------------------------------------------------------
            case ({push_happens, pop_happens})

                // Packet entered, nothing left
                2'b10:
                    packets_stored <= packets_stored + 1'b1;

                // Packet left, nothing entered
                2'b01:
                    packets_stored <= packets_stored - 1'b1;

                // Either:
                // - nothing happened
                // - one entered AND one left
                2'b00,
                2'b11:
                    packets_stored <= packets_stored;

            endcase
        end
    end

endmodule
