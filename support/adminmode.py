from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Message, Chat


support_admin_router = Router()

@support_admin_router.message(Command(commands=["get", "who"]), F.reply_to_message)
async def get_user_info(message: Message, bot: Bot):

    def get_full_name(chat: Chat):
        if not chat.first_name:
            return ""
        if not chat.last_name:
            return chat.first_name
        return f"{chat.first_name} {chat.last_name}"

    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        return await message.reply(str(ex))

    try:
        user = await bot.get_chat(user_id)
    except TelegramAPIError as ex:
        await message.reply(
                msg_id="cannot-get-user-info-error",
                args={"error": ex.message})
        return

    u = f"@{user.username}" if user.username else "no"
    await message.reply(
            msg_id="user-info",
            args={
                "name": get_full_name(user),
                "id": user.id,
                "username": u
            }
        )
    
def extract_id(message: Message) -> int:
    entities = message.entities or message.caption_entities
    
    if not entities or entities[-1].type != "hashtag":
        raise ValueError("Не удалось извлечь ID для ответа!")
    hashtag = entities[-1].extract_from(message.text or message.caption)
    
    if len(hashtag) < 4 or not hashtag[3:].isdigit(): 
        raise ValueError("Некорректный ID для ответа!")
    return int(hashtag[3:])



        
        
@support_admin_router.message(F.reply_to_message)
async def reply_to_user(message: Message):
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        return await message.reply(str(ex))

    try:
        await message.copy_to(user_id)
    except TelegramAPIError as ex:
        await message.reply(
                msg_id="cannot-answer-to-user-error",
                args={"error": ex.message})
        