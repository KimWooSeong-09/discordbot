import discord
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

test = commands.Bot(command_prefix='/', intents=intents)

@test.event
async def on_ready():
    print(f'✅ 로그인됨: {test.user}')

# 1) /타이머 [분]
@test.command(name='타이머')
async def timer(ctx, minutes: int):
    await ctx.send(f'⏲️ {minutes}분 타이머 시작!')
    await asyncio.sleep(minutes * 60)
    await ctx.send(f'⏰ {minutes}분이 지났습니다!')

# 2~3) /노래 실행 [URL], /노래 정지
@test.group(name='노래')
async def music(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('```사용법:\n/노래 실행 [URL]\n/노래 정지```')

@music.command(name='실행')
async def play(ctx, url: str):
    if not ctx.author.voice:
        return await ctx.send('❌ 먼저 음성 채널에 들어가 있어야 해요.')
    channel = ctx.author.voice.channel
    vc = discord.utils.get(test.voice_clients, guild=ctx.guild)
    if not vc or not vc.is_connected():
        vc = await channel.connect()
    elif vc.channel != channel:
        await vc.move_to(channel)

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info.get('title', 'Unknown')

    vc.play(test.FFmpegPCMAudio(audio_url), after=lambda e: print('Player error:', e) if e else None)
    await ctx.send(f'▶️ 재생 시작: **{title}**')

@music.command(name='정지')
async def stop(ctx):
    vc = discord.utils.get(test.voice_clients, guild=ctx.guild)
    if vc and vc.is_playing():
        vc.stop()
        await vc.disconnect()
        await ctx.send('⏹️ 재생을 멈추고 연결을 종료했어요.')
    else:
        await ctx.send('⚠️ 현재 재생 중인 노래가 없어요.')


