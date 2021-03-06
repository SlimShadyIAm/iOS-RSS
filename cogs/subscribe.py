import asyncio
from os import path
from os.path import abspath, dirname
import sqlite3
import sys
import traceback

import discord
from discord import Color, Embed
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='subscribe')
    @commands.has_permissions(manage_guild=True)
    async def subscribe(self, ctx, device: str, role_to_ping: discord.Role = 0):
        """Subscribe to updates from a certain device/feed.\n
        Optionally, you can set a role to ping when an update is posted (see examples)
        Available devices: iOS, macOS, watchOS, iPadOS, tvOS, Newsroom (Apple's press releases)\n
        Updates will be sent to the channel set by the `.channel` command, if set.\n
        Example usage: `.subscribe ios rolename/role ID/@role` or `.subscribe ios`"""

        devices = {"ios": "iOS_role",
                   "macos": "macOS_role",
                   "watchos": "watchOS_role",
                   "ipados": "iPadOS_role",
                   "tvos": "tvOS_role",
                   "newsroom": "newsroom_role"
                   }

        devices_proper = {"ios": "iOS",
                          "macos": "macOS",
                          "watchos": "watchOS",
                          "ipados": "iPadOS",
                          "tvos": "tvOS",
                          "newsroom": "Newsroom"
                          }
        device = device.lower()

        if device not in devices.keys():
            raise commands.BadArgument(
                "Please supply a valid device/feed to subscribe to.\nAvailable devices: iOS, macOS, watchOS, iPadOS, tvOS, Newsroom\n i.e `!subscribe macos`.")

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
                c.execute(f"UPDATE configs SET {devices[device]} = ? WHERE server_id = ?;", ((
                    role_to_ping if role_to_ping == 0 else role_to_ping.id), ctx.guild.id,))
                conn.commit()
            finally:
                conn.close()

            embed = Embed(title="Done!", color=Color(
                value=0x37b83b), description=f'You have subscribed to {devices_proper[device]} notifications.')
            embed.set_footer(
                text=f'Requested by {ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)

            if role_to_ping != 0:
                if role_to_ping.is_default():
                    role_to_ping = "@everyone"

                embed.add_field(
                    name="Role pings", value=f"We will ping {role_to_ping.mention if isinstance(role_to_ping, discord.Role) else role_to_ping} when there is a new update. If you don't want to ping a role, use `.subscribe devicename` with no role.", inline=False)
            else:
                embed.add_field(
                    name="Role pings", value=f"We will not ping any role when there is a new update. If you want me to ping a role, use `.subscribe devicename rolename`", inline=False)

            if res[0][6] == -1:
                embed.add_field(
                    name="Warning!", value="You haven't chosen a channel to send updates to. Please set one using `!channel set #channelname`", inline=False)
            else:
                channel = discord.utils.get(ctx.guild.channels, id=res[0][6])
                if channel is not None:
                    embed.add_field(
                        name="Channel", value=f"Updates will be posted in {channel.mention}. Change this using `.channel set #channelname`", inline=False)
                else:
                    embed.add_field(
                        name="Warning!", value="An invalid channel has been set for updates! Please set one using `!channel set #channelname`", inline=False)

            await ctx.send(embed=embed)
            return
        await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'An unforseen error occured, contact SlimShadyIAm#9999 (code: DB_SUBSCRIBE_ERR'))
    # err handling

    @subscribe.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error} If you are trying to use a role with spaces, put the name in quotes or mention it (`@role name`).'))
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=Embed(title="An error occured!", color=Color(value=0xEB4634), description=f'{error}. See `.help subscribe` if you need help.'))
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
