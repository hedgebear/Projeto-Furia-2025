import logging
import os
import random
import requests
import tweepy
from datetime import datetime
from functools import wraps, lru_cache
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    Defaults,
    Persistence
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API endpoints
PANDASCORE_API_URL = "https://api.pandascore.co/csgo/v2"

# Twitter API setup
twitter_client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

# Decorator for error handling
def error_handler(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            return await func(update, context)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Ocorreu um erro. Tente novamente mais tarde.",
                parse_mode=ParseMode.HTML
            )
    return wrapper

# Cache for API calls
@lru_cache(maxsize=32)
async def get_upcoming_matches():
    try:
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        response = requests.get(
            f"{PANDASCORE_API_URL}/teams/4401/matches/upcoming",
            headers=headers,
            params={"per_page": 5}
        )
        if response.status_code == 200:
            matches = response.json()
            return [f"🗓️ <b>{match['opponent']['name']}</b> vs FURIA\n📅 {datetime.fromisoformat(match['scheduled_at']).strftime('%d/%m/%Y %H:%M')}\n🏆 {match['league']['name']}" 
                   for match in matches]
        return ["Não foi possível obter os próximos jogos no momento."]
    except Exception as e:
        logger.error(f"Error fetching upcoming matches: {e}")
        return ["Erro ao buscar próximos jogos."]

@lru_cache(maxsize=32)
async def get_recent_results():
    try:
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        response = requests.get(
            f"{PANDASCORE_API_URL}/teams/4401/matches/past",
            headers=headers,
            params={"per_page": 5}
        )
        if response.status_code == 200:
            matches = response.json()
            return [f"🏆 <b>{match['opponent']['name']} {match['results'][0]['score']} x {match['results'][1]['score']} FURIA</b>\n📅 {datetime.fromisoformat(match['scheduled_at']).strftime('%d/%m/%Y')}" 
                   for match in matches]
        return ["Não foi possível obter os resultados recentes no momento."]
    except Exception as e:
        logger.error(f"Error fetching recent results: {e}")
        return ["Erro ao buscar resultados recentes."]

@lru_cache(maxsize=32)
async def get_current_roster():
    try:
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        response = requests.get(
            f"{PANDASCORE_API_URL}/teams/4401/players",
            headers=headers
        )
        if response.status_code == 200:
            players = response.json()
            return [f"👤 <b>{player['nickname']}</b> - {player['first_name']} {player['last_name']}" 
                   for player in players]
        return ["Não foi possível obter o elenco atual no momento."]
    except Exception as e:
        logger.error(f"Error fetching roster: {e}")
        return ["Erro ao buscar elenco."]

@lru_cache(maxsize=32)
async def get_recent_tweets():
    try:
        tweets = twitter_client.get_users_tweets(
            id="9215",  # FURIA's Twitter ID
            max_results=5,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if tweets.data:
            return [f"🐦 <b>Tweet recente:</b>\n{tweet.text}\n📅 {tweet.created_at.strftime('%d/%m/%Y %H:%M')}\n❤️ {tweet.public_metrics['like_count']} likes" 
                   for tweet in tweets.data]
        return ["Não foi possível obter tweets recentes no momento."]
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        return ["Erro ao buscar tweets recentes."]

# Command handlers
@error_handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 Elenco", callback_data='elenco')],
        [InlineKeyboardButton("📆 Próximos Jogos", callback_data='jogos')],
        [InlineKeyboardButton("🏆 Resultados", callback_data='resultados')],
        [InlineKeyboardButton("🤔 Curiosidades", callback_data='curiosidade')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 <b>Bem-vindo(a) ao Bot Oficial da FURIA CS:GO!</b>\n\n"
        "Aqui você encontra tudo sobre o time de CS:GO da FURIA:\n"
        "- Elenco atual\n"
        "- Próximos jogos\n"
        "- Resultados recentes\n"
        "- Curiosidades e muito mais!\n\n"
        "Use os botões abaixo ou os comandos no menu:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

@error_handler
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
<b>⚡ Comandos disponíveis:</b>

/start - Inicia o bot
/help - Mostra esta mensagem
/menu - Menu interativo com botões
/elenco - Mostra o elenco atual
/jogos - Próximos jogos agendados
/resultados - Últimos resultados
/curiosidade - Fatos interessantes
/frase - Frase motivacional
/quiz - Quiz sobre a FURIA
/status - Verifica se o bot está online

<b>🔗 Links úteis:</b>
- Site oficial: https://furia.gg
- Twitter: https://twitter.com/furiagg
- Loja: https://shop.furia.gg
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

@error_handler
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 Elenco", callback_data='elenco')],
        [InlineKeyboardButton("📆 Próximos Jogos", callback_data='jogos')],
        [InlineKeyboardButton("🏆 Resultados", callback_data='resultados')],
        [InlineKeyboardButton("🤔 Curiosidades", callback_data='curiosidade')],
        [InlineKeyboardButton("💬 Frase Motivacional", callback_data='frase')],
        [InlineKeyboardButton("❓ Quiz", callback_data='quiz')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🔍 <b>O que você quer saber sobre a FURIA?</b>', reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@error_handler
async def elenco_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roster = await get_current_roster()
    await update.message.reply_text(
        "👥 <b>Elenco Atual da FURIA:</b>\n" + "\n".join(roster),
        parse_mode=ParseMode.HTML
    )

@error_handler
async def jogos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matches = await get_upcoming_matches()
    await update.message.reply_text(
        "📆 <b>Próximos jogos da FURIA:</b>\n\n" + "\n\n".join(matches),
        parse_mode=ParseMode.HTML
    )

@error_handler
async def resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = await get_recent_results()
    await update.message.reply_text(
        "🏆 <b>Últimos resultados da FURIA:</b>\n\n" + "\n\n".join(results),
        parse_mode=ParseMode.HTML
    )

@error_handler
async def curiosidade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tweets = await get_recent_tweets()
    if tweets and tweets[0] != "Erro ao buscar tweets recentes.":
        await update.message.reply_text(
            "🐦 <b>Últimos tweets da FURIA:</b>\n\n" + "\n\n".join(tweets),
            parse_mode=ParseMode.HTML
        )
    else:
        curiosidades = [
            "A FURIA foi fundada em 2017 e já participou de vários Majors.",
            "A line da FURIA é uma das mais estáveis do cenário BR.",
            "FalleN trouxe muita experiência ao time ao entrar como IGL.",
            "FURIA é conhecida pelo estilo agressivo e ousado de jogo.",
            "FURIA foi o primeiro time brasileiro a ter uma casa de treino nos EUA.",
            "O nome FURIA vem da filosofia agressiva e ousada de jogar CS.",
            "KSCERATO recusou ofertas internacionais pra ficar no projeto da FURIA."
        ]
        await update.message.reply_text(
            f"🤔 <b>Curiosidade:</b>\n\n{random.choice(curiosidades)}",
            parse_mode=ParseMode.HTML
        )

@error_handler
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
    await update.message.reply_text(
        f"💬 <b>Frase do dia:</b>\n\n{random.choice(frases)}",
        parse_mode=ParseMode.HTML
    )

@error_handler
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        {
            "question": "🎮 Qual o jogador mais antigo da FURIA atualmente?",
            "options": ["KSCERATO", "arT", "yuurih", "VINI"],
            "answer": 1  # arT
        },
        {
            "question": "🏆 Em que ano a FURIA foi fundada?",
            "options": ["2015", "2016", "2017", "2018"],
            "answer": 2  # 2017
        }
    ]
    
    q = random.choice(questions)
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"quiz_{idx}_{q['answer']}")] 
        for idx, opt in enumerate(q['options'])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"❓ <b>Quiz FURIA:</b>\n\n{q['question']}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

@error_handler
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ <b>Bot online e funcionando!</b>\n\n"
        "Todos os sistemas operacionais normalmente.",
        parse_mode=ParseMode.HTML
    )

@error_handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'elenco':
        await elenco_cmd(update, context)
    elif query.data == 'jogos':
        await jogos_cmd(update, context)
    elif query.data == 'resultados':
        await resultados(update, context)
    elif query.data == 'curiosidade':
        await curiosidade_cmd(update, context)
    elif query.data == 'frase':
        await frase_cmd(update, context)
    elif query.data == 'quiz':
        await quiz(update, context)
    elif query.data.startswith('quiz_'):
        _, answer, correct = query.data.split('_')
        if int(answer) == int(correct):
            await query.edit_message_text(
                "✅ <b>Resposta correta!</b>\n\nParabéns, você conhece bem a FURIA!",
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                "❌ <b>Resposta incorreta!</b>\n\nTente novamente!",
                parse_mode=ParseMode.HTML
            )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚠️ <b>Ocorreu um erro inesperado.</b> Os desenvolvedores foram notificados.",
        parse_mode=ParseMode.HTML
    )

def main():
    # Create application
    defaults = Defaults(parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    application = ApplicationBuilder() \
        .token(TOKEN) \
        .defaults(defaults) \
        .persistence(Persistence()) \
        .build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("elenco", elenco_cmd))
    application.add_handler(CommandHandler("jogos", jogos_cmd))
    application.add_handler(CommandHandler("resultados", resultados))
    application.add_handler(CommandHandler("curiosidade", curiosidade_cmd))
    application.add_handler(CommandHandler("frase", frase_cmd))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("status", status))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.add_error_handler(error_handler)

    # Run bot
    logger.info("🤖 Bot da FURIA CS:GO iniciado e rodando...")
    application.run_polling()

if __name__ == "__main__":
    main()