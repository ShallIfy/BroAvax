import os
import asyncio
import openai
import requests
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv
from PIL import Image, ImageEnhance
import logging
from datetime import datetime

# -------------------------------
# Configuration and Setup
# -------------------------------

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_debug.log"),  # Log to file
        logging.StreamHandler()               # Log to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verify that all required environment variables are set
if not all([API_ID, API_HASH, BOT_TOKEN, OPENAI_API_KEY]):
    logger.error("Missing one or more environment variables (API_ID, API_HASH, BOT_TOKEN, OPENAI_API_KEY).")
    exit()

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY
logger.debug("OpenAI API key loaded successfully.")

# Initialize Telethon client
try:
    client = TelegramClient('bro_genie_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    logger.info("Telethon client initialized successfully.")
except Exception as e:
    logger.exception(f"Failed to initialize Telethon client: {e}")
    exit()

# Dictionary to track processing message IDs for each original message ID
processing_messages = {}

# -------------------------------
# Helper Functions
# -------------------------------

def download_image(image_url, save_path):
    """
    Downloads an image from a URL and saves it locally.
    """
    logger.debug(f"Attempting to download image from URL: {image_url}")
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            logger.info(f"Image downloaded successfully! Saved as: {save_path}")
            return True
        else:
            logger.error(f"Failed to download image. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.exception(f"Exception occurred while downloading image: {e}")
        return False

def resize_watermark(watermark_path, size=(150, 150)):
    """
    Resizes the watermark image to the given size.
    """
    logger.debug(f"Resizing watermark from path: {watermark_path} to size: {size}")
    try:
        watermark = Image.open(watermark_path).convert("RGBA")
        resized = watermark.resize(size, Image.Resampling.LANCZOS)
        logger.info("Watermark resized successfully.")
        return resized
    except Exception as e:
        logger.exception(f"Exception occurred while resizing watermark: {e}")
        return None

def add_watermark(base_image_path, watermark, position):
    """
    Adds a watermark to the image at the specified position with padding and transparency.
    """
    logger.debug(f"Adding watermark to image: {base_image_path} at position: {position}")
    try:
        base_image = Image.open(base_image_path).convert("RGBA")
        
        # Apply transparency (70% brightness for 30% transparency)
        watermark = ImageEnhance.Brightness(watermark).enhance(0.7)

        # Define positions with padding
        positions = {
            "top left": (50, 50),
            "top right": (base_image.width - watermark.width - 50, 50),
            "bottom left": (50, base_image.height - watermark.height - 50),
            "bottom right": (base_image.width - watermark.width - 50, base_image.height - watermark.height - 50)
        }

        pos = positions.get(position.lower())
        if not pos:
            logger.warning(f"Invalid position '{position}'. Defaulting to 'bottom right'.")
            pos = positions["bottom right"]

        logger.debug(f"Calculated watermark position: {pos}")

        # Paste watermark with transparency
        base_image.paste(watermark, pos, watermark)

        # Save the final image
        final_path = f"final_image_{os.getpid()}.png"
        base_image.save(final_path, format="PNG")
        logger.info(f"Watermark added successfully! Saved as: {final_path}")
        return final_path
    except Exception as e:
        logger.exception(f"Exception occurred while adding watermark: {e}")
        return None

async def generate_image(activity, unique_id):
    """
    Generates an image based on the activity using OpenAI's DALL-E.
    """
    combined_prompt = (
        f"A sturdy dwarf wizard {activity} in a mystical foggy background. "
        "The wizard wears a golden, curved hat with glowing blue Celtic patterns and a Bitcoin symbol. "
        "His glowing blue eyes, dark stone-like skin, and a fiery golden beard stand out. "
        "He dons a blue robe with glowing golden Celtic motifs and holds a dark wooden staff "
        "topped with a glowing $BRO symbol surrounded by magical blue light. "
        "Intense flames, magical energy, and dramatic lighting fill the scene."
    )

    logger.debug("Final Prompt Sent to OpenAI:")
    logger.debug(combined_prompt)

    logger.info("Generating the image, please wait...")
    try:
        # Generate image using OpenAI API
        response = openai.Image.create(
            model="dall-e-3",
            prompt=combined_prompt,
            n=1,
            size="1792x1024"
        )
        image_url = response['data'][0]['url']
        logger.info("Image successfully generated! Downloading now...")

        save_path = f"dwarf_wizard_image_{unique_id}.png"
        success = download_image(image_url, save_path)
        if success:
            return save_path
        else:
            return None
    except Exception as e:
        logger.exception(f"An error occurred during image generation: {e}")
        return None

# -------------------------------
# Event Handlers
# -------------------------------

@client.on(events.NewMessage(pattern=r'@BroGenie_bot\s+(.+)', outgoing=False))
async def handler(event):
    """
    Handles new messages that mention @BroGenie_bot followed by an activity.
    """
    logger.debug("New message received.")
    
    # Extract the activity from the message
    activity = event.pattern_match.group(1).strip()
    logger.debug(f"Extracted activity: {activity}")

    if not activity:
        await event.reply("Please provide an activity after @BroGenie_bot. Example: @BroGenie_bot battles Lucifer")
        logger.warning("No activity provided by the user.")
        return

    # Unique identifier for this interaction (original message ID)
    original_id = event.message.id
    processing_messages[original_id] = []

    # Send initial processing message
    processing_msg = await event.reply("🧙‍♂️ Initializing the arcane sequences...")
    processing_messages[original_id].append(processing_msg.id)
    await asyncio.sleep(1)

    # Update processing message with next step
    await processing_msg.edit("🔮 Channeling mystical energies...")
    await asyncio.sleep(1)

    # Update processing message with next step
    await processing_msg.edit("✨ Conjuring your customized wizard image...")
    await asyncio.sleep(1)

    # Update processing message with final processing step
    await processing_msg.edit("🔮 Finalizing enchantments...")
    await asyncio.sleep(1)

    logger.info("Updated processing message with all steps.")

    # Generate image
    generated_image_path = await generate_image(activity, original_id)
    if not generated_image_path:
        await event.reply("❌ Failed to generate image. Please try again later.")
        logger.error("Image generation failed.")
        return

    # Prepare watermark
    watermark_path = "img/bro_logo.png"  # Ensure this path is correct
    if not os.path.exists(watermark_path):
        await event.reply("❌ Watermark image not found.")
        logger.error(f"Watermark image not found at path: {watermark_path}")
        return

    resized_watermark = resize_watermark(watermark_path)
    if not resized_watermark:
        await event.reply("❌ Failed to process watermark.")
        logger.error("Failed to resize watermark.")
        return

    # Define buttons for watermark positions using only arrows
    buttons = [
        [Button.inline("↖️", b"top_left"), Button.inline("↗️", b"top_right")],
        [Button.inline("↙️", b"bottom_left"), Button.inline("↘️", b"bottom_right")]
    ]

    # Send the generated image with buttons
    try:
        image_msg = await client.send_file(
            event.chat_id,
            generated_image_path,
            reply_to=original_id,
            buttons=buttons,
            caption="🧙‍♂️ Choose the watermark position:"
        )
        logger.info("Sent generated image with watermark position buttons to the user.")
    except Exception as e:
        logger.exception(f"Failed to send generated image with buttons: {e}")

@client.on(events.CallbackQuery)
async def callback(event):
    """
    Handles callback queries from inline buttons (watermark position selection).
    """
    logger.debug("Button clicked by the user.")

    # Acknowledge the button press to remove the loading state
    try:
        await event.answer()
        logger.debug("Acknowledged the button press.")
    except Exception as e:
        logger.exception(f"Failed to acknowledge button press: {e}")

    # Map button data to positions
    position_map = {
        b"top_left": "top left",
        b"top_right": "top right",
        b"bottom_left": "bottom left",
        b"bottom_right": "bottom right"
    }

    # Get the selected position from the button data
    position = position_map.get(event.data, "bottom right")
    logger.debug(f"Selected watermark position: {position}")

    # Retrieve the message that contains the image with buttons
    try:
        image_message = await event.get_message()
    except Exception as e:
        logger.exception(f"Failed to retrieve the message associated with the callback: {e}")
        await event.edit("❌ Failed to retrieve the image message.")
        return

    if not image_message.media:
        await event.edit("❌ No image found to process.")
        logger.error("No image found in the message to process.")
        return

    # Retrieve the original message ID to delete processing messages
    try:
        original_message = await image_message.get_reply_message()
        if not original_message:
            await event.edit("❌ Original message not found.")
            logger.error("Original message not found.")
            return
        original_id = original_message.id
    except Exception as e:
        logger.exception(f"Failed to retrieve original message: {e}")
        await event.edit("❌ Failed to retrieve the original message.")
        return

    # Edit the processing message to show watermark application steps
    try:
        processing_msg_id = processing_messages.get(original_id, [None])[0]
        if processing_msg_id:
            processing_msg = await client.get_messages(image_message.chat_id, ids=processing_msg_id)
            if processing_msg:
                await processing_msg.edit("🔍 Applying the watermark with precision...")
                await asyncio.sleep(1)
                await processing_msg.edit("🧪 Aligning the mystical symbols...")
                await asyncio.sleep(1)
                await processing_msg.edit("🎨 Ensuring optimal visual aesthetics...")
                await asyncio.sleep(1)
                logger.info("Updated processing message with watermark application steps.")
    except Exception as e:
        logger.exception(f"Failed to update processing message: {e}")
        await event.edit("❌ Failed to update the processing message.")
        return

    # Prepare watermark
    watermark_path = "img/bro_logo.png"  # Ensure this path is correct
    if not os.path.exists(watermark_path):
        await event.edit("❌ Watermark image not found.")
        logger.error(f"Watermark image not found at path: {watermark_path}")
        return

    resized_watermark = resize_watermark(watermark_path)
    if not resized_watermark:
        await event.edit("❌ Failed to process watermark.")
        logger.error("Failed to resize watermark.")
        return

    # Apply watermark
    try:
        # Download the original image
        original_image_path = await image_message.download_media()
        logger.info(f"Downloaded original image: {original_image_path}")

        final_image_path = add_watermark(original_image_path, resized_watermark, position)
        if not final_image_path:
            await event.edit("❌ Failed to add watermark.")
            logger.error("Failed to add watermark to the image.")
            return
    except Exception as e:
        logger.exception(f"Failed to apply watermark: {e}")
        await event.edit("❌ Failed to apply watermark.")
        return

    # Fetch user information from the original message
    try:
        sender = await original_message.get_sender()
        name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        username = f"@{sender.username}" if sender.username else "N/A"
        logger.debug(f"Sender's name: {name}, username: {username}")
    except Exception as e:
        logger.exception(f"Failed to retrieve sender information: {e}")
        name = "Unknown"
        username = "N/A"

    # Get current time in specified format
    generated_at = datetime.now().strftime("%d-%m-%y %I:%M %p")
    logger.debug(f"Image generated at: {generated_at}")

    # Retrieve the user's input keyword (activity)
    try:
        user_input = original_message.message.split(' ', 1)[1].strip() if ' ' in original_message.message else "N/A"
    except Exception:
        user_input = "N/A"
    user_input_italic = f"<i>{user_input}</i>"
    logger.debug(f"User input (keyword): {user_input}")

    # Construct the caption with HTML markup
    caption = (
        "<b>🧙‍♂️ Bro Artist</b>\n"
        f"├ Name : {name}\n"
        f"└ Username : {username}\n\n"
        "<b>🎨 Art Generated</b>\n"
        f"├ Generated At : {generated_at}\n"
        f"└ Keyword : {user_input_italic}\n\n"
        "Your image has been successfully processed ✅"
    )

    # Send the final image as a reply with the formatted caption
    try:
        final_image_msg = await client.send_file(
            image_message.chat_id,
            final_image_path,
            reply_to=original_id,
            caption=caption,
            parse_mode='html'
        )
        logger.info("Sent final image with formatted caption to the user.")
    except Exception as e:
        logger.exception(f"Failed to send final image to the user: {e}")
        await event.edit("❌ Failed to send the final image.")
        return

    # Remove watermark selection message (including buttons)
    try:
        await client.delete_messages(image_message.chat_id, image_message.id)
        logger.info("Deleted watermark selection message and buttons.")
    except Exception as e:
        logger.exception(f"Failed to delete watermark selection message: {e}")
        # Optionally notify the user
        await event.edit("❌ Failed to delete the watermark selection message.")
        return

    # Delete the processing message
    try:
        if processing_msg_id:
            await client.delete_messages(image_message.chat_id, processing_msg_id)
            logger.info("Deleted the processing message.")
    except Exception as e:
        logger.exception(f"Failed to delete the processing message: {e}")

    # Clean up temporary files
    try:
        os.remove(original_image_path)
        os.remove(final_image_path)
        logger.info("Temporary files deleted successfully.")
    except Exception as e:
        logger.exception(f"Error deleting temporary files: {e}")

# -------------------------------
# Start the Bot
# -------------------------------

if __name__ == "__main__":
    logger.info("Bot is starting...")
    try:
        client.run_until_disconnected()
    except Exception as e:
        logger.exception(f"Bot encountered an exception: {e}")
