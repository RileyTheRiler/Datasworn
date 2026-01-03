from src.server import app

# Vercel needs the app object to be exported as 'app' or handled via a handler
# FastAPI works directly with Vercel's Python runtime if exported properly.
