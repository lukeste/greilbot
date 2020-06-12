import discord
import requests
import json
import datetime
import random
from discord.ext import commands

bot = commands.Bot(command_prefix='?')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


def fix_move_name(move_name: str):
    move_name = move_name.split('_')
    fixed = ''
    for word in move_name:
        word = word.title()
        if word != 'Fast':
            fixed += word + ' '
    fixed = fixed.strip()
    return fixed


@bot.command()
async def counters(ctx, mon: str, weather: str = None):
    """Displays the top 6 counters"""
    weathers = ['CLEAR', 'RAINY', 'PARTLY_CLOUDY', 'OVERCAST', 'WINDY',
                'SNOW', 'FOG', 'NO_WEATHER']
    if weather is None:
        weather = 'NO_WEATHER'
    if weather.upper() not in weathers:
        await ctx.send(f'Weather type not supported. Available weathers are '
                       f'`{weathers}`')
        return

    pb_link = f'https://fight.pokebattler.com/raids/defenders/{mon.upper()}/levels/RAID_LEVEL_5/attackers/levels/40/strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/DEFENSE_RANDOM_MC?sort=OVERALL&weatherCondition={weather.upper()}&dodgeStrategy=DODGE_REACTION_TIME&aggregation=AVERAGE&randomAssistants=-1&includeLegendary=true&includeShadow=false&attackerTypes=POKEMON_TYPE_ALL&friendLevel=FRIENDSHIP_LEVEL_4'
    r = requests.get(pb_link)
    d = r.json()

    try:
        info = d['attackers'][0]['randomMove']['defenders']
    except KeyError:
        await ctx.send('Something went wrong. Maybe a typo?')
        return

    embed = discord.Embed(title=f'{mon.title()} Counters',
                          colour=discord.Colour(random.randint(0, 16777215)),
                          url=pb_link.replace('fight.', ''),
                          description=f'The following are the top 6 counters '
                                      f'in **{weather}**.',
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=f'https://play.pokemonshowdown.com/sprites/ani/{mon.lower()}.gif')
    embed.set_footer(text='Data provided by pokebattler.com')

    with open('moves.json') as f:
        moves = json.load(f)
        for i in range(1, 7):
            counter_name = info[-i]['pokemonId'].title().replace('_', ' ')
            move1 = moves.get(info[-i]['byMove'][-1]['move1'])['fixedName']
            move1_emoji = moves.get(info[-i]['byMove'][-1]['move1'])['emojiId']
            move2 = moves.get(info[-i]['byMove'][-1]['move2'])['fixedName']
            move2_emoji = moves.get(info[-i]['byMove'][-1]['move2'])['emojiId']
            embed.add_field(name=f'**{counter_name}**',
                            value=f'{move1_emoji} {move1}\n'
                                  f'{move2_emoji} {move2}',
                            inline=True)
    await ctx.send(embed=embed)


def calc_cp(attack, defense, stamina):
    cpm = {15: 0.51739395,
           20: 0.5974,
           25: 0.667934,
           40: 0.7903}
    cp = {}
    for lvl in cpm:
        cp[lvl] = int((attack+15)*(defense+15)**0.5*(stamina+15)**0.5*cpm[
            lvl]**2/10)
    return cp


@bot.command()
async def hundo(ctx, mon: str):
    """Displays the 100%IV CP for a specified pokemon"""
    with open('pokemon.json') as f:
        dex = json.load(f)
        for pokemon in dex['pokemon']:
            if pokemon['pokemonId'] == mon.upper():
                break
            pokemon = None
        if pokemon is None:
            await ctx.send('Pokemon not found')
            return
        attack = pokemon['stats']['baseAttack']
        defense = pokemon['stats']['baseDefense']
        stamina = pokemon['stats']['baseStamina']
    cp_dict = calc_cp(attack, defense, stamina)
    embed = discord.Embed(title=f'100% {mon.title()} CP',
                          colour=discord.Colour(random.randint(0, 16777215)),
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(
        url=f'https://play.pokemonshowdown.com/sprites/ani/{mon.lower()}.gif')

    for cp in cp_dict:
        embed.add_field(name=f'**__Lvl {cp}__**', value=str(cp_dict[cp]),
                        inline=True)

    await ctx.send(embed=embed)


# @bot.event
# async def on_message(message):
#     if 'yikes' in message.content.lower():
#         await message.add_reaction('<:yikes:426912567819239424>')
#     elif 'raikou' in message.content.lower():
#         await message.add_reaction('<:raikou:338977485243023361>')
#     return

with open('key.txt') as keyfile:
    key = keyfile.read()

bot.run(key)
