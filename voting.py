import json
from dataclasses import asdict, dataclass, field
from discord import Embed

@dataclass()
class Voting:
    title: str
    description: str
    color: str
    fields: list

@dataclass
class VotingSystem:
    storage = "data.json"

    json_storage: list = None

    @staticmethod
    def load():
        if not VotingSystem.json_storage:
            try:
                with open(VotingSystem.storage, "r") as FILE:
                    VotingSystem.json_storage = json.load(FILE)
            except: ...

    @staticmethod
    def save():
        with open(VotingSystem.storage, "w") as FILE:
               json.dump(VotingSystem.json_storage, FILE)

    @staticmethod
    def add_voting(json: dict) -> tuple[Embed,list[str]]:
        voting = Voting(
            title = json["title"],
            description = json["description"],
            color = int(json["color"], base=16),
            fields = [(emoji, 0) for emoji in json["fields"]],
        )
        
        embed = Embed(
            color=voting.color, 
            title=voting.title,
            description=voting.description,
        )

        if not VotingSystem.json_storage:
            VotingSystem.json_storage = []
            VotingSystem.load()

        VotingSystem.json_storage.append(asdict(voting))
        VotingSystem.save()

        return embed, json["fields"], VotingSystem.json_storage.__len__()

    @staticmethod
    def get_votings(ID):
        if not VotingSystem.json_storage: VotingSystem.load()
        data = VotingSystem.json_storage[ID-1]["id"]
        return data

    @staticmethod
    def delete_voting(ID):
        VotingSystem.json_storage.pop(ID-1)
        VotingSystem.save()

    @staticmethod
    def set_mes_id(num, value):
        VotingSystem.json_storage[num-1]["id"] = value
        VotingSystem.save()
        