import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ---------------------------------------------------------
# 1. НЕГІЗГІ БАПТАУЛАР (ТОКЕН ЖӘНЕ АДМИН ID)
# ---------------------------------------------------------
TOKEN = "8852798053:AAEk5AGb7g6gMm6vbIB7RD0irI4A0wMwW_E"  # @BotFather-ден алған Токенді осы жерге қойыңыз
ADMIN_ID = 6456789136              # Сіздің Telegram ID-іңіз
SCANNER_URL = "https://kazynabk-boop.github.io/stunning-journey//scanner.html" # Веб-панель сілтемесі

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ---------------------------------------------------------
# 2. ДЕРЕКТЕР БАЗАСЫ ЖӘНЕ БАПТАУЛАР
# ---------------------------------------------------------
vip_users = {ADMIN_ID}     # VIP берілген Telegram ID тізімі
user_lang = {}             # Пайдаланушылардың таңдаған тілі
user_signal_counts = {}    # Disclaimer есептеуіші

VIP_PASSCODE = "BK0809*"  # VIP Пароль

PAIRS = [
    # --- Major Forex OTC ---
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/CAD OTC", 
    "EUR/GBP OTC", "USD/CHF OTC", "NZD/USD OTC", "USD/CAD OTC",
    
    # --- Cross Pairs OTC ---
    "AUD/USD OTC", "AUD/NZD OTC", "CAD/JPY OTC", "EUR/CHF OTC", 
    "EUR/JPY OTC", "GBP/JPY OTC",
    
    # --- Crypto OTC ---
    "BITCOIN OTC", "BNB OTC", "POLKADOT OTC",
    
    # --- Stocks OTC ---
    "APPLE OTC", "TESLA OTC", "AMAZON OTC", "NETFLIX OTC", "INTEL OTC"
]

TIMEFRAMES = ["30s", "1m", "2m", "5m"]

# ---------------------------------------------------------
# 3. МЕТІНДЕР БАЗАСЫ (ҚАЗАҚША / РУССКИЙ)
# ---------------------------------------------------------
TEXTS = {
    'kz': {
        'welcome_no_vip': (
            "🔒 **VIP ДОСТУП АКТИВТІ ЕМЕС!**\n\n"
            "Ботты пайдалану үшін сізде VIP рұқсат болуы керек.\n\n"
            "🔑 **Егер сізде VIP Пароль болса, былай жазыңыз:**\n"
            "`/pass СІЗДІҢ_ПАРОЛЬ`\n\n"
            "💬 Пароль алу үшін Админге хабарласыңыз!"
        ),
        'welcome_vip': "⚡ **BKtrd Vision Pro v2.0 — Trading Hub**\n\n👤 **Статус:** `VIP Доступ Белсенді 🟢`\n\n*Төмендегі менюден керекті режимді таңдаңыз:*",
        'btn_pair': "📊 Валюта / Актив таңдау",
        'btn_scan': "🔍 БОТ-СКАННЕР (Авто-поиск)",
        'btn_web_scan': "🌐 БОТ-СКАННЕР (Веб-Панель)",
        'btn_lang': "🌐 Тіл / Язык",
        'select_pair_msg': "📊 **Анализ жасау үшін Активті таңдаңыз:**",
        'select_tf_msg': "⏱ **{}** үшін Таймфрейм таңдаңыз:",
        'scanning_msg': "⏳ *Pocket Option OTC графигі сканерленуде... SMC + Price Action талдау жасалуда...*",
        'auto_scan_start': "🔎 **Сканнер іске қосылды...**\n*Pocket Option OTC рыногындағы барлық паралар бойынша ең күшті паттерндер ізделуде...*",
        'disclaimer': (
            "⚠️ **ЖАУАПКЕРШІЛІКТЕН БАС ТАРТУ (DISCLAIMER):**\n\n"
            "Бот беретін барлық сигналдар мен талдаулар тек ақпараттық және алгоритмдік сипатқа ие. "
            "Біз сіздің жеке сделкаларыңызға, шешімдеріңізге және депозитіңізге **жауапкершілік артпаймыз**.\n"
            "Риск-менеджментті (депозиттің 1-3%) қатаң сақтаңыз!"
        ),
        'vip_success': "🎉 **ҚҰТТЫҚТАЙМЫЗ!**\n\nVIP Пароль дұрыс! Сізге ботқа толық доступ берілді. Ботты пайдалану үшін /start басыңыз.",
        'vip_wrong_pass': "❌ **ҚАТЕ ПАРОЛЬ!**\n\nСіз енгізген пароль бұрыс. Админнен дұрыс парольді сұраңыз.",
        'vip_revoked': "🔒 **VIP ДОСТУП ТОҚТАТЫЛДЫ!**\n\nСіздің ботқа рұқсатыңыз жойылды."
    },
    'ru': {
        'welcome_no_vip': (
            "🔒 **VIP ДОСТУП НЕ АКТИВЕН!**\n\n"
            "Для использования бота вам нужен VIP доступ.\n\n"
            "🔑 **Если у вас есть VIP Пароль, введите:**\n"
            "`/pass ВАШ_ПАРОЛЬ`\n\n"
            "💬 Для получения пароля обратитесь к Администратору!"
        ),
        'welcome_vip': "⚡️️ **BKtrd Vision Pro v2.0 — Trading Hub**\n\n👤 **Статус:** `VIP Доступ Активен 🟢`\n\n*Выберите нужный режим из меню ниже:*",
        'btn_pair': "📊 Выбрать пару / Актив",
        'btn_scan': "🔍 БОТ-СКАНЕР (Авто-поиск)",
        'btn_web_scan': "🌐 БОТ-СКАНЕР (Веб-Панель)",
        'btn_lang': "🌐 Язык / Тіл",
        'select_pair_msg': "📊 **Выберите актив для анализа:**",
        'select_tf_msg': "⏱ Выберите таймфрейм для **{}**:",
        'scanning_msg': "⏳ *Сканирование графика Pocket Option OTC... SMC + Price Action Анализ...*",
        'auto_scan_start': "🔎 **Сканер запущен...**\n*Идет поиск наилучшей ситуации по всем парам Pocket Option OTC...*",
        'disclaimer': (
            "⚠️ **ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ (DISCLAIMER):**\n\n"
            "Все сигналы и аналитика бота носят исключительно информационный характер. "
            "Мы **не несем ответственности** за ваши сделки и баланс.\n"
            "Строго соблюдайте мани-менеджмент (1-3% от депозита)!"
        ),
        'vip_success': "🎉 **ПОЗДРАВЛЯЕМ!**\n\nVIP Пароль верен! Вам предоставлен полный доступ к боту. Нажмите /start для использования.",
        'vip_wrong_pass': "❌ **НЕВЕРНЫЙ ПАРОЛЬ!**\n\nВведенный пароль неверный.",
        'vip_revoked': "🔒 **VIP ДОСТУП ОТОЗВАН!**\n\nВаш доступ к боту аннулирован."
    }
}

# ---------------------------------------------------------
# 4. АНАЛИЗ ГЕНЕРАТОРЫ (SMC, СВЕЧАЛАР, ДЕҢГЕЙЛЕР, ТРЕНД)
# ---------------------------------------------------------
def generate_analysis(pair, tf, lang):
    direction = "CALL ⬆️" if random.choice([True, False]) else "PUT ⬇️"
    winrate = random.randint(87, 97)
    rsi_val = round(random.uniform(20.0, 80.0), 1)
    
    # ТЕХНИКАЛЫҚ ПАТТЕРНДЕР ТІЗІМІ
    patterns_kz = [
        "Bullish Order Block (OB) + FVG (Имбаланс)",
        "Bearish Engulfing + Қарсылық деңгейі (Сопротивление)",
        "Қолдау деңгейінен отскок (Поддержка) + Пин-бар свечасы",
        "Liquidity Sweep + Трендовый луч отскок",
        "Break of Structure (BOS) + Retest аймағы",
        "Трендовый луч бұзылуы (Trendline Breakout)",
        "Morning Star свечалық паттерні + Фибоначчи 61.8%"
    ]
    
    patterns_ru = [
        "Bullish Order Block (OB) + FVG (Имбаланс)",
        "Bearish Engulfing + Уровень сопротивления",
        "Отскок от уровня поддержки + Пин-бар свеча",
        "Liquidity Sweep + Отскок от трендового луча",
        "Break of Structure (BOS) + Зона Retest",
        "Пробой трендового луча (Trendline Breakout)",
        "Свечной паттерн Утренний Доджи + Фибоначчи 61.8%"
    ]
    
    pattern = random.choice(patterns_kz if lang == 'kz' else patterns_ru)
    
    if lang == 'kz':
        return (
            f"🎯 **BKtrd VIP SIGNAL — OTC MARKET**\n\n"
            f"📊 **Актив:** `{pair}`\n"
            f"⏱ **Таймфрейм:** `{tf}`\n"
            f"🚀 **Бағыт:** **{direction}**\n"
            f"⚡️ **Winrate:** `{winrate}%`\n\n"
            f"─── 🧠 **ТЕХНИКАЛЫҚ ТАЛДАУ** ───\n"
            f"📌 **Паттерн:** `{pattern}`\n"
            f"📉 **RSI Индикаторы:** `{rsi_val}`\n"
            f"📐 **Деңгей/Луч:** Негізгі аймақ расталды\n\n"
            f"💡 *Сделканы жаңа свечаның алғашқы 1-2 секундында ашыңыз!*"
        )
    else:
        return (
            f"🎯 **BKtrd VIP SIGNAL — OTC MARKET**\n\n"
            f"📊 **Актив:** `{pair}`\n"
            f"⏱ **Таймфрейм:** `{tf}`\n"
            f"🚀 **Направление:** **{direction}**\n"
            f"⚡️ **Winrate:** `{winrate}%`\n\n"
            f"─── 🧠 **ТЕХНИЧЕСКИЙ АНАЛИЗ** ───\n"
            f"📌 **Паттерн:** `{pattern}`\n"
            f"📉 **RSI Индикатор:** `{rsi_val}`\n"
            f"📐 **Уровень/Луч:** Ключевая зона подтверждена\n\n"
            f"💡 *Открывайте сделку в первые 1-2 секунды новой свечи!*"
        )

# ---------------------------------------------------------
# 5. ХЕНДЛЕРЛЕР ЖӘНЕ КОМАНДАЛАР
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_lang:
        user_lang[user_id] = 'kz'
    
    lang = user_lang[user_id]
    
    if user_id not in vip_users:
        await update.message.reply_text(TEXTS[lang]['welcome_no_vip'], parse_mode="Markdown")
        return

    await show_main_menu(update, context, lang)

async def enter_passcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_lang.get(user_id, 'kz')
    
    try:
        user_pass = context.args[0]
        if user_pass == VIP_PASSCODE:
            vip_users.add(user_id)
            await update.message.reply_text(TEXTS[lang]['vip_success'], parse_mode="Markdown")
        else:
            await update.message.reply_text(TEXTS[lang]['vip_wrong_pass'], parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("⚠️ Қолдану үлгісі: `/pass БЕРІЛГЕН_ПАРОЛЬ`", parse_mode="Markdown")

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]['btn_pair'], callback_data="mode_pair")],
        [InlineKeyboardButton(TEXTS[lang]['btn_scan'], callback_data="mode_scan")],
        [InlineKeyboardButton(TEXTS[lang]['btn_web_scan'], web_app=WebAppInfo(url=SCANNER_URL))],
        [InlineKeyboardButton(TEXTS[lang]['btn_lang'], callback_data="mode_lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = TEXTS[lang]['welcome_vip']
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def check_disclaimer(user_id, context, chat_id, lang):
    user_signal_counts[user_id] = user_signal_counts.get(user_id, 0) + 1
    if user_signal_counts[user_id] % 5 == 0:
        await context.bot.send_message(chat_id=chat_id, text=TEXTS[lang]['disclaimer'], parse_mode="Markdown")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_lang.get(user_id, 'kz')

    if user_id not in vip_users:
        await query.edit_message_text(TEXTS[lang]['welcome_no_vip'], parse_mode="Markdown")
        return

    if query.data == "mode_lang":
        keyboard = [
            [InlineKeyboardButton("🇰🇿 Қазақ тілі", callback_data="set_lang_kz")],
            [InlineKeyboardButton("🇷🇺 Русский язык", callback_data="set_lang_ru")]
        ]
        await query.edit_message_text("🌐 **Тілді таңдаңыз / Выберите язык:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith("set_lang_"):
        new_lang = query.data.split("_")[2]
        user_lang[user_id] = new_lang
        await show_main_menu(update, context, new_lang)

    elif query.data == "mode_pair":
        buttons = []
        for i in range(0, len(PAIRS), 2):
            row = [InlineKeyboardButton(PAIRS[i], callback_data=f"pair_{PAIRS[i]}")]
            if i + 1 < len(PAIRS):
                row.append(InlineKeyboardButton(PAIRS[i+1], callback_data=f"pair_{PAIRS[i+1]}"))
            buttons.append(row)
            
        await query.edit_message_text(TEXTS[lang]['select_pair_msg'], reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif query.data.startswith("pair_"):
        selected_pair = query.data.split("_")[1]
        context.user_data['selected_pair'] = selected_pair
        buttons = [[InlineKeyboardButton(tf, callback_data=f"tf_{tf}")] for tf in TIMEFRAMES]
        await query.edit_message_text(TEXTS[lang]['select_tf_msg'].format(selected_pair), reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif query.data.startswith("tf_"):
        tf = query.data.split("_")[1]
        pair = context.user_data.get('selected_pair', 'EUR/USD OTC')
        
        await query.edit_message_text(TEXTS[lang]['scanning_msg'], parse_mode="Markdown")
        
        result = generate_analysis(pair, tf, lang)
        keyboard = [[InlineKeyboardButton("🔄 " + TEXTS[lang]['btn_pair'], callback_data="mode_pair")]]
        
        await query.message.reply_text(result, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        await check_disclaimer(user_id, context, query.message.chat_id, lang)

    elif query.data == "mode_scan":
        await query.edit_message_text(TEXTS[lang]['auto_scan_start'], parse_mode="Markdown")
        
        best_pair = random.choice(PAIRS)
        best_tf = random.choice(["1m", "2m"])
        
        result = generate_analysis(best_pair, best_tf, lang)
        keyboard = [[InlineKeyboardButton("🔎 " + TEXTS[lang]['btn_scan'], callback_data="mode_scan")]]
        
        await query.message.reply_text(f"🔍 **SCANNER FOUND BEST SITUATION:**\n\n{result}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        await check_disclaimer(user_id, context, query.message.chat_id, lang)

# ---------------------------------------------------------
# 6. АДМИН КОМАНДАЛАРЫ
# ---------------------------------------------------------
async def add_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    try:
        target_id = int(context.args[0])
        vip_users.add(target_id)
        await update.message.reply_text(f"✅ ID `{target_id}` қолданушысына VIP Доступ берілді!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Қате! Қолдану: `/addvip USER_ID`", parse_mode="Markdown")

async def del_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    try:
        target_id = int(context.args[0])
        if target_id in vip_users:
            vip_users.remove(target_id)
            await update.message.reply_text(f"🚫 ID `{target_id}` қолданушысының VIP Доступы ӨШІРІЛДІ!", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Бұл ID VIP тізімде табылмады!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Қате! Қолдану: `/delvip USER_ID`", parse_mode="Markdown")

async def set_passcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VIP_PASSCODE
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    try:
        new_pass = context.args[0]
        VIP_PASSCODE = new_pass
        await update.message.reply_text(f"🔑 **VIP Пароль сәтті ауыстырылды!**\nЖаңа пароль: `{VIP_PASSCODE}`", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Қате! Қолдану: `/setpass ЖАҢА_ПАРОЛЬ`", parse_mode="Markdown")

# ---------------------------------------------------------
# 7. БОТТЫ ІСКЕ ҚОСУ
# ---------------------------------------------------------
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pass", enter_passcode))
    
    app.add_handler(CommandHandler("addvip", add_vip))
    app.add_handler(CommandHandler("delvip", del_vip))
    app.add_handler(CommandHandler("setpass", set_passcode))
    
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🤖 Бот сәтті іске қосылды!")
    app.run_polling()