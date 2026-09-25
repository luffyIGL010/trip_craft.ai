import uvicorn
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🚀 Starting TravelGenie AI Agent Server")
    print(" 🌐 Web Interface: http://127.0.0.1:8000")
    print(" 📖 Interactive Swagger API Docs: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
