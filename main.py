import time
import os

from threading import Thread
from sklearn.feature_extraction import DictVectorizer
import numpy as np
from pyfm import pylibfm
import telebot
from telebot import types
from telebot import apihelper
import inspect
def nameofper(x):
    caller_locals = inspect.currentframe().f_back.f_locals
    return str(*[name for name, value in caller_locals.items() if x is value])
def find_best(usr,que):
    global newfm
    X_train = [{"who_marked":str(usr), "marked_user":str(u)} for u in que]
    v = DictVectorizer()
    X = v.fit_transform(X_train)
    preds = newfm.predict(X)
    maxx = max(preds)
    print(maxx)
    if maxx > 0.8:
        return list(preds).index(maxx)
    else:
        return -1
def is_toxic(msg):
    return False
def writedata(sobes1,sobes2):
    for user in [str(sobes2), str(sobes1)]:
        for word in ["self", "like", "dislike"]:
            f = open("userinfo/" + user + '/' + word + ".txt", "a")
            if word == "self":
                try:
                    if len("\n".join(dialogtext[int(user)]) + "\n") > 30:
                        f.write("\n".join(dialogtext[int(user)]) + "\n")
                except:
                    print(dialogtext)
                    print(int(user))
            elif word == "like":
                if dialogs[int(user)][1] == '👍':
                    try:
                        if len("\n".join(dialogtext[dialogs[int(user)][0]]) + "\n" + str(
                                dialogs[int(user)][0]) + "\n") > 30:
                            f.write(
                                "\n".join(dialogtext[dialogs[int(user)][0]]) + "\n" + str(dialogs[int(user)][0]) + "\n")
                    except:
                        print(dialogtext)
                        print(int(user))

            elif word == "dislike":
                if dialogs[int(user)][1] == '👎':
                    try:
                        if len("\n".join(dialogtext[dialogs[int(user)][0]]) + "\n" + str(
                                dialogs[int(user)][0]) + "\n") > 30:
                            f.write(
                                "\n".join(dialogtext[dialogs[int(user)][0]]) + "\n" + str(dialogs[int(user)][0]) + "\n")
                    except:
                        print(dialogtext)
                        print(int(user))
def connecttwo(sobes1,sobes2):
    global afk,dialogs,dialogtext
    for user in [str(sobes2), str(sobes1)]:
        if user not in os.listdir("userinfo"):
            os.mkdir("userinfo/" + user)
            for word in ["self", "like", "dislike"]:
                f = open("userinfo/" + user + '/' + word + ".txt", "w")
                f.close()
    afk[tuple(sorted([sobes1, sobes2]))] = {sobes2: time.time(),
                                                         sobes1: time.time()}
    dialogs[sobes2] = sobes1
    dialogs[sobes1] = sobes2
    dialogtext[sobes2] = []
    dialogtext[sobes1] = []
    bot.send_message(sobes1, "Ваш собеседник найден, начинайте переписку.",
                     reply_markup=thirdmarkup)
    bot.send_message(sobes2, "Ваш собеседник найден, начинайте переписку.", reply_markup=thirdmarkup)
def checkint(smth):
    try:
        d = int(smth)
        if d > 10000:
            return True
        else:
            return False
    except:
        return False
def peretrain():
    X_train = []
    y = []
    for user in os.listdir("userinfo"):
        for file in os.listdir("userinfo/"+user):
            if file == "dislike.txt":
                dann = [int(i) for i in open("userinfo/"+user+'/'+file,"r").read().split() if checkint(i)]
                for d in dann:
                    X_train.append({"who_marked":str(user), "marked_user":str(d)})
                    y.append(0)
            elif file == "like.txt":
                dann = [int(i) for i in open("userinfo/"+user+'/'+file,"r").read().split() if checkint(i)]
                for d in dann:
                    X_train.append({"who_marked":str(user), "marked_user":str(d)})
                    y.append(1)
    v = DictVectorizer()
    X = v.fit_transform(X_train)
    y = np.array(y, dtype=np.float64)
    fm = pylibfm.FM(num_factors=20,num_iter=len(y)*3, verbose=False,task="regression", initial_learning_rate=0.001, learning_rate_schedule="optimal")
    fm.fit(X,y)
    return fm
newfm = peretrain()
searchque = []
dialogtext = {}
dialogs = {}
pics = {}
afk = {}
mainmarkupforu = {}
firstmarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
firstmarkup.add(types.KeyboardButton('Поиск'), types.KeyboardButton('Сбросить'), types.KeyboardButton('Загрузить фото'), types.KeyboardButton('Режим: Безопасный'))
firstmarkup2= types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
firstmarkup2.add(types.KeyboardButton('Поиск'), types.KeyboardButton('Сбросить'), types.KeyboardButton('Загрузить фото'),  types.KeyboardButton('Режим: Токсик'))
secondmarkup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
secondmarkup.add(types.KeyboardButton("Остановить поиск"))
newmarkup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
newmarkup.add(types.KeyboardButton("Остановить поиск"),types.KeyboardButton("Соединить рандомно"))
thirdmarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
thirdmarkup.add(types.KeyboardButton('👍'), types.KeyboardButton('👎'))
fourthmarkup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
fourthmarkup.add(types.KeyboardButton('Остановить'))
changemarkup = {"Режим: Безопасный":firstmarkup2,"Режим: Токсик":firstmarkup}

def smth(arr):
    if type(arr) == list:
        return arr[0]
    else:
        return arr
def gen_prox(ip,port):
    return {"https":"socks5://"+ip+":"+port,"http":"socks5://"+ip+":"+port}
def afkcheck():
    global afk, dialogs, newfm
    c = 0
    while True:
        c += 1
        if c % 15 == 0:
            newfm = peretrain()
        dellist = []
        for a in afk:
            if (time.time() - afk[a][a[0]]) > (60*5) or (time.time() - afk[a][a[1]]) > (60*5):
                for user in a:
                    if user in dialogs:
                        if type(dialogs[user]) == list:
                            writedata(user, dialogs[user])
                        del dialogs[user]
                    if user in dialogtext:
                        del dialogtext[user]
                    bot.send_message(user, "Выкидываем вас из-за длительного бездействия...", reply_markup=mainmarkupforu[user])
                    dellist.append(a)
        for d in set(dellist):
            del afk[tuple(d)]
        time.sleep(5)
print(gen_prox("geek:socks@t.geekclass.ru", "7777"))
apihelper.proxy = gen_prox("geek:socks@t.geekclass.ru", "7777")
token = "942671559:AAGkb1grArPQxs-zMomi0jhXFsB4HmO62QU"
bot = telebot.TeleBot(token)
for idd in os.listdir("userinfo"):
    try:
        pass
        #bot.send_message(int(idd),"Бот перезагрузился, извиняемся, если прервали вашу переписку. ", reply_markup=firstmarkup)
    except:
        pass
@bot.message_handler(content_types=['sticker'])
def handlee(message):
    if message.from_user.id in dialogs:
        if type(dialogs[message.from_user.id]) == int:
            bot.send_sticker(dialogs[message.from_user.id], message.sticker.file_id)
        else:
            if dialogs[dialogs[message.from_user.id][0]][1] == '👍' and dialogs[message.from_user.id][1] == '👍':
                bot.send_sticker(dialogs[message.from_user.id][0], message.sticker.file_id)
@bot.message_handler(content_types=['photo'])
def handle(message):
    if message.from_user.id not in searchque and message.from_user.id not in dialogs:
        file_id = message.photo[-1].file_id
        pics[message.from_user.id] = file_id
        """
        fileinfo = bot.get_file(file_id)
        downloaded_file = bot.download_file(fileinfo.file_path)
        if str(message.from_user.id)+".png" in os.listdir("pics"):
            os.remove("pics/"+str(message.from_user.id)+".png")
        with open("pics/"+str(message.from_user.id)+".png", 'wb') as new_file:
            new_file.write(downloaded_file)
        """
        bot.send_message(message.from_user.id, "Фото было успешно загружено.")
    else:
        bot.send_message(message.from_user.id, "Вы не можете скидывать фотографии.")
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global searchque,dialogs,dialogtext,afk
    try:
        if message.from_user.id not in mainmarkupforu:
            mainmarkupforu[message.from_user.id] = firstmarkup
        if message.from_user.id in searchque:
            if message.text == "Остановить поиск":
                searchque.remove(message.from_user.id)
                bot.send_message(message.from_user.id, "Вы вернулись.", reply_markup=mainmarkupforu[message.from_user.id])
            elif message.text == "Соединить рандомно":
                regime = nameofper(mainmarkupforu[message.from_user.id])
                newque = [q for q in searchque if nameofper(mainmarkupforu[q]) == regime]
                newque.remove(message.from_user.id)
                if newque:
                    sobes = newque[0]
                    searchque.remove(sobes)
                    searchque.remove(message.from_user.id)
                    connecttwo(message.from_user.id, sobes)
                else:
                    bot.send_message(message.from_user.id, "В данный момент нету доступных собеседников.", reply_markup=newmarkup)

            else:
                bot.send_message(message.from_user.id, "Мы еще не нашли вам собеседника, в очереди {} человек(а)".format(str(len(searchque))), reply_markup=secondmarkup)
        elif message.from_user.id in dialogs:
            afk[tuple(sorted([message.from_user.id, smth(dialogs[message.from_user.id])]))][message.from_user.id] = time.time()
            if message.text in ['👍', '👎']:
                dialogs[message.from_user.id] = [smth(dialogs[message.from_user.id]), message.text]
                if type(dialogs[dialogs[message.from_user.id][0]]) == list:
                    writedata(message.from_user.id, dialogs[message.from_user.id][0])
                    if message.from_user.id in dialogtext:
                        del dialogtext[message.from_user.id]
                    if dialogs[message.from_user.id][0] in dialogtext:
                        del dialogtext[dialogs[message.from_user.id][0]]
                    if dialogs[dialogs[message.from_user.id][0]][1] == '👍' and dialogs[message.from_user.id][1] == '👍':
                        bot.send_message(message.from_user.id, "У вас взаимная симпатия! Продолжайте общение",
                                         reply_markup=fourthmarkup)
                        bot.send_message(dialogs[message.from_user.id][0], "У вас взаимная симпатия! Продолжайте общение",
                                         reply_markup=fourthmarkup)
                        if dialogs[message.from_user.id][0] in pics:
                            bot.send_photo(message.from_user.id, pics[dialogs[message.from_user.id][0]])
                        if message.from_user.id in pics:
                            bot.send_photo(dialogs[message.from_user.id][0], pics[message.from_user.id])
                    else:
                        bot.send_message(message.from_user.id, "У вас взаимная несимпатия. Рассоединяем",
                                        reply_markup=mainmarkupforu[message.from_user.id])
                        bot.send_message(dialogs[message.from_user.id][0], "У вас взаимная несимпатия. Рассоединяем",
                                         reply_markup=mainmarkupforu[message.from_user.id])
                        try:
                            if message.from_user.id in dialogs:
                                try:
                                    del afk[tuple(sorted([message.from_user.id, dialogs[message.from_user.id][0]]))]
                                except:
                                    pass
                                del dialogs[dialogs[message.from_user.id][0]]
                                del dialogs[message.from_user.id]
                        except Exception as e:
                            print(e)
                else:
                    bot.send_message(dialogs[message.from_user.id][0], "Собеседник оценил переписку, теперь ваша очередь.", reply_markup=thirdmarkup)
                    bot.send_message(message.from_user.id, "Ожидаем пока собеседник оценит переписку...", reply_markup=thirdmarkup)
            else:
                if type(dialogs[smth(dialogs[message.from_user.id])]) == list and type(dialogs[message.from_user.id]) != list:
                    bot.send_message(message.from_user.id, "Вы должны поставить оценку собеседнику.")
                elif type(dialogs[smth(dialogs[message.from_user.id])]) != list and type(dialogs[message.from_user.id]) == list:
                    bot.send_message(message.from_user.id, "Ожидаем пока собеседник поставит оценку.")
                elif type(dialogs[smth(dialogs[message.from_user.id])]) == list and type(dialogs[message.from_user.id]) == list:
                    if message.text == "Остановить":
                        bot.send_message(message.from_user.id, "Рассоединяем...",
                                         reply_markup=mainmarkupforu[message.from_user.id])
                        bot.send_message(dialogs[message.from_user.id][0], "Рассоединяем...",
                                         reply_markup=mainmarkupforu[message.from_user.id])
                        try:
                            try:
                                del afk[tuple(sorted([message.from_user.id, dialogs[message.from_user.id][0]]))]
                            except:
                                pass
                            del dialogs[dialogs[message.from_user.id][0]]
                            del dialogs[message.from_user.id]

                        except Exception as e:
                            print(e)


                    else:
                        if nameofper(mainmarkupforu[message.from_user.id]) == "firstmarkup":
                            if is_toxic(message.text):
                                bot.send_message(message.from_user.id, "Переформулируйте сообщение, звучит токсично...")
                            else:
                                dialogtext[message.from_user.id].append(message.text)
                                bot.send_message(dialogs[message.from_user.id][0], message.text, reply_markup=fourthmarkup)
                        else:
                            bot.send_message(dialogs[message.from_user.id][0], message.text, reply_markup=fourthmarkup)

                else:
                    if nameofper(mainmarkupforu[message.from_user.id]) == "firstmarkup":
                        if is_toxic(message.text):
                            bot.send_message(message.from_user.id, "Переформулируйте сообщение, звучит токсично...")
                        else:
                            dialogtext[message.from_user.id].append(message.text)
                            bot.send_message(dialogs[message.from_user.id], message.text)
                    else:
                        dialogtext[message.from_user.id].append(message.text)
                        bot.send_message(dialogs[message.from_user.id], message.text)
        else:
            if message.text in ["/start","/help"]:
                bot.send_message(message.from_user.id,"Добро пожаловать, команды анонимного чата:\nПоиск - найти анонимного собеседника\nСбросить - сбросить всю персональную информацию, которая помогает в поиске идеального собеседника\nЗагрузить фото - вы загружаете фото, которое будет кидаться собеседнику при взаимной симпатии\nКогда наш бот соединит вас с собеседником, вы увидите две кнопки (Лайк, Дизлайк), нажимать их нужно только в случае, если разговор подходит к логическому завершению, либо вам больше не хочется общаться. Лайк вы ставите в случае, если вы получили удовольствие от беседы, дизлайк в обратном случае.\nУдачного пользования, надеюсь вы найдёте свою любовь, или соул мейта!", reply_markup=mainmarkupforu[message.from_user.id])
            elif message.text in ["Режим: Безопасный", "Режим: Токсик"]:
                mainmarkupforu[message.from_user.id] = changemarkup[message.text]
                bot.send_message(message.from_user.id, "Режим изменён.", reply_markup=mainmarkupforu[message.from_user.id])
            elif message.text == 'Загрузить фото':
                bot.send_message(message.from_user.id, "Просто загрузите фотографию в бота.", reply_markup=mainmarkupforu[message.from_user.id])

            elif message.text == 'Сбросить':
                """
                if str(message.from_user.id) in os.listdir("userinfo"):
                    for file in os.listdir("userinfo/"+str(message.from_user.id)):
                        f = open("userinfo/"+str(message.from_user.id)+'/'+file, "w")
                        f.close()
                bot.send_message(message.from_user.id, "Данные успешно очищены.")
                """
                bot.send_message(message.from_user.id, "На бета версии бота вы не можете удалить данные о себе, ну а что вы думали, нам нужны ваши данные для обучения.\nС любовью, Вова ❤")
            elif message.text == "Поиск":
                regime = nameofper(mainmarkupforu[message.from_user.id])
                quewithsameregime = [q for q in searchque if nameofper(mainmarkupforu[q]) == regime and q != message.from_user.id]
                if quewithsameregime:
                    if str(message.from_user.id) not in os.listdir("userinfo"):
                        sobes = quewithsameregime[0]
                        searchque.remove(sobes)
                        connecttwo(message.from_user.id,sobes)
                    else:
                        ind = find_best(message.from_user.id,quewithsameregime)
                        if ind == -1:
                            bot.send_message(message.from_user.id, "В очереди пока нету человека, который бы подходил вам, ожидаем...\nВы также можете соединиться рандомно, если устали ждать",
                                             reply_markup=newmarkup)
                            searchque.append(message.from_user.id)
                        else:
                            sobes = quewithsameregime[ind]
                            searchque.remove(sobes)
                            connecttwo(message.from_user.id,sobes)

                else:
                    bot.send_message(message.from_user.id, "Ожидайте, пока подключится собеседник с вашим режимом...", reply_markup=newmarkup)
                    searchque.append(message.from_user.id)
    except Exception as e:
        print(e)

Thread(target=afkcheck).start()
bot.polling()
