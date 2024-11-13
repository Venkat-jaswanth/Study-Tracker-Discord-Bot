from discord import (
    Interaction,
    Message,
    Embed,
    ui,
    File,
    NotFound,
    ButtonStyle,
    Color,
    AllowedMentions,
)
from io import BytesIO
from typing import Optional, List, Tuple, Any, Dict, Self, Protocol, TYPE_CHECKING
from utils.context_manager import ctx_mgr
from logging import error as err, info

if TYPE_CHECKING:
    from discord.ext.commands import Context, Bot  # type: ignore


async def get_channel(channel_id: int, bot: Optional["Bot"] = None):
    if bot is None:
        bot = ctx_mgr().get_context_bot()
    try:
        channel_api = await bot.fetch_channel(channel_id)
        return channel_api
    except NotFound:
        raise ValueError(f"Invalid channel_id: `{channel_id}` doesn't exist.")


async def get_user(user_id: int, bot: Optional["Bot"] = None):
    if bot is None:
        bot = ctx_mgr().get_context_bot()
    try:
        user_api = await bot.fetch_user(user_id)
        return user_api
    except NotFound:
        raise ValueError(f"Invalid user_id: `{user_id}` doesn't exist.")


async def get_files_from_message(message: Message) -> Dict[str, BytesIO]:
    files: Dict[str, BytesIO] = {}
    for file in message.attachments:
        file_bytes = await file.read()
        files[file.filename] = BytesIO(file_bytes)
    return files


async def send_message(
    *,
    content: Optional[str] = None,
    embed: Optional[Embed] = None,
    view: Optional[ui.View] = None,
    file: Optional[File] = None,
    files: Optional[List[File]] = None,
    mention_author: bool = False,
):
    message = ctx_mgr().get_active_msg()
    send_new_message = ctx_mgr().get_send_new_msg()

    files = files or []
    if file is not None:
        files.append(file)

    if embed is not None and hasattr(embed, "file"):
        if embed.file is not None:  # type: ignore
            files.append(embed.file)  # type: ignore

    if message is None or send_new_message:
        kwargs: Dict[str, Any] = {}
        for kwarg in ["embed", "view", "files", "mention_author"]:
            if locals()[kwarg] is not None:
                kwargs[kwarg] = locals()[kwarg]

        ctx = ctx_mgr().get_init_context()
        message = await ctx.reply(content=content, **kwargs)

    else:
        allowed_mentions = (
            AllowedMentions.all() if mention_author else AllowedMentions.none()
        )
        message = await message.edit(
            content=content,
            embed=embed,
            view=view,
            attachments=files,
            allowed_mentions=allowed_mentions,
        )

    ctx_mgr().set_active_msg(message)


class BaseEmbed(Embed):
    def __init__(
        self,
        *,
        title: str,
        description: Optional[str] = None,
        color: Tuple[int, int, int] = (0, 255, 255),
    ):
        if description is None:
            user_id = ctx_mgr().get_context_user_id()
            description = f"<@{user_id}>"
        super().__init__(
            title=title, description=description, color=Color.from_rgb(*color)
        )
        self.file: Optional[File] = None

    def add_field(self, *, name: str, value: str = "", inline: bool = False):  # type: ignore
        super().add_field(name=name, value=value, inline=inline)

    def set_image_from_bytes(self, b: bytes, filename: str = "img.png"):
        buf = BytesIO(b)
        buf.seek(0)
        self.file = File(buf, filename=filename)
        self.set_image_from_file(self.file.filename)

    def set_image_from_file(self, filename: str):
        self.set_image(url=f"attachment://{filename}")


class BaseView(ui.View):
    @classmethod
    async def send_view(cls, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def __init__(self):
        super().__init__()
        self.user: int = ctx_mgr().get_context_user_id()
        self.msg_content: Optional[str] = None

        self._init_ctx: Context[Bot] = ctx_mgr().get_init_context()
        self._active_message: Optional[Message] = ctx_mgr().get_active_msg()

        self._add_items()

    def _add_items(self):
        pass

    async def interaction_check(self, interaction: Interaction) -> bool:
        assert self._active_message is not None
        ctx_mgr().set_init_context(self._init_ctx)
        ctx_mgr().set_active_msg(self._active_message)
        if interaction.user.id == self.user:
            return True
        await interaction.response.send_message(
            "You are not allowed to interact with this message.", ephemeral=True
        )
        return False

    async def on_error(
        self, interaction: Interaction, error: Exception, item: ui.Item[Any]
    ):
        err(f"Error in {item}: {error}")
        assert interaction.message is not None
        await interaction.message.reply(
            f"An error occurred!\nitem: {item}\nError: {error}"
        )
        raise error

    async def _disable_children(self):
        for item in self.children:
            item.disabled = True  # type: ignore

        assert self._active_message is not None
        self._active_message = await self._active_message.edit(view=self)
        ctx_mgr().set_active_msg(self._active_message)

    async def on_timeout(self):
        await self._disable_children()

        assert self._active_message is not None
        info(f"{self.__class__.__name__} timed out.\nmsg_id: {self._active_message.id}")

    async def __del__(self):
        assert self._active_message is not None
        info(f"{self.__class__.__name__} deleted.\nmsg_id: {self._active_message.id}")

    def stop(self):
        super().stop()

        assert self._active_message is not None
        info(f"{self.__class__.__name__} stopped.\nmsg_id: {self._active_message.id}")

    def get_child(self, custom_id: str) -> ui.Item[Self]:
        for item in self.children:
            if item.custom_id == custom_id:  # type: ignore
                return item
        raise LookupError(f"Item with custom_id: `{custom_id}` not found.")

    async def get_embed_files(self) -> Tuple[Optional[Embed], Optional[List[File]]]:
        raise NotImplementedError

    async def send(self):
        embed, files = await self.get_embed_files()
        await send_message(
            content=self.msg_content, embed=embed, view=self, files=files
        )
        self._active_message = ctx_mgr().get_active_msg()

    async def update_view(self):
        self.clear_items()
        self._add_items()
        await self.send()

    def _add_button(
        self,
        *,
        label: str,
        custom_id: str,
        style: ButtonStyle = ButtonStyle.blurple,
        row: Optional[int] = None,
        disabled: bool = False,
        emoji: Optional[str] = None,
    ):
        button = BaseButton(
            label=label,
            custom_id=custom_id,
            style=style,
            row=row,
            disabled=disabled,
            emoji=emoji,
            button_clicked_callback=self._button_clicked,
        )
        self.add_item(button)

    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        raise NotImplementedError

    def _add_dropdown(
        self,
        *,
        custom_id: str,
        options: Dict[str, str],  # {value: label}
        placeholder: Optional[str],
        row: Optional[int] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        emojis: Optional[Dict[str, str]] = None,
    ):
        dropdown = BaseDropdown(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            row=row,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            emojis=emojis,
            dropdown_selected_callback=self._dropdown_selected,
        )
        self.add_item(dropdown)

    async def _dropdown_selected(
        self, *, interaction: Interaction, custom_id: str, values: List[str]
    ) -> None:
        raise NotImplementedError

    async def _modal_submit(
        self, *, interaction: Interaction, custom_id: str, values: Dict[str, str]
    ) -> None:
        raise NotImplementedError


class ButtonClickedCallback(Protocol):
    async def __call__(self, *, interaction: Interaction, custom_id: str) -> None: ...


class BaseButton(ui.Button[Any]):
    def __init__(
        self,
        *,
        label: str,
        custom_id: str,
        style: ButtonStyle,
        row: Optional[int],
        disabled: bool,
        emoji: Optional[str],
        button_clicked_callback: ButtonClickedCallback,
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style,
            row=row,
            disabled=disabled,
            emoji=emoji,
        )
        self.button_clicked_callback = button_clicked_callback

    async def callback(self, interaction: Interaction):
        assert self.custom_id is not None
        await self.button_clicked_callback(
            interaction=interaction, custom_id=self.custom_id
        )


class DropdownSelectedCallback(Protocol):
    async def __call__(
        self, *, interaction: Interaction, custom_id: str, values: List[str]
    ) -> None: ...


class BaseDropdown(ui.Select[Any]):
    def __init__(
        self,
        *,
        custom_id: str,
        options: Dict[str, str],
        placeholder: Optional[str],
        row: Optional[int],
        min_values: int,
        max_values: int,
        disabled: bool,
        emojis: Optional[Dict[str, str]],
        dropdown_selected_callback: DropdownSelectedCallback,
    ):
        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            row=row,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
        )

        emojis = emojis or {}
        for value, label in options.items():
            self.add_option(label=label, value=value, emoji=emojis.get(value, None))

        self.dropdown_selected_callback = dropdown_selected_callback

    async def callback(self, interaction: Interaction):
        await self.dropdown_selected_callback(
            interaction=interaction, custom_id=self.custom_id, values=self.values
        )
