
import fish.helpers.utils as Utils

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
        await self.streamelements.add_user_points(user=self.ctx.author.name, channel_id=channel_id, points=self.reward.chosenReward["value"])
        await self.ctx.send(message[0])
        userpoints = await self.streamelements.get_user_points(user=self.ctx.author.name, channel_id=channel_id)
        message[1] = f"Set {self.ctx.author.name} points to: {Utils.format_large_number(userpoints)}"
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
        await self.streamelements.add_user_points(user=self.ctx.author.name, channel_id=channel_id, points=points_to_add)
        await self.ctx.send(message[0])
        
        message[1] = f"Set {self.ctx.author.name} points to: {Utils.format_large_number(userpoints)}"
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
    "nothing": NothingRewardHandler
}

async def handle_reward(reward, ctx, token, streamelements):
    reward_type = reward.chosenReward.get("type")
    handler_class = reward_handler_mapping.get(reward_type, CustomRewardHandler)
    handler = handler_class(reward, ctx, token, streamelements)
    await handler.handle()
