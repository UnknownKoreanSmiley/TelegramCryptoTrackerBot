# TelegramCryptoTracker

## Description
TelegramCryptoTracker is a Telegram bot that provides live cryptocurrency market data using the Whitebit API. Users can access a list of available cryptocurrencies and receive real-time price updates along with graphical representations of price trends.

## Screenshot
<p float="left">
  <img src="https://github.com/UnknownKoreanSmiley/TelegramCryptoTrackerBot/blob/master/screenshot/Screenshot%202024-02-18%20175716.png" width="400" alt="Screenshot 1" />
  <img src="https://github.com/UnknownKoreanSmiley/TelegramCryptoTrackerBot/blob/master/screenshot/Screenshot%202024-02-18%20175726.png" width="400" alt="Screenshot 2" />
</p>

## Features
- **Live Price Updates**: Get real-time updates on cryptocurrency prices.
- **Interactive Interface**: Easily navigate through available cryptocurrencies using interactive buttons.
- **Graphical Representation**: View graphical representations of price trends for selected cryptocurrencies.
- **WebSocket Integration**: Utilizes WebSocket for efficient and real-time data transmission.

## Setup Instructions
1. Clone the repository: `git clone https://github.com/dhruvin771/TelegramCryptoTracker.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file based on the provided `.env.example` and add your Telegram Bot token and chat ID.
4. Obtain a Telegram Bot token from BotFather on Telegram.
5. Find your chat ID using Rose-Bot on Telegram.
6. Run the bot: `python bot.py`

## Usage
- **/start**: Initiate the bot and receive a welcome message.
- **/coins**: Display a list of available cryptocurrencies.
- **Selecting a Coin**: Upon choosing a cryptocurrency from the list, the bot will provide live price updates and a graphical representation of its price trend.
- **Navigating Through Coins**: Use the "Next" and "Previous" buttons to navigate through the list of cryptocurrencies.
- **Closing WebSocket Connection**: Use the "Close" button to terminate the WebSocket connection and stop receiving updates.

## Technologies Used
- Python
- Telebot (Telegram Bot API wrapper)
- Websockets
- Whitebit API

## Contributing
Contributions are welcome! If you'd like to contribute to TelegramCryptoTracker, please fork the repository, make your changes, and submit a pull request.

## Credits
TelegramCryptoTracker utilizes the Whitebit API for accessing cryptocurrency market data.

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). Feel free to modify and distribute it according to the terms of the license.
