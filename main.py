# coding utf-8

import discord
from discord import Member, VoiceState, Guild, VoiceChannel

import asyncio

import settings

class Client(discord.Client):
    channelToCreateTempChannelsId: int = 715965021569548344
    temporaryChannels: list[VoiceChannel] = list()

    async def on_ready(self):
        print(f"Logged as {self.user}")

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

    
if __name__ == "__main__":
    client = Client()
    client.run(settings.__TOKEN__)