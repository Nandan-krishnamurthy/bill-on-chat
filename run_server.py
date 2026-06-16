#!/usr/bin/env python
"""
Windows-compatible entry point for uvicorn using asyncio.run with SelectorEventLoop.
"""

import sys

if __name__ == "__main__":
    if sys.platform == 'win32':
        import asyncio
        import selectors
        
        # For Windows with psycopg3, use SelectorEventLoop
        def make_loop():
            return asyncio.SelectorEventLoop(selectors.SelectSelector())
        
        import uvicorn
        
        config = uvicorn.Config(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve(), loop_factory=make_loop)
    else:
        import uvicorn
        uvicorn.run(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False
        )



