import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = "8118913866:AAEVKeud9EPr36gb_A4g_WSrr9QI7nPSD68"

# Вопросы и ответы
questions = [
    {"question": "В каком году стартовала телевизионная Премьер-Лига КВН?", "options": ["2001", "2002", "2003", "2003"],
     "correct": 2},
    {"question": "Кто не становился чемпионом Первой Лиги КВН?", "options": ["Сборная Забойкальского края", "Евразия", "Плюшки", "Ингеборга Дапкунайте"],
     "correct": 2},
    {"question": "Кто дольше всех редактировал Премьер-Лигу КВН?", "options": ["Валентин Иванов", "Михаил Гуликов", "Евгений Донских", "Алексей Ляпичев"],
     "correct": 1},
    {"question": "В каком году Прима стала чемпионом Высшей Лиги КВН?", "options": ["2006", "2007", "2008", "2009"],
     "correct": 3},
    {"question": "Какой команде принадлежит шутка: — Я — это лучшее, что было в твоей жизни. — Это говорит не о твоих достоинствах, а о недостатках моей жизни.", "options": ["ЛУНА", "Будем Дружить Семьями", "Сборная Малых Народов", "Мегаполис"],
     "correct": 3},
    {"question": "Какая команда имеет самое большое количество выигранных КиВиНов?", "options": ["Максимум", "РУДН", "Русская Дорога", "Уральские Пельмени"],
     "correct": 1},
    {"question": "В каком году Голосящий КиВиН переехал в Светлогорск?", "options": ["2013", "2014", "2015", "2017"],
     "correct": 2},
    {"question": "Какая команда подряд выиграла Премьер-Лигу и Высшую лигу КВН?", "options": ["СОК", "Мегаполис", "Максимум", "Так-То"],
     "correct": 1},
    {"question": "Какой город представляла команда КВН Монди?", "options": ["Сыктывкар", "Саратов", "Смоленск", "Алупка"],
     "correct": 0},
    {"question": "Какая команда выиграла в конкурсе - перетягивание каната?",
     "options": ["СОК", "Максимум", "Казахи", "Пирамида"],
     "correct": 3},
    {"question": "По мнению команды КВН Станция Спортивная, именно он убийца.",
     "options": ["Садовник", "Проводник", "Почтальон", "Детектив"],
     "correct": 1},
    {"question": "Какая команда стала первым чемпионом возраждённого КВН?",
     "options": ["НГУ", "МГУ", "Парни из Баку", "Одесские джентльмены"],
     "correct": 3},
    {"question": "Сколько лет исполнится КВН в 2025 году?",
     "options": ["62", "63", "64", "65"],
     "correct": 2},
    {"question": "Какую команду вернул своим решением в конкурсе биатлон Константин Эрнст?",
     "options": ["Наполеоны", "Русская Дорога", "Так-То", "Сборная Татнефти"],
     "correct": 2},
    {"question": "Какая команда в 2013 году набрала в игре больше баллов, но в финал взяли другую?",
     "options": ["Физтех", "Плохая Компания", "Днепр", "Сборная Дагестана"],
     "correct": 0},
    {"question": "За какую команду КВН играла Пелагея?",
     "options": ["Уральские Пельмени", "НГУ", "Театр ДГУ", "Дети лейтенанта Шмидта"],
     "correct": 1},
    {"question": "В каком году Александр Васильевич Масляков перестал вести Высшую Украинскую Лигу?",
     "options": ["2010", "2011", "2012", "2013","2014"],
     "correct": 3},
    {"question": "В какой команде раньше начал играть Дмитрий Бушуев?",
     "options": ["25-ая", "Вятка Автомат", "Сборная Ульяновской области", "Махачкалинские Бродяги"], "correct": 1},
    {"question": "В каком году возродился КВН?", "options": ["1983", "1984", "1985", "1986"], "correct": 3},
    {"question": "Кто стал чемпионом Премьер-Лиги КВН в 2016 году?",
     "options": ["Сборная Грузии", "НАТЕ", "Театр Уральского Зрителя", "Физтех", "Саратов"], "correct": 1},
]
# Админ ID (замени на свой Telegram ID)
ADMIN_ID = 538226846


async def admin_panel(update: Update, context: CallbackContext) -> None:
    """Админ-панель для управления вопросами"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для доступа к админ-панели.")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Добавить вопрос", callback_data="add_question")],
        [InlineKeyboardButton("✏️ Редактировать вопрос", callback_data="edit_question")],
        [InlineKeyboardButton("🗑 Удалить вопрос", callback_data="delete_question")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ Админ-панель:", reply_markup=reply_markup)


async def admin_callback(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатий в админ-панели"""
    query = update.callback_query
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет прав на это действие.", show_alert=True)
        return

    action = query.data
    if action == "add_question":
        await query.message.reply_text(
            "✏️ Введите новый вопрос в формате: Вопрос | Ответ1, Ответ2, Ответ3, Ответ4 | Номер правильного ответа (0-3)")
        context.user_data["admin_action"] = "add"
    elif action == "edit_question":
        await query.message.reply_text("📋 Список вопросов:")
        for i, q in enumerate(questions):
            await query.message.reply_text(f"{i + 1}. {q['question']}")
        await query.message.reply_text("✏️ Введите номер вопроса для редактирования:")
        context.user_data["admin_action"] = "edit"
    elif action == "delete_question":
        await query.message.reply_text("📋 Список вопросов:")
        for i, q in enumerate(questions):
            await query.message.reply_text(f"{i + 1}. {q['question']}")
        await query.message.reply_text("🗑 Введите номер вопроса для удаления:")
        context.user_data["admin_action"] = "delete"

    await query.answer()
# Храним прогресс, результаты и задачи с таймерами
user_progress = {}
user_scores = {}
user_timers = {}
leaderboard = []
user_attempts = {}


async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_username = update.effective_user.username or "Аноним"
    current_time = time.time()

    # Проверяем, проходил ли пользователь тест за последние 24 часа
    if user_id in user_attempts and current_time - user_attempts[user_id] < 86400:
        await update.message.reply_text("❌ Вы уже проходили тест сегодня. Попробуйте снова завтра!")
        return

    user_attempts[user_id] = current_time
    user_progress[user_id] = 0
    user_scores[user_id] = {"correct": 0, "incorrect": 0, "start_time": current_time, "username": user_username}
    await send_question(update, context, user_id)


async def send_question(update: Update, context: CallbackContext, user_id: int):
    """Отправка вопроса пользователю с таймером"""
    index = user_progress.get(user_id, 0)
    if index >= len(questions):
        await send_results(update, user_id)
        return

    question_data = questions[index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(question_data["options"])]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await update.effective_message.reply_text(f"⏳ {question_data['question']}", reply_markup=reply_markup)
    user_timers[user_id] = asyncio.create_task(answer_timeout(update, context, user_id, msg, question_data))


async def answer_timeout(update: Update, context: CallbackContext, user_id: int, msg, question_data):
    """Таймер с обратным отсчетом."""
    time_left = 30
    while time_left > 0:
        await asyncio.sleep(1)
        time_left -= 1
        try:
            await msg.edit_text(f"⏳ {question_data['question']}\nОсталось: {time_left} сек",
                                reply_markup=msg.reply_markup)
        except:
            break

    if user_id in user_progress and user_progress[user_id] < len(questions):
        user_scores[user_id]["incorrect"] += 1
        try:
            await msg.delete()
        except:
            pass

        await update.effective_message.reply_text("⏳ Время на вопрос истекло!")
        user_progress[user_id] += 1
        if user_progress[user_id] < len(questions):
            await send_question(update, context, user_id)
        else:
            await send_results(update, user_id)


async def button_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора варианта ответа"""
    query = update.callback_query
    user_id = query.from_user.id
    index = user_progress.get(user_id, 0)

    if index >= len(questions):
        return

    if user_id in user_timers:
        user_timers[user_id].cancel()
        del user_timers[user_id]

    question_data = questions[index]
    selected_option = int(query.data)
    correct_option = question_data["correct"]

    if selected_option == correct_option:
        reply_text = "✅ Правильно!"
        user_scores[user_id]["correct"] += 1
    else:
        reply_text = f"❌ Неправильно. Правильный ответ: {question_data['options'][correct_option]}"
        user_scores[user_id]["incorrect"] += 1

    await query.answer()
    await query.edit_message_text(text=f"{question_data['question']}\n\n{reply_text}")

    user_progress[user_id] += 1

    # Добавляем задержку перед следующим вопросом
    await asyncio.sleep(2)

    if user_progress[user_id] < len(questions):
        await send_question(update, context, user_id)
    else:
        await send_results(update, user_id)



async def send_results(update: Update, user_id: int):
    """Отправка результатов теста"""
    user_username = user_scores[user_id]["username"]
    correct = user_scores[user_id]["correct"]
    incorrect = user_scores[user_id]["incorrect"]
    elapsed_time = time.time() - user_scores[user_id]["start_time"]

    leaderboard.append({"username": user_username, "score": correct, "time": elapsed_time})
    leaderboard.sort(key=lambda x: (-x["score"], x["time"]))
    top_10 = leaderboard[:10]
    total_users = len(set(user["username"] for user in leaderboard))  # Количество уникальных пользователей

    leaderboard_text = "\n".join(
        [f"{i + 1}. {user['username']} - {user['score']} баллов ({user['time']:.2f} сек)" for i, user in
         enumerate(top_10)])

    result_text = (
        f"🎉 Тест завершен!\n👤 Логин: {user_username}\n✅ Правильных ответов: {correct}\n❌ Неправильных ответов: {incorrect}\n"
        f"⏳ Время прохождения: {elapsed_time:.2f} сек\n\n🏆 ТОП-10 участников:\n{leaderboard_text}\n\n📊 Всего пользователей прошли тест: {total_users}")

    await update.effective_message.reply_text(result_text)


async def view_leaderboard(update: Update, context: CallbackContext) -> None:
    """Отображение рейтинга по запросу"""
    leaderboard.sort(key=lambda x: (-x["score"], x["time"]))
    top_10 = leaderboard[:10]
    total_users = len(set(user["username"] for user in leaderboard))

    leaderboard_text = "\n".join(
        [f"{i + 1}. {user['username']} - {user['score']} баллов ({user['time']:.2f} сек)" for i, user in
         enumerate(top_10)])

    result_text = f"🏆 ТОП-10 участников:\n{leaderboard_text}\n\n📊 Всего пользователей прошли тест: {total_users}"

    await update.message.reply_text(result_text)


def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("top10", view_leaderboard))
    app.add_handler(CallbackQueryHandler(button_handler))  # Исправлено: callback_router заменён на button_handler
    print("✅ Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
