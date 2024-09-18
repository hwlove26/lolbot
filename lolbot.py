import discord
from discord import app_commands
from discord.ext import commands
import random



intents = discord.Intents.all()
intents.voice_states = True
token = open("token.txt", "r").readline()


bot = commands.Bot(command_prefix="!sad", intents= intents)

@bot.event
async def on_ready():
    print("ㄹㄷ")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="롤", description="5명 선택 랜덤 라인")
@app_commands.describe(user1 = "1번")
@app_commands.describe(user2 = "2번")
@app_commands.describe(user3 = "3번")
@app_commands.describe(user4 = "4번")
@app_commands.describe(user5 = "5번")
async def lol(interation: discord.Interaction, user1:discord.User, user2:discord.User, user3:discord.User, user4:discord.User, user5:discord.User):
    users = [user1,user2,user3,user4,user5]
    random.shuffle(users)
    await interation.response.send_message(f"탑: {users[0].mention}, 정글: {users[1].mention}, 미드: {users[2].mention}, 원딜: {users[3].mention}, 서폿: {users[4].mention}")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="팀수동", description="10명 선택 랜덤 팀")
@app_commands.describe(user1 = "1번")
@app_commands.describe(user2 = "2번")
@app_commands.describe(user3 = "3번")
@app_commands.describe(user4 = "4번")
@app_commands.describe(user5 = "5번")
@app_commands.describe(user6 = "6번")
@app_commands.describe(user7 = "7번")
@app_commands.describe(user8 = "8번")
@app_commands.describe(user9 = "9번")
@app_commands.describe(user10 = "10번")
async def teamsu(interaction: discord.Interaction, user1:discord.User, user2:discord.User, user3:discord.User, user4:discord.User, user5:discord.User, user6:discord.User, user7:discord.User, user8:discord.User, user9:discord.User, user10:discord.User):
    users = [user1,user2,user3,user4,user5,user6,user7,user8,user9,user10]
    random.shuffle(users)
    midpoint = len(users) // 2

    team1 = users[:midpoint]
    team2 = users[midpoint:]

    team1mention = ' '.join([User.mention for User in team1])
    team2mention = ' '.join([User.mention for User in team2])
    await interaction.response.send_message(f"1팀 :{team1mention}, 2팀 :{team2mention}")

'''
@bot.tree.command(name="test")
@app_commands.describe(user1 = "hi")
async def test(interation: discord.Interaction, user1:discord.User):
    author = bot.get_user(int(interation.user.id))
    voice_state = interation.user.voice
    if voice_state is None or voice_state.channel is None:
        await interation.response.send_message("채널 들가고 써라")
        return
    users = voice_state.channel.members
    for i in users :
        if i.bot:
            users.remove(i)
    await interation.response.send_message(users)
    .
'''

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="ㅇㄹㄴ", description="아레나를 위한")
async def arena(interation : discord.Interaction):
    voice_state = interation.user.voice


    if voice_state is None or voice_state.channel is None:
        await interation.response.send_message("채널 들가고 써라")
        return


    teams = []
    users = voice_state.channel.members
    for i in users :
        if i.bot:
            users.remove(i)

    if len(users) > 16:
        await interation.response.send_message("야 사람이 너무 많다;;")
        return

    if len(users) % 2 != 0:
        users.append(bot.get_user(1235948852780077077))

    random.shuffle(users)

    for i in range(0, len(users), 2):
        teams.append((users[i], users[i+1]))

    formatted_string = "팀들:\n"
    for i, team in enumerate(teams):
        formatted_string += f"팀 {i+1}: {team[0].mention} 와(과) {team[1].mention}\n"

    await interation.response.send_message(formatted_string)


@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="ㄹㄹ", description="채널에 들어가있는 사람으로 자동 라인")
async def auto(interation: discord.Interaction, ex: discord.User=None, ex2: discord.User=None, ex3: discord.User=None, ex4: discord.User=None, ex5: discord.User=None):
    author = bot.get_user(interation.user.id)
    voice_state = interation.user.voice


    if voice_state is None or voice_state.channel is None:
        await interation.response.send_message("채널 들가고 써라")
        return

    voice_channel = voice_state.channel


    users = voice_state.channel.members

    for i in users :
        if ex is not None:
            if i.id == ex.id:
                users.remove(i)
        if ex2 is not None:
            if i.id == ex2.id:
                users.remove(i)
        if ex3 is not None:
            if i.id == ex3.id:
                users.remove(i)
        if ex4 is not None:
            if i.id == ex4.id:
                users.remove(i)
        if ex5 is not None:
            if i.id == ex5.id:
                users.remove(i)

        if i.bot:
            users.remove(i)


    if len(users) > 5:
        await interation.response.send_message("야 사람이 너무 많다;;")
        return

    while len(users) < 5:
        users.append(bot.get_user(1235948852780077077))

    if len(users) != 5:
        await  interation.response.send_message("위잉 위잉 오류 오류 이유는 몰루")
        return

    random.shuffle(users)
    await interation.response.send_message(f"탑: {users[0].mention}, 정글: {users[1].mention}, 미드: {users[2].mention}, 원딜: {users[3].mention}, 서폿: {users[4].mention}")

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="팀", description="채널에 들어가있는 사람으로 2팀으로 나누기")
async def team(interaction: discord.Interaction):
    voice_state = interaction.user.voice
    if voice_state is None or voice_state.channel is None:
        await interaction.response.send_message("채널 들가고 써라")
        return

    users = voice_state.channel.members
    for i in users :
        if i.bot:
            users.remove(i)
    random.shuffle(users)
    midpoint = len(users) // 2

    team1 = users[:midpoint]
    team2 = users[midpoint:]

    team1mention = ' '.join([User.mention for User in team1])
    team2mention = ' '.join([User.mention for User in team2])
    await interaction.response.send_message(f"1팀 :{team1mention}, 2팀 :{team2mention}")

bot.run(token)