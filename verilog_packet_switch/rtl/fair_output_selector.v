module fair_output_selector (
    input        clk,               // Clock controlling priority updates
    input        reset,             // Returns priority to its starting position
    input  [3:0] request,           // One request bit for each of the four input ports
    input        transfer_accepted, // High when the granted packet actually moves
    output reg [3:0] grant          // One-hot selection of the winning input
);

    // -------------------------------------------------------------------------
    // Round-robin priority state
    // -------------------------------------------------------------------------
    reg [1:0] priority_start; // Input number checked first during arbitration


    // -------------------------------------------------------------------------
    // Combinational grant selection
    // -------------------------------------------------------------------------
    always @(*) begin
        grant = 4'b0000;

        case (priority_start)
            2'd0: begin
                if      (request[0]) grant = 4'b0001;
                else if (request[1]) grant = 4'b0010;
                else if (request[2]) grant = 4'b0100;
                else if (request[3]) grant = 4'b1000;
            end

            2'd1: begin
                if      (request[1]) grant = 4'b0010;
                else if (request[2]) grant = 4'b0100;
                else if (request[3]) grant = 4'b1000;
                else if (request[0]) grant = 4'b0001;
            end

            2'd2: begin
                if      (request[2]) grant = 4'b0100;
                else if (request[3]) grant = 4'b1000;
                else if (request[0]) grant = 4'b0001;
                else if (request[1]) grant = 4'b0010;
            end

            2'd3: begin
                if      (request[3]) grant = 4'b1000;
                else if (request[0]) grant = 4'b0001;
                else if (request[1]) grant = 4'b0010;
                else if (request[2]) grant = 4'b0100;
            end
        endcase
    end


    // -------------------------------------------------------------------------
    // Clocked priority update and reset logic
    // -------------------------------------------------------------------------
    always @(posedge clk) begin
        if (reset) begin
            priority_start <= 2'd0;
        end else if (transfer_accepted) begin
            case (grant)
                4'b0001: priority_start <= 2'd1;
                4'b0010: priority_start <= 2'd2;
                4'b0100: priority_start <= 2'd3;
                4'b1000: priority_start <= 2'd0;
                default: priority_start <= priority_start;
            endcase
        end
    end

endmodule
