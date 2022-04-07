#                   ДОБАВЛЕНИЕ БИБЛИОТЕК
import discord
from discord import member
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import *
from discord_slash.utils.manage_components import *
from discord_slash.model import ButtonStyle
import asyncio
import mysql.connector
import config
#                   СОЗДАНИЕ БОТА
bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)
time_to_dlt_msgs = 15
server_id = 953546586259083304
server_name = 'Bot test'
servers_ids = []

#                   MySQL CONNECT
try:
    print('Connecting to MySQL database...')
    db = mysql.connector.connect(
        host="mysql104.1gb.ru",
        database="gb_ivanbd",
        user="gb_ivanbd",
        password="C87a-YGMzmPH")
    print("Connection established")
except mysql.connector.Error as err:
    print(err)
else:
    sql = db.cursor()

sql.execute("SELECT number,server_id FROM Servers")
result = sql.fetchall()
for row in result:
    servers_ids.insert(row[0], row[1])
print(servers_ids)
#                   РОЛИ
admin_role_id = 953561378084487188
moder_role_id = 954773866130055310
mute_role_id = 953578703378599956

#                   КАНАЛЫ
logs_channel_id = 953667780476014592


#                   СОБЫТИЯ
@bot.event
async def on_ready():
    sql.execute("SELECT count(*) FROM Servers")
    servers_summ = sql.fetchone()
    # print(servers_summ)
    # print(discord.Status.online)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('/help on {} servers'.format(
        servers_summ[0])))
    print("Bot connected")


'''
@bot.event
async def on_member_join(ctx, user: discord.Member):
    id = user.id
    guild_id = discord.utils.get(ctx.guild.id)
    db.execute("INSERT INTO `gb_jk08`.`Servers` (`number`, `server_name`, `server_id`, `admin_role_id`,"
               " `moderator_role_id`, `mute_role_id`, `logs_channel_id`, `time_to_dlt_msgs`, `lang`) "
               f"VALUES ('', '{guild_id}', '', '', '', '', '', '', '')")
    user.send()'''

'''
@bot.event  # ловим реакции
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    emoji: PartialEmoji = payload.emoji
    print(emoji)
    if emoji.name in dictionary.emoji_flags:
        print(emoji.name)
        react_lang = emoji.name
        channel = payload.channel_id
        message_id = payload.message_id
        msg = discord.Message
        message_text = msg.content
        author = msg.author
        user = payload.member
        result = translator.translate(message_text, dest=react_lang)
        answer = discord.Embed(title='{}'.format(author),
                               description='{} -> {}'.format(message_text, result))
        answer.set_thumbnail(url=channel.author.avatar_url)
        await channel.send(answer)'''


#                   КОМАНДА НАСТРОЙКИ
'''
@bot.command()
# @commands.has_guild_permissions()
async def startbot(ctx):
    guild_id = ctx.guild.id
    print(guild_id)
    guild_name = bot.get_guild(ctx.guild.id)
    sql.execute("INSERT INTO `Servers`(`number`, `server_name`, `server_id`, `admin_role_id`, `moderator_role_id`,"
                " `mute_role_id`, `logs_channel_id`, `time_to_dlt_msgs`, `lang`) VALUES"
                f" (NULL,'{guild_name}',{guild_id},'','','','',15,en)")
    await ctx.send("Бот зарегистрирован.")
'''

'''@slash.slash(name='server_settings',
             description='Настройки сервера (отправлять в приватный канал)',
             guild_ids=[server_id])
@commands.bot_has_guild_permissions(Administrator = True)
async def _settings(ctx: SlashContext):
    await ctx.send(embed=discord.Embed(title='Server settings',
                                       description='Choose button'))
    btns1 = [
        create_button(style=ButtonStyle.gray, label="", emoji=''),      # language
        create_button(style=ButtonStyle.gray, label="", emoji=''),      # modules
        create_button(style=ButtonStyle.gray, label="", emoji='')]      # commands and this roles permission
    row = create_actionrow(*btns1)
    await ctx.send(components=[row])'''


#                   КОМАНДЫ
# mute
@slash.slash(name="mute",
             description="Мутит пользователя",
             guild_ids=servers_ids,
             options=([
                 create_option(
                     name="member",
                     description="Введите имя пользователя",
                     required=True,
                     option_type=6),
                 create_option(
                     name="time",
                     description="Введите время",
                     required=True,
                     option_type=4),
                 create_option(
                     name="reason",
                     description="Введите причину",
                     required=True,
                     option_type=3)
             ]))
@commands.has_role(moder_role_id)
async def _mute(ctx: SlashContext, user: discord.Member, time: int, reason: str):
    author = ctx.author
    guild_id = bot.get_guild(ctx.guild.id)
    sql.execute("SELECT moderator_role_id FROM Servers WHERE server_id = '{guild_id}'")
    moder_role_id = sql.fetchone()
    sql.execute("SELECT admin_role_id FROM Servers WHERE server_id = '{guild_id}'")
    admin_role_id = sql.fetchone()
    if moder_role_id or admin_role_id not in author.roles:
        await ctx.send('{}, у вас нет права на использование этой команды!'.format(author.mention))
    else:
        sql.execute("SELECT mute_role_id FROM Servers WHERE server_id = '{guild_id}'")
        mute_role_id = sql.fetchone()
        mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)
        if mute_role in user.roles:
            await ctx.send('У этого пользователя уже есть мут')
            await asyncio.sleep(time_to_dlt_msgs)
            await ctx.message.delete()
        else:
            await user.add_roles(mute_role)
            await ctx.send('Модератор {} замутил пользователя {} на {}, причина: {}'.format(ctx.author.mention,
                                                                                            user.mention, time, reason))
            logs_channel_id = db.execute(f"SELECT 'logs_channel_id' INTO 'Servers' WHERE server_id = '{guild_id}'")
            print(logs_channel_id)
            logs_channel = discord.utils.get(ctx.guild.get_channel(channel_id=logs_channel_id))
            await logs_channel.send('Модератор {} замутил пользователя {} на {}, причина: {}'.format(ctx.author.mention,
                                                                                                     user.mention, time,
                                                                                                     reason))
            await asyncio.sleep(time_to_dlt_msgs)
            await ctx.message.delete()
            await asyncio.sleep(time - time_to_dlt_msgs)
            try:
                if mute_role in user.roles:
                    await user.remove_roles(mute_role)
                    await logs_channel.send(
                        "Пользователь {} был разбанен. Причина: время бана закончилось.".format(member))
                    await user.send(embed=discord.Embed(title='Вы разбанены по истечению времени.',
                                                        description='Сервер: {}'.format(server_name)))
                    guild = bot.get_guild(server_id)
                    invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=1, temporary=False)
                    btns = [
                        create_button(style=ButtonStyle.URL, label="Вернуться на сервер!",
                                      url='https://discord.gg/{}'.format(invite.code))]
                    row = create_actionrow(*btns)
                    await user.send(components=[row])
                else:
                    pass
            finally:
                pass


# unmute
@slash.slash(name="unmute",
             description="Снимает мут с пользователя",
             guild_ids=servers_ids,
             options=[
                 create_option(
                     name="member",
                     description="Введите имя пользователя",
                     required=True,
                     option_type=6)
             ])
async def _unmute(ctx: SlashContext, member: discord.Member):
    author = ctx.author
    guild_id = bot.get_guild(ctx.guild.id)
    sql.execute(f"SELECT moderator_role_id FROM Servers WHERE server_id = '{guild_id}'")
    moder_role_id = sql.fetchone()
    sql.execute(f"SELECT admin_role_id FROM Servers WHERE server_id = '{guild_id}'")
    admin_role_id = sql.fetchone()
    if moder_role_id or admin_role_id not in author.roles:
        await ctx.send('{}, у вас нет права на использование этой команды!'.format(author.mention))
    else:
        sql.execute(f"SELECT logs_channel_id FROM Servers WHERE server_id = '{guild_id}'")
        id_channel = sql.fetchone()
        logs_channel = bot.get_channel(id_channel[0])
        sql.execute(f"SELECT mute_role_id INTO Servers WHERE server_id = '{guild_id}'")
        mute_role_id = sql.fetchone()
        mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send('Модератор {} снял мут с пользователя {}'.format(ctx.author.mention, member.mention))
            await logs_channel.send('Модератор {} снял мут с пользователя {}'.format(
                ctx.author.mention, member.mention))
        else:
            await ctx.send('У этого пользователя сейчас нет мута')
            await asyncio.sleep(time_to_dlt_msgs)
            await ctx.message.delete()


# clear
@slash.slash(name="clear",
             description="Удаляет сообщения в этом канале",
             guild_ids=servers_ids,
             options=[
                 create_option(
                     name="amount",
                     description="Введите кол-во сообщений",
                     required=True,
                     option_type=4)
             ])
async def _clear(ctx: SlashContext, amount: int):
    author = ctx.author
    guild_id = bot.get_guild(ctx.guild.id)
    sql.execute(f"SELECT moderator_role_id FROM Servers WHERE server_id = '{guild_id}'")
    moder_role_id = sql.fetchone()
    print(moder_role_id)
    sql.execute(f"SELECT admin_role_id FROM Servers WHERE server_id = '{guild_id}'")
    admin_role_id = sql.fetchone()
    if moder_role_id or admin_role_id not in author.roles:
        await ctx.send('{}, у вас нет права на использование этой команды!'.format(author.mention))
    else:
        sql.execute(f"SELECT logs_channel_id FROM Servers WHERE server_id = '{guild_id}'")
        id_channel = sql.fetchone()
        logs_channel = bot.get_channel(id_channel[0])
        await ctx.send('{} удаляет сообщения...'.format(ctx.author.mention))
        await logs_channel.send('{} удалил сообщения. Amount = {}.'.format(ctx.author.mention, amount))
        await asyncio.sleep(5)
        await ctx.channel.purge(limit=amount + 1)


# deathnote
@slash.slash(name="deathnote",
             description="Навсегда банит пользователя",
             guild_ids=servers_ids,
             options=[
                 create_option(
                     name="member",
                     description="Введите имя пользователя",
                     required=True,
                     option_type=6),
                 create_option(name="reason",
                               description="Введите причину",
                               required=True,
                               option_type=3)
             ])
async def _deathnote(ctx: SlashContext, member: discord.Member, reason: str):
    author = ctx.author
    guild_id = bot.get_guild(ctx.guild.id)
    sql.execute("SELECT admin_role_id FROM Servers WHERE server_id = '{guild_id}'")
    admin_role_id = sql.fetchone()
    if admin_role_id not in author.roles:
        await ctx.send('{}, у вас нет права на использование этой команды!'.format(author.mention))
    else:
        sql.execute(f"SELECT logs_channel_id FROM Servers WHERE server_id = '{guild_id}'")
        id_channel = sql.fetchone()
        logs_channel = bot.get_channel(id_channel[0])
        await member.send(embed=discord.Embed(title='Вы были забанены навсегда на сервере {}'.format(server_name),
                                              description='Причина: {}'
                                                          'Модератор: {}'.format(reason, ctx.author.mention)))
        await logs_channel.send('Модератор {} забанил пользователя {} навсегда. Причина: '.format(author.mention,
                                                                                                  member.mention,
                                                                                                  reason))
        await ctx.send('Модератор {} забанил пользователя {} навсегда. Причина: '.format(author.mention,
                                                                                         member.mention, reason))
        await asyncio.sleep(time_to_dlt_msgs)
        await ctx.message.delete()
        await member.ban(reason=reason)


# ban
@slash.slash(name="ban",
             description="Банит пользователя",
             guild_ids=servers_ids,
             options=[
                 create_option(
                     name="member",
                     description="Введите имя пользователя",
                     required=True,
                     option_type=6),
                 create_option(
                     name="time",
                     description="Введите время",
                     required=True,
                     option_type=4),
                 create_option(
                     name="reason",
                     description="Введите причину",
                     required=True,
                     option_type=3)
             ])
@commands.has_role(moder_role_id)
async def _ban(ctx: SlashContext, member: discord.Member, time: int, reason: str):
    author = ctx.author
    guild_id = bot.get_guild(ctx.guild.id)
    sql.execute(f"SELECT moderator_role_id FROM Servers WHERE server_id = '{guild_id}'")
    moder_role_id = sql.fetchone()
    sql.execute(f"SELECT admin_role_id FROM Servers WHERE server_id = '{guild_id}'")
    admin_role_id = sql.fetchone()
    if moder_role_id or admin_role_id not in author.roles:
        await ctx.send('{}, у вас нет права на использование этой команды!'.format(author.mention))
    else:
        sql.execute(f"SELECT logs_channel_id FROM Servers WHERE server_id = '{guild_id}'")
        id_channel = sql.fetchone()
        logs_channel = bot.get_channel(id_channel[0])
        try:
            banned = await member.guild.fetch_ban(member)
        except discord.NotFound:
            banned = False
        if banned:
            await ctx.send('Этот пользователь уже забанен!')
            await asyncio.sleep(time_to_dlt_msgs)
            await ctx.message.delete()
        else:
            await ctx.guild.ban(user=member, reason=reason)
            await ctx.send("Пользователь {} был забанен модератором {} на {} секунд. Причина: {}".format(
                member.mention, ctx.author.mention, time, reason))
            await logs_channel_id.send("Пользователь {} был забанен модератором {} на {} секунд. Причина: {}".format(
                member.mention, ctx.author.mention, time, reason))
            await member.send(embed=discord.Embed(title='Вы были забанены на сервере {}'.format(server_name),
                                                  description='Модератор: {} \n'
                                                              'Причина: {} \n'
                                                              'Время: {}'.format(ctx.author.mention, reason, time)))
            await ctx.guild.ban(user=member, reason=reason)
            await asyncio.sleep(time_to_dlt_msgs)
            await ctx.message.delete()
            await asyncio.sleep(time - time_to_dlt_msgs)
            try:
                banned = await member.guild.fetch_ban(member)
            except discord.NotFound:
                banned = False
            if banned:
                guild = bot.get_guild(ctx.guild.id)
                invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=1, temporary=False)
                btns = [
                    create_button(style=ButtonStyle.URL, label="Вернуться на сервер!",
                                  url='https://discord.gg/{}'.format(invite.code))]
                row = create_actionrow(*btns)
                await member.unban(reason=None)
                await logs_channel.send("Пользователь {} был разбанен. Причина: время бана закончилось.".format(member))
                await member.send(embed=discord.Embed(title='Вы разбанены по истечению времени.',
                                                      description='Сервер: {}'.format(server_name),
                                                      components=[row]))
                await member.send(components=[row])
            else:
                pass


# kick (готово)
@slash.slash(name="kick",
             description="Кикает пользователя с сервера",
             guild_ids=servers_ids,
             options=[
                 create_option(
                     name="member",
                     description="Введите имя пользователя",
                     required=True,
                     option_type=6),
                 create_option(
                     name="reason",
                     description="Введите причину",
                     required=True,
                     option_type=3
                 )
             ])
async def _kick(ctx: SlashContext, member: discord.Member, reason: str):
    guild = bot.get_guild(ctx.guild.id)
    author = ctx.author
    sql.execute("SELECT moderator_role_id FROM Servers WHERE server_id = '{guild_id}'")
    moder_role_id = sql.fetchone()
    sql.execute("SELECT admin_role_id FROM Servers WHERE server_id = '{guild_id}'")
    admin_role_id = sql.fetchone()
    if moder_role_id or admin_role_id not in author.roles:
        await ctx.send('{}, у вас нет права на использование этой команды!'.format(author.mention))
    else:
        guild_id = bot.get_guild(ctx.guild.id)
        sql.execute(f"SELECT logs_channel_id From Servers WHERE server_id = '{guild_id}'")
        id_channel = sql.fetchone()
        logs_channel = bot.get_channel(id_channel[0])
        invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=1, temporary=False)
        btns = [
            create_button(style=ButtonStyle.URL, label="Вернуться на сервер!", url='https://discord.gg/{}'.format(
                invite.code))]
        row = create_actionrow(*btns)
        await member.send(embed=discord.Embed(title='{}, вы кикнуты с сервера {}'.format(member, server_name),
                                              description='Причина: {} \n Вы всегда сможете вернуться на сервер с '
                                                          'помощью кнопки.'.format(reason)))
        await ctx.send(
            'Модератор {} кикнул пользователя {}. Причина: {}'.format(ctx.author.mention, member.mention, reason))
        await logs_channel.send(
            'Модератор {} кикнул пользователя {}. Причина: {}'.format(ctx.author.mention, member.mention, reason))
        await member.send(components=[row])
        await member.kick(reason=reason)


#                   ЗАПУСК БОТА
bot.run(config.TOKEN)
