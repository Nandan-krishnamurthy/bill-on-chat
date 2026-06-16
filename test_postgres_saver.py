from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import inspect

print([m for m in dir(AsyncPostgresSaver) if "setup" in m.lower()])