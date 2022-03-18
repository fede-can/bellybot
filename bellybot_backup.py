import discord  # Imports discord library. This is an asynchronous library (things are done with callbacks)
import asyncio
from discord.ext import commands
from discord.ext.commands import BucketType

bot = commands.Bot(command_prefix="$")


@bot.event  # This is used to register an event.
# [A CALLBACK is a function that is called when something else happens].
async def on_ready():  # The 'on_ready()' event is called when the bot is ready to start being used.
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):  # When the bot receives a message the 'on_message()' event is called.
    if message.author == bot.user:  # The bot won't do anything if the message is by ourselves.
        return  # <- The code will return

    if message.content.startswith('$hello'):  # If message content starts with '$hello',
        await message.channel.send('Hello! I am Belly')  # the bot replies 'Hello!'.

    await bot.process_commands(message)


## STARTS THE TIMER <<<<<<<<<<<<<<<<<<<<<<<<
def green_embed(text):
    return discord.Embed(description=text, color=0x23ddf1)


@bot.command()
async def timer(ctx, time_left):
    """Starts a countdown. The offset must be set to 30 seconds or 1, 2, 3, 4, 5 minutes. It will update the timer
    every 5 seconds."""

    time_left = int(time_left)

    #   When people call the command, this message tells them what the chosen time for the timer is and starts a short
    #   countdown previous to the main one.
    if time_left == 30:
        embed_1 = green_embed(f"The countdown of **{time_left}s** set up by "
                              f"{ctx.author.mention} **will start in: 5s**.")
        timer_set_msg = await ctx.send(embed=embed_1)

        for a in range(4, -1, -1):
            await asyncio.sleep(1)
            embed_2 = green_embed(f"The countdown of **{time_left}s** set up by "
                                  f"{ctx.author.mention} **will start in: {a}s**.")
            await timer_set_msg.edit(embed=embed_2)

    elif time_left == 1 or time_left == 2 or time_left == 3 or time_left == 4 or time_left == 5:
        embed_1 = green_embed(f"The countdown of **{time_left}min** set up by "
                              f"{ctx.author.mention} **will start in: 5s**.")
        timer_set_msg = await ctx.send(embed=embed_1)

        for a in range(4, -1, -1):
            await asyncio.sleep(1)
            embed_2 = green_embed(f"The countdown of **{time_left}min** set up by "
                                  f"{ctx.author.mention} **will start in: {a}s**.")
            await timer_set_msg.edit(embed=embed_2)

        time_left = time_left * 60

    else:
        await ctx.send(f"Please choose any of the following values to set your timer: \n• Seconds: *30*"
                       f"\n• Minutes: *1*, *2*, *3*, *4* or *5* \nFor example: `;timer 5`.")
        return

    # Countdown:
    mins, secs = divmod(time_left, 60)
    timer = f"{mins}:{secs:02d}"
    embed_countdown = green_embed(f"Time left: `{timer}`")
    msg_countdown = await ctx.send(embed=embed_countdown)
    await asyncio.sleep(1)
    time_left -= 1
    await timer_set_msg.add_reaction('❌')
    await timer_set_msg.add_reaction('↩')
    await timer_set_msg.add_reaction('🔟')
    await timer_set_msg.add_reaction('🆓')

    while time_left > 0:
        mins, secs = divmod(time_left, 60)
        timer = f"{mins}:{secs:02d}"
        time_left -= 1
        embed_countdown = green_embed(f"Time left: `{timer}`")
        await msg_countdown.edit(embed=embed_countdown)
        await asyncio.sleep(1)

    embed_end = green_embed(f"Time out!")
    await msg_countdown.edit(embed=embed_end)



bot.run('OTUzMDY2NTgwMjAyMzU2NzM4.Yi_Kaw.5YC_uz3QANgWLgiR9BaJO6H9i0A')  # Bot token (Password).
