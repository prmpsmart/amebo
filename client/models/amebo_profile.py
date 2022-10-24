from .amebo_object import *


class AmeboMiniProfile(IMiniProfile):
    def __init__(
        self,
        display_name: str,
        description: str,
        avatar: str,
    ):
        # as the name implies.
        self.display_name = display_name
        self.description = description
        # the profile image maybe later we can add cover_image
        #  and slide_images like telegram.
        self.avatar = avatar

    @property
    def unique_name(self):
        return self.display_name.lower()

    def edit(self, display_name=str, description=str, avatar=str):
        if display_name:
            self.display_name = display_name
        if description:
            self.description = description
        if avatar:
            self.avatar = avatar

    def json(self) -> Json:
        return Json(
            display_name=self.display_name,
            description=self.description,
            avatar=self.avatar,
        )


class AmeboProfile(AmeboObject, AmeboMiniProfile, IProfile):
    def __init__(
        self,
        id: int,
        created_at: int,
        display_name: str,
        description: str,
        avatar: str,
        unique_id: str,
    ):
        AmeboObject.__init__(self, id, created_at)
        AmeboMiniProfile.__init__(
            self,
            display_name=display_name,
            description=description,
            avatar=avatar,
        )

        self.unique_id = unique_id

    @property
    def json(self) -> Json:
        return Json(
            unique_id=self.unique_id,
            **AmeboObject.json(self),
            **AmeboMiniProfile.json(self)
        )
