Medical Image Encryption using Fresnel Zone Formula and Neural Networks
This repository contains a Python implementation of the advanced medical image encryption algorithm proposed in the paper: "Medical image encryption algorithm based on Fresnel zone formula, differential neural networks, and pixel-guided perturbation techniques" by Muhammed Jassem Al-Muhammed.

The algorithm provides robust, multi-layered security for digital images, making it particularly suitable for sensitive data like medical scans.

📜 Overview
The core of this project is a novel encryption technique that combines three powerful, independent security layers to protect image data from various cryptanalytic attacks. Unlike traditional methods, this algorithm ensures that even a single-bit change in the input image or the secret key results in a completely different encrypted output, a property known as high diffusion and confusion.

Key Features
🛡️ Deep Pixel Substitution: Utilizes a non-linear Fresnel Zone formula to perform a dynamic, dual-pass substitution on pixel values, effectively eliminating any correlation with the plain image.

🔀 Pixel-Guided Perturbation: A chaotic scrambling mechanism that shuffles pixel positions. The scrambling pattern is dependent on the image's own pixel values, making it highly sensitive and unpredictable.

🧠 Differential Neural Network: A specialized neural network generates complex "blurring codes" based on the secret key and the image data. This adds a final, robust layer of confusion, making the cipher resilient to differential attacks.

🔑 Key-Driven Initialization: The entire process is seeded from a secret key using the SHA-512 hash function and a logistic map for chaotic number generation.

⚙️ How It Works: The Encryption Flow
The encryption process is a sequential application of the core security layers. Decryption is the exact reverse of this flow, applying the inverse of each operation.

1. Initialization
A secret key is hashed using SHA-512.

The hash is used to initialize the parameters of a chaotic logistic map.

The logistic map generates weights for the Differential Neural Network.

2. Encryption Stages
First Block Substitution: The image rows undergo a deep, two-pass substitution using the Fresnel Zone formula.

Pixel Perturbation: The positions of all pixels in the intermediate image are chaotically scrambled.

Second Block Substitution: The scrambled image undergoes another round of Fresnel Zone substitution.

Blurring Code Generation: The Differential Neural Network produces blurring codes, which are XORed with the image blocks to create the final ciphered image.

📂 Project Structure
medical-image-encryption/
│
├── src/
│   ├── __init__.py
│   ├── substitution.py      # Implements Fresnel Zone substitution
│   ├── perturbation.py      # Implements pixel scrambling
│   ├── neural_network.py    # Implements the Differential Neural Network
│   └── crypto_utils.py      # Key hashing and chaotic map setup
│
├── images/
│   ├── input/               # Directory for plain images
│   ├── output/              # Directory for encrypted/decrypted images
│
├── main.py                  # Main script to run encryption/decryption
├── requirements.txt         # Project dependencies
└── README.md                # You are here!

🚀 Getting Started
Prerequisites
Python 3.8+

NumPy

Pillow (PIL Fork)

OpenCV-Python

Installation
Clone the repository:

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

Install the required packages:

pip install -r requirements.txt

Usage
The main.py script is the entry point for performing encryption and decryption.

To Encrypt an Image
Place your input image in the images/input/ directory.

python main.py encrypt --input images/input/brain_mri.png --output images/output/brain_mri_encrypted.png --key "a-very-secret-key-123!"

To Decrypt an Image
python main.py decrypt --input images/output/brain_mri_encrypted.png --output images/output/brain_mri_decrypted.png --key "a-very-secret-key-123!"

📄 Citation
This implementation is based on the following research paper. If you use this code in your work, please consider citing the original author.

Al-Muhammed, M. J. (2024). Medical image encryption algorithm based on Fresnel zone formula, differential neural networks, and pixel-guided perturbation techniques. Computers and Electrical Engineering, 120, 109722. https://doi.org/10.1016/j.compeleceng.2024.109722

📜 License
This project is licensed under the MIT License. See the LICENSE file for more details.
