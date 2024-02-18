from asyncio import get_event_loop, create_task, gather
import re
from typing import List
from aiohttp import ClientSession

TELEPHONE_REGEX = re.compile(r"\b(?:\+7|7|8)?\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}\b")
MOSCOW_PHONE_CODE = ["8", "4", "9", "5"]


def transform_tel(phone_number: str):
    """Converting a telephone number to the required format 8KKKNNNNNNN"""
    required_format_phone = list(re.sub(r"[^0-9]", "", phone_number))
    if len(required_format_phone) == 10:
        required_format_phone.insert(0, "8")
    elif len(required_format_phone) == 7:
        required_format_phone = MOSCOW_PHONE_CODE + required_format_phone
    elif required_format_phone[0] == "7":
        required_format_phone[0] = "8"
    return "".join(required_format_phone)


async def get_phones(client: ClientSession, url: str):
    """Executes a request to a specified URL, extracts phone numbers from the HTML code of a page, and removes
    duplicates. """
    async with client.get(url) as response:
        html = await response.text()
        list_phone_numbers = TELEPHONE_REGEX.findall(html)
        list_of_unique_phone_numbers = list(set(list_phone_numbers))
        return url, list(set(transform_tel(phone_number) for phone_number in list_of_unique_phone_numbers))


async def start_parsing(urls: List[str]):
    """Creating and running multiple tasks"""
    async with ClientSession() as session:
        tasks = [create_task(get_phones(session, url)) for url in urls]
        return await gather(*tasks)


def main():
    urls = ['https://hands.ru/company/about', 'https://repetitors.info']
    result = get_event_loop().run_until_complete(start_parsing(urls))
    print(result)


if __name__ == '__main__':
    main()
