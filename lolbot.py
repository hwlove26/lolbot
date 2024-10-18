import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime
import pytz
import sqlite3

conn = sqlite3.connect('betting.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER,
                guild_id INTEGER,
                balance INTEGER DEFAULT 1000,
                last_claim TEXT,
                PRIMARY KEY (user_id, guild_id))''')

c.execute('''CREATE TABLE IF NOT EXISTS bet_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                guild_id INTEGER,
                bet_amount INTEGER,
                bet_on TEXT,
                result TEXT DEFAULT 'pending',
                timestamp TEXT)''')
conn.commit()

# 배팅 상태를 저장하는 변수
current_bet_active = False  # 배팅이 시작되었는지 여부
candidate_1 = None
candidate_2 = None

betting_status = {}

intents = discord.Intents.all()
intents.voice_states = True
intents.message_content = True
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

def get_balance(user_id, guild_id):
    c.execute("SELECT balance FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    result = c.fetchone()
    if result is None:
        # 새로운 사용자는 기본 잔액 1000으로 설정
        c.execute("INSERT INTO users (user_id, guild_id, balance, last_claim) VALUES (?, ?, 1000, ?)",
                  (user_id, guild_id, None))
        conn.commit()
        return 1000
    else:
        return result[0]

def update_balance(user_id, guild_id, amount):
    c.execute("UPDATE users SET balance=? WHERE user_id=? AND guild_id=?", (amount, user_id, guild_id))
    conn.commit()

def save_bet_history(user_id, guild_id, bet_amount, result):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO bet_history (user_id, guild_id, bet_amount, bet_on, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, guild_id, bet_amount, result, timestamp))
    conn.commit()

def update_bet_result(user_id, guild_id, bet_id, result):
    c.execute("UPDATE bet_history SET result=? WHERE id=? AND user_id=? AND guild_id=?", (result, bet_id, user_id, guild_id))
    conn.commit()

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="돈지급", description="배팅 시작하기")
@app_commands.checks.has_permissions(moderate_members=True)
async def give_money(interation: discord.Interaction, member: discord.Member, amount: int):
    guild_id = ctx.guild.id
    current_balance = get_balance(member.id, guild_id)

    # 잔액 업데이트
    new_balance = current_balance + amount
    update_balance(member.id, guild_id, new_balance)

    await ctx.send(f"{member.mention}님에게 {amount}원을 추가했습니다. 현재 잔액: {new_balance}원.")

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="배팅시작", description="배팅 시작하기")
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(candidate1="후보1", candidate2="후보2")
async def start_betting(interation: discord.Interaction, candidate1: str, candidate2: str):
    guild_id = interation.guild.id

    if interation.user.guild_permissions.administrator:

        if guild_id in betting_status and betting_status[guild_id]['active']:
            await interation.response.send_message("이미 배팅이 진행 중입니다.")
            return

        # 서버별로 배팅 상태 저장
        betting_status[guild_id] = {
            'active': True,
            'candidate_1': candidate1,
            'candidate_2': candidate2
        }

        await interation.response.send_message(f"배팅이 시작되었습니다! 후보 1: **{candidate1}**, 후보 2: **{candidate2}**. 이제 배팅을 시작하세요!")

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="배팅", description="배팅하기")
async def bet(interation: discord.Interaction, amount: int, bet_on: str):
    user_id = interation.user.id
    guild_id = interation.guild.id
    balance = get_balance(user_id, guild_id)

    if guild_id not in betting_status or not betting_status[guild_id]['active']:
        await interation.response.send_message("배팅이 아직 시작되지 않았습니다!")
        return

    candidate_1 = betting_status[guild_id]['candidate_1']
    candidate_2 = betting_status[guild_id]['candidate_2']


    if bet_on.lower() not in [candidate_1.lower(), candidate_2.lower()]:
        await interation.response.send_message(f"올바른 후보를 입력하세요! 후보: {candidate_1} 또는 {candidate_2}")
        return

    if amount <= 0:
        await interation.response.send_message("0원 이하로 배팅할 수 없습니다!")
        return
    elif amount > balance:
        await interation.response.send_message(f"잔액이 부족합니다! 현재 잔액: {balance}원")
        return

    c.execute("SELECT bet_on FROM bet_history WHERE user_id=? AND guild_id=? AND result='pending'", (user_id, guild_id))
    existing_bet = c.fetchone()

    if existing_bet:
        existing_candidate = existing_bet[0]
        if existing_candidate.lower() != bet_on.lower():
            await interation.response.send_message(f"이미 {existing_candidate}에게 배팅하셨습니다! 다른 후보에게는 배팅할 수 없습니다.")
            return

    # 배팅 기록 저장
    save_bet_history(user_id, guild_id, amount, bet_on)

    # 잔액 업데이트 (임시로 배팅 금액을 차감)
    new_balance = balance - amount
    update_balance(user_id, guild_id, new_balance)

    await interation.response.send_message(f"{interation.user.mention}님이 {bet_on}에게 {amount}원을 배팅했습니다. 현재 잔액: {new_balance}원.")

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="잔액", description="잔액 확인")
async def balance(interation: discord.Interaction):
    user_id = interation.user.id
    guild_id = interation.guild.id  # 서버 ID 가져오기
    balance = get_balance(user_id, guild_id)
    await interation.response.send_message(f"{interation.user.mention}님의 현재 잔액은 {balance}원입니다.")

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="기록", description="배팅 기록 확인")
async def history(interation: discord.Interaction):
    user_id = interation.user.id
    guild_id = interation.guild.id  # 서버 ID 가져오기
    c.execute("SELECT bet_amount, result, timestamp FROM bet_history WHERE user_id=? AND guild_id=? ORDER BY timestamp DESC LIMIT 5",
              (user_id, guild_id))
    history = c.fetchall()

    if history:
        history_msg = "\n".join([f"{row[2]} - {row[1].upper()} - {row[0]}원" for row in history])
        await interation.response.send_message(f"{interation.user.mention}님의 최근 배팅 기록:\n{history_msg}")
    else:
        await interation.response.send_message(f"{interation.user.mention}님의 배팅 기록이 없습니다.")

@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="배팅종료", description="배팅 종료 하기")
@app_commands.checks.has_permissions(moderate_members=True)  # 관리자 권한 필요
async def end_betting(interation: discord.Interaction, winner: str):
    string = f"배팅이 종료되었습니다! 승리자: {winner}\n"
    guild_id = interation.guild.id

    if guild_id not in betting_status or not betting_status[guild_id]['active']:
        await interation.response.send_message("진행 중인 배팅이 없습니다.")
        return

    candidate_1 = betting_status[guild_id]['candidate_1']
    candidate_2 = betting_status[guild_id]['candidate_2']

    if winner.lower() not in [candidate_1.lower(), candidate_2.lower()]:
        await interation.response.send_message(f"올바른 승리자를 입력하세요! 후보: {candidate_1} 또는 {candidate_2}")
        return

    # 모든 배팅 기록에서 승리자를 확인하여 결과를 업데이트
    c.execute("SELECT user_id, bet_amount, bet_on FROM bet_history WHERE guild_id=? AND result='pending'", (guild_id,))
    bets = c.fetchall()

    for bet in bets:
        user_id, bet_amount, bet_on = bet
        if bet_on.lower() == winner.lower():
            winnings = bet_amount * 2
            balance = get_balance(user_id, guild_id) + winnings
            update_balance(user_id, guild_id, balance)
            string += f"<@{user_id}>님이 {winnings}원을 획득했습니다! 현재 잔액: {balance}원\n"
        else:
            new_balance = get_balance(user_id, guild_id) - bet_amount
            update_balance(user_id, guild_id, new_balance)
            string += f"<@{user_id}>님은 패배했습니다. {bet_amount}원을 잃었습니다.\n"

    # 배팅 기록의 결과 업데이트
    c.execute("UPDATE bet_history SET result=? WHERE guild_id=? AND result='pending'", (winner, guild_id))
    conn.commit()

    # 배팅 상태 초기화

    betting_status[guild_id]['active'] = False
    await interation.response.send_message(string)



@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="lag", description="지금 몇시지")
async def lag(interation: discord.Interaction):
    current_time = datetime.now(pytz.timezone("US/Central")).strftime("%Y-%m-%d %H:%M:%S")
    await interation.response.send_message(current_time)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="롤", description="5명 선택 랜덤 라인")
@app_commands.describe(user1 = "1번", user2 = "2번", user3 = "3번", user4 = "4번", user5 = "5번")
async def lol(interation: discord.Interaction, user1:discord.User, user2:discord.User, user3:discord.User, user4:discord.User, user5:discord.User):
    users = [user1,user2,user3,user4,user5]
    random.shuffle(users)
    await interation.response.send_message(f"탑: {users[0].mention}, 정글: {users[1].mention}, 미드: {users[2].mention}, 원딜: {users[3].mention}, 서폿: {users[4].mention}")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="팀수동", description="10명 선택 랜덤 팀")
@app_commands.describe(user1 = "1번", user2 = "2번", user3 = "3번", user4 = "4번", user5 = "5번", user6 = "6번", user7 = "7번", user8 = "8번", user9 = "9번", user10 = "10번")
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
@app_commands.describe(ex="제외(1)", ex2="제외(2)",ex3="제외(3)", ex4="제외(4)", ex5="제외(5)")
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
            if str(i.id) == str(ex.id):
                users.remove(i)
        if ex2 is not None:
            if str(i.id) == str(ex2.id):
                users.remove(i)
        if ex3 is not None:
            if str(i.id) == str(ex3.id):
                users.remove(i)
        if ex4 is not None:
            if str(i.id) == str(ex4.id):
                users.remove(i)
        if ex5 is not None:
            if str(i.id) == str(ex5.id):
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