from typing import Any
from fastapi import APIRouter

router = APIRouter()

@router.post("/home")
def home() -> Any:

    return {
        "message": "Hello From Fast API"
    }