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



@bot.tree.command(name="롤", description="랜덤 라인")
@app_commands.describe(user1 = "1번")
@app_commands.describe(user2 = "2번")
@app_commands.describe(user3 = "3번")
@app_commands.describe(user4 = "4번")
@app_commands.describe(user5 = "5번")
async def lol(interation: discord.Interaction, user1:discord.Member, user2:discord.Member, user3:discord.Member, user4:discord.Member, user5:discord.Member):
    users = [user1,user2,user3,user4,user5]
    random.shuffle(users)
    await interation.response.send_message(f"탑: {users[0].mention}, 정글: {users[1].mention}, 미드: {users[2].mention}, 원딜: {users[3].mention}, 서폿: {users[4].mention}")
'''
@bot.tree.command(name="test")
@app_commands.describe(user1 = "hi")
async def test(interation: discord.Interaction, user1:discord.Member):
    author = bot.get_user(int(interation.user.id))
    await interation.response.send_message(user1.id)
'''

@bot.tree.command(name="ㄹㄹ", description="채널에 들어가있는 사람으로 자동 라인")
async def auto(interation: discord.Interaction):
    author = bot.get_user(interation.user.id)
    voice_state = interation.user.voice


    if voice_state is None or voice_state.channel is None:
        await interation.response.send_message("채널 들가고 써라")
        return

    voice_channel = voice_state.channel
    if len(voice_channel.members) > 5:
        await interation.response.send_message("야 사람이 너무 많다;;")
        return

    users = []

    for member in voice_channel.members:
        users.append(member)

    while len(users) < 5:
        users.append(bot.get_user(1235948852780077077))

    if len(users) != 5:
        await  interation.response.send_message("위잉 위잉 오류 오류 이유는 몰루")
        return

    random.shuffle(users)
    await interation.response.send_message(f"탑: {users[0].mention}, 정글: {users[1].mention}, 미드: {users[2].mention}, 원딜: {users[3].mention}, 서폿: {users[4].mention}")

@bot.tree.command(name="팀", description="채널에 들어가있는 사람으로 2팀으로 나누기")
async def team(interaction: discord.Interaction):
    voice_state = interaction.user.voice
    if voice_state is None or voice_state.channel is None:
        await interaction.response.send_message("채널 들가고 써라")
        return

    voice_channel = voice_state.channel
    users = []
    for member in voice_channel.members:
        users.append(member)
    random.shuffle(users)
    midpoint = len(users) // 2

    team1 = users[:midpoint]
    team2 = users[midpoint:]

    team1mention = ' '.join([member.mention for member in team1])
    team2mention = ' '.join([member.mention for member in team2])
    await interaction.response.send_message(f"1팀 :{team1mention}, 2팀 :{team2mention}")

bot.run(token)