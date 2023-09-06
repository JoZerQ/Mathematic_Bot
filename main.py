import random
from aiogram import Bot, Dispatcher, types, executor
from decouple import config

bot = Bot(config("API_TOKEN"))
dp = Dispatcher(bot)

correct_answers = 0
incorrect_answers = 0
max_incorrect_answers = 5

def generate_question():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(['+', '-', '*', '/'])
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    elif operator == '*':
        answer = num1 * num2
    else:
        if num2 == 0:
            return generate_question()
        if num1 % num2 != 0:
            return generate_question()
        answer = num1 // num2
    return f"{num1} {operator} {num2} =", str(answer)

def generate_answer_options(correct_answer):
    options = [correct_answer]
    while len(options) < 4:
        random_option = str(random.randint(1, 100))
        if random_option != correct_answer and random_option not in options:
            options.append(random_option)
    random.shuffle(options)
    return options

def create_keyboard(correct_answer, options):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for option in options:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=option))
    return keyboard

user_data = {}

@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    global correct_answers, incorrect_answers
    correct_answers = 0
    incorrect_answers = 0
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"correct_answers": 0, "incorrect_answers": 0}

    await message.reply("Вітаю! Я математична гра. Відповідай на питання правильно, щоб заробити бали.")
    await ask_question(message)

async def ask_question(message: types.Message):
    global correct_answers, incorrect_answers
    question, correct_answer = generate_question()
    answer_options = generate_answer_options(correct_answer)
    keyboard = create_keyboard(correct_answer, answer_options)
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"correct_answers": 0, "incorrect_answers": 0}
    
    user_data[user_id]["question"] = question
    user_data[user_id]["correct_answer"] = correct_answer

    await message.reply(f"Який результат {question}", reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: True)
async def check_answer(callback_query: types.CallbackQuery):
    user_answer = callback_query.data
    user_id = callback_query.from_user.id

    correct_answer = user_data[user_id]["correct_answer"]

    if user_answer == correct_answer:
        user_data[user_id]["correct_answers"] += 1
        await callback_query.answer("Правильно!")
    else:
        user_data[user_id]["incorrect_answers"] += 1
        await callback_query.answer(f"Невірно. Правильна відповідь: {correct_answer}")

    if user_data[user_id]["incorrect_answers"] >= max_incorrect_answers:
        await end_game(callback_query.message)
    else:
        await ask_question(callback_query.message)

async def end_game(message: types.Message):
    user_id = message.from_user.id
    correct_answers = user_data[user_id]["correct_answers"]
    incorrect_answers = user_data[user_id]["incorrect_answers"]
    await message.reply(f"Ви досягли {incorrect_answers} неправильних відповідей. Ваша кінцева оцінка - {correct_answers} правильних відповідей та {incorrect_answers} неправильних відповідей. Дякую за гру!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

