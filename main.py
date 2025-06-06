import asyncio
from app import App

if __name__ == "__main__":
    print("Starting app...")
    app = App()
    asyncio.run(app.main())
