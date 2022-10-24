from .amebo_profile import AmeboMiniProfile
from .amebo_object import *


class AmeboMemberPermissions(IMemberPermissions):
    ...


class AmeboMemberRole(AmeboMiniProfile, IMemberRole):
    def __init__(
        self,
        display_name: str,
        description: str,
        avatar: str,
        permissions: list[AmeboMemberPermissions],
    ):
        AmeboMiniProfile.__init__(
            self,
            display_name=display_name,
            description=description,
            avatar=avatar,
        )

        # permissions that this message has in a room,
        # whether, to message, edit room info, etc
        self.permissions = permissions


# a default role for everyone in the room a privileged
# member can assigned the permissions of this role.
MEMBER_ROLE = AmeboMemberRole(
    "everyone",
    "all members",
    "",
    [
        AmeboMemberPermissions.SEND_MESSAGES,
        AmeboMemberPermissions.EMBED_LINKS,
        AmeboMemberPermissions.ATTACH_FILES,
    ],
)
