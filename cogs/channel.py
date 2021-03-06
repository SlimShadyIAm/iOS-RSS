import asyncio
import sqlite3
import sys
import traceback
from os import path
from os.path import abspath, dirname

import discord
from discord import Color, Embed
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='channel')
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, action: str, channel: discord.TextChannel = None):
        """Choose where updates go to, or stop updates.\nExample usage: `.channel set #general` or `.channel unset`"""

        action = action.lower()
        if action != "set" and action != "unset":
            raise commands.BadArgument(
                "Argument `action` must be 'set' or 'unset'!, i.e `.channel set #general` or `.channel unset`")

        # ensure user passed in argument
        if action == "set" and channel is None:
            raise commands.BadArgument(
                "Please supply a channel, i.e `.channel set #general`!")

        if action == "set":
            me = discord.utils.get(ctx.guild.members, id=self.bot.user.id)
            if not channel.permissions_for(me).send_messages:
                await ctx.send(embed=Embed(title="Warning", color=Color(value=0xeba64d), description=f"I don't have permission to speak in {channel.mention}"))

        BASE_DIR = dirname(dirname(abspath(__file__)))
        db_path = path.join(BASE_DIR, "db.sqlite")
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM configs WHERE server_id = ?;",
                      (ctx.guild.id,))
            res = c.fetchall()
        finally:
            conn.close()

        if len(res) == 1:
            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("UPDATE configs SET logging_channel = ? WHERE server_id = ?;",
                          (-1 if action == "unset" else channel.id, ctx.guild.id))
                conn.commit()
            finally:
                conn.close()

            if action == "set":
                await ctx.send(embed=Embed(title="Done!", color=Color(value=0x37b83b), description=f'All update notifications will go to {channel.mention}').set_footer(text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url))
            else:
                await ctx.send(embed=Embed(title="Done!", color=Color(value=0x37b83b), description=f'Updates will no longer be sent anywhere.').set_footer(text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url))
            return

        await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'An unforseen error occured, contact SlimShadyIAm#9999 (code: DB_CHANNEL_SET_ERR'))

    # err handling
    @channel.error
    async def channel_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}'))
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}. See `.help channel` if you need help.'))
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description="You need `MANAGE_SERVER` permission to run this command."))
            return
        else:
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}. Send a screenshot of this error to SlimShadyIAm#9999'))
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
            return


def setup(bot):
    bot.add_cog(Utilities(bot))
