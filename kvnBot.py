import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = "8118913866:AAH4rioUioiN37NjvaowIjJUQq0Sdi_NpGY"

# Вопросы и ответы
questions = [
    {"question": "В каком году Прима стала чемпионом Высшей Лиги КВН?", "options": ["2006", "2007", "2008", "2009"],
     "correct": 3},
    {"question": "В какой команде раньше начал играть Дмитрий Бушуев",
     "options": ["25-ая", "Вятка Автомат", "Сборная Ульяновской области"], "correct": 1},
]

# Храним прогресс, результаты и задачи с таймерами
user_progress = {}
user_scores = {}
user_timers = {}


async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_progress[user_id] = 0  # Начинаем с первого вопроса
    user_scores[user_id] = {"correct": 0, "incorrect": 0}  # Обнуляем счет

    await send_question(update, context, user_id)


async def send_question(update: Update, context: CallbackContext, user_id: int):
    """Отправка вопроса пользователю с таймером"""
    index = user_progress.get(user_id, 0)

    if index >= len(questions):  # Если тест закончен
        correct = user_scores[user_id]["correct"]
        incorrect = user_scores[user_id]["incorrect"]
        result_text = f"🎉 Тест завершен!\n✅ Правильных ответов: {correct}\n❌ Неправильных ответов: {incorrect}"

        if update.message:
            await update.message.reply_text(result_text)
        elif update.callback_query:
            await update.callback_query.message.reply_text(result_text)

        return

    question_data = questions[index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(question_data["options"])]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        msg = await update.message.reply_text(f"⏳ {question_data['question']}\nОсталось: 30 секунд", reply_markup=reply_markup)
    elif update.callback_query:
        msg = await update.callback_query.message.reply_text(f"⏳ {question_data['question']}\nОсталось: 30 секунд", reply_markup=reply_markup)

    # Запуск таймера с обратным отсчетом (1 сек)
    if user_id in user_timers:
        user_timers[user_id].cancel()  # Отменяем предыдущий таймер

    user_timers[user_id] = asyncio.create_task(answer_timeout(update, context, user_id, msg, question_data))


async def answer_timeout(update: Update, context: CallbackContext, user_id: int, msg, question_data):
    """Таймер с обратным отсчетом. Если время истекло, засчитываем неправильный ответ."""
    time_left = 30
    while time_left > 0:
        await asyncio.sleep(1)  # Обновляем каждую секунду
        time_left -= 1
        try:
            await msg.edit_text(f"⏳ {question_data['question']}\nОсталось: {time_left} секунд", reply_markup=msg.reply_markup)
        except:
            break  # Если сообщение уже изменено, выходим

    # Если пользователь не ответил - засчитываем ошибку
    if user_id in user_progress and user_progress[user_id] < len(questions):
        user_scores[user_id]["incorrect"] += 1  # Засчитываем неправильный ответ
        await msg.reply_text("⏳ Время вышло! Ответ не получен. Переход к следующему вопросу.")

        # Переход к следующему вопросу
        user_progress[user_id] += 1
        await send_question(update, context, user_id)


async def button_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора варианта ответа"""
    query = update.callback_query
    user_id = query.from_user.id
    index = user_progress.get(user_id, 0)

    if index >= len(questions):
        return

    # Останавливаем таймер, так как ответ получен
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

    # Переход к следующему вопросу
    user_progress[user_id] += 1
    if user_progress[user_id] < len(questions):
        await send_question(update, context, user_id)
    else:
        correct = user_scores[user_id]["correct"]
        incorrect = user_scores[user_id]["incorrect"]
        result_text = f"🎉 Тест завершен!\n✅ Правильных ответов: {correct}\n❌ Неправильных ответов: {incorrect}"
        await query.message.reply_text(result_text)


def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
