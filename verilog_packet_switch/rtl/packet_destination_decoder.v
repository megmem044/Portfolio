module packet_destination_decoder #(
    parameter PACKET_WIDTH = 16 // Total number of bits in one packet
) (
    input      [PACKET_WIDTH-1:0] front_packet,  // Oldest packet in an input queue
    input                         queue_empty,   // High when the input queue has no packet
    output reg [3:0]              output_request // One-hot request for one of four outputs
);

    // -------------------------------------------------------------------------
    // Destination extraction
    // -------------------------------------------------------------------------
    wire [1:0] destination; // Output number stored in the packet's upper two bits

    assign destination = front_packet[PACKET_WIDTH-1:PACKET_WIDTH-2];


    // -------------------------------------------------------------------------
    // One-hot output request decoding
    // -------------------------------------------------------------------------
    always @(*) begin
        output_request = 4'b0000;

        if (!queue_empty) begin
            case (destination)
                2'b00: output_request = 4'b0001;
                2'b01: output_request = 4'b0010;
                2'b10: output_request = 4'b0100;
                2'b11: output_request = 4'b1000;
            endcase
        end
    end

endmodule
