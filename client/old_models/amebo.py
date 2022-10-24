from models.amebo_room import *


class Amebo:

    amebo_users: dict[int, AmeboUser] = {}
    amebo_bots: dict[int, AmeboBot] = {}
    amebo_groups: dict[int, AmeboGroup] = {}
    amebo_broadcast_channels: dict[int, AmeboBroadcastChannel] = {}

    @classmethod
    def create_user(cls, **kwargs):
        ...

    @classmethod
    def create_bot(cls, **kwargs):
        ...

    @classmethod
    def create_group(cls, creator: AmeboUser, **kwargs):
        ...

    @classmethod
    def create_broadcast_channel(cls, creator: AmeboUser, **kwargs):
        ...

    @classmethod
    def delete_user(cls, user: AmeboUser):
        ...

    @classmethod
    def delete_bot(cls, bot: AmeboBot):
        ...

    @classmethod
    def delete_group(cls, group: AmeboGroup):
        ...

    @classmethod
    def delete_broadcast_channel(cls, broadcast_channel: AmeboBroadcastChannel):
        ...

    @classmethod
    def unique_id_exist(cls, unique_id: str):
        user = GET_BY_ATTR(
            cls.amebo_users, validator=LOWER_VALIDATOR, unique_id=unique_id.lower()
        )
        if user:
            return user

        bot = GET_BY_ATTR(
            cls.amebo_bots, validator=LOWER_VALIDATOR, unique_id=unique_id.lower()
        )
        if bot:
            return bot

        group = GET_BY_ATTR(
            cls.amebo_groups, validator=LOWER_VALIDATOR, unique_id=unique_id.lower()
        )
        if group:
            return group

        broadcast_channel = GET_BY_ATTR(
            cls.amebo_broadcast_channels,
            validator=LOWER_VALIDATOR,
            unique_id=unique_id.lower(),
        )
        if broadcast_channel:
            return broadcast_channel

        return False

    @classmethod
    def get_user(cls, validator=None, **attrs_values: dict[str, Any]):
        return GET_BY_ATTR(cls.amebo_users, validator=validator, **attrs_values)

    @classmethod
    def get_bot(cls, validator=None, **attrs_values: dict[str, Any]):
        return GET_BY_ATTR(cls.amebo_bots, validator=validator, **attrs_values)

    @classmethod
    def get_group(cls, validator=None, **attrs_values: dict[str, Any]):
        return GET_BY_ATTR(cls.amebo_groups, validator=validator, **attrs_values)

    @classmethod
    def get_broadcast_channel(cls, validator=None, **attrs_values: dict[str, Any]):
        return GET_BY_ATTR(
            cls.amebo_broadcast_channels, validator=validator, **attrs_values
        )

    @classmethod
    def user_or_bot(cls, id: int) -> Union[AmeboUser, AmeboBot, None]:
        return GET(cls.amebo_users, id) or GET(cls.amebo_bots, id)

    @classmethod
    def get_room(self, json: Json) -> Union[AmeboGroup, AmeboBroadcastChannel]:
        room_id = json.room_id
        is_broadcast = json.is_broadcast
        if room_id and is_broadcast:
            rooms = (
                Amebo.amebo_groups
                if not is_broadcast
                else Amebo.amebo_broadcast_channels
            )
            return GET(rooms, room_id)
