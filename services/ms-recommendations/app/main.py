from fastapi import FastAPI

app = FastAPI(title="Nombre del Microservicio")

@app.get("/health")
def health():
    return {"status": "ok"}