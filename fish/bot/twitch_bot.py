from twitchio.ext import commands
from twitchio import PartialUser, User
from fish.helpers.configurator import Config
from fish.helpers.fish_rewards import FishRewards
from datetime import datetime
from fish.managers.streamelements_manager import StreamElementsManager
import fish.managers.reward_manager as RewardHandler
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
    @commands.cooldown(rate=1, per=420, bucket=commands.Bucket.member)
    async def fish(self, ctx: commands.Context):
        rewardsFilePath = Utils.get_fish_rewards_file_path(ctx)
        print(f"Rewards file path: {rewardsFilePath}")
        reward = FishRewards(
            chatterRole="sub" if ctx.author.is_subscriber else "unsub", 
            rewardsFilePath=rewardsFilePath,
            username=ctx.author.name,
            channel_name=ctx.channel.name
        )
        if (reward.chatterRole == "sub"):
            cooldown = reward.rewardsJSON.get("sub_cooldown", 1000)
        else:
            cooldown = reward.rewardsJSON.get("base_cooldown", 1000)
        Utils.set_command_cooldown(ctx, cooldown)
        reward.chosenReward = reward.choose_default_reward()
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print(f"{current_date} {ctx.author.name} fished! on {ctx.channel.name} channel")
        print(f"User {ctx.author.name} cooldown is {Utils.format_time(cooldown)}")
        await RewardHandler.handle_reward(reward, ctx, self.config.token, self.streamElements)
        print(f"------ {ctx.author.name} finished fishing on {ctx.channel.name} channel! ------")


    @commands.command()
    @commands.cooldown(rate=1, per=10, bucket=commands.Bucket.member)
    async def fishrewards(self, ctx: commands.Context):
        rewardsFilePath = Utils.get_fish_rewards_file_path(ctx)
        reward = FishRewards(chatterRole="sub" if ctx.author.is_subscriber else "unsub", rewardsFilePath=rewardsFilePath, username=ctx.author.name, channel_name=ctx.channel.name)
        messages = []
        messages = Utils.generate_reward_strings(reward.get_probabilities())
        message = ""
        for msg in messages:
            message += msg
            message += " "
        chunks = []
        current_pos = 0
        while current_pos < len(message):
            end_pos = current_pos + 500
            if end_pos >= len(message):
                chunks.append(message[current_pos:])
                break
            split_pos = message.rfind(' ', current_pos, end_pos)
            if split_pos == -1 or split_pos <= current_pos:
                actual_end = end_pos
            else:
                actual_end = split_pos   
            chunk = message[current_pos:actual_end]
            chunks.append(chunk)
            current_pos = actual_end + 1 if actual_end == split_pos else actual_end 
        
        for chunk_part in chunks:
            await ctx.send(chunk_part)
           
    
    @commands.command()
    async def fishcooldown(self, ctx: commands.Context):
        rewards_path = Utils.get_fish_rewards_file_path(ctx)
        reward = FishRewards(chatterRole="sub" if ctx.author.is_subscriber else "unsub", rewardsFilePath=rewards_path, username=ctx.author.name, channel_name=ctx.channel.name)
        if reward.chatterRole == "sub":
            cooldown = reward.rewardsJSON.get("sub_cooldown", 1000)
        else:
            cooldown = reward.rewardsJSON.get("base_cooldown", 1000)
        cooldown_left = Utils.get_command_cooldown(self._commands['fish'], ctx, cooldown)
        if (cooldown_left == 0):
            await ctx.send(f"Fish cooldown for user {ctx.author.name} is {Utils.format_time(cooldown)} (fishing is ready!)")
        else:
            await ctx.send(f"Fish cooldown for user {ctx.author.name} is {Utils.format_time(cooldown)} ({Utils.format_time(cooldown_left)} left)")
        