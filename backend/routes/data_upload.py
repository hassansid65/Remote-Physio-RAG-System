from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.services.weaviate_store import weaviate_store
import json
import csv
from io import StringIO
from typing import List
import chardet

router = APIRouter(prefix="/data", tags=["data"])

def safe_decode_content(content: bytes) -> str:
    """Safely decode file content with multiple encoding attempts"""
    # First check if content is empty or too small
    if len(content) == 0:
        return ""

    # Try common encodings in order of preference
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']

    for encoding in encodings:
        try:
            decoded = content.decode(encoding)
            # Check if decoded content makes sense (not just replacement characters)
            if '�' not in decoded or decoded.count('�') < len(decoded) * 0.1:
                return decoded
        except (UnicodeDecodeError, LookupError):
            continue

    # If all encodings fail, try with chardet
    try:
        detected = chardet.detect(content)
        if detected['encoding'] and detected['confidence'] > 0.7:
            return content.decode(detected['encoding'])
    except:
        pass

    # Check if it might be binary data
    if b'\x00' in content[:100]:  # Null bytes suggest binary
        raise ValueError("File appears to contain binary data")

    # Last resort: decode with errors='replace' to avoid crashes
    return content.decode('utf-8', errors='replace')

@router.post("/upload/assessment")
async def upload_assessment(
    file: UploadFile = File(...),
    category: str = Form(...)
):
    """Upload assessment data"""
    
    try:
        content = await file.read()
        text_content = safe_decode_content(content)
        
        # Handle different file formats
        if file.filename.endswith('.json'):
            data = json.loads(text_content)
            if isinstance(data, list):
                documents = [
                    {
                        "content": item.get("content", str(item)),
                        "type": "assessment",
                        "category": category
                    }
                    for item in data
                ]
            else:
                documents = [{
                    "content": data.get("content", str(data)),
                    "type": "assessment",
                    "category": category
                }]
        
        elif file.filename.endswith('.csv'):
            csv_file = StringIO(text_content)
            reader = csv.DictReader(csv_file)
            documents = [
                {
                    "content": row.get("content", str(row)),
                    "type": "assessment",
                    "category": category
                }
                for row in reader
            ]
        
        else:
            # Plain text file
            documents = [{
                "content": text_content,
                "type": "assessment",
                "category": category
            }]
        
        # Add to Weaviate
        weaviate_store.add_batch_documents(documents)
        
        return {
            "message": f"Successfully uploaded {len(documents)} assessment documents",
            "count": len(documents),
            "category": category
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading assessment: {str(e)}")

@router.post("/upload/exercise")
async def upload_exercise(
    file: UploadFile = File(...),
    category: str = Form(...)
):
    """Upload exercise data"""
    
    try:
        content = await file.read()
        text_content = safe_decode_content(content)
        
        # Handle different file formats
        if file.filename.endswith('.json'):
            data = json.loads(text_content)
            if isinstance(data, list):
                documents = [
                    {
                        "content": item.get("content", str(item)),
                        "type": "exercise",
                        "category": category
                    }
                    for item in data
                ]
            else:
                documents = [{
                    "content": data.get("content", str(data)),
                    "type": "exercise",
                    "category": category
                }]
        
        elif file.filename.endswith('.csv'):
            csv_file = StringIO(text_content)
            reader = csv.DictReader(csv_file)
            documents = [
                {
                    "content": row.get("content", str(row)),
                    "type": "exercise",
                    "category": category
                }
                for row in reader
            ]
        
        else:
            # Plain text file
            documents = [{
                "content": text_content,
                "type": "exercise",
                "category": category
            }]
        
        # Add to Weaviate
        weaviate_store.add_batch_documents(documents)
        
        return {
            "message": f"Successfully uploaded {len(documents)} exercise documents",
            "count": len(documents),
            "category": category
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading exercise: {str(e)}")

@router.post("/upload/text")
async def upload_text_data(
    content: str = Form(...),
    data_type: str = Form(...),
    category: str = Form(...)
):
    """Upload text data directly"""
    
    if data_type not in ["assessment", "exercise"]:
        raise HTTPException(status_code=400, detail="Type must be 'assessment' or 'exercise'")
    
    try:
        weaviate_store.add_document(content, data_type, category)
        
        return {
            "message": f"Successfully uploaded {data_type} data",
            "type": data_type,
            "category": category
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading data: {str(e)}")