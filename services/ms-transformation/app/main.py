from fastapi import FastAPI

app = FastAPI(title="Nombre del Microservicio")

@app.get("/health")
def health():
    return {"status": "ok"}

# Aquí incluyes los routers con tus endpoints específicos
# from app.routers import datos
# app.include_router(datos.router, prefix="/api")

# Si no tienes routers aún, deja solo /health.