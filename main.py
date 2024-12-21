from pathlib import Path
from fastapi import FastAPI, APIRouter
from app.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

BASE_PATH = Path(__file__).resolve().parent
root_router = APIRouter()
app = FastAPI(title="Caption Generator API's")

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        return response

app.add_middleware(CSPMiddleware)

app.include_router(api_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React app's origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    # Use this for debugging purposes only       
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.main()