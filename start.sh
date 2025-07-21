#!/bin/bash

# Railway startup script for Room Allocation System

# Create data directory if it doesn't exist
mkdir -p data

# Set default port if not provided
export PORT=${PORT:-8501}

# Run the Streamlit application
streamlit run app.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --browser.gatherUsageStats false
