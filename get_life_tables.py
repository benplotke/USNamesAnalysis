import aiohttp
import asyncio

# Downloads period life tables from the social security administration

async def get_table(session, url, path):
    async with session.get(url) as resp:
        text = await resp.text()
        return (text, path)

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for year in range(1900, 2021, 10):
            url = f'https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_6_{year}.html'
            path = f'./period_life_expectancy_tables/{year}.html'
            tasks.append(asyncio.ensure_future(get_table(session, url, path)))

        tables = await asyncio.gather(*tasks)
        for table in tables:
            with open(table[1], 'w') as f:
                f.write(table[0])

asyncio.run(main())


