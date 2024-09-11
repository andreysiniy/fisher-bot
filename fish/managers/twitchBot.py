from twitchio.ext import commands
from helpers.configurator import Config
from helpers.fishRewardsConfig import FishRewards
import helpers.utils as Utils

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
    @commands.cooldown(rate=1, per=300, bucket=commands.Bucket.subscriber) # does not work how intended 
    async def fish(self, ctx: commands.Context):
        reward = FishRewards(chatterRole="sub" if ctx.author.is_subscriber else "unsub")
        print(reward)
        print(ctx.author.name)
        messages = self.message_builder(reward, ctx.author.name)
        print(messages[1])
        await ctx.send(messages[0])
        await ctx.send(messages[1])

    @staticmethod
    def message_builder(fishReward: FishRewards, user: str):
        message = ["", ""]
        valueMsg = 0
        minutesMsg = 0         
        message[0] = fishReward.rewardsJSON["base_message"].format(username = user) 
        if fishReward.chosenReward["type"] == "points":
            message[1] = fishReward.chosenReward["cmd"].format(username = user, value = fishReward.chosenReward["value"])
            valueMsg = Utils.format_number(fishReward.chosenReward["value"] / 1000)    
        elif fishReward.chosenReward["type"] == "timeout":
            message[1] = fishReward.chosenReward["cmd"].format(username = user) # !timeout 
            minutesMsg = Utils.format_number(fishReward.chosenReward["seconds"] / 60)
        message[0] += fishReward.chosenReward["message"].format(username = user, value = valueMsg, minutes = minutesMsg)
        print(message[0])
        return message