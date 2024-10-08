import logging
from aiogram.types import Message

import asyncio
import imaplib
import os

from email import message_from_bytes
from email.header import decode_header


from config import EMAIL, PASSWORD, SAVE_DIR, imap_server

from sqlalchemy import select
from database.models import Fires
from sqlalchemy.ext.asyncio import AsyncSession

from msg_sender import msg_sender
from utils.db_saver import save_to_db





async def decode_file_name(encoded_name):
    d_header = decode_header(encoded_name)[0]
    if isinstance(d_header[0], bytes):
        return d_header[0].decode(d_header[1] or 'utf-8')
    return d_header[0]


async def save_file(part, filename):
    filepath = os.path.join(SAVE_DIR, filename)
    await asyncio.to_thread(lambda: open(filepath, 'wb').write(part.get_payload(decode=True)))
    return filepath


async def extract_content(email_message):
    mail_content = ""
    for part in email_message.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if "attachment" not in content_disposition and content_type == "text/plain":
            mail_content += part.get_payload(decode=True).decode()
    return mail_content


async def fetch_and_save_files(session: AsyncSession):
    email_id = None
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    mail = imaplib.IMAP4_SSL(imap_server)

    await asyncio.to_thread(mail.login, EMAIL, PASSWORD)
    await asyncio.to_thread(mail.select, 'inbox')

    result, data = await asyncio.to_thread(mail.search, None, 'ALL')
    email_nums = data[0].split()


    num = email_nums[-1]
    result, email_data = await asyncio.to_thread(mail.fetch, num, '(RFC822)')
    raw_email = email_data[0][1]
    msg = message_from_bytes(raw_email)

    subject_header = msg["Subject"]
    if subject_header is not None:
        decoded_subject = decode_header(subject_header)[0][0]
        decoded_subject.decode() if isinstance(
            decoded_subject, bytes) else decoded_subject

    await extract_content(msg)

    global global_email_id
    email_id = msg["Message-ID"]
    global_email_id = email_id
    if msg.is_multipart():
        for part in msg.walk():
            part.get_content_type()
            content_disposition = part.get("Content-Disposition")
            if content_disposition and "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    filename = await decode_file_name(filename)
                    file_bytes = part.get_payload(decode=True)
                    check_email_query = select(Fires.email_id).where(
                        Fires.email_id == email_id)
                    result = await session.execute(check_email_query)
                    already_exists = result.first()
                    if already_exists is None:
                        await save_to_db(file_bytes, email_id, session)
                        await msg_sender(Message, session, email_id)

                            
                        
    await asyncio.to_thread(mail.logout)

    return email_id
