import os.path
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append((os.path.dirname(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Config import globalConfig
from views.user.db import create_db_and_tables
from extensions.logger import log_init
from extensions.geoserver import init_geoserver, init_database
from exceptions.DatabaseException import TableCreateException, table_create_exception_handler
from views.map.router import router as geoserver_router
from views.user.router import router as user_router
from views.code_server.router import router as coder_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(TableCreateException, table_create_exception_handler)

app.include_router(geoserver_router, prefix='/api')
app.include_router(user_router)
app.include_router(coder_router, prefix='/api')


@app.on_event('startup')
async def _():
    log_init()
    await create_db_and_tables()
    init_database()
    await init_geoserver()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='app:app', host="0.0.0.0", port=globalConfig.port, reload=True, debug=globalConfig.DEBUG)
