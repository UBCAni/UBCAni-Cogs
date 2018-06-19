import discord
import operator

from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os

def check_folders():
    if not os.path.exists("data/UBCAniCogs/auction"):
        print("Creating data/UBCAniCogs/auction folder...")
        os.makedirs("data/UBCAniCogs/auction")

def check_files():
    f = "data/UBCAniCogs/auction/auction.json"
    if not dataIO.is_valid_json(f):
        print("Creating default auction.json...")
        dataIO.save_json(f, {})

class Auction:
    """Allows auctioning functions"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/UBCAniCogs/auction/auction.json"
        self.data = dataIO.load_json(self.file_path)

    @commands.group(pass_context=True, no_pm=True)
    async def auction(self, ctx):
        """Auctioning group of commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @auction.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def open(self, ctx):
        """Opens the auction"""
        if "open" not in self.data:
            self.data["open"] = True

        self.data["open"] = True
        dataIO.save_json(self.file_path, self.data)

        await self.bot.say("The auction is now open")

    @auction.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def close(self, ctx):
        """Closes the auction"""
        if "open" not in self.data:
            self.data["open"] = False

        self.data["open"] = False
        dataIO.save_json(self.file_path, self.data)

        await self.bot.say("The auction is now closed")

    @auction.command(pass_context=True, no_pm=True)
    async def bid(self, ctx, amount : int, user : discord.Member = None):
        """Place a bid on another user"""
        if await self._is_open(ctx):
            await self._bid(ctx, amount, user)

    async def _bid(self, ctx, amount, user):

        author = ctx.message.author
        server = ctx.message.server
        bank = self.bot.get_cog("Economy").bank

        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.file_path, self.data)

        if user is None:
            user = author

        if amount == 0:
            return await self.bot.say("The amount must be non-zero")

        if bank.account_exists(author):
            server_data = self.data[server.id]

            if amount < 0:
                if user.id not in server_data or author.id not in server_data[user.id]:
                    if user.id == author.id:
                        return await self.bot.say("You have not bid on behalf of yourself")
                    else:
                        return await self.bot.say("You have not bid on behalf of the other user")

                removed_amount = abs(amount)
                if removed_amount > server_data[user.id][author.id]:
                    return await self.bot.say("You cannot decrease your bid by more than {} credits".format(server_data[user.id][author.id]))

                server_data[user.id][author.id] -= removed_amount
                bank.deposit_credits(author, removed_amount)

                dataIO.save_json(self.file_path, self.data)

                return await self.bot.say("{} credits removed from the bid. The total bid pool is now {}".format(removed_amount, sum(server_data[user.id].values())))
            else:
                if not bank.can_spend(author, amount):
                    return await self.bot.say("Your bank account has insufficient funds")

                if user.id not in server_data:
                    server_data[user.id] = {}
                if author.id not in server_data[user.id]:
                    server_data[user.id][author.id] = 0

                server_data[user.id][author.id] += amount
                bank.withdraw_credits(author, amount)

                dataIO.save_json(self.file_path, self.data)

                return await self.bot.say("{} credits added to the bid. The total bid pool is now {}".format(amount, sum(server_data[user.id].values())))
        else:
            return await self.bot.say("Your bank account has insufficient funds")

    @auction.command(pass_context=True, no_pm=True)
    async def bids(self, ctx, user : discord.Member = None):
        """Lists all the bids made by either the specified user, or the author of the message if empty"""

        author = ctx.message.author
        server = ctx.message.server

        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.file_path, self.data)

        if user is None:
            user = author

        bids = self._get_bids(server, user)

        if len(bids) == 0:
            if author.id == user.id:
                return await self.bot.say("No bids were placed by you")
            else:
                return await self.bot.say("No bids were placed by {}".format(user.name))

        results = []

        for key, value in bids.items():
            member = discord.utils.get(ctx.message.server.members, id=key)
            results.append("{}: {}".format(member.name, value))

        await self.bot.say("```\n{}\n```".format('\n'.join(results)))

    @auction.command(pass_context=True, no_pm=True)
    async def resetbid(self, ctx):
        """Resets all bids made by the current user, returning all the credits to the bank"""
        if await self._is_open(ctx):
            server = ctx.message.server
            author = ctx.message.author
            bank = self.bot.get_cog("Economy").bank

            if server.id not in self.data:
                self.data[server.id] = {}
                dataIO.save_json(self.file_path, self.data)

            returned_amounts = self._reset(server, ctx.message.author)

            if len(returned_amounts) == 0:
                return await self.bot.say("No bids were placed, so nothing was withdrawn for you")

            await self.bot.say("The total amount withdrawn is {}".format(sum(returned_amounts.values())))

            results = []

            for key, value in returned_amounts.items():
                member = discord.utils.get(ctx.message.server.members, id=key)
                results.append("{} credits withdrawn from bid on {}".format(value, member.name))
                bank.deposit_credits(author, value)

            dataIO.save_json(self.file_path, self.data)
            await self.bot.say("```\n{}\n```".format('\n'.join(results)))

    @auction.command(pass_context=True, no_pm=True)
    async def score(self, ctx, limit=5):
        """Shows the current top 5 bidders"""
        server = ctx.message.server

        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.file_path, self.data)

        leaderboard = self._get_leaderboard(server, limit)

        if len(leaderboard) == 0:
            return await self.bot.say("The leaderboard is empty")

        rank = 0
        results = []

        for (key, value) in leaderboard:
            rank += 1
            member = discord.utils.get(ctx.message.server.members, id=key)
            results.append("{}. {}: {}".format(rank, member.name, value))

        await self.bot.say("```\n{}\n```".format('\n'.join(results)))

    @auction.command(name="raise", pass_context=True, no_pm=True)
    async def raise_bid(self, ctx, amount = 100, user : discord.Member = None):
        """Raises the bid on either the specified user or the author to the current highest bid, plus some"""
        if await self._is_open(ctx):
            author = ctx.message.author
            server = ctx.message.server
            bank = self.bot.get_cog("Economy").bank

            if user is None:
                user = author

            if server.id not in self.data:
                self.data[server.id] = {}
                dataIO.save_json(self.file_path, self.data)

            if user.id not in self.data[server.id]:
                self.data[server.id][user.id] = {}
                dataIO.save_json(self.file_path, self.data)

            leaderboard = self._get_leaderboard(server)

            raise_from = 0

            if len(leaderboard) != 0:
                (member, top) = leaderboard[0]
                raise_from = top

            delta = raise_from - sum(self.data[server.id][user.id].values()) + amount

            await self._bid(ctx, delta, user)

    @auction.command(pass_context=True, no_pm=True)
    async def bidders(self, ctx, user : discord.Member = None):
        """Shows the current top 5 bidders"""
        
        server = ctx.message.server

        if user is None:
            user = author

        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.file_path, self.data)

        if user.id not in self.data[server.id]:
            self.data[server.id][user.id] = {}
            dataIO.save_json(self.file_path, self.data)

        server_data = self.data[server.id]

        bidders = server_data[user.id]

        results = []

        for (key, value) in bidders.items():
            member = discord.utils.get(ctx.message.server.members, id=key)
            results.append("{}: {}".format(member.name, value))

        await self.bot.say("```\n{}\n```".format('\n'.join(results)))

    @auction.command(pass_context=True, no_pm=True)
    async def allin(self, ctx, user : discord.Member = None):
        if await self._is_open(ctx):
            author = ctx.message.author
            server = ctx.message.server
            bank = self.bot.get_cog("Economy").bank

            if user is None:
                user = author

            if server.id not in self.data:
                self.data[server.id] = {}
                dataIO.save_json(self.file_path, self.data)

            if user.id not in self.data[server.id]:
                self.data[server.id][user.id] = {}
                dataIO.save_json(self.file_path, self.data)

            amount = bank.get_balance(author)

            await self._bid(ctx, amount, user)

    @auction.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def ubi(self, ctx, amount = 50000):
        if await self._is_open(ctx):
            author = ctx.message.author
            server = ctx.message.server
            bank = self.bot.get_cog("Economy").bank

            if server.id not in self.data:
                self.data[server.id] = {}
                dataIO.save_json(self.file_path, self.data)

            results = []

            accs = bank.get_server_accounts(server)
            for acc in accs:
                member = discord.utils.get(ctx.message.server.members, id=acc.id)
                bank.deposit_credits(member, amount)
                results.append("{}: {}".format(member.name, amount))

            await self.bot.say("```\n{}\n```".format('\n'.join(results)))
        
    async def _is_open(self, ctx):
        if "open" not in self.data:
            self.data["open"] = False
            dataIO.save_json(self.file_path, self.data)

        if not self.data["open"]:
            await self.bot.say("The auction is currently not open")

        return self.data["open"]

    def _reset(self, server, user):
        """Resets all of the user's bids on others to 0, and returns a dictionary where the keys are the original users and the values are the removed amounts"""

        bids = self._get_bids(server, user)

        server_data = self.data[server.id]

        for user_bid_on, amounts in server_data.items():
            if user.id in amounts:
                del amounts[user.id]

        return bids

    def _get_bids(self, server, user):
        """Retrieves a dict of bids placed by the user, where the key is on who and the value is the amount bid"""

        server_data = self.data[server.id]

        ret = {}

        for user_bid_on, amounts in server_data.items():
            if user.id in amounts:
                ret[user_bid_on] = amounts[user.id]

        return ret

    def _get_leaderboard(self, server, limit = 5):
        """Retrieves a sorted list of tuples (member id, amount) to show users with the highest bids so far"""

        server_data = self.data[server.id]

        ret = {}

        for user_bid_on, amounts in server_data.items():
            ret[user_bid_on] = sum(amounts.values())

        scores = sorted(ret.items(), key=operator.itemgetter(1), reverse=True)

        return scores[:limit]


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Auction(bot))
