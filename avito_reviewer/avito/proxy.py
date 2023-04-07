import aiohttp
from playwright.async_api import ProxySettings


async def check_ip_address(ip):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://ipwho.is/{ip}') as resp:
            d = await resp.json()
            # print(d)
            return d


async def create_proxy_settings(ip: str, port: str, username: str, password: str) -> ProxySettings:
    return ProxySettings(
        server=f"http://{ip}:{port}",
        username=username,
        password=password
    )
