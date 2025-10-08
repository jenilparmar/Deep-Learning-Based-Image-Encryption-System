import numpy as np

class DifferentialNeuralNetwork:
    """
    Implements the Differential Neural Network from Algorithm 5 to generate
    blurring codes for image encryption.
    """
    def __init__(self, key, chaotic_weights, num_neurons=16, num_hidden_layers=3):
        """
        Initializes the neural network based on the secret key and chaotic weights.
        This corresponds to lines 1-3 of Algorithm 5.
        
        Args:
            key (str): The encryption secret key.
            chaotic_weights (list or np.array): A flat list of pre-generated chaotic numbers.
            num_neurons (int): The number of neurons in each layer.
            num_hidden_layers (int): The number of hidden layers.
        """
        self.num_neurons = num_neurons
        self.num_layers = num_hidden_layers + 2 # (input + hidden + output)

        # --- Step 1: Initialize weights ---
        self.weights = []
        weights_per_layer = self.num_neurons * self.num_neurons
        start_index = 0
        # There are (num_layers - 1) connections between layers
        for _ in range(self.num_layers - 1):
            end_index = start_index + weights_per_layer
            layer_w = np.array(chaotic_weights[start_index:end_index]).reshape(self.num_neurons, self.num_neurons)
            self.weights.append(layer_w)
            start_index = end_index

        # --- Step 2: Initialize input layer from key ---
        # Pad or truncate key to match the number of neurons
        key_bytes = [ord(c) for c in key.ljust(self.num_neurons, '\0')]
        self.input_layer_state = np.array(key_bytes, dtype=np.uint8)

        # --- Step 3: Initialize bias vector ---
        self.bias_vector = np.zeros(self.num_neurons, dtype=np.uint8)

    def generate_codes_and_update(self, image_block):
        """
        Performs one full cycle: generates blurring codes for a block and updates the network's state.
        This corresponds to lines 5-15 of Algorithm 5.
        This version iteratively runs the network until enough codes are generated
        to match the length of the image_block.
        
        Args:
            image_block (np.array): A single row/block from the V matrix.
            
        Returns:
            np.array: The generated blurring codes for the block.
        """
        
        block_len = len(image_block)
        all_codes = []
        
        # Line 4 & 16: Repeat until desired blurring code length is reached
        while len(all_codes) < block_len:
            # --- Lines 5-13: Feedforward Pass ---
            current_layer_values = self.input_layer_state.astype(np.float64)
            first_hidden_layer_output = None

            for i, layer_weights in enumerate(self.weights):
                # Calculate weighted sum
                z = np.dot(current_layer_values, layer_weights)

                # Line 8: Add bias vector ONLY for the first hidden layer
                if i == 0:
                    z += self.bias_vector
                    first_hidden_layer_output = z
                
                current_layer_values = z

            # The final output of the network becomes the next batch of blurring codes
            current_codes = (current_layer_values.astype(np.uint64) % 256).astype(np.uint8)
            all_codes.extend(current_codes)

            # --- Line 14: Update the bias vector using a corresponding part of the image block ---
            # Determine which part of the image_block corresponds to the codes just generated
            start_idx = len(all_codes) - self.num_neurons
            end_idx = start_idx + self.num_neurons
            block_segment = image_block[start_idx:end_idx]
            
            # The segment might be shorter than num_neurons if block_len isn't a multiple.
            # Pad the segment to match the bias_vector length for the XOR operation.
            if len(block_segment) < self.num_neurons:
                 padding = np.zeros(self.num_neurons - len(block_segment), dtype=np.uint8)
                 block_segment = np.concatenate((block_segment, padding))

            diff = block_segment.astype(np.int16) - current_codes.astype(np.int16)
            self.bias_vector = np.bitwise_xor(block_segment, diff.astype(np.uint8))
            
            # --- Line 15: Send output of first hidden layer as input feedback ---
            self.input_layer_state = (first_hidden_layer_output.astype(np.uint64) % 256).astype(np.uint8)
        
        # Trim the generated codes to match the exact block length
        return np.array(all_codes[:block_len], dtype=np.uint8)

# --- Example of how to use this class in your main script ---
if __name__ == '__main__':
    # --- 1. Define your inputs (replace with your actual data) ---
    secret_key = "JenilIsVeryHandSomeGuy"
    
    # Use a realistic image width (e.g., 256) which is different from num_neurons (16)
    # This will correctly test the new iterative code generation.
    image_width = 256
    image_height = 256
    V_matrix = np.random.randint(0, 256, size=(image_height, image_width), dtype=np.uint8)
    
    # Generate placeholder chaotic weights
    num_neurons = 16
    num_layers = 5 # 1 input + 3 hidden + 1 output
    total_weights_needed = (num_layers - 1) * (num_neurons * num_neurons)
    chaotic_weights = np.random.rand(total_weights_needed) * 255


    # --- 2. Initialize the network (one time) ---
    dnn = DifferentialNeuralNetwork(secret_key, chaotic_weights, num_neurons=num_neurons)
    

    # --- 3. Process each row of V to get the final encrypted matrix C ---
    encrypted_rows = []
    print(f"Processing {image_height} rows of V to generate final encrypted image C...")
    
    # This loop will now work correctly for any image width
    for v_row in V_matrix:
        # Generate blurring codes for the current row (length will match v_row)
        codes = dnn.generate_codes_and_update(v_row)
        
        # XOR the row with the codes to get the encrypted row
        encrypted_row = np.bitwise_xor(v_row, codes)
        encrypted_rows.append(encrypted_row)

    # Combine all encrypted rows into the final matrix
    C_matrix = np.array(encrypted_rows, dtype=np.uint8)

    print("\n--- Final Encrypted Matrix C ---")
    print(C_matrix)
    print(f"\nShape of C: {C_matrix.shape}")
    print("Encryption process complete! 🎉")

