# coding utf-8

import discord
from discord import (
    Message,
    Member, 
    VoiceState, 
    Guild, 
    VoiceChannel, 
    TextChannel, 
    Role,
    VoiceClient,
    RawReactionActionEvent,
    RawReactionClearEvent,
    Attachment
)

import asyncio

import settings
import datetime

import requests

import re

import os

from voting import VotingSystem

import requests

from youtube import YTDLSource

YT_LINK_PATTERN = re.compile("^(http|https):\/\/www\.youtube\.com\/watch\?v=[0-9a-zA-Z]*")

class Client(discord.Client):
    activeVoiceChannel: VoiceClient | None = None

    channelToCreateTempChannelsId: int = settings.__TEMP_CHANNEL_CREATING_CHANNEL_ID__
    temporaryChannels: list[VoiceChannel] = list()

    async def on_ready(self):
        self.guild: Guild = self.guilds[0]
        print(f"Logged as {self.user}")
        await self.__check_milestones()

    async def on_message(self, message: Message):
        await self.__check_milestones()
        if message.attachments.__len__() == 1:
            attachment: Attachment = message.attachments[0]
            if attachment.filename == "vote.json":
                ...
                jsonVoting = requests.get(
                    attachment.url
                ).json()
                embed, emojis, vote_no = VotingSystem.add_voting(jsonVoting)

                channel: TextChannel = await self.fetch_channel(settings.__VOTING_CHANNEL__)
                innerMessage: Message = await channel.send(content=f"Vote №{vote_no}")
                VotingSystem.set_mes_id(vote_no-1, innerMessage.id)
                await innerMessage.edit(embed=embed)
                for emoji in emojis:
                    await innerMessage.add_reaction(emoji)

                    await message.delete(delay=10.)
        

        if message.content.startswith(settings.__BOT_COMMAND_SYMBOL__):
            _, command = message.content.split(settings.__BOT_COMMAND_SYMBOL__)
            command, *args = command.split(" ")

            command: str
            args: list[str]

            if command in ["cat", "fox", "dog", "bird"]:
                r = requests.get(f'https://some-random-api.ml/img/{command}').json()

                embed = discord.Embed(color=0xff9900, title=f"Your Random {command.capitalize()}")
                embed.set_image(url=r["link"])

                await self._send_embed(
                    message=message, 
                    embed=embed
                )
            
            elif command == "play":
                if self.activeVoiceChannel: return
                if re.fullmatch(pattern=YT_LINK_PATTERN, string=args[0]):
                    if voiceChannel := message.author.voice.channel:
                        await self.__play(voiceChannel, args[0])
                        ...
            
            elif command == "stop": 
                await self.__clear_and_dc()

            elif command == "vote":
                try: args[0] = int(args[0])
                except: return

                messageId = VotingSystem.get_votings(int(args[0]))
                
                channel: TextChannel = await self.fetch_channel(settings.__VOTING_CHANNEL__)
                voting: Message = await channel.fetch_message(messageId)

                text = ""
                print(voting)
                for reaction in voting.reactions:
                    text += f"For {reaction} voted: \n"
                    
                    async for member in reaction.users():
                        if type(member) == discord.User: continue
                        else: member: Member
                        
                        if not member.bot:
                            text += f"{member} \n"
                    
                    text += "\n\n"

                embed = discord.Embed(
                    title=f"Results of voting №{args[0]}",
                    description=text
                )

                await message.reply(embed=embed)

    async def _send_embed(self, message: discord.Message, embed: discord.Embed):
        await message.reply(embed=embed)

    # ----- reactions -----
    async def on_raw_reaction_event(self, payload: RawReactionActionEvent): 
        
        ...



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

            new_channel = await guild.create_voice_channel(f"Temporary channel {self.temporaryChannels.__len__()+1}", reason=message)
            await member.move_to(new_channel)

            self.temporaryChannels.append(new_channel)

    # ----- role adding logic -----
    async def on_member_join(self, member: Member):
        await self.__check_milestones()
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

        if not self.intents.members: return

        guild: Guild = self.guilds[0]

        milestones: tuple[tuple[datetime.timedelta, datetime.timedelta, Role]] = tuple([
            tuple([datetime.timedelta(minutes=0), datetime.timedelta(minutes=1), guild.get_role(986011722181644318)]),
            tuple([datetime.timedelta(minutes=1), datetime.timedelta(minutes=5), guild.get_role(986011898027839568)]),
            tuple([datetime.timedelta(minutes=5), datetime.timedelta(minutes=15), guild.get_role(986012004244402227)]),
            tuple([datetime.timedelta(minutes=15), datetime.timedelta(minutes=30), guild.get_role(986012103393546312)]),
            tuple([datetime.timedelta(minutes=30), datetime.timedelta(weeks=28), guild.get_role(986012261288132688)]),
        ])

        async for member in self.guilds[0].fetch_members():
            member: Member
            for _from, _to, _role in milestones:
                if _from < (datetime.datetime.now() - member.joined_at) <= _to:
                    await member.add_roles(_role)
                else:
                    try:
                        await member.remove_roles(_role)
                    except: 
                        pass

    # ----- yt_music -----
    async def __play(self, voiceChannel: VoiceChannel, source: str):
        await self.__check_milestones()
        vc = await voiceChannel.connect()
        player = await YTDLSource.from_url(url=source)

        self.activeVoiceChannel = vc

        while vc.is_playing():
            pass

        await self.__clear_and_dc()
        
    async def __clear_and_dc(self, vc: VoiceClient = None, route="./temp/"):
        await self.__check_milestones()
        if not vc and self.activeVoiceChannel:
            vc = self.activeVoiceChannel

        if vc:
            await vc.disconnect()
            self.activeVoiceChannel = None
        
        for file in [f for f in os.listdir(route) if os.path.isfile(os.path.join(route, f))]:
            os.remove(route + file)

    
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True

    client = Client(intents=intents)
    client.run(settings.__TOKEN__)