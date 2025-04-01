# Auto-Gif-Search

A real-time chat application with intelligent GIF suggestions powered by CLIP and Giphy API.

## Features

- Real-time chat between two users
- Intelligent GIF suggestions based on:
  - User messages
  - Generated replies
  - Sentiment analysis
- CLIP-powered semantic search for relevant GIFs
- Giphy API integration for high-quality GIFs
- Sentiment analysis for better context understanding

## Tech Stack

- Backend:
  - Python/Flask
  - CLIP (Contrastive Language-Image Pre-training)
  - Giphy API
  - NLTK for text processing
- Frontend (Coming Soon):
  - React
  - WebSocket for real-time communication
  - Modern UI with GIF previews

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Auto-Gif-Search.git
cd Auto-Gif-Search
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Create a `.env` file in the root directory
- Add your Giphy API key:
```
GIPHY_API_KEY=your_api_key_here
```

4. Run the backend server:
```bash
python src/main.py
```

The server will start on `http://localhost:5001`

## API Endpoints

- `POST /send_message_user2`: Send a message from User 2
- `POST /generate_reply_and_gifs`: Generate reply and get GIF suggestions
- `GET /`: Welcome message

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
