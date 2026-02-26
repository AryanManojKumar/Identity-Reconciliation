from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import init_db, get_db
from service import identify_contact
from typing import Optional

app = FastAPI(title="Identity Reconciliation API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()

class IdentifyRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None

@app.post("/identify")
def identify(request: IdentifyRequest, db: Session = Depends(get_db)):
    if not request.email and not request.phoneNumber:
        raise HTTPException(status_code=400, detail="Either email or phoneNumber is required")
    
    try:
        result = identify_contact(db, request.email, request.phoneNumber)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    import uvicorn
    import os
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
