import discord
from discord.ext import commands
from pymongo import MongoClient
import tictactoe
import random
from KEY import *
import asyncio
from random_word import RandomWords
from PyDictionary import PyDictionary


client = MongoClient("mongodb://localhost:27017/")
db = client["bot-data"]
games_leaderboard = db["games"]

d = PyDictionary()
r = RandomWords()

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def ttt(self, ctx, opponent: discord.Member=None, bet: int=None):
        if opponent == ctx.message.author:
            return await ctx.send("you fucking moron, trying to play with yourself.")
        out = ""
        board = tictactoe.initial_state()
        start = random.choice([tictactoe.X, tictactoe.O])
        original_message = await ctx.send(content=f"**New Game of Tictactoe** \n {ctx.author.mention} X vs {opponent.mention} O \n {out} \n {start} starts! (make a move for the board to appear)")

        def player1_check(m):
            if m.author == ctx.message.author and len(m.content.split()) == 2:
                return True
            
        def player2_check(m):
            if m.author == opponent and len(m.content.split()) == 2:
                return True

        while not tictactoe.terminal(board):
            if tictactoe.player(board, start) == tictactoe.X:
                try:
                    reply = await self.bot.wait_for('message', check=player1_check)
                    if not tictactoe.valid_action(tuple([int(i) for i in reply.content.split()]), board):
                        raise IndexError
                    coords = [int(i) for i in reply.content.split()]
                    board[coords[0]][coords[1]] = tictactoe.X
                except IndexError:
                    await ctx.send(f"{tictactoe.player(board, start)}, you've tried an invalid move")
                
                out = tictactoe.board_converter(board)
                await original_message.edit(content=out)
            elif tictactoe.player(board, start) == tictactoe.O:
                try:
                    reply = await self.bot.wait_for('message', check=player2_check)
                    if not tictactoe.valid_action(tuple([int(i) for i in reply.content.split()]), board):
                        raise IndexError
                    coords = [int(i) for i in reply.content.split()]
                    board[coords[0]][coords[1]] = tictactoe.O
                except IndexError:
                    await ctx.send(f"{tictactoe.player(board, start)}, you've tried an invalid move")
                out = tictactoe.board_converter(board)
                await original_message.edit(content=out)
        else:
            win_person = tictactoe.winner(board)
            if win_person is not None:
                games_leaderboard.update_one({"user":win_person}, {"$inc":{"wins":1}}, upsert=True)
            await ctx.send(f"game over, winner is {tictactoe.winner(board)}")

    @commands.command(name="guess")
    async def guess(self, ctx):
        await ctx.send(f"{ctx.author.mention}, check your DMs!")
        #wait_for checks
        def reply_check(m):
            if m.author == ctx.message.author and m.guild is None:
                return True

        def answer_check(m):
            nonlocal answer
            if m.author != ctx.message.author and m.content.lower() == answer_val.lower():
                return True

        await ctx.author.send("Send the word that everyone has to guess! Send 'plshelp' if you don't have a word.")
        try:
            answer = await self.bot.wait_for('message', check=reply_check, timeout=30)
            if answer.content == 'plshelp':
                await ctx.author.send("Note: the auto word picking thing may not always work (no word might be sent to the channel, incorrect meaning) etc so, dont blame me too much :(")
                try:
                    async with ctx.author.dm_channel.typing():
                        answer_val = r.get_random_word(hasDictionaryDef="true", maxLength=6)
                        clue_dict = d.meaning(answer_val)
                        answer_val = answer_val.lower()
                    clue_val = list(clue_dict.values())
                    await ctx.author.dm_channel.send(f"Chosen a word! The word is **{answer_val}**")
                except:
                    await ctx.author.send("whoops something fucked up. Starting the command again 😔....")
                    return await self.guess(ctx)
                await ctx.send(f"{ctx.author.mention} has chosen a word! Everyone has 1 minute to guess it.")
                await ctx.send(f"Clue - **{clue_val}**")
                try:
                    reply = await self.bot.wait_for('message', check=answer_check, timeout=60)
                except asyncio.TimeoutError:
                    return await ctx.send(f"Time up! No one guessed the word. The word was **{answer_val}**")
        
                games_leaderboard.update_one({"user":str(reply.author)}, {"$inc":{"wins":1}}, upsert=True)
                return await ctx.send(f"{reply.author.mention} got it right! The word was **{reply.content}**")

            else:
                await ctx.author.send("Send a clue for your word!")
                clue = await self.bot.wait_for('message', check=reply_check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.author.send("Time up!")
        
        await ctx.send(f"{ctx.author.mention} has chosen a word! Everyone has 1 minute to guess it.")
        answer_val = answer.content
        clue_val = clue.content
        await ctx.send(f"Clue - **{clue_val}**")

        try:
            reply = await self.bot.wait_for('message', check=answer_check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send(f"Time up! No one guessed the word. The word was **{answer_val}**")
        
        games_leaderboard.update_one({"user":str(reply.author)}, {"$inc":{"wins":1}}, upsert=True)
        return await ctx.send(f"{reply.author.mention} got it right! The word was **{reply.content}**")

    @commands.command(name="games-leaderboard", aliases=["g-lb", "glb", "g-top", "gtop", "games-top"])
    async def games_top(self, ctx):
        out = ""
        for i, j in enumerate(games_leaderboard.find({"$query":{}, "$orderby":{"wins":-1}})):
            out += f"{i+1}. {j['user']}  **{j['wins']}** wins\n"
        await ctx.send(out)
    

def setup(bot):
    bot.add_cog(Games(bot))