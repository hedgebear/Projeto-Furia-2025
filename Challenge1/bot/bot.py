import logging
import os
import random
import requests
import tweepy
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
STRAFE_API_KEY = os.getenv("STRAFE_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# CS API endpoints
PANDASCORE_API_URL = "https://api.pandascore.co/csgo/v2"
STRAFE_API_URL = "https://api.strafe.com/v1"

# Twitter API setup
twitter_client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

async def get_upcoming_matches():
    try:
        # Using PandaScore API to get upcoming matches
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        response = requests.get(
            f"{PANDASCORE_API_URL}/teams/4401/matches/upcoming",  # 4401 is FURIA's PandaScore ID
            headers=headers,
            params={"per_page": 5}
        )
        if response.status_code == 200:
            matches = response.json()
            return [f"🗓️ {match['opponent']['name']} vs FURIA - {match['scheduled_at']} ({match['league']['name']})" 
                   for match in matches]
        return ["Não foi possível obter os próximos jogos no momento."]
    except Exception as e:
        logger.error(f"Error fetching upcoming matches: {e}")
        return ["Erro ao buscar próximos jogos."]

async def get_recent_results():
    try:
        # Using PandaScore API to get recent results
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        response = requests.get(
            f"{PANDASCORE_API_URL}/teams/4401/matches/past",  # 4401 is FURIA's PandaScore ID
            headers=headers,
            params={"per_page": 5}
        )
        if response.status_code == 200:
            matches = response.json()
            return [f"🏆 {match['opponent']['name']} {match['results'][0]['score']} x {match['results'][1]['score']} FURIA" 
                   for match in matches]
        return ["Não foi possível obter os resultados recentes no momento."]
    except Exception as e:
        logger.error(f"Error fetching recent results: {e}")
        return ["Erro ao buscar resultados recentes."]

async def get_current_roster():
    try:
        # Using PandaScore API to get current roster
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        response = requests.get(
            f"{PANDASCORE_API_URL}/teams/4401/players",  # 4401 is FURIA's PandaScore ID
            headers=headers
        )
        if response.status_code == 200:
            players = response.json()
            return [f"👤 {player['nickname']} - {player['first_name']} {player['last_name']}" 
                   for player in players]
        return ["Não foi possível obter o elenco atual no momento."]
    except Exception as e:
        logger.error(f"Error fetching roster: {e}")
        return ["Erro ao buscar elenco."]

async def get_recent_tweets():
    try:
        tweets = twitter_client.get_users_tweets(
            id="9215",
            max_results=5,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if tweets.data:
            return [f"🐦 {tweet.text}\n📅 {tweet.created_at.strftime('%d/%m/%Y %H:%M')}\n❤️ {tweet.public_metrics['like_count']} likes" 
                   for tweet in tweets.data]
        return ["Não foi possível obter tweets recentes no momento."]
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        return ["Erro ao buscar tweets recentes."]

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bem-vindo(a) ao Bot da FURIA!\n\n"
        "Use os comandos abaixo para explorar:\n"
        "/elenco - Ver elenco atual\n"
        "/jogos - Próximos jogos\n"
        "/resultados - Últimos resultados\n"
        "/curiosidade - Fatos sobre a FURIA\n"
        "/frase - Frase motivacional\n"
        "/quiz - Teste seu conhecimento"
    )

async def elenco_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roster = await get_current_roster()
    await update.message.reply_text("👥 Elenco Atual da FURIA:\n" + "\n".join(roster))

async def jogos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matches = await get_upcoming_matches()
    await update.message.reply_text("📆 Próximos jogos:\n" + "\n".join(matches))

async def resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = await get_recent_results()
    await update.message.reply_text("🏆 Últimos jogos:\n" + "\n".join(results))

async def curiosidade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tweets = await get_recent_tweets()
    if tweets and tweets[0] != "Erro ao buscar tweets recentes.":
        await update.message.reply_text("🐦 Últimos tweets da FURIA:\n\n" + "\n\n".join(tweets))
    else:
        # Fallback to hardcoded curiosities if Twitter API fails
        curiosidades = [
            "A FURIA foi fundada em 2017 e já participou de vários Majors.",
            "A line da FURIA é uma das mais estáveis do cenário BR.",
            "FalleN trouxe muita experiência ao time ao entrar como IGL.",
            "FURIA é conhecida pelo estilo agressivo e ousado de jogo.",
            "FURIA foi o primeiro time brasileiro a ter uma casa de treino nos EUA.",
            "O nome FURIA vem da filosofia agressiva e ousada de jogar CS.",
            "KSCERATO recusou ofertas internacionais pra ficar no projeto da FURIA."
        ]
        await update.message.reply_text("🤔 " + random.choice(curiosidades))

async def frase_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    frases = [
        "Ser FURIA é lutar até o fim. 💪",
        "Aqui é FURIA, irmão. Ninguém joga com medo! 🔥",
        "A vitória começa na mente. 🧠",
        "Confia no processo. Vai dar bom. ⚡",
        "Seja o leão da selva, não a presa. – FURIA",
        "Nunca duvide de um time com garra.",
        "Respeita a cal! 🔥"
    ]
    await update.message.reply_text("💬 " + random.choice(frases))

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 Quiz Rápido: Qual o jogador mais antigo da FURIA?")

# Initialize bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("elenco", elenco_cmd))
    app.add_handler(CommandHandler("jogos", jogos_cmd))
    app.add_handler(CommandHandler("resultados", resultados))
    app.add_handler(CommandHandler("curiosidade", curiosidade_cmd))
    app.add_handler(CommandHandler("frase", frase_cmd))
    app.add_handler(CommandHandler("quiz", quiz))

    # Run app
    logger.info("🤖 Bot da FURIA rodando...")
    app.run_polling()
