import asyncio
import random
import aiohttp


async def read_pokemons_page(offset: int, session: aiohttp.ClientSession):
    async with session.get(f"/api/v2/pokemon?offset={offset}&limit=10") as response:
        response = await response.json()
        pokemons = response['results']
        count = response['count']

        return count, pokemons


async def read_pokemon_stats(pokemon_number: int, session: aiohttp.ClientSession):
    async with session.get(f"/api/v2/pokemon/{pokemon_number}") as response:
        response = await response.json()
        attack_stat = next((stat["base_stat"] for stat in response["stats"] if stat["stat"]["name"] == "attack"))
        defense_stat = next((stat["base_stat"] for stat in response["stats"] if stat["stat"]["name"] == "defense"))
        speed_stat = next((stat["base_stat"] for stat in response["stats"] if stat["stat"]["name"] == "speed"))

        return attack_stat, defense_stat, speed_stat


async def read_pokemons():
    async with aiohttp.ClientSession(base_url="https://pokeapi.co") as session:
        total_count, first_page = await read_pokemons_page(0, session)

        total_pages = total_count // len(first_page)
        pokemons = first_page

        coroutines = []
        for page_number in range(1, total_pages + 1):  # Start from 1 as the first page is already fetched
            coroutines.append(read_pokemons_page(page_number * 10, session))

        results = await asyncio.gather(*coroutines)

        for _, page_pokemons in results:
            pokemons.extend(page_pokemons)

        pokemons_stats = []

        random_pokemons = random.sample(range(1, 100), 10)

        for pokemon in random_pokemons:
            pokemon_name = next(
                (poke["name"] for poke in pokemons if poke["url"] == f"https://pokeapi.co/api/v2/pokemon/{pokemon}/")
            )
            attack, defense, speed = await read_pokemon_stats(pokemon, session)
            strength = sum((attack, defense, speed))
            pokemons_stats.append(dict(name=pokemon_name, strength=strength, attack=attack, defense=defense, speed=speed))

        return pokemons_stats


def battle(fighters: list):
    print(f"{fighters[0]['name'].capitalize()} vs {fighters[1]['name'].capitalize()}")
    winner_index = 1
    if fighters[0]["strength"] > fighters[1]["strength"]:
        winner_index = 0
    return (
        f"{fighters[winner_index]['name'].capitalize()} wins! His attack is {fighters[winner_index]['attack']}, defense is {fighters[winner_index]['defense']},"
        f" speed is {fighters[winner_index]['speed']}. Total strength is {fighters[winner_index]['strength']}.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pokemons = loop.run_until_complete(read_pokemons())
    poke_fighters = random.sample(pokemons, 2)
    print(battle(poke_fighters))
