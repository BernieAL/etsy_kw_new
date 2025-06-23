#!/bin/bash

echo "🚀 Starting Etsy Monitor Frontend..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🌐 Starting development server..."
echo "📱 Frontend will be available at: http://localhost:5173"
echo "🔗 API should be running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev 