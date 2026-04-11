from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import contract, rules

app = FastAPI(title="合同风险审核 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contract.router)
app.include_router(rules.router)


@app.get("/")
def root():
    return {"service": "合同风险审核", "docs": "/docs"}
