# Bro Genie Bot

Bro Genie Bot is a feature-rich Telegram bot that generates personalized, artistic wizard images using OpenAI's DALL-E, adds customizable watermarks, and delivers them to users with a seamless experience. It integrates Telegram messaging, OpenAI's image generation capabilities, and a user-friendly watermarking feature.

## Features

- **Dynamic Image Generation**: Create stunning, personalized wizard images based on user prompts.
- **Customizable Watermarks**: Add watermarks to images with position options via inline buttons.
- **Logging and Debugging**: Comprehensive logging to track bot operations and debug issues.
- **Environment Configuration**: Easy setup using `.env` for storing sensitive keys.
- **User-friendly Interaction**: Real-time feedback and intuitive steps during image generation and watermarking.

## Requirements

- Python 3.8+
- Telegram Bot API credentials
- OpenAI API key
- Required Python libraries (listed in `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ShallIfy/bro-genie-bot.git
   cd bro-genie-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add the following environment variables:
   ```env
   API_ID=<your_telegram_api_id>
   API_HASH=<your_telegram_api_hash>
   BOT_TOKEN=<your_telegram_bot_token>
   OPENAI_API_KEY=<your_openai_api_key>
   ```

5. Ensure that the `img/bro_logo.png` file exists for watermarking purposes.

## Usage

1. Start the bot:
   ```bash
   python main.py
   ```

2. Mention the bot in a Telegram chat with an activity prompt, for example:
   ```
   @BroGenie_bot battling a dragon
   ```

3. The bot will generate an artistic wizard image and ask you to choose a watermark position.

4. Once a position is selected, the bot will finalize the image and send it to you with details about the process.

## File Structure

```
project-root/
├── main.py               # Main bot script
├── requirements.txt      # List of dependencies
├── .env                  # Environment variables
├── img/
│   └── bro_logo.png      # Default watermark image
├── bot_debug.log         # Log file for debugging
└── README.md             # Project documentation
```

## Logging

- Logs are stored in `bot_debug.log` and include detailed information about the bot's operations.
- Logging levels can be adjusted in the `logging.basicConfig` configuration.

## Customization

- **Prompts**: Modify the `generate_image` function to customize the prompts sent to OpenAI's API.
- **Watermark**: Replace the default `img/bro_logo.png` with your desired watermark.
- **Button Layout**: Update the `buttons` variable to change the inline button options.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for feature requests or bug reports.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Telethon](https://docs.telethon.dev/) for Telegram client API.
- [OpenAI](https://openai.com/) for their amazing DALL-E API.
- The Python community for the excellent libraries used in this project.

## Disclaimer

This bot is intended for educational and personal use. Ensure you comply with Telegram and OpenAI's terms of service while using this project.
