from app.application import create_app
from app.core.settings import APP_CONFIG

app = create_app(APP_CONFIG)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
