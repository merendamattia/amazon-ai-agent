# 📝 Amazon AI Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/merendamattia/amazon-ai-agent?label=release)](https://github.com/merendamattia/amazon-ai-agent/releases)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)

An intelligent AI agent that generates detailed and professional Amazon product reviews and sales listings from product links. Powered by OpenAI's latest models with advanced web scraping and content analysis capabilities.

## ✨ Features

- 🤖 **OpenAI Integration** - Leverages GPT models for high-quality content generation
- 📝 **Product Reviews** - Generate detailed and professional Amazon product reviews
- 💼 **Sales Listings** - Create persuasive sales listings for platforms like eBay, Subito, or Facebook Marketplace
- 🔗 **Direct Link Processing** - Paste an Amazon product link and get instant output
- 📱 **Telegram Bot** - Interact with the agent directly through Telegram
- 🌐 **Web Content Extraction** - Advanced web fetching with intelligent token management
- 📊 **Smart Token Management** - Automatic content truncation for optimal performance
- 💬 **Multi-Tool Agent System** - Uses DataPizza framework for powerful agent capabilities
- 🛡️ **Error Handling** - Robust error handling and logging throughout
- ⚙️ **Configurable Models** - Easy switching between different OpenAI models

## 📋 Requirements

- **Python 3.11+**
- **OpenAI API Key**

## 🚀 Getting Started

### Installation

1. **Clone the repository and enter the directory:**
   ```bash
   git clone https://github.com/merendamattia/amazon-ai-agent.git
   cd amazon-ai-agent
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   conda create --name amazon-ai-agent-env python=3.11.13
   conda activate amazon-ai-agent-env
   ```

   Or using venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and model preference
   ```

   Your `.env` file should contain:
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4.1-mini
   ```

### Running the Application

#### CLI - Generate a review or sales listing for an Amazon product:

```bash
# Generate a review (default)
python app.py https://www.amazon.com/your-product-link

# Generate a sales listing
python app.py --type listing https://www.amazon.com/your-product-link
```

The agent will:
1. Fetch the product page content
2. Extract product information and existing reviews
3. Analyze the data using AI
4. Generate a professional, comprehensive review or sales listing

#### Telegram Bot - Interactive chat interface:
Quick start:
```bash
# 1. Update .env with TELEGRAM_BOT_TOKEN
# 2. Run the bot
python telegram_bot.py
```

Then open Telegram, find your bot, and start using it!

**Bot Features:**
- 📝 Interactive menu to generate reviews or sales listings
- 🔗 Simply paste Amazon links
- ⏳ Real-time processing status updates
- 💬 Support for long outputs (automatically split into multiple messages)
- ❌ Easy cancel option
- 💼 Choose between product reviews and sales listings

### Docker

**Telegram Bot Mode:**
```bash
docker build -t amazon-ai-agent:local .
docker run --env-file .env --restart unless-stopped amazon-ai-agent:local
```

**Docker Compose (easiest):**
```bash
# Run Telegram Bot
docker compose up
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Commit conventions
- Pull request process

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY and OPENAI_MODEL must be defined in .env"**
- Ensure your `.env` file exists and contains both variables
- Check that the file is in the project root directory

**"Connection timeout"**
- Verify your internet connection
- Check OpenAI API status at [status.openai.com](https://status.openai.com)

**"Rate limit exceeded"**
- Wait a moment before retrying
- Consider using a model with lower costs like `gpt-3.5-turbo`

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## 📞 Support

For issues, feature requests, or questions:
- Open an [issue on GitHub](https://github.com/merendamattia/amazon-ai-agent/issues)

## 🙏 Acknowledgments

- Built with [DataPizza AI Framework](https://datapizza.ai)
- Powered by [OpenAI](https://openai.com)
