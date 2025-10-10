import React, { useState, useRef } from 'react';
import { Lock, Upload, Download, Key, RefreshCw } from 'lucide-react';

export default function EncryptionUIDesign() {
  const [encryptionKey, setEncryptionKey] = useState('');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        alert('Please upload a valid image file (PNG, JPEG)');
        return;
      }

      setUploadedImage(file);

       // Create preview and base64
       const reader = new FileReader();
       reader.onloadend = () => {
         setImagePreview(reader.result);
         const base64 = reader.result.split(',')[1];
         setImageBase64(base64);
         console.log('Image base64 set:', base64 ? 'yes' : 'no');
       };
       reader.readAsDataURL(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      // Simulate file input change
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInputRef.current.files = dataTransfer.files;
      handleImageUpload({ target: { files: [file] } });
    }
  };

  const generateKey = () => {
    // Generate a random 224-bit key (56 hex characters)
    const characters = '0123456789abcdef';
    let key = '';
    for (let i = 0; i < 56; i++) {
      key += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    setEncryptionKey(key);
  };

  const processImage = async () => {
    console.log('processImage called');
    if (!uploadedImage) {
      alert('Please upload an image first');
      return;
    }
    if (!encryptionKey) {
      alert('Please enter or generate an encryption key');
      return;
    }
    if (!imageBase64) {
      alert('Image base64 not available. Please re-upload the image.');
      return;
    }

    try {
      console.log('Sending request to backend');
      const response = await fetch('http://127.0.0.1:5000/api/process_base64', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: imageBase64,
          key: encryptionKey,
          operation: 'encrypt'
        }),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (data.success) {
        setProcessedImage(data.image);
        alert(data.message);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error processing image:', error);
      alert('Failed to process image. Make sure the backend server is running on http://127.0.0.1:5000');
    }
  };

  const downloadResult = () => {
    if (!processedImage) {
      alert('No processed image to download');
      return;
    }

    // Create download link
    const link = document.createElement('a');
    link.href = processedImage;
    link.download = `encrypted_image.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Lock className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-800">Medical Image Encryption</h1>
          </div>
          <p className="text-center text-gray-600">Secure encryption using Fresnel Zone & Neural Networks</p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">

          {/* Key Input */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <Key className="w-5 h-5" />
              Encryption Key
            </h2>
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="Enter your encryption key..."
                value={encryptionKey}
                onChange={(e) => setEncryptionKey(e.target.value)}
                className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none text-gray-700 font-mono"
              />
              <button
                onClick={generateKey}
                className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors flex items-center gap-2 font-medium"
              >
                <RefreshCw className="w-4 h-4" />
                Generate
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-2">224-bit encryption key required</p>
          </div>

          {/* Image Upload */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Upload Image
            </h2>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png, image/jpeg, image/jpg"
              onChange={handleImageUpload}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="border-3 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-indigo-400 transition-all cursor-pointer bg-gray-50 block"
            >
              {imagePreview ? (
                <div className="space-y-4">
                  <img
                    src={imagePreview}
                    alt="Uploaded preview"
                    className="max-h-64 mx-auto rounded-lg shadow-md"
                  />
                  <p className="text-green-600 font-medium">✓ {uploadedImage?.name}</p>
                  <p className="text-sm text-gray-500">Click to change image</p>
                </div>
              ) : (
                <>
                  <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 text-lg mb-2">Drop image here or click to browse</p>
                  <p className="text-sm text-gray-500">Supports: PNG, JPEG, DICOM</p>
                </>
              )}
            </label>
          </div>

          {/* Process Button */}
          <div className="mb-8 text-center">
            <button
              onClick={async () => {
                await processImage()
              }}
              className="px-12 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Encrypt Image
            </button>
          </div>

          {/* Result Section */}
          <div className="border-2 border-gray-200 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Result</h2>
            <div className="bg-gray-100 rounded-xl p-12 mb-4 min-h-[300px] flex items-center justify-center">
              {processedImage ? (
                <img
                  src={processedImage}
                  alt="Processed result"
                  className="max-h-96 rounded-lg shadow-md"
                />
              ) : (
                <div className="text-center text-gray-400">
                  <div className="w-24 h-24 border-4 border-gray-300 rounded-lg mx-auto mb-4 flex items-center justify-center">
                    <span className="text-4xl">🖼️</span>
                  </div>
                  <p className="text-lg">Encrypted image will appear here</p>
                </div>
              )}
            </div>
            <div className="text-center">
              <button
                onClick={downloadResult}
                disabled={!processedImage}
                className={`px-8 py-3 rounded-xl transition-colors inline-flex items-center gap-2 font-medium ${processedImage
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
              >
                <Download className="w-5 h-5" />
                Download Result
              </button>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-gray-600">
          <p className="text-sm">Based on Fresnel Zone Formula & Differential Neural Networks</p>
        </div>
      </div>
    </div>
  );
}
