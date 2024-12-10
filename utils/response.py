from fastapi.responses import JSONResponse
from utils.messages import messages
from fastapi import status

def response(status_code, data=[]):
    content = messages.get(status_code)
    return JSONResponse(
        {
            "success": content[2],
            "code": status_code,
            "msg": content[0],
            "data": data,
        },
        content[1] or status.HTTP_200_OK,
    )