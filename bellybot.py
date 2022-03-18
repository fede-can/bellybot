import discord  # Imports discord library. This is an asynchronous library (things are done with callbacks)
import asyncio
from discord.ext import commands
from discord.ext.commands import BucketType

bot = commands.Bot(command_prefix="b!")


@bot.event  # This is used to register an event.
# [A CALLBACK is a function that is called when something else happens].
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


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
    else:
        raise error


@commands.max_concurrency(1, BucketType.channel)
@bot.command()
async def timer(ctx, time_left=0):
    """Starts a countdown. The offset must be set to 30 seconds or 1, 2, 3, 4, 5 minutes. It will update the timer
    every 5 seconds."""
    status = 0

    try:
        time_left = int(time_left)
        if time_left not in [1, 2, 3, 4, 5, 30]:
            raise ValueError
    except ValueError:
        await ctx.send(f"Please choose any of the following values to set your timer: \n• Seconds: *30*"
                       f"\n• Minutes: *1*, *2*, *3*, *4* or *5* \nFor example: `;timer 5`.")
        return

    # Defining the reaction functions
    # Ending the timer function:

    async def end_timer():
        if general_status == 0:
            embed_abort_timer = green_embed(f"The countdown of **30s** set up by "
                                            f"{ctx.author.mention} **has been aborted**.")
        if general_status == 1:
            embed_abort_timer = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                            f"{ctx.author.mention} **has been aborted**.")
        await msg_countdown.edit(embed=embed_abort_timer)
        try:
            await msg_countdown.clear_reactions()
        except (discord.Forbidden, discord.NotFound):
            return
        return

    # Restarting the timer function:
    async def restart_timer():
        if general_status == 0:
            embed_countdown = green_embed(f"The countdown of **30s** set up by "
                                          f"{ctx.author.mention} **has been restarted**."
                                          f"\n\nTime left: `{timer}`")
        if general_status == 1:
            embed_countdown = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                          f"{ctx.author.mention} **has been restarted**."
                                          f"\n\nTime left: `{timer}`")
        await msg_countdown.edit(embed=embed_countdown)

        try:
            await msg_countdown.clear_reaction('↩')
            await msg_countdown.clear_reaction('🔟')
        except (discord.Forbidden, discord.NotFound):
            pass

    # Adding 10 seconds to the timer:
    async def add_seconds():
        if general_status == 0:
            embed_countdown = green_embed(f"The countdown of **30s** set up by "
                                          f"{ctx.author.mention} **is already running**!"
                                          f"\n\nTime left: `{timer}`. Ten seconds added!")
        if general_status == 1:
            embed_countdown = green_embed(f"The countdown of {chosen_time_min} set up by "
                                          f"{ctx.author.mention} **is already running**!"
                                          f"\n\nTime left: `{timer}`. Ten seconds added!")
        await msg_countdown.edit(embed=embed_countdown)

        try:
            await msg_countdown.clear_reaction('↩')
            await msg_countdown.clear_reaction('🔟')
        except (discord.Forbidden, discord.NotFound):
            pass

    # When people call the command, this message tells them what the chosen time for the timer is and starts a short
    # countdown previous to the main one. For 30s:
    if time_left == 30:
        general_status = 0
        embed_1 = green_embed(f"The countdown of **{time_left}s** set up by "
                              f"{ctx.author.mention} **will start in: 5s**.")
        msg_countdown = await ctx.send(embed=embed_1)

        for a in range(4, -1, -1):
            await asyncio.sleep(1)
            embed_2 = green_embed(f"The countdown of **{time_left}s** set up by "
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
        mins, secs = divmod(time_left, 60)
        timer = f"{mins}:{secs:02d}"
        embed_countdown = green_embed(f"The countdown of **30s** set up by "
                                      f"{ctx.author.mention} **is already running**!"
                                      f"\n\nTime left: `{timer}`")
        await msg_countdown.edit(embed=embed_countdown)
        await asyncio.sleep(1)
        time_left -= 1

        while time_left > 0:
            mins, secs = divmod(time_left, 60)
            timer = f"{mins}:{secs:02d}"
            time_left -= 1
            if status == 0:
                embed_countdown = green_embed(f"The countdown of **30s** set up by "
                                              f"{ctx.author.mention} **is already running**!"
                                              f"\n\nTime left: `{timer}`")
            if status == 1:
                embed_countdown = green_embed(f"The countdown of **30s** set up by "
                                              f"{ctx.author.mention} **has been restarted**."
                                              f"\n\nTime left: `{timer}`")
            if status == 2:
                embed_countdown = green_embed(f"The countdown of **30s** set up by "
                                              f"{ctx.author.mention} **is already running**!"
                                              f"\n\nTime left: `{timer}`. Ten seconds added!")
            await msg_countdown.edit(embed=embed_countdown)

            try:
                reaction_added, user_react = await bot.wait_for("reaction_add", check=check_reactions, timeout=1)
            except asyncio.TimeoutError:
                pass
            else:
                if str(reaction_added) == '❌':
                    await end_timer()
                    return
                if str(reaction_added) == "↩":
                    status = 1
                    time_left = time_left_backup
                    await restart_timer()
                if str(reaction_added) == "🔟":
                    status = 2
                    time_left = time_left + 10
                    await add_seconds()

        embed_end = green_embed(f"The countdown of **30s** set up by "
                                f"{ctx.author.mention} **has finished**!"
                                f"\n\nTime out!")
        await msg_countdown.edit(embed=embed_end)
        try:
            await msg_countdown.clear_reactions()
        except (discord.Forbidden, discord.NotFound):
            return
        return

    # When people call the command, this message tells them what the chosen time for the timer is and starts a short
    # countdown previous to the main one. For 1,2,3,4,5 minutes:
    elif time_left == 1 or time_left == 2 or time_left == 3 or time_left == 4 or time_left == 5:
        general_status = 1
        embed_1 = green_embed(f"The countdown of **{time_left}min** set up by "
                              f"{ctx.author.mention} **will start in: 5s**.")
        msg_countdown = await ctx.send(embed=embed_1)

        for a in range(4, -1, -1):
            await asyncio.sleep(1)
            embed_2 = green_embed(f"The countdown of **{time_left}min** set up by "
                                  f"{ctx.author.mention} **will start in: {a}s**.")
            await msg_countdown.edit(embed=embed_2)

        chosen_time_min = time_left
        time_left = time_left * 60
        chosen_time_sec = time_left

        await msg_countdown.add_reaction('❌')
        await msg_countdown.add_reaction('↩')
        await msg_countdown.add_reaction('🔟')

        def check_reactions(reaction: discord.Reaction, user: discord.User) -> bool:
            return str(reaction) in '❌↩🔟' \
                   and user.id == ctx.author.id \
                   and reaction.message.id == msg_countdown.id

        # Countdown:
        mins, secs = divmod(time_left, 60)
        timer = f"{mins}:{secs:02d}"
        embed_countdown = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                      f"{ctx.author.mention} **is already running**!"
                                      f"\n\nTime left: `{timer}`")
        await msg_countdown.edit(embed=embed_countdown)
        await asyncio.sleep(1)
        time_left -= 1

        while time_left > 0:
            mins, secs = divmod(time_left, 60)
            timer = f"{mins}:{secs:02d}"
            time_left -= 1

            if status == 0:
                embed_countdown = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                              f"{ctx.author.mention} **is already running**!"
                                              f"\n\nTime left: `{timer}`")
            if status == 1:
                embed_countdown = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                              f"{ctx.author.mention} **has been restarted**."
                                              f"\n\nTime left: `{timer}`")
            if status == 2:
                embed_countdown = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                              f"{ctx.author.mention} **is already running**!"
                                              f"\n\nTime left: `{timer}`. Ten seconds added!")
            await msg_countdown.edit(embed=embed_countdown)
            try:
                reaction_added, user_react = await bot.wait_for("reaction_add", check=check_reactions, timeout=1)
            except asyncio.TimeoutError:
                pass
            else:
                if str(reaction_added) == '❌':
                    await end_timer()
                    return
                if str(reaction_added) == "↩":
                    status = 1
                    time_left = chosen_time_sec
                    await restart_timer()
                if str(reaction_added) == "🔟":
                    status = 2
                    time_left = time_left + 10
                    await add_seconds()

        embed_end = green_embed(f"The countdown of **{chosen_time_min}min** set up by "
                                f"{ctx.author.mention} **has finished**!"
                                f"\n\nTime out!")
        await msg_countdown.edit(embed=embed_end)
        try:
            await msg_countdown.clear_reactions()
        except (discord.Forbidden, discord.NotFound):
            return
        return

    # If the value added isn't 30, 1, 2, 3, 4 or 5 it will return this and end the function:
    else:
        await ctx.send(f"Please choose any of the following values to set your timer: \n• Seconds: *30*"
                       f"\n• Minutes: *1*, *2*, *3*, *4* or *5* \nFor example: `;timer 5`")
        return


with open("APIKey.txt") as f:
    bot.run(f.read())
