from twitchio.ext import commands
from twitchio import PartialUser, User
from fish.helpers.configurator import Config
from fish.helpers.fishRewardsConfig import FishRewards
from datetime import datetime
from fish.managers.streamelements_manager import StreamElementsManager
import fish.managers.rewardManager as RewardHandler
import fish.helpers.utils as Utils

class TwitchBot(commands.Bot):
    def __init__(self):
        self.config = Config()
        self.streamElements = StreamElementsManager(config=self.config)
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
        reward = FishRewards(
            chatterRole="sub" if ctx.author.is_subscriber else "unsub", 
            rewardsFilePath=rewardsFilePath
        )
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print(f"{current_date} {ctx.author.name} fished! on {ctx.channel.name} channel")
        await RewardHandler.handle_reward(reward, ctx, self.config.token, self.streamElements)


    @commands.command()
    @commands.cooldown(rate=1, per=10, bucket=commands.Bucket.member)
    async def fishrewards(self, ctx: commands.Context):
        rewardsFilePath = self.get_fish_rewards_file_path(ctx)
        reward = FishRewards(chatterRole="sub" if ctx.author.is_subscriber else "unsub", rewardsFilePath=rewardsFilePath)
        messages = []
        messages = Utils.generate_reward_strings(reward.get_probabilities())
        message = ""
        for msg in messages:
            message += msg
            message += " "
        chunks = [message[i:i+255] for i in range(0, len(message), 255)]
        for chunk in chunks:
            await ctx.send(chunk)
           
    
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