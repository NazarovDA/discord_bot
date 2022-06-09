# coding utf-8

import discord
from discord import Member, VoiceState, Guild, VoiceChannel, TextChannel, Role

import asyncio

import settings
import datetime

class Client(discord.Client):
    channelToCreateTempChannelsId: int = settings.__TEMP_CHANNEL_CREATING_CHANNEL_ID__
    temporaryChannels: list[VoiceChannel] = list()

    async def on_ready(self):
        print(f"Logged as {self.user}")
        # await self.__check_milestones()
        if not self.intents.members: return
        guild: Guild = self.guilds[0]

        async for member in guild.fetch_members():
            print(member)

    async def on_message(self, message: discord.Message):
        print(message)

    #  ----- temporary channel logic -----
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if not discord.Permissions.manage_channels: return
        if member.bot: return

        if before.channel in self.temporaryChannels:
            if before.channel.members.__len__() == 0:
                
                await asyncio.sleep(settings.__TEMPORARY_CHANNELS_TIMEOUT__)
                
                if before.channel.members.__len__() == 0:
                    self.temporaryChannels.remove(before.channel)
                    # if still no user -> delete
                    await before.channel.delete()

        if after.channel != None and after.channel.id == Client.channelToCreateTempChannelsId:
            guild: Guild = self.guilds[0]

            message = f"New temporary channel created by {member.nick}"

            new_channel = await guild.create_voice_channel("Temporary channel", reason=message)
            await member.move_to(new_channel)

            self.temporaryChannels.append(new_channel)

    # ----- role adding logic -----
    async def on_member_join(self, member: Member):
        if not discord.Intents.members or not discord.Permissions.manage_roles: return

        welcome_channel: TextChannel = member.guild.get_channel(settings.__GREETINGS_CHANNEL_ID__)
        await welcome_channel.send(f"Hello there {member.nick}")

        await member.add_roles(
            roles=[member.guild.get_role(settings.__NEW_MEMBER_ROLE_ID__)], reason=f"New member {member.nick} has joined"
        )

    async def __check_milestones(self):
        """
        adding role for passing milestiones
        """
        milestones: tuple[datetime.timedelta, datetime.timedelta, Role]

        for member in self.guilds[0].members:
            member: Member
            for _from, _to, _role in milestones:
                if _from < member.joined_at - datetime.datetime.now() <= _to:
                    member.add_roles(_role)
                    member.remove_roles([obj[2] for obj in milestones].remove(_role))


    
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True

    client = Client(intents=intents)
    client.run(settings.__TOKEN__)