# Railway Build Configuration
# This file tells Railway how to build your Python application

# Install Python dependencies
pip install -r backend/requirements.txt

# Set Python path
export PYTHONPATH=backend

# Start the application
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
