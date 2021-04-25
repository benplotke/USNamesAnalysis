from aiohttp import ClientSession
import asyncio
import os


# Downloads period life tables from the social security administration


OUT_DIRECTORY = 'period_life_expectancy_tables'


async def get_table(session: ClientSession, url: str, path: str) -> tuple[str, str]:
    async with session.get(url) as resp:
        text = await resp.text()
        return text, path


async def get_tables() -> None:
    async with ClientSession() as session:
        tasks = []
        for year in range(1900, 2021, 10):
            url = f'https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_6_{year}.html'
            path = os.path.join(OUT_DIRECTORY, f'{year}.html')
            tasks.append(asyncio.ensure_future(get_table(session, url, path)))

        tables = await asyncio.gather(*tasks)
        for table in tables:
            with open(table[1], 'w') as f:
                f.write(table[0])


if not os.path.exists(OUT_DIRECTORY):
    os.makedirs(OUT_DIRECTORY)

asyncio.run(get_tables())
