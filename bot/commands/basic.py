import discord
from discord.ext import commands

class BasicCommands(commands.Cog):
    """Basic utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='hello')
    async def hello(self, ctx):
        """Simple hello command to test the bot"""
        await ctx.send(f'Hello {ctx.author.mention}! 👋')
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! 🏓 Latency: {latency}ms')
    
    @commands.command(name='myid')
    async def my_id(self, ctx):
        """Get your Discord user ID"""
        await ctx.send(f'Your Discord ID is: `{ctx.author.id}`')
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show available commands"""
        commands_list = []
        for command in self.bot.commands:
            if command.help:
                commands_list.append(f'**!{command.name}** - {command.help}')
            else:
                commands_list.append(f'**!{command.name}**')
        
        embed = discord.Embed(
            title="📋 Available Commands",
            description="\n".join(commands_list),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Use {self.bot.command_prefix}<command> to execute")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))