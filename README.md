# Backend Setup Guide

## Prerequisites

Before setting up the backend, ensure you have the following installed:

- **Python 3.10.0** (Required)
- **pip** (Python package manager)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/happyy07/payment-backend-management.git
   cd backend
   ```

2. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Backend Server

Start the FastAPI server with Uvicorn:

```sh
python -m uvicorn app.main:app --reload
```

### Default Server Address

- The backend will run on **http://127.0.0.1:8000** by default.

### API Documentation

Once the server is running, you can access API documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
