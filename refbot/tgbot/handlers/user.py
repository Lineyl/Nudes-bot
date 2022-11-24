from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.services.repository import Repo


class Withdraw(StatesGroup):
    InputCard = State()
    InputAmount = State()
    Confirm = State()


user_mm_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
user_mm_kb.row(KeyboardButton("Мои реф. ссылки 🔗"))
user_mm_kb.row(KeyboardButton("Баланс 💰"))
user_mm_kb.insert(KeyboardButton("Помощь 🆘"))
user_mm_kb.row(KeyboardButton("Реферальная программа 📈"))
user_mm_kb.row(KeyboardButton("Информация о покупках"))

balance_kb = InlineKeyboardMarkup()
balance_kb.row(InlineKeyboardButton("Вывод", callback_data="withdraw"))

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.row(KeyboardButton("Отмена"))

user_wc_cd = CallbackData("u", "action")
withdraw_confirmation_kb = InlineKeyboardMarkup()
withdraw_confirmation_kb.row(InlineKeyboardButton("Заполнить снова", callback_data=user_wc_cd.new("decline")))
withdraw_confirmation_kb.row(InlineKeyboardButton("Отправить заявку", callback_data=user_wc_cd.new("accept")))

admin_wc_cd = CallbackData("a", "user_id", "amount", "action")


def get_withdraw_kb(user_id, amount):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅Подтвердить", callback_data=admin_wc_cd.new(user_id, amount, "accept")))
    markup.row(InlineKeyboardButton("❌Отклонить", callback_data=admin_wc_cd.new(user_id, amount, "decline")))
    return markup


async def user_start(m: Message, repo: Repo, state: FSMContext):
    await state.finish()
    args = m.get_args()
    print(args)
    user = await repo.get_user(m.from_user.id)

    if not user:
        await repo.add_user(m.from_user.id, args)
        invited_by = await repo.find_user({"referral_info.code": args})
        if not invited_by:
            await m.bot.send_message(-1001542772472, f"""
<a href='tg://user?id={m.from_user.id}'>{m.from_user.full_name}</a>
ID: <code>{m.from_user.id}</code>

<code>/new_ref {m.from_user.id}</code>
<code>/set_procent {m.from_user.id}</code>
<code>/set_price {m.from_user.id}</code>
""")
        else:
            await m.bot.send_message(-1001542772472, f"""
<a href='tg://user?id={m.from_user.id}'>{m.from_user.full_name}</a>
ID: <code>{m.from_user.id}</code>
Пригласил: <a href='tg://user?id={invited_by["user_id"]}'>{invited_by["user_id"]}</a>

<code>/new_ref {m.from_user.id}</code>
<code>/set_procent {m.from_user.id}</code>
<code>/set_price {m.from_user.id}</code>
<code>/set_ref_procent {m.from_user.id}</code>
""")
        await m.answer("Запрос отправлен")
        return
    elif user["status"] == 1:
        await m.answer("Главное меню", reply_markup=user_mm_kb)
    else:
        await m.answer("Ваша заявка на вступление отправлена")


async def user_referral(m: types.Message, repo: Repo):
    user = await repo.get_user(m.from_user.id)
    text = f"""<b>Ваша реф ссылка:</b>
https://t.me/{(await m.bot.get_me()).username}?start={user['referral_info']['code']}

Пригласи покупателя в бота и получи хороший % с его дохода.

<u>3-10%</u>

Для конкретный условий напишите @burja_purga

<b>🤝Доход с друзей:</b> {user["stats"]["summary"]["profit_from_referrals"]}$
<b>🧮 Ваши рефералы:</b>\n
"""
    for counter, ref in enumerate(user["referral_info"]["referrals"], start=1):
        text += f"""{counter}) <a href='tg://user?id={ref}'>{ref}</a>
<b>Получили с пользователя: </b>{user["referral_info"]["referrals"][str(ref)]["profit"]}$
<b>Процент от прибыли:</b> {user["referral_info"]["referrals"][str(ref)]["percent"]}%

"""
    await m.answer(text)


async def user_balance(m: types.Message, repo: Repo):
    user = await repo.get_user(m.from_user.id)
    await m.answer(f"""
<b>🏦Общий баланс:</b> {user["balance"]}$
<b>🤝Доход с друга:</b> {user["stats"]["summary"]["profit_from_referrals"]}$
<b>🙇Запрошено:</b> {user["to_withdraw"]}$
<b>💰Выплачено в сумме:</b> {user["stats"]["summary"]["withdraws"]}$

🪙Минимальная сумма вывода: 6$

🧾Комиссии QIWI за перевод:
🥝QIWI карты: 2%
💳Банк. карты: 2% + 1$""", reply_markup=balance_kb)


async def user_help(m: types.Message):
    await m.answer("""
<b>По всем вопросам</b> писать @burja_purga, ответит и решит все вопросы ✅

<b>Не дошел платеж</b> в течении 30 минут <b>после одобрения</b> выплаты - сообщи @burja_purga.

<b>Информационный канал</b>, где можно найти актуальную информацию об обновлениях и ответы на многие вопросы: 
https://t.me/+WjqVF2_2yytmYWUy""", disable_web_page_preview=True)


def generate_user_links(bots, user):
    text = ""
    for counter, bot in enumerate(bots, start=1):
        text += f"""
🔗Реф. ссылка {counter}:
https://t.me/{bot["username"]}?start={user["referral_info"]["code"]}
📊Всего пользователей {user["stats"][str(bot["bot_id"])]["clicks"]}
💰Доход по ссылке(за клик): {user["stats"][str(bot["bot_id"])]["profit_from_clicks"]}$
💰Доход по ссылке(% с продаж): {user["stats"][str(bot["bot_id"])]["profit_from_purchases"]}$
"""

    text += f"""
📈Общая статистика:
📊Всего пользователей: {user["stats"]["summary"]["clicks"]}
💰Доход за клик: {user["stats"]["summary"]["profit_from_clicks"]}$
💰Общий процент: {user["stats"]["summary"]["profit_from_purchases"]}$

    """
    return text


async def user_links(m: types.Message, repo: Repo):
    bots = await repo.get_bots()
    for bot in bots:
        await repo.update_users({"stats.{}".format(bot["bot_id"]): {"$exists": False}}, {"$set": {"stats.{}".format(bot["bot_id"]): {
            "profit_from_purchases": 0,
            "purchases": 0,
            "profit_from_clicks": 0,
            "profit_from_referrals": 0,
            "withdraws": 0,
            "clicks": 0
        }}})
    user = await repo.get_user(m.from_user.id)

    text = generate_user_links(bots, user)
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            await m.answer(text[x:x + 4096], disable_web_page_preview=True)
    else:
        await m.answer(text,disable_web_page_preview=True)


async def user_withdraw(c: types.CallbackQuery, repo: Repo):
    user = await repo.get_user(c.from_user.id)
    if user["balance"] < 6:
        await c.answer("Минимальная сумма для выплаты - 6$")
        return
    await c.message.delete()
    await c.message.answer("""
Вы <b>запросили</b> вывод

Вы получите сообщение когда ваша заявка будет одобрена
Введите номер карты:""", reply_markup=cancel_kb)
    await Withdraw.InputCard.set()


async def user_input_card(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["card"] = m.text
    await m.answer(f"""
На карту: {m.text} будут выведены средства, введите сумму: """)
    await Withdraw.InputAmount.set()


async def user_input_withdraw_amount(m: types.Message, repo: Repo, state: FSMContext):
    try:
        amount = float(m.text.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенное значение")
        return

    user = await repo.get_user(m.from_user.id)
    if user["balance"] < amount:
        await m.answer(f"Ваш баланс - {user['balance']}$")
        return
    async with state.proxy() as data:
        data["amount"] = amount

        await m.answer(f"""Проверьте введенные данные и подтвердите/отклоните их:
Карта: {data["card"]}
Сумма: {data["amount"]}$""", reply_markup=withdraw_confirmation_kb)
    await Withdraw.Confirm.set()


async def user_accept_withdraw(c: types.CallbackQuery, repo: Repo, state: FSMContext):
    async with state.proxy() as data:
        await c.bot.send_message(-1001792579223, f"""
Пользователь с ID <a href='tg://user?id={c.from_user.id}'>{c.from_user.full_name}</a> запросил вывод 
<b>Сумма:</b> {data["amount"]}$
<b>Сумма с комиссией:</b> {data["amount"] * 0.98}$
<b>Карта:</b> {data["card"]}
        """, reply_markup=get_withdraw_kb(c.from_user.id, data["amount"]))
        await c.message.delete()
        await c.message.answer(f"""
Заявка на вывод успешно создана: 
ID: <a href='tg://user?id={c.from_user.id}'>{c.from_user.full_name}</a>
Карта: {data["card"]}
Сумма: {data["amount"]}$
Сумма с комиссией: {data["amount"] * 0.98}$
        """, reply_markup=user_mm_kb)
        await repo.update_user(c.from_user.id, {"$set": {"user_name": c.from_user.full_name}, "$inc": {"balance": -data["amount"], "to_withdraw": data["amount"]}})
    await state.finish()


async def user_purchases(m: types.Message, repo: Repo):
    user = await repo.get_user(m.from_user.id)
    await m.answer(f"""
<b>📊 Всего пользователей:</b> {user["stats"]["summary"]["clicks"]}
<b>💰Общий процент:</b> {user["stats"]["summary"]["profit_from_purchases"]}$
<b>⭐️Товара купили:</b> {user["stats"]["summary"]["purchases"]}

<b>Ваш % с продаж:</b> {user["profit_percent"]}%
<b>Цена за клик:</b> {user["reward_per_click"]}$
""", reply_markup=balance_kb)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, text=["Отмена"], state="*")
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_help, text="Помощь 🆘", state="*")
    dp.register_message_handler(user_referral, text="Реферальная программа 📈", state="*")
    dp.register_message_handler(user_links, text="Мои реф. ссылки 🔗", state="*")
    dp.register_message_handler(user_balance, text="Баланс 💰", state="*")
    dp.register_message_handler(user_purchases, text="Информация о покупках", state="*")

    dp.register_callback_query_handler(user_withdraw, text="withdraw", state="*")
    dp.register_message_handler(user_input_card, state=Withdraw.InputCard)
    dp.register_message_handler(user_input_withdraw_amount, state=Withdraw.InputAmount)

    dp.register_callback_query_handler(user_withdraw, user_wc_cd.filter(action="decline"), state=Withdraw.Confirm)
    dp.register_callback_query_handler(user_accept_withdraw, user_wc_cd.filter(action="accept"), state=Withdraw.Confirm)
