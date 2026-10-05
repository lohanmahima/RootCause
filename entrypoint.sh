#!/bin/bash

# Start Ollama in the background
echo "Starting Ollama server..."
ollama serve &

# Wait for Ollama to be ready
sleep 5

# Pull the model (this will take a few minutes on first boot)
echo "Pulling gemma3:4b..."
ollama pull gemma3:4b

# Run Streamlit on the port Hugging Face Spaces expects
echo "Starting Streamlit..."
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
