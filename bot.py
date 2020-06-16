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
async def counters(ctx, pokemon: str, weather: str = None):
    # TODO: check if pokemon has underscore, append _form

    """Displays the top 6 counters"""
    weathers = ['CLEAR', 'RAINY', 'PARTLY_CLOUDY', 'OVERCAST', 'WINDY',
                'SNOW', 'FOG', 'NO_WEATHER']
    if weather is None:
        weather = 'NO_WEATHER'
    if weather.upper() not in weathers:
        await ctx.send(f'Usage: `?counters <pokemon> [weather]`\n\nAvailable '
                       f'weathers are `{weathers}`\nForm pokemon should be '
                       f'formatted like `raichu_alola_form`')
        return

    pb_link = f'https://fight.pokebattler.com/raids/defenders/' \
              f'{pokemon.upper()}/levels/RAID_LEVEL_5/attackers/levels/35' \
              f'/strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/DEFENSE_RANDOM_MC' \
              f'?sort=ESTIMATOR&weatherCondition={weather.upper()}' \
              f'&dodgeStrategy=DODGE_REACTION_TIME&aggregation=AVERAGE' \
              f'&randomAssistants=-1&includeLegendary=true&includeShadow=false'\
              f'&attackerTypes=POKEMON_TYPE_ALL'
    r = requests.get(pb_link)
    d = r.json()

    try:
        info = d['attackers'][0]['randomMove']['defenders']
    except KeyError:
        await ctx.send('Something went wrong. Maybe a typo?')
        return

    embed = discord.Embed(title=f'{pokemon.title()} Counters',
                          colour=discord.Colour(random.randint(0, 16777215)),
                          url=pb_link.replace('fight.', ''),
                          description=f'The following are the top 6 counters '
                                      f'in **{weather}**.',
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=f'https://play.pokemonshowdown.com/sprites/ani/'
                            f'{pokemon.lower()}.gif')
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


def calc_cp(attack, defense, stamina, level):
    cpm = {1: 0.094, 1.5: 0.1351374318, 2: 0.16639787, 2.5: 0.192650919,
           3: 0.21573247, 3.5: 0.2365726613, 4: 0.25572005, 4.5: 0.2735303812,
           5: 0.29024988, 5.5: 0.3060573775, 6: 0.3210876, 6.5: 0.3354450362,
           7: 0.34921268, 7.5: 0.3624577511, 8: 0.3752356, 8.5: 0.387592416,
           9: 0.39956728, 9.5: 0.4111935514, 10: 0.4225, 10.5: 0.4329264091,
           11: 0.44310755, 11.5: 0.4530599591, 12: 0.4627984, 12.5: 0.472336093,
           13: 0.48168495, 13.5: 0.4908558003, 14: 0.49985844,
           14.5: 0.508701765, 15: 0.51739395, 15.5: 0.5259425113, 16: 0.5343543,
           16.5: 0.5426357375, 17: 0.5507927, 17.5: 0.5588305862, 18: 0.5667545,
           18.5: 0.5745691333, 19: 0.5822789, 19.5: 0.5898879072, 20: 0.5974,
           20.5: 0.6048236651, 21: 0.6121573, 21.5: 0.6194041216, 22: 0.6265671,
           22.5: 0.6336491432, 23: 0.64065295, 23.5: 0.6475809666,
           24: 0.65443563, 24.5: 0.6612192524, 25: 0.667934, 25.5: 0.6745818959,
           26: 0.6811649, 26.5: 0.6876849038, 27: 0.69414365, 27.5: 0.70054287,
           28: 0.7068842, 28.5: 0.7131691091, 29: 0.7193991, 29.5: 0.7255756136,
           30: 0.7317, 30.5: 0.7347410093, 31: 0.7377695, 31.5: 0.7407855938,
           32: 0.74378943, 32.5: 0.7467812109, 33: 0.74976104,
           33.5: 0.7527290867, 34: 0.7556855, 34.5: 0.7586303683,
           35: 0.76156384, 35.5: 0.7644860647, 36: 0.76739717,
           36.5: 0.7702972656, 37: 0.7731865, 37.5: 0.7760649616,
           38: 0.77893275, 38.5: 0.7817900548, 39: 0.784637, 39.5: 0.7874736075,
           40: 0.7903, 41: 0.79530001}

    return int(attack * defense**0.5 * stamina**0.5 * cpm[level]**2 / 10)


@bot.command()
async def hundo(ctx, mon: str):
    # TODO: check if pokemon has underscore, append _form
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
    embed = discord.Embed(title=f'100% {mon.title()} CP',
                          colour=discord.Colour(random.randint(0, 16777215)),
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(
        url=f'https://play.pokemonshowdown.com/sprites/ani/{mon.lower()}.gif')

    lvls = [15, 20, 25, 40]
    for lvl in lvls:
        cp = calc_cp(attack + 15, defense + 15, stamina + 15, lvl)
        embed.add_field(name=f'**__Lvl {lvl}__**', value=str(cp), inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def cp(ctx, target_cp: int):
    d = {}
    unreleased = open('unreleased.txt').read().splitlines()
    with open('pokemon.json', 'r') as f:
        dex = json.load(f)
        for mon in dex['pokemon']:
            name = mon['pokemonId']
            if name in unreleased:
                continue
            stamina = mon['stats']['baseStamina']
            attack = mon['stats']['baseAttack']
            defense = mon['stats']['baseDefense']

            # TODO: if max CP == target CP, add to d. Change range to (12, 15)
            # calculate max CP
            max_cp = calc_cp(attack + 15, defense + 15, stamina + 15, 41)
            # calculate min CP
            min_cp = calc_cp(attack, defense, stamina, 1)

            if target_cp > max_cp or target_cp < min_cp:
                continue

            for i in range(2, 82):
                level = i / 2.0
                if level == 40.5:
                    level = 41

                for atk_iv in range(12, 16):
                    for def_iv in range(12, 16):
                        for sta_iv in range(12, 16):
                            atk_total = attack + atk_iv
                            def_total = defense + def_iv
                            sta_total = stamina + sta_iv
                            # iv = round(((atk_iv + def_iv + sta_iv) / 45.0) *
                            #            100, 1)
                            cp = calc_cp(atk_total, def_total, sta_total, level)
                            if cp == target_cp:
                                iv_string = f'{atk_iv}/{def_iv}/{sta_iv}'
                                if name not in d:
                                    d[name] = {level: [iv_string]}
                                elif level in d[name]:
                                    d[name][level].append(iv_string)
                                else:
                                    d[name].update({level: [iv_string]})

    if len(d) == 0:
        await ctx.send('No combinations found')
    else:
        output_string = ''
        for mon in d:
            output_string += f'**{mon.title()}**\n'
            for lvl in d[mon]:
                output_string += f'`Lvl {lvl}: '
                for iv in d[mon][lvl]:
                    output_string += f'{iv} '
                output_string = output_string.strip()
                output_string += '`\n'
        #  print(f'Length: {len(output_string)}')
        if len(output_string) > 1999:
            await ctx.send('Too many results')
        else:
            await ctx.send(output_string)


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
