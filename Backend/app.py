from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import base64
import sys
import os

# Add the encryption folder to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'encryption'))

from SHA_function import create_sha_key
from logistic_map import calculate_r_and_x
from generate_weights import create_weights
from forward_pass import Substitute, Perturbation, Substitute_Inv, Perturbation_Inv
from Deferentail_Neural_network import DifferentialNeuralNetwork

app = Flask(__name__)
CORS(app=app)  # Enable CORS for frontend communication

def encrypt_image(image_array, password):
    """
    Encrypts the image using the complete encryption pipeline.
    
    Args:
        image_array: numpy array of the image
        password: encryption key/password
        
    Returns:
        encrypted_image: numpy array of encrypted image
    """
    # Step 1: Generate keys and parameters
    key = create_sha_key(password)
    [x, r] = calculate_r_and_x(password)
    
    # Step 2: First Substitution
    T = []
    for b in image_array:
        substitute_block = Substitute(b)
        T.append(substitute_block)
    T = np.array(T)
    
    # Step 3: Perturbation
    [c_perturbation, r_perturbation] = calculate_r_and_x(password)
    perturbed_image = Perturbation(T, r_perturbation, c_perturbation)
    
    # Step 4: Second Substitution
    V = []
    for p in perturbed_image:
        sec_sub = Substitute(p)
        V.append(sec_sub)
    V = np.array(V)
    
    # Step 5: Differential Neural Network Encryption
    num_neurons = len(password)
    num_layers = 5  # 1 input + 3 hidden + 1 output
    total_weights_needed = (num_layers - 1) * (num_neurons * num_neurons)
    W_i = create_weights(x, total_weights_needed)
    dnn = DifferentialNeuralNetwork(password, W_i, num_neurons=num_neurons)
    
    encrypted_rows = []
    for v_i in V:
        # Generate blurring codes for the current row
        codes = dnn.generate_codes_and_update(v_i)
        
        # XOR the row with the codes to get the encrypted row
        encrypted_row = np.bitwise_xor(v_i, codes)
        encrypted_rows.append(encrypted_row)
    
    # Combine all encrypted rows into the final matrix
    C_matrix = np.array(encrypted_rows, dtype=np.uint8)
    
    return C_matrix


def decrypt_image(encrypted_array, password):
    """
    Decrypts the image using the reverse encryption pipeline.
    
    Args:
        encrypted_array: numpy array of the encrypted image
        password: decryption key/password
        
    Returns:
        decrypted_image: numpy array of decrypted image
    """
    # Step 1: Generate keys and parameters
    key = create_sha_key(password)
    [x, r] = calculate_r_and_x(password)
    
    # Step 2: Differential Neural Network Decryption
    num_neurons = len(password)
    num_layers = 5
    total_weights_needed = (num_layers - 1) * (num_neurons * num_neurons)
    W_i = create_weights(x, total_weights_needed)
    dnn = DifferentialNeuralNetwork(password, W_i, num_neurons=num_neurons)
    
    decrypted_rows = []
    for c_i in encrypted_array:
        # Generate blurring codes for the current row
        codes = dnn.generate_codes_and_update(c_i)
        
        # XOR to recover V
        v_row = np.bitwise_xor(c_i, codes)
        decrypted_rows.append(v_row)
    
    V = np.array(decrypted_rows, dtype=np.uint8)
    
    # Step 3: Inverse Second Substitution
    perturbed_image = []
    for v in V:
        inv_sub = Substitute_Inv(v)
        perturbed_image.append(inv_sub)
    perturbed_image = np.array(perturbed_image)
    
    # Step 4: Inverse Perturbation
    [c_perturbation, r_perturbation] = calculate_r_and_x(password)
    T = Perturbation_Inv(perturbed_image, r_perturbation, c_perturbation)
    
    # Step 5: Inverse First Substitution
    original_image = []
    for t in T:
        inv_sub = Substitute_Inv(t)
        original_image.append(inv_sub)
    original_image = np.array(original_image, dtype=np.uint8)
    
    return original_image


@app.route('/api/process', methods=['POST'])
def process_image():
    """
    POST endpoint to encrypt or decrypt an image.
    
    Expected form data:
        - image: image file
        - key: encryption/decryption key (string)
        - operation: 'encrypt' or 'decrypt'
    
    Returns:
        JSON response with base64 encoded processed image
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        if 'key' not in request.form:
            return jsonify({'error': 'No encryption key provided'}), 400
        
        if 'operation' not in request.form:
            return jsonify({'error': 'No operation specified'}), 400
        
        # Get form data
        image_file = request.files['image']
        encryption_key = request.form['key']
        operation = request.form['operation']
        
        # Validate operation
        if operation not in ['encrypt', 'decrypt']:
            return jsonify({'error': 'Invalid operation. Must be "encrypt" or "decrypt"'}), 400
        
        # Validate key length
        if len(encryption_key) < 8:
            return jsonify({'error': 'Encryption key must be at least 8 characters long'}), 400
        
        # Read and process image
        image = Image.open(image_file.stream).convert('L')  # Convert to grayscale
        image_array = np.array(image)
        
        # Process image based on operation
        if operation == 'encrypt':
            processed_array = encrypt_image(image_array, encryption_key)
            message = 'Image encrypted successfully'
        else:  # decrypt
            processed_array = decrypt_image(image_array, encryption_key)
            message = 'Image decrypted successfully'
        
        # Convert processed array back to image
        processed_image = Image.fromarray(processed_array.astype(np.uint8))
        
        # Convert to base64 for JSON response
        buffered = io.BytesIO()
        processed_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': message,
            'image': f'data:image/png;base64,{img_base64}',
            'operation': operation
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/process_base64', methods=['POST'])
def process_image_base64():
    """
    POST endpoint to encrypt or decrypt an image from base64.

    Expected JSON data:
        - image: base64 encoded image string
        - key: encryption/decryption key (string)
        - operation: 'encrypt' or 'decrypt'

    Returns:
        JSON response with base64 encoded processed image
    """
    print("Received POST to /api/process_base64")
    try:
        # Get JSON data
        data = request.get_json()
        print("Data received:", data)
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        if 'image' not in data:
            return jsonify({'error': 'No image base64 provided'}), 400

        if 'key' not in data:
            return jsonify({'error': 'No encryption key provided'}), 400

        if 'operation' not in data:
            return jsonify({'error': 'No operation specified'}), 400

        # Get data
        image_base64 = data['image']
        encryption_key = data['key']
        operation = data['operation']

        # Validate operation
        if operation not in ['encrypt', 'decrypt']:
            return jsonify({'error': 'Invalid operation. Must be "encrypt" or "decrypt"'}), 400

        # Validate key length
        if len(encryption_key) < 8:
            return jsonify({'error': 'Encryption key must be at least 8 characters long'}), 400

        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes)).convert('L')  # Convert to grayscale
            image_array = np.array(image)
        except Exception as e:
            return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400

        # Process image based on operation
        if operation == 'encrypt':
            processed_array = encrypt_image(image_array, encryption_key)
            message = 'Image encrypted successfully'
        else:  # decrypt
            processed_array = decrypt_image(image_array, encryption_key)
            message = 'Image decrypted successfully'

        # Convert processed array back to image
        processed_image = Image.fromarray(processed_array.astype(np.uint8))

        # Convert to base64 for JSON response
        buffered = io.BytesIO()
        processed_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print(image_base64)
        return jsonify({
            'success': True,
            'message': message,
            'image': f'data:image/png;base64,{img_base64}',
            'operation': operation
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Image Encryption API is running'
    })


if __name__ == '__main__':
    print("🚀 Starting Flask Image Encryption API...")
    print("📡 Server running on http://localhost:5000")
    print("🔐 Endpoints:")
    print("   POST /api/process - Encrypt/Decrypt images")
    print("   GET  /api/health  - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)
