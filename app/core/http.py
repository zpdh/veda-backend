import httpx

http_client = httpx.AsyncClient(timeout=15.0)


def get_http_client() -> httpx.AsyncClient:
    return http_client


async def close_http_connection() -> None:
    await http_client.aclose()
