import asyncio
from app import App

print("Starting app...")
if __name__ == "__main__":
    app = App()
    asyncio.run(app.main())
