import redis.asyncio as aioredis
from .config import Config

# Expiry time for JTI in seconds
JTI_EXPIRY = 3600

# Initialize Redis client
token_blocklist = aioredis.from_url(Config.REDIS_URL, decode_responses=True)


async def add_jti_to_blocklist(jti: str) -> None:
    """
    Add a JTI (JWT ID) to the blocklist with an expiration time.

    Args:
        jti (str): The JWT ID to block.
    """
    await token_blocklist.set(name=jti, value=1, ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    """
    Check if a JTI (JWT ID) is in the blocklist.

    Args:
        jti (str): The JWT ID to check.

    Returns:
        bool: True if the JTI is in the blocklist, False otherwise.
    """
    exists = await token_blocklist.exists(jti)
    return exists > 0
