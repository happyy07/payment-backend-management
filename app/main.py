from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
from bson import ObjectId
from gridfs import GridFS
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import json
import math

from .database import db
from .models import Payment, PaymentUpdate
from .utils import normalize_csv_data, calculate_total_due

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and math.isnan(obj):
            return float('-1')  # This will serialize as NaN in JSON
        return super().default(obj)

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=True,
            cls=CustomJSONEncoder
        ).encode("utf-8")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect_db()
    yield
    # Shutdown
    await db.close_db()

app = FastAPI(lifespan=lifespan, default_response_class=CustomJSONResponse)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/payments/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    df = pd.read_csv(file.file)
    normalized_data = normalize_csv_data(df)
    
    # Convert date objects to ISO format strings
    for record in normalized_data:
        if isinstance(record.get('payee_due_date'), date):
            record['payee_due_date'] = record['payee_due_date'].isoformat()
    
    result = await db.db.payments.insert_many(normalized_data)
    return {"message": f"Inserted {len(result.inserted_ids)} records"}

@app.get("/payments")
async def get_payments(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    status: Optional[str] = None,
    search: Optional[str] = None
):
    skip = (page - 1) * limit
    query = {}
    
    if status:
        query["payee_payment_status"] = status
    
    if search:
        query["$or"] = [
            {"payee_first_name": {"$regex": search, "$options": "i"}},
            {"payee_last_name": {"$regex": search, "$options": "i"}},
            {"payee_email": {"$regex": search, "$options": "i"}}
        ]

    # Update status based on due date
    today = date.today()
    await db.db.payments.update_many(
        {"payee_due_date": today.isoformat(), "payee_payment_status": {"$ne": "completed"}},
        {"$set": {"payee_payment_status": "due_now"}}
    )
    await db.db.payments.update_many(
        {"payee_due_date": {"$lt": today.isoformat()}, "payee_payment_status": {"$ne": "completed"}},
        {"$set": {"payee_payment_status": "overdue"}}
    )

    # Get total count for pagination
    total_items = await db.db.payments.count_documents(query)
    
    # Get paginated results
    cursor = db.db.payments.find(query).skip(skip).limit(limit)
    payments = await cursor.to_list(length=limit)
    
    # Process payments
    for payment in payments:
        payment["_id"] = str(payment["_id"])
        payment["total_due"] = calculate_total_due(
            payment["due_amount"],
            payment.get("discount_percent"),
            payment.get("tax_percent")
        )
        payment["evidence_file"] = None
    
    return {
        "total": total_items,
        "data": payments
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)