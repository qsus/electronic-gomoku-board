# if config.py is not found, copy from default_config.py
from os import stat
try:
    stat('config.py')
except OSError:
    print("config.py not found, copying from default_config.py")
    # Copy default_config.py to config.py on micropython (shutil not available)
    with open('default_config.py', 'r') as default_config:
        with open('config.py', 'w') as config:
            config.write(default_config.read())

import asyncio
from app import App

if __name__ == "__main__":
    print("Starting app...")
    app = App()
    asyncio.run(app.main())
