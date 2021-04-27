from aiohttp import ClientSession
from datetime import date
import asyncio
import os


# Downloads cohort life tables from the social security administration
# After downloading, run life_html_to_csv.py to generate CSVs with the pertinent data


OUT_DIRECTORY = 'cohort_life_expectancy_tables'
SSA_TABLE_INCREMENT = 10


async def _get_table(session: ClientSession, url: str, path: str) -> tuple[str, str]:
    async with session.get(url) as resp:
        text = await resp.text()
        return text, path


async def _get_tables() -> None:
    async with ClientSession() as session:
        tasks = []
        for year in range(1900, date.today().year, SSA_TABLE_INCREMENT):
            url = f'https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_{year}.html'
            path = os.path.join(OUT_DIRECTORY, f'{year}.html')
            tasks.append(asyncio.ensure_future(_get_table(session, url, path)))

        tables = await asyncio.gather(*tasks)
        for table in tables:
            with open(table[1], 'w') as f:
                f.write(table[0])


if not os.path.exists(OUT_DIRECTORY):
    os.makedirs(OUT_DIRECTORY)

asyncio.run(_get_tables())
