
import fish.helpers.utils as Utils
import random
import asyncio

class BaseRewardHandler:
    def __init__(self, reward, ctx, token, streamelements):
        self.reward = reward
        self.ctx = ctx
        self.token = token
        self.streamelements = streamelements

    async def handle(self):
        raise NotImplementedError("Handle method must be implemented by subclasses.")

# ---- Reward Handlers ----

class PointsRewardHandler(BaseRewardHandler):
    async def handle(self):
        message = ["", ""]    
        message[0] = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        valueMsg = Utils.format_large_number(self.reward.chosenReward["value"])
        message[0] += self.reward.chosenReward["message"].format(username = self.ctx.author.name, value = valueMsg)
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name) 
        response = await self.streamelements.add_user_points(user=self.ctx.author.name, channel_id=channel_id, points=self.reward.chosenReward["value"])
        await self.ctx.send(message[0])
        message[1] = f"Set {self.ctx.author.name} points to: {Utils.format_large_number(response['newAmount'])} ({Utils.format_large_number_sign(response['amount'])})"
        await self.ctx.send(message[1])

class TimeoutRewardHandler(BaseRewardHandler):
    async def handle(self):
        message = ["", ""]    
        message[0] = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        timeMsg = Utils.format_time(self.reward.chosenReward["seconds"])
        message[0] += self.reward.chosenReward["message"].format(username = self.ctx.author.name, time = timeMsg)
        user = await self.ctx.channel.user()
        message[1] = f"User {self.ctx.author.name} was timed out for {timeMsg}!"
        await user.timeout_user(token=self.token, moderator_id=self.ctx.bot.user_id, user_id=self.ctx.author.id, duration=self.reward.chosenReward["seconds"], reason=f"Nice catch!! {self.reward.chosenReward['seconds']} seconds timeout!!")
        await self.ctx.send(message[0])
        await self.ctx.send(message[1])

class VipRewardHandler(BaseRewardHandler):
    async def handle(self):
        message = ""
        message = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        message += self.reward.chosenReward["message"].format(username = self.ctx.author.name)
        await self.ctx.send(message)

class PercentagePointsRewardHandler(BaseRewardHandler):
    async def handle(self):
        message = ["", ""]
        message[0] = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        percentageMsg = Utils.format_percent(self.reward.chosenReward["percentage"])
        message[0] += self.reward.chosenReward["message"].format(username = self.ctx.author.name, percentage = percentageMsg)
        channel_id = await self.streamelements.get_channel_id(self.ctx.channel.name) 
        userpoints = await self.streamelements.get_user_points(user=self.ctx.author.name, channel_id=channel_id)
        points_to_add = int(userpoints * self.reward.chosenReward["percentage"])
        response = await self.streamelements.add_user_points(user=self.ctx.author.name, channel_id=channel_id, points=points_to_add)
        await self.ctx.send(message[0])
        
        message[1] = f"Set {self.ctx.author.name} points to: {Utils.format_large_number(response['newAmount'])} ({Utils.format_large_number_sign(response['amount'])})"
        await self.ctx.send(message[1])

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
        message = ["", ""]
        chambers = self.reward.chosenReward["chambers"]
        bullets = self.reward.chosenReward["bullets"]
        message[0] = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        message[0] += self.reward.chosenReward["message"].format(username = self.ctx.author.name, chambers = chambers, bullets = bullets)
        await self.ctx.send(message[0])
        await asyncio.sleep(4)
        if self.was_shot(bullets, chambers):
            await shot_penalty_mapping[self.reward.chosenReward.get("penalty_type")]()
        else:
            message[1] = self.reward.chosenReward["safe_message"].format(username = self.ctx.author.name)
            await self.ctx.send(message[1])

class CustomRewardHandler(BaseRewardHandler):
    async def handle(self):
        message = ["", ""]
        message[0] = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        message[0] += self.reward.chosenReward["message"].format(username = self.ctx.author.name)
        message[1] = self.reward.chosenReward["cmd"].format(username = self.ctx.author.name)
        await self.ctx.send(message[0])
        await self.ctx.send(message[1])

class NothingRewardHandler(BaseRewardHandler):
    async def handle(self):
        message = self.reward.rewardsJSON["base_message"].format(username = self.ctx.author.name)
        message += self.reward.chosenReward["message"].format(username = self.ctx.author.name)
        await self.ctx.send(message)

# ---- Reward Handler Mapping ----

reward_handler_mapping = {
    "points": PointsRewardHandler,
    "timeout": TimeoutRewardHandler,
    "vip": VipRewardHandler,
    "percentage_points": PercentagePointsRewardHandler,
    "russian_roulette": RussianRouletteRewardHandler,
    "nothing": NothingRewardHandler
}

async def handle_reward(reward, ctx, token, streamelements):
    reward_type = reward.chosenReward.get("type")
    handler_class = reward_handler_mapping.get(reward_type, CustomRewardHandler)
    handler = handler_class(reward, ctx, token, streamelements)
    await handler.handle()
