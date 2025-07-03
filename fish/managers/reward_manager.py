
import fish.helpers.utils as Utils
import random
import asyncio
from fish.helpers.fish_rewards import FishRewards
from fish.helpers.user_state import add_unlocked_ids

class BaseRewardHandler:
    def __init__(self, reward, ctx, token, streamelements):
        self.reward = reward
        self.ctx = ctx
        self.token = token
        self.streamelements = streamelements

    async def handle(self):
        message = self.get_formatted_message(self.reward.rewardsJSON.get("base_message", ""))
        message += self.get_formatted_message(self.reward.chosenReward.get("message", ""))
        await self.ctx.send(message)

        unlock_configs = {
            "unlocks": self.ctx.author.name,
            "global_unlocks": "global"
        }
        
        reward_data = self.reward.chosenReward
        for unlock_key, target_user in unlock_configs.items():
            ids_to_unlock = reward_data.get(unlock_key)
            if ids_to_unlock:
                if add_unlocked_ids(self.ctx.channel.name, target_user, ids_to_unlock):
                    unlock_msg = self.get_formatted_message(reward_data.get("unlock_message", ""))
                    await self.ctx.send(unlock_msg)               

    
    def get_formatted_message(self, msg: str) -> str:
        format_map = {
            'username': self.ctx.author.name,
            'value': Utils.format_large_number(self.reward.chosenReward.get("value", 0)),
            'amount': self.reward.chosenReward.get("amount", 0),
            'time': Utils.format_time(self.reward.chosenReward.get("seconds", 0)),
            'bullets': self.reward.chosenReward.get("bullets", 0),
            'chambers': self.reward.chosenReward.get("chambers", 0),
            'percentage': Utils.format_percent(self.reward.chosenReward.get("percentage", 0)),
            'delay': self.reward.chosenReward.get("delay", 0)
        }
        message = msg.format_map(format_map)
        return message
                                              


# ---- Reward Handlers ----

class PointsRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()
        message = ""
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name) 
        response = await self.streamelements.add_user_points(user=self.ctx.author.name, channel_id=channel_id, points=self.reward.chosenReward["value"])
        message = f"Set {self.ctx.author.name} points to: {Utils.format_large_number(response['newAmount'])} ({Utils.format_large_number_sign(response['amount'])})"
        await self.ctx.send(message)

class TimeoutRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()
        message = ""    
        user = await self.ctx.channel.user()
        message = f"User {self.ctx.author.name} was timed out for {Utils.format_time(self.reward.chosenReward.get('seconds', 0))}!"
        await user.timeout_user(token=self.token, moderator_id=self.ctx.bot.user_id, user_id=self.ctx.author.id, duration=self.reward.chosenReward["seconds"], reason=f"Nice catch!! {self.reward.chosenReward['seconds']} seconds timeout!!")
        await self.ctx.send(message)

class VipRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()

class PercentagePointsRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name) 
        userpoints = await self.streamelements.get_user_points(user=self.ctx.author.name, channel_id=channel_id)
        points_to_add = int(userpoints * self.reward.chosenReward["percentage"])
        response = await self.streamelements.add_user_points(user=self.ctx.author.name, channel_id=channel_id, points=points_to_add)
        message = f"Set {self.ctx.author.name} points to: {Utils.format_large_number(response['newAmount'])} ({Utils.format_large_number_sign(response['amount'])})"
        await self.ctx.send(message)

class RussianRouletteRewardHandler(BaseRewardHandler):
    def was_shot(self, bullets: int, chambers: int) -> bool:
        cylinder = [1]*bullets + [0]*(chambers - bullets)
        random.shuffle(cylinder) 
        return random.choice(cylinder) == 1
    
    async def handle_timeout(self):
        user = await self.ctx.channel.user()
        timeMsg = Utils.format_time(self.reward.chosenReward["seconds"])
        message = self.reward.chosenReward["shot_message"].format(username = self.ctx.author.name, time = timeMsg)
        await user.timeout_user(token=self.token, moderator_id=self.ctx.bot.user_id, user_id=self.ctx.author.id, duration=self.reward.chosenReward["seconds"], reason=f"Nice catch!! {self.reward.chosenReward['seconds']} seconds timeout!!")
        await self.ctx.send(message)

    async def handle_percentage(self):
        percentageMsg = Utils.format_percent(self.reward.chosenReward["percentage"])
        message = self.reward.chosenReward["shot_message"].format(username = self.ctx.author.name, percentage = percentageMsg)
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name)
        userpoints = await self.streamelements.get_user_points(user=self.ctx.author.name, channel_id=channel_id)
        shot_points = int(userpoints * self.reward.chosenReward["percentage"])
        response = await self.streamelements.remove_user_points(user=self.ctx.author.name, channel_id=channel_id, points=shot_points)
        await self.ctx.send(message)
        await self.ctx.send(f"Set {self.ctx.author.name} points to: {Utils.format_large_number(response['newAmount'])} ({Utils.format_large_number_sign(response['amount'])})")

    
    async def handle_points(self):
        pointsMsg = Utils.format_large_number(self.reward.chosenReward["value"])
        message = self.reward.chosenReward["shot_message"].format(username = self.ctx.author.name, value = pointsMsg)
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name)
        response = await self.streamelements.remove_user_points(user=self.ctx.author.name, channel_id=channel_id, points=self.reward.chosenReward["value"])
        await self.ctx.send(message)
        await self.ctx.send(f"Set {self.ctx.author.name} points to: {Utils.format_large_number(response['newAmount'])} ({Utils.format_large_number_sign(response['amount'])})")

    async def handle_nothing(self):
        message = self.reward.chosenReward["shot_message"].format(username = self.ctx.author.name)
        await self.ctx.send(message)


    async def handle(self):
        shot_penalty_mapping = {
            "timeout": self.handle_timeout,
            "percentage": self.handle_percentage,
            "points": self.handle_points,
            "nothing": self.handle_nothing
        }
        message = ""
        chambers = self.reward.chosenReward["chambers"]
        bullets = self.reward.chosenReward["bullets"]
        await super().handle()
        await asyncio.sleep(self.reward.chosenReward.get("delay", 4))
        if self.was_shot(bullets, chambers):
            await shot_penalty_mapping[self.reward.chosenReward.get("penalty_type")]()
        else:
            message = self.reward.chosenReward["safe_message"].format(username = self.ctx.author.name)
            await self.ctx.send(message)

class RobberyRewardHandler(BaseRewardHandler):
    def get_robbed_user_rank(self, rank: int, rank_range: int) -> int:
        possible_ranks = [r for r in range(rank - rank_range, rank) if r != rank and r > 0]
        if not possible_ranks:
            return 2  
        return random.choice(possible_ranks)

    async def swap_points(self, channel_id: str, user1: str, user2: str, points: int):
        """
        Swap points between two users.
        Args:
            channel_id (str): The ID of the channel.
            user1 (str): The username of the first user losing the points.
            user2 (str): The username of the second user gaining the points.
            points (int): The number of points to swap.
        """
        user1_points = await self.streamelements.get_user_points(user=user1, channel_id=channel_id)
        points_to_rob = min(points, user1_points)
        response_user1 = await self.streamelements.remove_user_points(user=user1, channel_id=channel_id, points=points_to_rob)
        response_user2 = await self.streamelements.add_user_points(user=user2, channel_id=channel_id, points=points_to_rob)
        await self.ctx.send(
            f"{user2} {Utils.format_large_number(response_user2['newAmount'])} "
            f"({Utils.format_large_number_sign(response_user2['amount'])}) robbed "
            f"{user1} {Utils.format_large_number(response_user1['newAmount'])} "
            f"({Utils.format_large_number_sign(response_user1['amount'])})!"
            )


    async def handle_points_robbery(self, channel_id: str, robbed_user: str):
        value = self.reward.chosenReward["value"]
        message = self.reward.chosenReward["robbery_message"].format(username = self.ctx.author.name, value = Utils.format_large_number(value), victim = robbed_user)
        await self.ctx.send(message)
        await self.swap_points(channel_id=channel_id, user1=robbed_user, user2=self.ctx.author.name, points=value)
        

    async def handle_percentage_robbery(self, channel_id: str, robbed_user: str):
        percentage = self.reward.chosenReward["percentage"]
        message = self.reward.chosenReward["robbery_message"].format(username = self.ctx.author.name, percentage = Utils.format_percent(percentage), victim = robbed_user)
        await self.ctx.send(message)
        robbed_user_points = await self.streamelements.get_user_points(user=robbed_user, channel_id=channel_id)
        points_to_rob = int(robbed_user_points * percentage)
        await self.swap_points(channel_id=channel_id, user1=robbed_user, user2=self.ctx.author.name, points=points_to_rob)


    async def handle(self):
        await super().handle()
       
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name)
        rank = await self.streamelements.get_user_rank(user=self.ctx.author.name, channel_id=channel_id)
        rank_range = self.reward.chosenReward["range"]
        robbed_user_rank = self.get_robbed_user_rank(rank=rank, rank_range=rank_range)
        robbed_user = await self.streamelements.get_username_by_rank(rank=robbed_user_rank, channel_id=channel_id)

        if not robbed_user:
            await self.ctx.send(f"{self.ctx.author.name} everyone around you is too poor to rob! Unlucky!")
            return

        robbery_type_mapping = {
            "percentage": lambda: self.handle_percentage_robbery(channel_id=channel_id, robbed_user=robbed_user),
            "value": lambda: self.handle_points_robbery(channel_id=channel_id, robbed_user=robbed_user)
        }

        for key, handler in robbery_type_mapping.items():
            if key in self.reward.chosenReward:
                await handler()
        
class DupeRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()
        delay = self.reward.chosenReward.get("delay", 3)
        amount = self.reward.chosenReward.get("amount", 2)
        for i in range(1, amount + 1):
            rewardsFilePath = Utils.get_fish_rewards_file_path(self.ctx)
            reward = FishRewards(
                chatterRole="sub" if self.ctx.author.is_subscriber else "unsub", 
                rewardsFilePath=rewardsFilePath, 
                username=self.ctx.author.name, 
                channel_name=self.ctx.channel.name
            )
            reward.chosenReward = reward.choose_default_reward()
            await asyncio.sleep(delay)
            await handle_reward(reward, self.ctx, self.token, self.streamelements)
            
        

class CustomRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()
        message = ""
        message = self.reward.chosenReward["cmd"].format(username = self.ctx.author.name)
        await self.ctx.send(message)

class NothingRewardHandler(BaseRewardHandler):
    async def handle(self):
        await super().handle()

# ---- Reward Handler Mapping ----

reward_handler_mapping = {
    "points": PointsRewardHandler,
    "timeout": TimeoutRewardHandler,
    "vip": VipRewardHandler,
    "percentage_points": PercentagePointsRewardHandler,
    "russian_roulette": RussianRouletteRewardHandler,
    "dupe": DupeRewardHandler,
    "robbery": RobberyRewardHandler,
    "nothing": NothingRewardHandler
}

async def handle_reward(reward, ctx, token, streamelements):
    reward_type = reward.chosenReward.get("type")
    handler_class = reward_handler_mapping.get(reward_type, CustomRewardHandler)
    handler = handler_class(reward, ctx, token, streamelements)
    await handler.handle()
