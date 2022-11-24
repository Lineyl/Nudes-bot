import json
from pprint import pprint
from operator import itemgetter

from aiogram import Dispatcher, types
from aiogram.utils.exceptions import ChatNotFound, BotBlocked

from tgbot.handlers.user import user_mm_kb, admin_wc_cd
from tgbot.models.role import UserRole
# async def admin_start(m: Message):
#     await m.reply("Hello, admin!")
from tgbot.services.repository import Repo


async def top_15_referrals(m: types.Message, repo: Repo):
    users = await repo.list_for_top_users()

    top_list = []
    try:
        for user in users:
            user_id = user["user_id"]

            try:
                user_name = user["user_name"]
            except:
                user_name = str(user_id) 

            try:
                top_list.append((user_name, user["stats"]["summary"]["profit_from_purchases"], user_id))
            except:
                pass
        top_list = sorted(top_list, key=itemgetter(1), reverse = True)

        if (len(top_list) > 15):
            del top_list[15:]

        msg = """🤩TOP 15 referals🤩

        """

        i_num = 1
        for tpl in top_list:
            msg += ("""
{}) <a href='tg://user?id={}'>{}</a>  {:.2f}$
""".format(i_num, tpl[2], tpl[0], float(tpl[1])))
            i_num += 1


        await m.answer(msg)
    except Exception as ex:
        await m.answer("Что-то пошло не так :(")
        print(ex)
        print(ex)
        print(ex)
        print(ex)
        print(ex)
        print(ex)


async def all_referrals_profit(m: types.Message, repo: Repo):
    users = await repo.list_for_all_users()

    top_list = []
    try:
        for user in users:
            user_id = user["user_id"]

            try:
                user_name = user["user_name"]
            except:
                user_name = str(user_id) 

            try:
                top_list.append((user_name, user['balance'], user_id))
            except:
                pass
        top_list = sorted(top_list, key=itemgetter(1), reverse = True)

        msg = """🤩All referals🤩

        """

        i_num = 1
        Sum = 0.0
        for tpl in top_list:
            msg += ("""
{}) <a href='tg://user?id={}'>{}</a>  {:.2f}$
""".format(i_num, tpl[2], tpl[0], float(tpl[1])))
            i_num += 1
            Sum += float(tpl[1])

        msg += ("""

Общая сумма: {:.2f}$
        """.format(Sum))


        await m.answer(msg)
    except Exception as ex:
        await m.answer("Что-то пошло не так :(")
        print(ex)
        print(ex)
        print(ex)
        print(ex)
        print(ex)
        print(ex)


async def admin_add_user(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await m.answer("Проверьте введенное значение")
        return

    user = await repo.get_user(user_id)
    if user and user["status"] == 1:
        await m.answer("Пользователь с таким ID уже зарегистрирован")
        return
    elif user and user["status"] == 0:
        await repo.update_user(user_id, {"$set": {"status": 1}})
    elif not user:
        await repo.add_user(user_id)
        await repo.update_user(user_id, {"$set": {"status": 1}})

    try:
        await m.bot.send_message(user_id, "Вас добавили в рефералы", reply_markup=user_mm_kb)
    except (ChatNotFound, BotBlocked):
        await m.answer("Пользователь добавлен, но у него нет активного диалога с ботом")
        return
    await m.answer("Пользователь добавлен")


async def admin_set_profit_percent(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, percent = args.split()
    except ValueError:
        await m.answer("Необходимо передать только 2 параметра - user_id и процент")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return

    try:
        percent = float(percent.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенный процент")
        return

    user = await repo.get_user(user_id)
    if not user or user["status"] == 0:
        await m.answer("Пользователь не является рефералом")
        return
    else:
        await repo.update_user(user_id, {"$set": {"profit_percent": percent}})
        await m.answer(f"Процент с продаж изменен с {user['profit_percent']}% на {percent}%")
    try:
        await m.bot.send_message(user_id, f"❗️Ваш процент изменили с {user['profit_percent']}% на {percent}%")
    except (ChatNotFound, BotBlocked) as ex:
        pass


async def admin_set_reward_per_click(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, reward = args.split()
    except ValueError:
        await m.answer("Необходимо передать только 2 параметра - user_id и награду за клик")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return

    try:
        percent = float(reward.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенный процент")
        return

    user = await repo.get_user(user_id)
    if not user or user["status"] == 0:
        await m.answer("Пользователь не является рефералом")
    else:
        await repo.update_user(user_id, {"$set": {"reward_per_click": percent}})
        await m.answer(f"Награда за клик изменена на {percent}$")


async def admin_get_sells(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return
    user = await repo.get_user(user_id)
    if not user:
        await m.answer(f"Пользователь с ID {user_id} не найден")
        return

    await m.reply(f"Кол-во покупок: <code>{user['stats']['summary']['purchases']}</code>")


async def admin_get_user(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return
    user = await repo.get_user(user_id)
    if not user:
        await m.answer(f"Пользователь с ID {user_id} не найден")
        return
    tg_user = await m.bot.get_chat(user_id)
    ref = await repo.find_user({f"referral_info.referrals.{user_id}.percent": {"$exists": True}})
    if not ref:
        await m.reply(f"""<a href="tg://user?id={tg_user.id}">{tg_user.full_name}</a>
Баланс: {user["balance"]}$
Процент с продаж: {user["profit_percent"]}%
Оплата за клик: {user["reward_per_click"]}$""")
    else:
        await m.reply(f"""<a href="tg://user?id={tg_user.id}">{tg_user.full_name}</a>
Баланс: {user["balance"]}$
Процент с продаж: {user["profit_percent"]}%
Оплата за клик: {user["reward_per_click"]}$
Реф. процент: {ref["referral_info"]["referrals"][str(tg_user.id)]["percent"]}%""")


async def admin_get_users(m: types.Message, repo: Repo):
    users = await repo.list_users(args={'status': 1})
    text = '<b>🍀Все рефералы:</b>\n'
    for i, user in enumerate(users, start=1):
        user_id = user['user_id']
        username = user['user_name'] if user.get('user_name') else user_id
        text += f'{i}. <a href="tg://user?id={user_id}">{username}</a>\n'
    await m.answer(text)


async def admin_get_balance(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return
    user = await repo.get_user(user_id)
    if not user:
        await m.answer(f"Пользователь с ID {user_id} не найден")
        return

    await m.reply(f"Текущий баланс: <code>{user['balance']}</code>$")


async def admin_get_proc(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return
    user = await repo.get_user(user_id)
    if not user:
        await m.answer(f"Пользователь с ID {user_id} не найден")
        return

    await m.reply(f"Текущий процент: <code>{user['stats']['summary']['profit_from_purchases']}</code>%")


async def admin_set_sells(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, sells = args.split()
    except ValueError:
        await m.answer("Необходимо передать только 2 параметра - user_id и кол-во продаж")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return

    try:
        sells = float(sells.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенное кол-во продаж")
        return

    await repo.update_user(user_id, {"$set": {"stats.summary.purchases": sells}})
    await m.answer(f"Кол-во продаж изменено на {sells}")


async def admin_set_balance(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, balance = args.split()
    except ValueError:
        await m.answer("Необходимо передать только 2 параметра - user_id и новое значение баланса")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return

    try:
        balance = float(balance.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенный баланс")
        return

    await repo.update_user(user_id, {"$set": {"balance": balance}})
    await m.answer(f"Баланс изменен на {balance}$")


async def admin_set_proc(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, profit = args.split()
    except ValueError:
        await m.answer("Необходимо передать только 2 параметра - user_id и новый процент")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return

    try:
        profit = float(profit.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенный процент")
        return

    await repo.update_user(user_id, {"$set": {"stats.summary.profit_from_purchases": profit}})
    await m.answer(f"Общий процент изменен на {profit}")


async def admin_accept_withdraw(c: types.CallbackQuery, repo: Repo, callback_data: dict):
    await c.bot.send_message(int(callback_data["user_id"]), "Заявка на вывод одобрена. Вывод осуществлён✅💸")
    await repo.update_user(int(callback_data["user_id"]), {"$inc": {"to_withdraw": -float(callback_data["amount"]),
                                                                    "stats.summary.withdraws": float(
                                                                        callback_data["amount"])}})
    await c.message.edit_reply_markup(None)


async def admin_decline_withdraw(c: types.CallbackQuery, repo: Repo, callback_data: dict):
    await c.bot.send_message(int(callback_data["user_id"]),
                             """Заявка на вывод отклонена❌, если вы считаете , что это ошибка - свяжитесь с @burja_purga""")
    await repo.update_user(int(callback_data["user_id"]), {"$inc": {"to_withdraw": -float(callback_data["amount"]),
                                                                    "balance": float(
                                                                        callback_data["amount"])}})
    await c.message.edit_reply_markup(None)


async def admin_set_friend(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, ref_id = args.split()
    except ValueError:
        await m.answer("Вы должны ввести только id рефа и друга")
        return

    try:
        user_id = int(user_id)
        ref_id = int(ref_id)
    except ValueError:
        await m.answer("Проверьте введенные значения")
        return
    print(user_id, ref_id)
    user = await repo.get_user(user_id)
    if not user:
        await m.answer("Реф с таким ID не найден")
        return

    ref = await repo.get_user(ref_id)
    print(ref)
    if not ref:
        await repo.add_user(ref_id)

    await repo.update_user(ref_id, {"$set": {"status": 1, "invited_by": user_id}})
    await repo.update_user(user_id, {"$unset": {f"referral_info.referrals.{ref_id}": ""}}, {})
    await repo.update_user(user_id, {"$set": {f"referral_info.referrals.{ref_id}": {"percent": 1, "profit": 0}}})
    await m.answer("Друг успешно добавлен")
    try:
        await m.bot.send_message(ref_id, "Вас добавили в рефералы", reply_markup=user_mm_kb)
    except:
        pass


async def admin_ser_ref_percent(m: types.Message, repo: Repo):
    args = m.get_args()
    try:
        user_id, reward = args.split()
    except ValueError:
        await m.answer("Необходимо передать только 2 параметра - user_id и реф. процень")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await m.answer("Проверьте введенный ID")
        return

    try:
        percent = float(reward.replace(",", "."))
    except ValueError:
        await m.answer("Проверьте введенный процент")
        return

    user = await repo.get_user(user_id)
    if not user:
        await m.answer("Пользовтель с таким ID не найден")
        return

    await repo.update_user(user_id, {"$set": {f"referral_info.referrals.{user_id}.percent": percent}},
                           {f"referral_info.referrals.{user_id}": {"$exists": True}})
    await m.answer(f"Реф. процент изменен на {percent}")


async def admin_add_admin(message: types.Message, repo: Repo):
    args = message.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await message.answer("Необходимо ввести ID пользователя")
        return

    user = await repo.get_user(user_id)
    if not user:
        await message.answer("Пользователь не найден в боте")
        return
    await repo.update_user(user["user_id"], {"$set": {"is_admin": True}})
    await message.answer("Админ добавлен")


async def admin_del_admin(message: types.Message, repo: Repo):
    args = message.get_args()
    try:
        user_id = int(args)
    except ValueError:
        await message.answer("Необходимо ввести ID пользователя")
        return

    user = await repo.get_user(user_id)
    if not user:
        await message.answer("Пользователь не найден в боте")
        return
    await repo.update_user(user["user_id"], {"$set": {"is_admin": False}})
    await message.answer("Админ удалён")


async def admin_mailing(message: types.Message, repo: Repo):
    users = await repo.list_users()
    count_sent_message = 0
    count_unsent_message = 0
    await message.answer("Начал отправку рассылки...")
    for user in users:
        try:
            await message.reply_to_message.copy_to(user["user_id"])
            print(count_sent_message)
            count_sent_message += 1
        except:
            count_unsent_message += 1
            print(count_unsent_message)
    total_count = count_unsent_message + count_sent_message
    percent = 100
    if (total_count != 0):
        percent = count_unsent_message * 100 / total_count

    await message.answer(f"""
Рассылку отправил!

Из {total_count} получателей - {count_unsent_message} не приняли сообщение (заблокировали бота) - это {percent}% от общего количества
            """)


async def admin_set_cookies(message: types.Message, repo: Repo):
    args = message.get_args()
    platform, cookies = args.split(maxsplit=1)
    cookies = json.loads(cookies.replace("'", '"'))
    pprint(cookies)
    if platform == "facebook":
        await repo.conn.cookies.update_one({"platform": "facebook"}, {"$set":{"cookies_dict": cookies}})
    else:
        await repo.conn.cookies.update_one({"platform": "instagram"}, {"$set": {"cookies_dict": cookies}})
    await message.answer("OK")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(top_15_referrals, commands=["top"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(all_referrals_profit, commands=["get_balance_all"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_add_user, commands=["new_ref"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_add_admin, commands=["add_admin"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_del_admin, commands=["del_admin"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_set_cookies, commands=["c_set"], state="*", role=UserRole.ADMIN)

    dp.register_message_handler(admin_set_profit_percent, commands=["set_procent"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_set_reward_per_click, commands=["set_price"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_get_user, commands=["get_user"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_get_users, commands=["referrals"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_get_sells, commands=["get_sells"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_get_balance, commands=["get_balance"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_get_proc, commands=["get_proc"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_set_sells, commands=["set_sells"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_set_balance, commands=["set_balance"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_set_proc, commands=["set_proc"], state="*", role=UserRole.ADMIN)

    dp.register_message_handler(admin_set_friend, commands=["set_friend"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_ser_ref_percent, commands=["set_ref_procent"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(admin_mailing, state="*", role=UserRole.ADMIN, is_reply=True,
                                content_types=types.ContentType.all())
    dp.register_callback_query_handler(admin_accept_withdraw, admin_wc_cd.filter(action="accept"), state="*")
    dp.register_callback_query_handler(admin_decline_withdraw, admin_wc_cd.filter(), state="*")
