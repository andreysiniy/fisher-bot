from twitchio.ext import commands
from twitchio import PartialUser, User
from helpers.configurator import Config
from helpers.fishRewardsConfig import FishRewards
from datetime import datetime
import helpers.utils as Utils

class TwitchBot(commands.Bot):
    def __init__(self):
        self.config = Config()
        args = {
            'token': self.config.token,
            'prefix': self.config.commandPrefix,
            'initial_channels': self.config.username, 
        }

        super().__init__(**args)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown) & self.config.enableCooldownMsg:
         await ctx.send(f'Fishing is tiring man. Try again in {error.retry_after:.2f} seconds.')    

    @commands.command()
    @commands.cooldown(rate=1, per=600, bucket=commands.Bucket.member)
    async def fish(self, ctx: commands.Context):
        rewardsFilePath = self.get_fish_rewards_file_path(ctx)
        reward = FishRewards(chatterRole="sub" if ctx.author.is_subscriber else "unsub", rewardsFilePath=rewardsFilePath)
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print(f"{current_date} {ctx.author.name} fished!")
        messages = self.message_builder(reward, ctx.author.name)
        print(messages[1])
        if reward.chosenReward["type"] == "timeout":
            await self.timeout_reward(ctx=ctx, rew_duration=reward.chosenReward["seconds"])
        await ctx.send(messages[0])
        await ctx.send(messages[1])

    @commands.command()
    @commands.cooldown(rate=1, per=10, bucket=commands.Bucket.user)
    async def fishrewards(self, ctx: commands.Context):
        rewardsFilePath = self.get_fish_rewards_file_path(ctx)
        reward = FishRewards(chatterRole="sub" if ctx.author.is_subscriber else "unsub", rewardsFilePath=rewardsFilePath)
        messages = []
        messages = Utils.generate_reward_strings(reward.get_probabilities())
        message = ""
        for msg in messages:
            message += msg
            message += " "
        await ctx.send(message)
    
    async def timeout_reward(self, ctx, rew_duration):
        user = await ctx.channel.user()
        await user.timeout_user(token=self.config.token, moderator_id=ctx.bot.user_id, user_id=ctx.author.id, duration=rew_duration, reason=f"Nice catch!! {rew_duration} seconds timeout!!")
        

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
    
    @staticmethod
    def get_fish_rewards_file_path(ctx):
        rewardsFilePath = f"rewards/{ctx.channel.name}/fishRewards"
        if ctx.author.is_vip:
            rewardsFilePath += "_vip.json"
        elif ctx.author.is_mod | ctx.author.is_broadcaster:
            rewardsFilePath += "_mod.json"
        else:
            rewardsFilePath += ".json"
        return rewardsFilePath