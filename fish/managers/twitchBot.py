from twitchio.ext import commands
from helpers.configurator import Config
from helpers.fishRewardsConfig import FishRewards

class TwitchBot(commands.Bot):
    def __init__(self):
        self.config = Config()
        args = {
            'token': self.config.token,
            'prefix': self.config.commandPrefix,
            'initial_channels': [self.config.username], 
        }

        super().__init__(**args)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown) & self.config.enableCooldownMsg:
         await ctx.send(f'Fishing is tiring man. Try again in {error.retry_after:.2f} seconds.')    

    @commands.command()
    @commands.cooldown(rate=1, per=600, bucket=commands.Bucket.user)
    async def fish(self, ctx: commands.Context):

        reward = FishRewards()
        print(reward)
        print(ctx.author.name)
        messages = self.message_builder(reward, ctx.author.name)
        await ctx.send(messages[0])
        await ctx.send(messages[1])


    @staticmethod
    def message_builder(fishReward: FishRewards, user: str):
        message = ["", ""]
        message[0] = fishReward.rewardsJSON["base_message"]
        message[0] = message[0].replace("$user", user)
        message[0] += fishReward.chosenReward["message"]
        if fishReward.chosenReward["cmd"] != "":
            message[1] = fishReward.chosenReward["cmd"]
            message[1] = message[1].replace("$user", user)
            match fishReward.chosenReward["type"]:
                case "points":
                    valstr = fishReward.chosenReward["value"]
                    message[1] = message[1].replace("$value", f"{valstr}")
                case "timeout":
                    valstr = fishReward.chosenReward["seconds"]
                    message[1] = message[1].replace("$timeout", f"{valstr}")

        return message

        