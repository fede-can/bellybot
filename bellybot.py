import discord  # Imports discord library. This is an asynchronous library (things are done with callbacks)
import asyncio
from discord.ext import commands
from discord.ext.commands import BucketType

bot = commands.Bot(command_prefix="b!")


@bot.event  # This is used to register an event.
# [A CALLBACK is a function that is called when something else happens].
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:  # The bot won't do anything if the message is by ourselves.
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello! I am Belly')

    await bot.process_commands(message)


# THE TIMER STARTS HERE <<<<<<<<<<<<<<<<<<<<<<<<
def green_embed(text):
    return discord.Embed(description=text, color=0x23ddf1)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MaxConcurrencyReached):
        if ctx.author == discord.user:
            pass
        else:
            await ctx.send("There is a timer currently active in this channel.\nTry later.")
            return

    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Please choose any of the following values to set your timer: \n• Seconds: *30*"
                       f"\n• Minutes: *1*, *2*, *3*, *4* or *5* \nFor example: `;timer 5`.")
        return

    else:
        raise error


@commands.max_concurrency(1, BucketType.channel)
@bot.command()
async def timer(ctx, time_left=0):
    """Starts a countdown. The offset must be set to 30 seconds or 1, 2, 3, 4, 5 minutes. It will update the timer
    every 5 seconds."""
    time_left = int(time_left)
    if time_left not in [1, 2, 3, 4, 5, 30]:
        raise commands.BadArgument


    # When people call the command, this message tells them what the chosen time for the timer is and starts a short
    # countdown previous to the main one. For 30s:
    if time_left == 30:
        time_str = f"{time_left}s"
    else:
        time_str = f"{time_left}min"

    embed_1 = green_embed(f"The countdown of **{time_str}** set up by "
                          f"{ctx.author.mention} **will start in: 5s**.")
    msg_countdown = await ctx.send(embed=embed_1)

    for a in range(4, -1, -1):
        await asyncio.sleep(1)
        embed_2 = green_embed(f"The countdown of **{time_str}** set up by "
                              f"{ctx.author.mention} **will start in: {a}s**.")
        await msg_countdown.edit(embed=embed_2)

    await msg_countdown.add_reaction('❌')
    await msg_countdown.add_reaction('↩')
    await msg_countdown.add_reaction('🔟')

    def check_reactions(reaction: discord.Reaction, user: discord.User) -> bool:
        return str(reaction) in '❌↩🔟' \
               and user.id == ctx.author.id \
               and reaction.message.id == msg_countdown.id

    time_left_backup = time_left

    # Countdown:
    aborted = False
    restarted = False
    added_seconds = False
    while time_left:  # I deleted the > 0 because when it eventually reaches zero that'll count as not "while time_left"
        mins, secs = divmod(time_left, 60)
        time_left_str = f"{mins}:{secs:02d}"
        if restarted:
            embed_text = f"The countdown of **30s** set up by {ctx.author.mention} **has been restarted**." \
                         f"\n\nTime left: `{time_left_str}`"
        elif added_seconds:
            embed_text = f"The countdown of **30s** set up by {ctx.author.mention} **is already running**!" \
                         f"\n\nTime left: `{time_left_str}`. Ten seconds added!"
        else:  # Normal operation
            embed_text = f"The countdown of **30s** set up by {ctx.author.mention} **is already running**!" \
                     f"\n\nTime left: `{time_left_str}`"

        embed_countdown = green_embed(embed_text)
        await msg_countdown.edit(embed=embed_countdown)

        try:
            reaction_added, user_react = await bot.wait_for("reaction_add", check=check_reactions, timeout=1)
        except asyncio.TimeoutError:
            time_left -= 1  # Restart loop
        else:
            if str(reaction_added) == '❌':
                aborted = True
                time_left = 0
            if str(reaction_added) == "↩":
                restarted = True
                time_left = time_left_backup
            if str(reaction_added) == "🔟":
                added_seconds = True
                time_left = time_left + 10

    if aborted:
        text_end = f"The countdown of **{time_str}** set up by {ctx.author.mention} **has been aborted**."
    else:
        text_end = f"The countdown of **{time_str}** set up by {ctx.author.mention} **has finished**!\n\nTime out!"

    embed_end = green_embed(text_end)
    await msg_countdown.edit(embed=embed_end)

    try:
        await msg_countdown.clear_reactions()
    except (discord.Forbidden, discord.NotFound):
        return


with open("APIKey.txt") as f:
    bot.run(f.read())
