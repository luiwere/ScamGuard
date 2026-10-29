"""
Modal Serverless Deployment for ScamGuard Backend
Deploy on Modal GPUs / CPU containers using your Modal credits.

Run:
  modal deploy backend/modal_app.py
"""

import modal

# Define container image with all backend dependencies
scamguard_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.6.0",
        "websockets>=13.1",
        "httpx>=0.27.2",
        "python-dotenv>=1.0.1",
    )
    .add_local_dir("backend/app", remote_path="/root/app")
    .add_local_dir("backend/data", remote_path="/root/data")
)

app = modal.App("scamguard-api", image=scamguard_image)


@app.function(
    secrets=[
        modal.Secret.from_name("scamguard-secrets")  # Set FIREWORKS_API_KEY, TELEGRAM_BOT_TOKEN
    ]
)
@modal.asgi_app()
def fastapi_app():
    import sys
    sys.path.insert(0, "/root")
    from app.main import app as scamguard_fastapi
    return scamguard_fastapi
