"""
Health check server
"""

import os

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from starlette.routing import Route
import uvicorn


async def health_check(request: Request) -> Response:
    return JSONResponse({
        "status": "down" if not app.state.status else "up",
        "version": "0.0.1",
    })


routes = [
    Route("/health", endpoint=health_check)
]

app = Starlette(debug=False, routes=routes)
app.state.status = False

if __name__ == "__main__":
    uvicorn.run(app, http='h11', loop='uvloop', port=os.getenv("HEALTHCHECK_PORT", 8000))
