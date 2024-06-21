#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../')

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api
import random

# Для указания смены дериктории
xXx = ''






# allData['datas'][id] = {телефон, ФИО, Ребенок1: {ФИО, возраст, школа}, ...}
# allData['НазваниеПредприятия'] = {id: {1: {Имя участника, возраст}, ..., дата участия}}
allData = {'datas': {},
           'Стеклотех': {},
           'СНГК': {},
           'Автоград': {}}




nowPerson = {}
newReg = {}
newChange = {}


# names['НазваниеПредприятия']['fullname'] = полное навзвание предприятия
# names['НазваниеПредприятия']['prefix'] = приставка (в/на)
# names['НазваниеПредприятия']['adress'] = полный адрес предприятия
names = {'Стеклотех': {'fullName': 'Стеклотарный завод "Стеклотех"', 'prefix': 'на', 'adress': 'рп. Богандинский, Кирова, 10а (https://go.2gis.com/wwoh3) у входа на предприятие, перед шлагбаумом'},
         'СНГК': {'fullName': 'Завод по ремонту спецтехники «СНГК»', 'prefix': 'на', 'adress': 'Старый Тобольский тракт 5 километр, 15 к2 ст2 (https://go.2gis.com/3fgwy) у входа на предприятие'},
         'Автоград': {'fullName': 'Автоград – автомобильный холдинг', 'prefix': 'в', 'adress': 'ул. Республики 276, Автосалон Лэндровер-Ягуар. (https://go.2gis.com/zcqmu) у входа в автосалон'}}

dates = {}




# В клавиатуре step относится к текущим сообщениям и клавиатуре, а при получении сообщений от пользователя - step - предыдущий шаг
step = 0
stepUp = 0
getName = 0
getSchool = 0
nowChild = 0
popi = 0

numerals = {1: 'первого', 2: 'второго', 3: 'третьего', 4: 'четвертого', 5: 'пятого', 6: 'шестого'}

token ='vk1.a.ImP3H1-WzhHqmxInEatsUHuKg_M3hdNfA-CEtM2jYXxuZFsxdGPEtnjTJNiyUWezNl3QOIBVQ11yceqy0au7YZ6ctZ7TiVEVIzRRxO_tq_UL0EAaO4QB9qSQLQTC9FNWsk4CyWZgc5A9r3DJFBTRYOLb43h2hmEhyxK1xM6aqfPl8Y2TwMfDRDzdTrxcDdfNaQzjZM6ai3TIfnznKl950w'
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Окончания слов при исчислении
def ending(cnt):
    if str(cnt)[-1] in '2 3 4':
        return 'a'
    elif cnt == 1 or str(cnt) in '5 6 7 8 9' or cnt >= 10:
        return ''

# Обновление dates (Даты экскурсий)
def updateDates():
    global xXx, dates
    f = open(f'{xXx}Даты.csv', encoding='utf-8').readlines()
    for i in f:
        dates[i.split(';')[0]] = i.replace('\n', '').split(';')[1:]

# Обновление allData (регистрационные данные пользователей)
def updateDatas():
    global xXx, allData
    f = open(f'{xXx}dataBase.csv', encoding='utf-8').readlines()
    for i in f:
        q = i.split(';')
        if q[0] in allData['datas']:
            pass
        else:
            try:
                int(q[0])
                cnt = 1
                allData['datas'][q[0]] = {}
                allData['datas'][q[0]]['name'] = q[1].replace('\n', '')
                allData['datas'][q[0]]['tel'] = q[2].replace('\n', '')
                needCnt = 3
                for i in range(int(len(q[3:]) / 3)):
                    j = q[needCnt:]
                    needCnt += 3
                    allData['datas'][q[0]][cnt] = {'name': str(j[0]).title(), 'age': int(j[1]), 'school': str(j[2])}
                    cnt += 1
            except ValueError or KeyError or TypeError as ad:
                pass

    for qw in allData:
        if qw != 'datas':
            f = open(f'{xXx}{qw}.csv', encoding='utf-8').readlines()
            for i in f:
                q = i.split(';')
                try:
                    date = q[-1].replace('\n', '')
                    allData[qw][date] = {}
                    allData[qw][date][q[0]] = {}
                    quantityNow = len(q[1:-1]) // 2
                    cnt = 1
                    for i in range(quantityNow):
                        i += 1
                        allData[qw][date][q[0]][i] = {'name': q[cnt], 'age': q[cnt+1]}
                        cnt += 2
                except ValueError or KeyError or TypeError as ad:
                    pass
        else:
            pass




# Поиск анкеты пользователя {id} в экскурсии на предприятие {name} (дата - {date})
def verification(name, id, date):
    global xXx
    f = open(f'{xXx}{name}.csv', encoding='utf-8').readlines()
    for i in f:
        try:
            if int(i.split(';')[0]) == int(id):
                if i.split(';')[-1].split() == date.split():
                    return True
        except ValueError or KeyError:
            pass
    return False

# Создание списка допустимых для посещения пользователем {id} предприятий
def createListCan(id):
    global names, dates
    updateDates()
    can = {}
    for i in names:
        can[i] = ''
        for j in dates[i]:
            if verification(i, id, j):
                pass
            else:
                can[i] += str(j) + ';'
    return can


def saveReg(name):
    global allData, xXx
    updateDatas()
    f = open(f'{xXx}{name}.csv', 'w', encoding='utf-8')
    # i - дата
    s = None
    for i in allData[name]:
        # j - id
        for j in allData[name][i]:
            f.write(f'{str(j)};')
            # q - 1, 2, 3, ...
            for q in allData[name][i][j]:
                try:
                    int(q)
                    s = f'{str(allData[str(name)][str(i)][str(j)][int(q)]["name"])};'
                    f.write(s)
                    s = f'{str(allData[str(name)][str(i)][str(j)][int(q)]["age"])};'
                    f.write(s)
                except ValueError or TypeError or KeyError:
                    pass
        if s:
            f.write(f'{str(i)}\n')

# Сохранение регистрационных данных в файл dataBase
def saveUser():
    global allData, xXx
    f = open(f'{xXx}dataBase.csv', 'a+', encoding='utf-8')
    s = open(f'{xXx}dataBase.csv', encoding='utf-8').readlines()
    flag = []
    for i in allData['datas']:
        if len(s) != 0:
            for j in s:
                if str(i) in j:
                    flag.append(False)
                else:
                    flag.append(True)
            if all(flag):
                f.write(f"{str(i)};{str(allData['datas'][i]['name'])};{str(allData['datas'][i]['tel'])};")
                for j in range(len(allData['datas'][i]) - 2):
                    j += 1
                    if j != len(allData['datas'][i]) - 2:
                        if allData['datas'][i][j]['age'] <= 17:
                            f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};{allData['datas'][i][j]['school']};")
                        else:
                            f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};")
                    else:
                        if allData['datas'][i][j]['age'] <= 17:
                            f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};{allData['datas'][i][j]['school']}\n")
                        else:
                            f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']}\n")
            else:
                updateDatas()
                f = open(f'{xXx}dataBase.csv', 'w', encoding='utf-8')
                for i in allData['datas']:
                    f.write(f"{str(i)};{str(allData['datas'][i]['name'])};{str(allData['datas'][i]['tel'])};")
                    for j in range(len(allData['datas'][i]) - 2):
                        j += 1
                        if j != len(allData['datas'][i]) - 2:
                            if allData['datas'][i][j]['age'] <= 17:
                                f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};{allData['datas'][i][j]['school']};")
                            else:
                                f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};")
                        else:
                            if allData['datas'][i][j]['age'] <= 17:
                                f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};{allData['datas'][i][j]['school']}\n")
                            else:
                                f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']}\n")
        else:
            f.write(f"{str(i)};{str(allData['datas'][i]['name'])};{str(allData['datas'][i]['tel'])};")
            for j in range(len(allData['datas'][i]) - 2):
                j += 1
                if j != len(allData['datas'][i]) - 2:
                    if allData['datas'][i][j]['age'] <= 17:
                        f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};{allData['datas'][i][j]['school']};")
                    else:
                        f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};")
                else:
                    if allData['datas'][i][j]['age'] <= 17:
                        f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']};{allData['datas'][i][j]['school']}\n")
                    else:
                        f.write(f"{allData['datas'][i][j]['name']};{allData['datas'][i][j]['age']}\n")
    f.close()

def create_keyboard(step=None, stepUp=None, close=None, name=None):
    global names
    keyboard = VkKeyboard(one_time=False)

    # После кнопки Начать
    if step == 1:
        if close:
            updateDatas()
            if str(close) in allData['datas']:
                keyboard.add_button('Записаться на экскурсию', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Посмотреть или изменить личные данные', color=VkKeyboardColor.SECONDARY)
                f = []
                for i in allData:
                    if i != 'datas':
                        for j in allData[i]:
                            if str(close) in allData[i][j]:
                                f.append(True)
                            else:
                                f.append(False)
                if True in f:
                    keyboard.add_line()
                    keyboard.add_button('Посмотреть или изменить мои заявки', color=VkKeyboardColor.SECONDARY)
                keyboard.add_line()
                keyboard.add_button('Задать вопрос', color=VkKeyboardColor.PRIMARY)
            else:
                keyboard.add_button('Записаться на экскурсию', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('Задать вопрос', color=VkKeyboardColor.PRIMARY)
        else:
            keyboard.add_button('Записаться на экскурсию', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('Задать вопрос', color=VkKeyboardColor.PRIMARY)


    # Предложение регистрации
    elif step == 2 and stepUp == 0:
        keyboard.add_button('Зарегестрироваться', color=VkKeyboardColor.POSITIVE)

    # Количество членов семьи
    elif step == 2 and stepUp == 2:
        keyboard.add_button('1', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('2', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('3', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('4', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('5', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('6', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Прекратить регистрацию', color=VkKeyboardColor.NEGATIVE)

    # Список предприятий
    elif step == 3:
        if stepUp == 1 and name:
            s = 0
            for i in name:
                if s == 0:
                    s += 1
                else:
                    keyboard.add_line()
                keyboard.add_button(names[i]['fullName'], color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('Отменить запись', color=VkKeyboardColor.NEGATIVE)

        elif stepUp == 2 and name:
            s = 0
            for i in name:
                if s == 0 or s % 2 != 0:
                    s += 1
                else:
                    keyboard.add_line()
                keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('Отменить запись', color=VkKeyboardColor.NEGATIVE)

        elif stepUp == 3 and name:
            s = 0
            for i in name:
                if s == 0:
                    s += 1
                else:
                    keyboard.add_line()
                keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)
            if close == 3:
                keyboard.add_line()
                keyboard.add_button('Закончить выбор участников', color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()
            keyboard.add_button('Отменить запись', color=VkKeyboardColor.NEGATIVE)

    # Спрятать клавиатуру
    elif close == 1:
        return keyboard.get_empty_keyboard()

    elif close == 2:
        keyboard.add_button('Прекратить регистрацию', color=VkKeyboardColor.NEGATIVE)

    elif close == 4:
        keyboard.add_button('Изменить данные', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('Оставить данные без изменений', color=VkKeyboardColor.PRIMARY)

    elif step == 4:
        keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)

    elif step == 5:
        if stepUp == 1 and name:
            s = 0
            for i in name:
                if s == 0 or s % 5 != 0:
                    s += 1
                else:
                    keyboard.add_line()
                keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
        elif stepUp == 2:
            keyboard.add_button('Изменить заявку', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('Удалить заявку', color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()
            keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
        elif stepUp == 3:
            keyboard.add_button('Сохранить заявку', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Удалить заявку', color=VkKeyboardColor.NEGATIVE)

    elif step == 10:
        keyboard.add_button('Подтвердить участие в экскурсии', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Я отказываюсь от участия', color=VkKeyboardColor.NEGATIVE)

    elif step == 101 and name:
        s = 0
        for i in name:
            if s == 0:
                s += 1
            else:
                keyboard.add_line()
            keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)

    elif step == 102 and name:
        s = 0
        for i in name:
            if s == 0 or s % 2 != 0:
                s += 1
            else:
                keyboard.add_line()
            keyboard.add_button(i, color=VkKeyboardColor.PRIMARY)

    elif step == 100:
        keyboard.add_button('!Рассылка', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('!Узнать участников экскурсии', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('!Сообщение всем пользователям', color=VkKeyboardColor.PRIMARY)




    keyboard = keyboard.get_keyboard()
    return keyboard


def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',{id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})













for event in longpoll.listen():
    updateDatas()
    updateDates()
    if event.type == VkEventType.MESSAGE_NEW:

        response = event.text
        if event.from_user and not event.from_me:
            # Нажата кнопка "Начать" или "Прекратить регистрацию"
            if response == "Начать" or response == 'Прекратить регистрацию' or response == 'Отменить запись' or response == "Отмена" or response == 'Оставить данные без изменений':
                step = 1
                send_message(vk_session, 'user_id', event.user_id, message='В этом боте Вы можете онлайн подавать заявки на посещение промышленных предприятий Тюмени с экскурсионными группами.', keyboard=create_keyboard(close=1))
                send_message(vk_session, 'user_id', event.user_id, message='Для регистрации на экскурсию воспользуйтесь кнопкой "Записаться на экскурсию"', keyboard=create_keyboard(close=1))
                send_message(vk_session, 'user_id', event.user_id, message='Если у Вас возникли вопросы - используйте кнопку "Задать вопрос".', keyboard=create_keyboard(step, close=event.user_id))



            elif response == '!Модератор':
                step = 100
                send_message(vk_session, 'user_id', event.user_id, message=f'Режим модератора открыт. Здравствуйте, господин модератор.', keyboard=create_keyboard(step=step))


            elif response == '!Рассылка':
                step = 101
                Nname = []
                updateDatas()
                for i in allData:
                    if i != 'datas' and allData[i]:
                        Nname.append(i)
                if Nname:
                    send_message(vk_session, 'user_id', event.user_id, message=f'Участникам экскурсий на какое предприятие сделать рассылку?', keyboard=create_keyboard(step=step, name=Nname))
                else:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин Модератор, рассылку делать некому...', keyboard=create_keyboard(step=step))

            elif step == 101:
                step = 102
                updateDatas()
                Nname = response
                Ndate = []
                for i in allData[response]:
                    Ndate.append(i)
                if Ndate:
                    send_message(vk_session, 'user_id', event.user_id, message=f'Участникам экскурсии какого числа сделать рассылку?', keyboard=create_keyboard(step=step, name=Ndate))
                else:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин Модератор, рассылку делать некому...', keyboard=create_keyboard(step=step))


            elif step == 102:
                Ndate = response
                try:
                    updateDatas()
                    listId = []
                    for i in allData[Nname][Ndate]:
                        listId.append(int(i))
                    if len(listId) >= 1:
                        for i in listId:
                            step = 10
                            send_message(vk_session, 'user_id', i, message=f'Напоминаем, что {Ndate}, пройдет экскурсия на предприятие: {Nname}. Пожалуйста, подтвердите своё участие.', keyboard=create_keyboard(step=step))
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message='Рассылка сделана.', keyboard=create_keyboard(step=step))
                except KeyError:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин Модератор, рассылку делать некому...', keyboard=create_keyboard(step=step))
















            elif response == '!Сообщение всем пользователям':
                if allData['datas']:
                    step = 105
                    send_message(vk_session, 'user_id', event.user_id, message=f'Введите текст сообщения.', keyboard=create_keyboard(close=1))
                else:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин модератор, нет зарегестрированных пользователей.', keyboard=create_keyboard(step=step))
            elif step == 105:
                for i in allData:
                    send_message(vk_session, 'user_id', int(i), message=response, keyboard=create_keyboard(close=str(i)))
                send_message(vk_session, 'user_id', event.user_id, message='Отправлено.', keyboard=create_keyboard(close=str(i)))




            elif response == '!Узнать участников экскурсии':
                step = 103
                Nname = []
                updateDatas()
                for i in allData:
                    if i != 'datas' and allData[i]:
                        Nname.append(i)
                print(Nname)
                if Nname:
                    send_message(vk_session, 'user_id', event.user_id, message=f'Участников экскурсии на какое предприятие вы хотите узнать?', keyboard=create_keyboard(step=101, name=Nname))
                else:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин Модератор, нет никого, кто зарегестрирован на экскурсии...', keyboard=create_keyboard(step=step))

            elif step == 103:
                step = 104
                updateDatas()
                Nname = response
                Ndate = []
                for i in allData[response]:
                    Ndate.append(i)
                if Ndate:
                    send_message(vk_session, 'user_id', event.user_id, message=f'Участников экскурсии на какое число вам показать?', keyboard=create_keyboard(step=102, name=Ndate))
                else:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин Модератор, нет никого, кто зарегестрирован на экскурсии на предприятие {Nname}...', keyboard=create_keyboard(step=step))


            elif step == 104:
                Ndate = response
                try:
                    updateDatas()
                    listId = []
                    for i in allData[Nname][Ndate]:
                        listId.append(int(i))
                    if len(listId) >= 1:
                        cnt = 1
                        text = f'Предприятие: {Nname} \nДата: {Ndate}\n\nУчастники:'
                        for i in listId:
                            keys = list(allData[Nname][Ndate][str(i)].keys())
                            text += f'\n\n{cnt}. VK: @id{str(i)}\nИмя родителя: {allData["datas"][str(i)]["name"]}\nКоличество экскурсников: {max(keys) + 1}\nВозраста детей: '
                            for j in keys:
                                text += f"{allData[Nname][Ndate][str(i)][j]['age']}, "
                            text = text[:-2] + '\n'
                            text += 'Имена детей: '
                            for j in keys:
                                text += f"{allData[Nname][Ndate][str(i)][j]['name']}, "
                            text = text[:-2] + '\n\n'
                            cnt += 1
                        step = 100
                        send_message(vk_session, 'user_id', event.user_id, message=text, keyboard=create_keyboard(step=step))
                except KeyError:
                    step = 100
                    send_message(vk_session, 'user_id', event.user_id, message=f'Господин Модератор, рассылку делать некому...', keyboard=create_keyboard(step=step))






























            elif step == 10:
                answers = ['Я отказываюсь от участия', 'Подтвердить участие в экскурсии']
                if response in answers:
                    if answers[1] == response:
                        step = 1
                        send_message(vk_session, 'user_id', event.user_id, message=f"Отлично, ждём вас {Ndate} по адресу: {names[Nname]['adress']}.", keyboard=create_keyboard(step=step, close=str(event.user_id)))
                    else:
                        step = 1
                        updateDatas()
                        del allData[Nname][Ndate][str(event.user_id)]
                        saveReg(Nname)
                        send_message(vk_session, 'user_id', event.user_id, message=f'Очень жаль, надеемся вы присоединитесь к другии экскурсиям.', keyboard=create_keyboard(step=step))
                else:
                    step = 10
                    send_message(vk_session, 'user_id', event.user_id, message=f'Используйте кнопки ниже для ответа.', keyboard=create_keyboard(step=step))


            elif len(response.split(' // ')) == 3 and event.user_id == 538063822:
                step = 1
                send_message(vk_session, 'user_id', response.split(' // ')[2], message=f"Модератор ответил на ваш вопрос: '{response.split(' // ')[1]}'.\n\nОтвет модератора: {response.split(' // ')[0]}", keyboard=create_keyboard(step=step))






            # Нажата кнопка "Записаться на экскурсию"
            elif response == "Записаться на экскурсию" and step == 1:
                updateDatas()
                keys = list(allData['datas'].keys())
                # Если пользователь не зарегестрирован
                if str(event.user_id) not in keys:
                    step = 2
                    stepUp = 0
                    send_message(vk_session, 'user_id', event.user_id, message='Пожалуйста зарегестрируйтесь в системе для продолжения.', keyboard=create_keyboard(step, stepUp))
                # Если пользователь зарегестрирован
                else:
                    # Проверка регистрации на события и вывод кнопок регистрации на события, куда пользователь еще не зарегестрирован
                    step = 3
                    stepUp = 1
                    x = createListCan(event.user_id)
                    name = []
                    for i in x:
                        if x[i]:
                            name.append(i)
                    if name:
                        send_message(vk_session, 'user_id', event.user_id, message='Выберите предприятие, куда хотите отправиться на экскурсию.', keyboard=create_keyboard(step=step, stepUp=stepUp, name=name))
                    else:
                        step = 1
                        send_message(vk_session, 'user_id', event.user_id, message='Вы подали заявки на все предстоящие экскурсии. Вы можете изменить или удалить их, нажав кнопку "Посмотреть или изменить мои заявки".', keyboard=create_keyboard(step=step, close=event.user_id))





            # Нажата кнопка "Задать вопрос"
            elif response == "Задать вопрос" and step == 1:
                step = 4
                send_message(vk_session, 'user_id', event.user_id, message='Максимально подробно опишите ваш вопрос. Вам ответит перывый освободившийся модератор.', keyboard=create_keyboard(step=step))


            elif step == 4:
                step = 1
                send_message(vk_session, 'user_id', event.user_id, message='Спасибо за ваше обращение. Ожидайте ответа модератора.', keyboard=create_keyboard(step=step))
                send_message(vk_session, 'user_id', 538063822, message=f'Вопрос от пользователя: @id{event.user_id}\n\nТекст вопроса: {response}\n\nФормат ответа: \nТекст ответа // {response} // {event.user_id}', keyboard=create_keyboard(step=step))


            # Нажата кнопка "Посмотреть или изменить мои заявки"
            elif response == "Посмотреть или изменить мои заявки" and step == 1:
                updateDatas()
                s = createListCan(event.user_id)
                canNow = []
                for i in allData:
                    if i != 'datas':
                        for j in allData[i]:
                            if str(event.user_id) in allData[i][j] and names[i]['fullName'] not in canNow:
                                canNow.append(names[i]['fullName'])
                step = 5
                stepUp = 1
                text = 'Ваши заявки:'
                cnt = 1
                newChange = {}
                for i in allData:
                    if i != 'datas':
                        for j in allData[i]:
                            if str(event.user_id) in allData[i][j]:
                                text += f'\n\n{cnt}. Предприятие: {i}\nДата экскурсии: {j}\nУчастники: Вы или другой родитель, '
                                for k in allData[i][j][str(event.user_id)]:
                                    try:
                                        int(k)
                                        if int(k) + 1 in allData[i][j][str(event.user_id)]:
                                            text += f"{allData[i][j][str(event.user_id)][int(k)]['name']}, "
                                        else:
                                            text += f"{allData[i][j][str(event.user_id)][int(k)]['name']}."
                                    except ValueError or TypeError or KeyError:
                                        pass
                                newChange[cnt] = {'name': i, 'date': j}
                                cnt += 1
                s = []
                for i in range(len(text.split('\n\n')) - 1):
                    s.append(str(i+1))

                text += '\n\nВыберите, какую заявку вы хотите удалить или изменить:'
                send_message(vk_session, 'user_id', event.user_id, message=text, keyboard=create_keyboard(step=step, stepUp=stepUp, name=s))


                # send_message(vk_session, 'user_id', event.user_id, message=f'Заявку на какое предприятие вы хотите посмотреть/изменить?', keyboard=create_keyboard(step=step, stepUp=stepUp, name=canNow))
































            elif step == 5:
                if stepUp == 1:
                    try:
                        globNeed = int(response)
                        step = 5
                        stepUp = 2
                        updateDatas()
                        text = f"Заявка: \n\nПредприятие: {newChange[globNeed]['name']}\nДата: {newChange[globNeed]['date']}\nУчастники: Вы или другой родитель, "
                        for k in allData[newChange[globNeed]['name']][newChange[globNeed]['date']][str(event.user_id)]:
                            try:
                                int(k)
                                if int(k) + 1 in allData[newChange[globNeed]['name']][newChange[globNeed]['date']][str(event.user_id)]:
                                    text += f"{allData[newChange[globNeed]['name']][newChange[globNeed]['date']][str(event.user_id)][int(k)]['name']}, "
                                else:
                                    text += f"{allData[newChange[globNeed]['name']][newChange[globNeed]['date']][str(event.user_id)][int(k)]['name']}."
                            except ValueError or TypeError or KeyError:
                                pass
                        text += '\n\nВажно: при изменении заявки, вы можете поменять только состав участников. Если вы хотите изменить дату экскурсии, то вам прийдется удалить заявку и зарегестрироваться на другое число, используя кнопку "Записаться на экскурсию".\n\nВыберите действие:'
                        send_message(vk_session, 'user_id', event.user_id, message=text, keyboard=create_keyboard(step=step, stepUp=stepUp))

                    except ValueError or TypeError or KeyError:
                        send_message(vk_session, 'user_id', event.user_id, message='Используйте кнопки снизу для ответа.', keyboard=create_keyboard(step=step, stepUp=stepUp, name=s))


                elif stepUp == 2:
                    listAnswers = ['Изменить заявку', 'Удалить заявку']
                    if response in listAnswers:
                        if listAnswers.index(response) == 0:
                            # newReg = {'name': '', 'date': '', 'id': '', 1: 'name', 2: 'name', ...}
                            newReg = {'name': newChange[globNeed]['name'], 'date': newChange[globNeed]['date'], 'id': str(event.user_id)}
                            listNamesImportant = []
                            for i in allData['datas'][str(event.user_id)]:
                                try:
                                    int(i)
                                    listNamesImportant.append(allData['datas'][str(event.user_id)][int(i)]['name'])
                                except ValueError or KeyError or TypeError:
                                    pass
                            step = 3
                            stepUp = 3
                            globCnt = 0
                            wasChild = []
                            send_message(vk_session, 'user_id', event.user_id, message=f'Выберите из ваших детей примет участие в экскурсии.', keyboard=create_keyboard(step=3, stepUp=stepUp, name=listNamesImportant))
                        else:
                            stepUp = 3
                            send_message(vk_session, 'user_id', event.user_id, message='Вы уверены, что хотите удалить заявку?', keyboard=create_keyboard(step=step, stepUp=stepUp))
                    else:
                        send_message(vk_session, 'user_id', event.user_id, message='Повторите попытку. Для ответа используйте кнопки внизу.', keyboard=create_keyboard(step=step, stepUp=stepUp))



                elif stepUp == 3:
                    listAnswers = ['Сохранить заявку', 'Удалить заявку']
                    if response in listAnswers:
                        if listAnswers.index(response) == 0:
                            step = 1
                            send_message(vk_session, 'user_id', event.user_id, message='Заявка сохранена, спасибо, что остаётесь с нами.', keyboard=create_keyboard(step=step))
                        else:
                            del allData[newChange[globNeed]['name']][newChange[globNeed]['date']][str(event.user_id)]
                            saveReg(newChange[globNeed]['name'])
                            step = 1
                            send_message(vk_session, 'user_id', event.user_id, message='Заявка удалена. Мы ждём вас на других экскурсиях.', keyboard=create_keyboard(step=step))
                    else:
                        send_message(vk_session, 'user_id', event.user_id, message='Нет такого варианта ответа. Используйте для ответа кнопки внизу.', keyboard=create_keyboard(step=step, stepUp=stepUp))






























            # Нажата кнопка "Посмотреть или изменить личные данные"
            elif response == "Посмотреть или изменить личные данные" and step == 1:
                text = f"Текущие личные данные:\n\nИмя родителя/представителя: {allData['datas'][str(event.user_id)]['name']}\nТелефон: {allData['datas'][str(event.user_id)]['tel']}\n\n"
                x = 0
                updateDatas()
                for i in allData['datas'][str(event.user_id)]:
                    try:
                        int(i)
                        x += 1
                    except ValueError or TypeError:
                        pass
                if x == 1:
                    text += f"Имя ребенка: {allData['datas'][str(event.user_id)][1]['name']}\nВозраст ребенка: {allData['datas'][str(event.user_id)][1]['age']}\n"
                    text += f"Школа, где обучается ребенок: {allData['datas'][str(event.user_id)][1]['school']}"
                else:
                    g = []
                    for k in allData['datas'][str(event.user_id)]:
                        if type(k) == type(1):
                            g.append(int(k))
                    for i in g:
                        text += f"Имя {numerals[int(i)]} ребенка: {allData['datas'][str(event.user_id)][int(i)]['name']}\nВозраст ребенка: {allData['datas'][str(event.user_id)][int(i)]['age']}\n"
                        text += f"Школа, где обучается ребенок: {allData['datas'][str(event.user_id)][int(i)]['school']}\n\n"

                step = 1.1
                stepUp = 0
                send_message(vk_session, 'user_id', event.user_id, message=text, keyboard=create_keyboard(close=4))






            elif step == 1.1:
                if response == 'Изменить данные':
                    nowPerson[str(event.user_id)] = {}
                    step = 2
                    stepUp = 1
                    send_message(vk_session, 'user_id', event.user_id, message='Введите свой номер телефона, в формате: 89220062243', keyboard=create_keyboard(close=2))



            # Регистрация в системе
            elif step == 2:
                # Нажата кнопка "Зарегестрироваться"
                if stepUp == 0:
                    nowPerson[str(event.user_id)] = {}
                    step = 2
                    stepUp = 1
                    send_message(vk_session, 'user_id', event.user_id, message='Введите свой номер телефона, в формате: 89220062243', keyboard=create_keyboard(close=2))
                # Введён номер телефона
                elif stepUp == 1:
                    try:
                        int(response)
                        if len(response) == 11 and response[0] == '8':
                            nowPerson[str(event.user_id)]['tel'] = response
                            step = 2
                            stepUp = 1.1
                            send_message(vk_session, 'user_id', event.user_id, message='Введите свои ФИО.', keyboard=create_keyboard(close=2))
                        else:
                            send_message(vk_session, 'user_id', event.user_id, message='Формат ввода номера телефона: 89220062243. \nПовторите попытку.', keyboard=create_keyboard(close=2))
                    except ValueError or KeyError:
                        send_message(vk_session, 'user_id', event.user_id, message='Не вводите посторонние символы. Формат ввода номера телефона: 89220062243. \nПовторите попытку.', keyboard=create_keyboard(close=2))

                elif stepUp == 1.1:
                    test = []
                    if len(response.title().split(' ')) == 3:
                        for i in response.title().split(' '):
                            if len(i) >= 2:
                                test.append(True)
                            else:
                                test.append(False)
                        if all(test):
                            nowPerson[str(event.user_id)]['name'] = response.title()
                            step = 2
                            stepUp = 2
                            send_message(vk_session, 'user_id', event.user_id, message='Сколько детей в вашей семье?', keyboard=create_keyboard(step, stepUp))
                        else:
                            step = 2
                            stepUp = 1.1
                            send_message(vk_session, 'user_id', event.user_id, message='Фамилия, имя или отчество не может состоять из менее чем двух символов.', keyboard=create_keyboard(close=2))
                    else:
                        step = 2
                        stepUp = 1.1
                        send_message(vk_session, 'user_id', event.user_id, message='Введите 3 слова через пробел. Фамилия, имя и отчество.', keyboard=create_keyboard(close=2))


                # Нажата кнопка ввода количества членов семьи
                elif stepUp == 2:
                    if getName == 1:
                        try:
                            int(response)
                            age = int(response)
                            getName = 0
                            nowPerson[str(event.user_id)][nowChild]['age'] = age
                            getSchool = 1
                            send_message(vk_session, 'user_id', event.user_id, message=f'Введите ФИО ребенка.', keyboard=create_keyboard(close=2))
                        except ValueError or TypeError or KeyError:
                            send_message(vk_session, 'user_id', event.user_id, message=f'Введите возраст ребенка, используя только цифры. Например: 12.', keyboard=create_keyboard(close=2))

                    elif getSchool == 1:
                        try:
                            if len(response.split()) == 3:
                                aller = []
                                for i in nowPerson[str(event.user_id)]:
                                    if i != 'tel' and i != 'name':
                                        if nowPerson[str(event.user_id)]['name'].upper() != response.upper():
                                            if 'name' in nowPerson[str(event.user_id)][i]:
                                                if nowPerson[str(event.user_id)][i]['name'].upper() != response.upper():
                                                    aller.append(True)
                                                else:
                                                    aller.append(False)
                                                    typeError = 'ФИО ребенка не может повторяться.'
                                            else:
                                                aller.append(True)
                                        else:
                                            aller.append(False)
                                            typeError = 'ФИО ребенка должно отличаться от ФИО родителя.'

                                if all(aller):
                                    getSchool = 0
                                    nowPerson[str(event.user_id)][nowChild]['name'] = response.title()
                                    quantity -= 1
                                    if quantity != 0:
                                        nowChild += 1
                                        nowPerson[str(event.user_id)][nowChild] = {}
                                    else:
                                        stepUp = 3
                                    send_message(vk_session, 'user_id', event.user_id, message=f'Введите название учебного учреждения, где обучается ребенок. \nЕсли ребенок не ходит в школу, напишите "нет".', keyboard=create_keyboard(close=2))
                                else:
                                    getName = 0
                                    send_message(vk_session, 'user_id', event.user_id, message=typeError, keyboard=create_keyboard(close=2))
                            else:
                                getName = 0
                                send_message(vk_session, 'user_id', event.user_id, message=f'Имя, фамилия и отчество должны состоять не менее, чем из 2 букв каждое.', keyboard=create_keyboard(close=2))
                        except ValueError or TypeError or KeyError:
                            send_message(vk_session, 'user_id', event.user_id, message=f'Ошибка ввода. Введите ФИО ребенка повторно.', keyboard=create_keyboard(close=2))


                    elif nowChild >= 2:
                        try:
                            nowPerson[str(event.user_id)][nowChild-1]['school'] = str(response)
                            getName = 1
                            send_message(vk_session, 'user_id', event.user_id, message=f'Введите возраст {numerals[nowChild]} ребенка.', keyboard=create_keyboard(close=2))
                        except ValueError or TypeError or KeyError:
                            send_message(vk_session, 'user_id', event.user_id, message=f'Ошибка ввода. Введите название учебного учреждения, где обучается ребенок повторно.', keyboard=create_keyboard(close=2))

                    else:
                        try:
                            quantity = int(response)
                            nowChild = 1
                            nowPerson[str(event.user_id)][nowChild] = {}
                            getName = 1
                            if quantity == 1:
                                send_message(vk_session, 'user_id', event.user_id, message=f'Введите числом возраст ребенка. Например: 12.', keyboard=create_keyboard(close=2))
                            else:
                                send_message(vk_session, 'user_id', event.user_id, message=f'Введите числом возраст первого ребенка. Например: 12.', keyboard=create_keyboard(close=2))
                        except ValueError or TypeError:
                            step = 2
                            stepUp = 2
                            send_message(vk_session, 'user_id', event.user_id, message='Укажите сколько детей в вашей семье, используя только кнопки снизу.', keyboard=create_keyboard(step, stepUp))

                elif stepUp == 3:
                    nowPerson[str(event.user_id)][nowChild]['school'] = response
                    allData['datas'][str(event.user_id)] = nowPerson[str(event.user_id)]
                    saveUser()
                    step = 1
                    send_message(vk_session, 'user_id', event.user_id, message='Регистрация пройдена. Теперь вы можете записаться на экскурсию.', keyboard=create_keyboard(step=step, close=event.user_id))




            elif step == 3:
                # Выбрано предприятие для экскурсии
                error = 0
                if stepUp == 1:
                    listDates = []
                    response = response.replace('&quot;', '"')
                    listNames = {}
                    for i in names:
                        listNames[names[i]['fullName']] = i
                    x = createListCan(event.user_id)
                    if x[listNames[response]]:
                        if response in listNames:
                            globName = listNames[response]
                            for i in dates[globName]:
                                for k in x:
                                    if i in x[k]:
                                        listDates.append(i.replace('\n', ''))
                            step = 3
                            stepUp = 2


























                            # newReg = {'name': '', 'date': '', 'id': '', 1: 'name', 2: 'name', ...}




















                            newReg = {'name': globName, 'date': '', 'id': str(event.user_id)}
                            send_message(vk_session, 'user_id', event.user_id, message=f'Выберите дату, когда вы хотели бы принять участие в экскурсии.', keyboard=create_keyboard(step=step, stepUp=stepUp, name=listDates))
                        else:
                            step = 3
                            stepUp = 1
                            name = list(createListCan(event.user_id).keys())
                            send_message(vk_session, 'user_id', event.user_id, message='Выберите предприятие из предложенных ниже.', keyboard=create_keyboard(step=step, stepUp=stepUp, name=name))
                    else:
                        step = 1
                        send_message(vk_session, 'user_id', event.user_id, message=f'Вы подали заявки на все экскурсии данного предприятия. Вы можете изменить или удалить заявку, нажав кнопку "Посмотреть или изменить мои заявки".', keyboard=create_keyboard(step=step, close=event.user_id))

                # Выбрана дата экскурсии
                elif stepUp == 2:
                    if response in dates[newReg['name']]:
                        newReg['date'] = response
                        listNamesImportant = []
                        for i in allData['datas'][str(event.user_id)]:
                            try:
                                int(i)
                                listNamesImportant.append(allData['datas'][str(event.user_id)][int(i)]['name'])
                            except ValueError or KeyError or TypeError:
                                pass
                        stepUp = 3
                        globCnt = 0
                        wasChild = []
                        send_message(vk_session, 'user_id', event.user_id, message=f'Выберите, кто из ваших детей примет участие в экскурсии.', keyboard=create_keyboard(step=3, stepUp=stepUp, name=listNamesImportant))
                    else:
                        step = 3
                        stepUp = 2
                        send_message(vk_session, 'user_id', event.user_id, message=f'Выберите дату из предложенных ниже.', keyboard=create_keyboard(step=step, stepUp=stepUp, name=listDates))

                elif stepUp == 3:
                    allNames = []
                    for i in allData['datas'][str(event.user_id)]:
                        try:
                            int(i)
                            allNames.append(allData['datas'][str(event.user_id)][int(i)]['name'])
                        except ValueError or KeyError or TypeError:
                                pass
                    if response.title() in allNames:
                        globCnt += 1
                        newReg[globCnt] = response.title()
                        wasChild.append(response.title())
                        if len(allNames) == 0:
                            stepUp = 4
                            if newReg['name'] in names:
                                allData[newReg['name']]= {newReg['date']: {str(event.user_id): {}}}
                                for i in range(globCnt):
                                    i += 1
                                    allData[newReg['name']][newReg['date']][str(event.user_id)][i] = {'name': newReg[i]}
                                    nowNames = []
                                    for j in allData['datas'][str(event.user_id)]:
                                        try:
                                            int(j)
                                            if allData['datas'][str(event.user_id)][int(j)]['name'] == allData[newReg['name']][newReg['date']][str(event.user_id)][i]['name']:
                                                allData[newReg['name']][newReg['date']][str(event.user_id)][i]['age'] = allData['datas'][str(event.user_id)][int(j)]['age']
                                        except ValueError or TypeError or KeyError:
                                            pass
                                saveReg(newReg['name'])
                                step = 1
                                send_message(vk_session, 'user_id', event.user_id, message=f'Заявка успешно подана, вы можете посмотреть её, нажав кнопку "Посмотреть или изменить мои заявки". Мы проинформируем вас при появлении новых дат экскурсий.', keyboard=create_keyboard(step=step, close=event.user_id))
                        else:
                            listNamesImportantNew = []
                            for i in allNames:
                                f = []
                                for j in wasChild:
                                    if i != j:
                                        f.append(True)
                                    else:
                                        f.append(False)
                                if all(f):
                                    listNamesImportantNew.append(i)
                            if str(response.title().split(' ')[-1])[-3:] == 'вна':
                                sex = 'а'
                            else:
                                sex = ''
                            if len(listNamesImportantNew) == 0:
                                stepUp = 4
                                if newReg['name'] in names:
                                    allData[newReg['name']] = {newReg['date']: {str(event.user_id): {}}}
                                    for i in range(globCnt):
                                        i += 1
                                        allData[newReg['name']][newReg['date']][str(event.user_id)][i] = {'name': newReg[i]}
                                        nowNames = []
                                        for j in allData['datas'][str(event.user_id)]:
                                            try:
                                                int(j)
                                                if allData['datas'][str(event.user_id)][int(j)]['name'] == allData[newReg['name']][newReg['date']][str(event.user_id)][i]['name']:
                                                    allData[newReg['name']][newReg['date']][str(event.user_id)][i]['age'] = allData['datas'][str(event.user_id)][int(j)]['age']
                                            except ValueError or TypeError or KeyError:
                                                pass
                                    saveReg(newReg['name'])
                                    step = 1
                                    send_message(vk_session, 'user_id', event.user_id, message=f'Заявка успешно подана, вы можете посмотреть её, нажав кнопку "Посмотреть или изменить мои заявки". Мы проинформируем вас при появлении новых дат экскурсий.', keyboard=create_keyboard(step=step, close=event.user_id))
                            else:
                                stepUp = 3
                                send_message(vk_session, 'user_id', event.user_id, message=f'{response.title()} добавлен{sex}. Кто еще?', keyboard=create_keyboard(step=3, stepUp=stepUp, name=listNamesImportantNew, close=3))



                    elif response == 'Закончить выбор участников':
                        stepUp = 4
                        if newReg['name'] in names:
                            allData[newReg['name']] = {newReg['date']: {str(event.user_id): {}}}
                            for i in range(globCnt):
                                i += 1
                                allData[newReg['name']][newReg['date']][str(event.user_id)][i] = {'name': newReg[i]}
                                nowNames = []
                                for j in allData['datas'][str(event.user_id)]:
                                    try:
                                        int(j)
                                        if allData['datas'][str(event.user_id)][int(j)]['name'] == allData[newReg['name']][newReg['date']][str(event.user_id)][i]['name']:
                                            allData[newReg['name']][newReg['date']][str(event.user_id)][i]['age'] = allData['datas'][str(event.user_id)][int(j)]['age']
                                    except ValueError or TypeError or KeyError:
                                        pass
                            saveReg(newReg['name'])
                            step = 1
                            send_message(vk_session, 'user_id', event.user_id, message=f'Заявка успешно подана, вы можете посмотреть её, нажав кнопку "Посмотреть или изменить мои заявки". Мы проинформируем вас при появлении новых дат экскурсий.', keyboard=create_keyboard(step=step, close=event.user_id))


                    else:
                        listNamesImportant = []
                        for i in allData['datas'][str(event.user_id)]:
                            try:
                                int(i)
                                listNamesImportant.append(allData['datas'][str(event.user_id)][int(i)]['name'])
                            except ValueError or KeyError or TypeError:
                                pass
                        stepUp = 3
                        send_message(vk_session, 'user_id', event.user_id, message=f'Используйте кнопки внизу для ответа.', keyboard=create_keyboard(step=3, stepUp=stepUp, name=listNamesImportant))














            # elif event.user_id == 538063822:
            #     pass

            else:
                if ' // ' not in response:
                    step = 1
                    send_message(vk_session, 'user_id', event.user_id, message='В этом боте Вы можете онлайн подавать заявки на посещение промышленных предприятий Тюмени с экскурсионными группами.', keyboard=create_keyboard(close=1))
                    send_message(vk_session, 'user_id', event.user_id, message='Для регистрации на экскурсию воспользуйтесь кнопкой \n"Записаться на экскурсию"', keyboard=create_keyboard(close=1))
                    send_message(vk_session, 'user_id', event.user_id, message='Если у Вас возникли вопросы - используйте кнопку \n"Задать вопрос".', keyboard=create_keyboard(step, close=event.user_id))