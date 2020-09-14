import asyncio
from base64 import b64encode
import configparser
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import praw

config = configparser.ConfigParser()
config.read("./config.ini")


reddit = praw.Reddit(user_agent=config["reddit"]["user_agent"],
                     client_id=config["reddit"]["client_id"], client_secret=config["reddit"]["client_secret"],
                     username=config["reddit"]["username"], password=config["reddit"]["password"])


def upload_image(image, title) -> str:
    """Uploads the image to imgur, returns the raw URL."""
    headers = {"Authorization": "Client-ID " + config["imgur"]["client_id"]}
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    url = "https://api.imgur.com/3/upload.json"
    res = requests.post(
        url,
        headers=headers,
        data={
            'image': b64encode(buffer.getvalue()),
            'type': 'base64',
            'name': '1.png',
            'title': title
        }
    )
    return "http://i.imgur.com/" + res.json()["data"]["id"] + ".png"


def draw_text(text, img) -> str:
    """Draws text onto image, uploads the edit and returns the URL"""
    base_width, base_height = img.size
    font_size = round(0.035*base_width)
    font = ImageFont.truetype("./IBMPlexSans-Medium.ttf", font_size)
    line = ""
    lines = []
    width_of_line = 0
    number_of_lines = 0
    for token in text.split():
        token = token + ' '
        token_width = font.getsize(token)[0]
        if width_of_line+token_width < base_width:
            line += token
            width_of_line += token_width
        else:
            lines.append(line)
            number_of_lines += 1
            width_of_line = 0
            line = ""
            line += token
            width_of_line += token_width
    if line:
        lines.append(line)
        number_of_lines += 1
    # create a background strip for the text
    font_height = font.getsize('|')[1]
    background = Image.new('RGBA', (base_width, round(font_height*(number_of_lines + 1))), (255, 255, 255))  # creating the black strip
    draw = ImageDraw.Draw(background)
    y_text = 0  #h
    for index, line in enumerate(lines):
        width, height = font.getsize(line)
        draw.text(((base_width - width) / 2, index*font_height), line, font=font, fill=(0, 0, 0))

        y_text += font_height
    bigger_img = Image.new("RGBA", (base_width, base_height + y_text + 2*font_height), (255, 255, 255))
    bigger_img.paste(background, (0, font_height))
    bigger_img.paste(img, (0, y_text + 2*font_height))
    return upload_image(bigger_img, text)


async def loop():
    while True:
        for message in reddit.inbox.stream():
            subject = message.subject.lower()
            if subject == 'username mention' and isinstance(message, praw.reddit.models.Comment):
                message.mark_read()
                if not message.submission.is_self:
                    try:
                        post_title = message.submission.title
                        print(f"Got new submission! Title: {post_title}")
                        response = requests.get(message.submission.url)
                        message.reply("Hey there, please check your DMs as I just sent you the link.")
                        imgur_url = draw_text(post_title, Image.open(BytesIO(response.content)))
                        message.author.message("Your requested image", "Hey there, here's the image you wanted me to put the post's title onto. " + imgur_url)
                    except Exception:
                        message.author.message("Your requested image", "Something went wrong, please try again later.")

        await asyncio.sleep(1)

loop_ = asyncio.get_event_loop()
loop_.run_until_complete(loop())
loop_.close()
