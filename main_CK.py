import re, sys, time, requests, json, datetime
# -*- coding: utf-8 -*-
class Handler:
  reload(sys)
  sys.setdefaultencoding('UTF8')
  #
  # new message handler
  #
  def new_message_handler(self, input_data, c2d):
    input_message = input_data['message']['text']
    message_id = input_data['message']['id']
    client_id = input_data['client']['id']
    dialog_id = input_data['message']['dialogID']
    client_info = c2d.get_company_info() 
    if (dialog_id is None) and (input_message == "Українська мова" or input_message == "1"):
      self.assign_custom_field_lang(client_id,'ua')
    elif (dialog_id is None) and (input_message == "Русский язык" or input_message == "2"):
      self.assign_custom_field_lang(client_id,'ru')
    elif (dialog_id is None) and (input_message in list_with_messages_to_ignore_ua or input_message in list_with_messages_to_ignore_ru):
      pass
    else:
      time.sleep(0.5)
      c2d.send_message(client_id, 'else','system')
      first_mess_yes = self.get_client_inform(client_id, message_id, client_info, dialog_id, input_message, c2d)
      self.assign_custom_field_first_mess(client_id)

  def get_client_inform(self, client_id, message_id, client_info, dialog_id, input_message, c2d):
    client_information = requests.get('https://api.chat24.io/v1/clients/' + str(client_id),
      headers={
      'Authorization': api_token,
      'Content-Type': 'application/json'},
      timeout=10
    )
    client_field = json.loads(client_information.text)['data']['custom_fields']
    #c2d.send_message(client_id, str(client_field),'system')

    #ночь + пункт перевод на оператора + язык укр
    if (input_message in list_chat_with_operator_ua) and ('first_message' in client_field) and (client_field['language'] == 'ua') and (client_info['online'] == False):
      c2d.send_message(client_id, 'first-yes-ua-night-operator','system')
      #self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Всі оператори вже відпочивають. Спробуйте знайти відповідь в меню самообслуговування. Або залиште своє повідомлення і контактні дані. Ми обов' + "'" + 'язково відповімо в робочий час.','to_client')
      c2d.transfer_message(message_id, bot_id) #на бота
      time.sleep(3)
      c2d.send_menu_item(client_id, menu_id_ua)

    #ночь + пункт перевод на оператора + язык рус
    elif (input_message in list_chat_with_operator_ru) and ('first_message' in client_field) and (client_field['language'] == 'ru') and (client_info['online'] == False):
      c2d.send_message(client_id, 'first-yes-ru-night-operator','system')
      #self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Все операторы уже отдыхают. Попробуйте найти ответ в меню самообслуживания. Или оставьте свое сообщение и контактные данные. Мы обязательно ответим в рабочее время.','to_client')
      c2d.transfer_message(message_id, bot_id) #на бота
      time.sleep(3)
      c2d.send_menu_item(client_id, menu_id_ru)

    #день + пункт перевод на оператора + язык укр
    elif (input_message in list_chat_with_operator_ua) and (dialog_id is None) and ('first_message' in client_field) and (client_field['language'] == 'ua') and ('automessage' not in client_field) and (client_info['online'] == True):
      c2d.send_message(client_id, 'first-yes-ua-day-operator','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Ваше звернення переадресовано оператору. Ми відповімо найближчим часом.','to_client')
      c2d.transfer_message_to_group(message_id, operators_group) #на оператора

    #день + пункт перевод на оператора + язык рус
    elif (input_message in list_chat_with_operator_ua) and (dialog_id is None) and ('first_message' in client_field) and (client_field['language'] == 'ru') and ('automessage' not in client_field) and (client_info['online'] == True):
      c2d.send_message(client_id, 'first-yes-ru-day-operator','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Ваше обращение переадресовано оператору. Мы ответим в ближайшее время.','to_client')
      c2d.transfer_message_to_group(message_id, operators_group) #на оператора

    #день + не выбран язык
    elif (dialog_id is None) and ('first_message' in client_field) and ('automessage' not in client_field) and ('language' not in client_field) and (client_info['online'] == True):
      c2d.send_message(client_id, 'first-yes-nolang-day','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Ваше звернення переадресовано оператору. Ми відповімо найближчим часом.','to_client')
      c2d.transfer_message_to_group(message_id, operators_group) #на оператора

    #ночь + не выбран язык
    elif ('first_message' in client_field) and ('language' not in client_field) and ('automessage' not in client_field) and (client_info['online'] == False):
      c2d.send_message(client_id, 'first-yes-nolang-night','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Всі оператори вже відпочивають. Спробуйте знайти відповідь в меню самообслуговування. Або залиште своє повідомлення і контактні дані. Ми обов' + "'" + 'язково відповімо в робочий час.','to_client')
      c2d.transfer_message(message_id, bot_id) #на бота
      time.sleep(3)
      c2d.send_menu_item(client_id, menu_id_ua)

    #день + язык укр
    elif (dialog_id is None) and ('first_message' in client_field) and (client_field['language'] == 'ua') and ('automessage' not in client_field) and (client_info['online'] == True):
      c2d.send_message(client_id, 'first-yes-ua-day','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Ваше звернення переадресовано оператору. Ми відповімо найближчим часом.','to_client')
      c2d.transfer_message_to_group(message_id, operators_group) #на оператора

    #ночь + язык укр
    elif ('first_message' in client_field) and (client_field['language'] == 'ua') and ('automessage' not in client_field) and (client_info['online'] == False):
      c2d.send_message(client_id, 'first-yes-ua-night','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Всі оператори вже відпочивають. Спробуйте знайти відповідь в меню самообслуговування. Або залиште своє повідомлення і контактні дані. Ми обов' + "'" + 'язково відповімо в робочий час.','to_client')
      c2d.transfer_message(message_id, bot_id) #на бота
      time.sleep(3)
      c2d.send_menu_item(client_id, menu_id_ua) 

    #день + язык рус
    elif (dialog_id is None) and ('first_message' in client_field) and (client_field['language'] == 'ru') and ('automessage' not in client_field) and (client_info['online'] == True):
      c2d.send_message(client_id, 'first-yes-ru-day','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Ваше обращение переадресовано оператору. Мы ответим в ближайшее время.','to_client')
      c2d.transfer_message_to_group(message_id, operators_group) #на оператора

    #ночь + язык рус
    elif ('first_message' in client_field) and (client_field['language'] == 'ru') and ('automessage' not in client_field) and (client_info['online'] == False):
      c2d.send_message(client_id, 'first-yes-ru-night','system')
      self.assign_custom_field_automessage(client_id)
      time.sleep(3)
      c2d.send_message(client_id, 'Все операторы уже отдыхают. Попробуйте найти ответ в меню самообслуживания. Или оставьте свое сообщение и контактные данные. Мы обязательно ответим в рабочее время.','to_client')
      c2d.transfer_message(message_id, bot_id) #на бота
      time.sleep(3)
      c2d.send_menu_item(client_id, menu_id_ru) 

    else: 
      c2d.send_message(client_id, 'None pass','system')
      #pass

  def assign_custom_field_automessage(self, client_id):
    customfields = {
        'custom_fields': {
            'automessage': 'yes'                                
        }
    }
    requests.put('https://api.chat24.io/v1/clients/' + str(client_id),
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        data=json.dumps(customfields),
        timeout=3
    )

  def delete_custom_field_automessage(self, client_id):
    customfieldsauto = {
        'custom_fields': {
            'automessage': ''
        }
    }
    requests.put('https://api.chat24.io/v1/clients/' + str(client_id),
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        data=json.dumps(customfieldsauto),
        timeout=10
    )

  def assign_custom_field_lang(self, client_id, lang):
    customfieldslang = {
        'custom_fields': {
            'language': lang                                
        }
    }
    requests.put('https://api.chat24.io/v1/clients/' + str(client_id),
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        data=json.dumps(customfieldslang),
        timeout=10
    )

  def delete_custom_field_lang(self, client_id):
    customfieldslang = {
        'custom_fields': {
            'language': ''                                
        }
    }
    requests.put('https://api.chat24.io/v1/clients/' + str(client_id),
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        data=json.dumps(customfieldslang),
        timeout=10
    ) 

  def assign_custom_field_first_mess(self, client_id):
    customfieldsmess = {
        'custom_fields': {
            'first_message': 'yes'                                
        }
    }
    requests.put('https://api.chat24.io/v1/clients/' + str(client_id),
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        data=json.dumps(customfieldsmess),
        timeout=10
    )

  def delete_custom_field_first_mess(self, client_id):
    customfieldsauto = {
        'custom_fields': {
            'first_message': ''
        }
    }
    requests.put('https://api.chat24.io/v1/clients/' + str(client_id),
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        data=json.dumps(customfieldsauto),
        timeout=10
    )

  #
  # before sending message handler
  #
  def before_sending_message_handler(self, input_data, c2d):
    return '[before_sending_message] do logic here'

  #
  # after closing dialog handler
  #
  def after_closing_dialog_handler(self, input_data, c2d):
    client_id = input_data['client']['id']
    self.delete_custom_field_automessage(client_id)
    self.delete_custom_field_first_mess(client_id)
    self.delete_custom_field_lang(client_id)

  #
  # before closing dialog handler
  #
  def before_closing_dialog_handler(self, input_data, c2d):
    return '[after_closing_dialog] do logic here'

  #
  # auto checking handler
  #
  def auto_checking_handler(self, input_data, c2d):
    timeisnow = datetime.datetime.now().time().strftime("%H:%M")
    dayisnow = datetime.datetime.now().weekday()
    #c2d.send_message(26025052,'time: ' + str(timeisnow),'to_client')
    #c2d.send_message(26025052,'day: ' + str(dayisnow),'system')
    info = c2d.get_company_info()
    if (info['online'] == True) and (dayisnow <= 4) and (timeisnow > "08:10" and timeisnow < "22:00"):
      all_bot_chats = requests.get('https://api.chats.novait.com.ua/v1/dialogs?operator_id=' + str(bot_id) + '&limit=25',
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        timeout=2
      )
      bot_data_chats = json.loads(all_bot_chats.text)['data']
      all_bot_messages_ids = []
      for g in bot_data_chats:
        all_bot_messages_ids.append(g['last_message']['id'])
      #c2d.send_message(26025052, 'messages_ids: ' + str(all_bot_messages_ids),'system')
      for m_id in all_bot_messages_ids:
        #c2d.send_message(26025052, m_id,'system')
        c2d.transfer_message_to_group(m_id, operators_group) #на оператора
      #c2d.send_message(26025052, 'dialog_ids: ' + str(bot_data_chats),'system')
    elif (info['online'] == True) and (dayisnow >= 5 ) and (timeisnow > "10:10" and timeisnow < "22:00"):
      all_bot_chats = requests.get('https://api.chats.novait.com.ua/v1/dialogs?operator_id=' + str(bot_id) + '&limit=25',
        headers={
        'Authorization': api_token,
        'Content-Type': 'application/json'},
        timeout=2
      )
      bot_data_chats = json.loads(all_bot_chats.text)['data']
      all_bot_messages_ids = []
      for g in bot_data_chats:
        all_bot_messages_ids.append(g['last_message']['id'])
      #c2d.send_message(26025052, 'dialog_ids: ' + str(all_bot_chats_ids),'system')
      for m_id in all_bot_messages_ids:
        #c2d.send_message(26025052, m_id,'system')
        c2d.transfer_message_to_group(m_id, operators_group) #на оператора
    else:
      pass
  #
  # after scanning QR-code handler
  #
  def qr_code_result_handler(self, input_data, c2d):
    return '[qr_code_result] do logic here'

  #
  # after manually call
  #
  def manually_handler(self, input_data, c2d):
    return '[manually] do logic here'

  #
  # after chat bot don't triggered
  #
  def chat_bot_not_triggered_handler(self, input_data, c2d):
    return '[manually] do logic here'

  #
  # dialog transfer handler
  #
  def dialog_transfer_handler(self, input_data, c2d):
    return '[dialog_transfer] do logic here'

  #
  # new request handler
  #
  def new_request_handler(self, input_data, c2d):
    return '[new_request] do logic here'

  #
  # client updated handler
  #
  def client_updated_handler(self, input_data, c2d):
    return '[client_updated] do logic here'


api_token = 'token'
menu_id_ua = 333
menu_id_ru = 444
bot_id = 777
operators_group = 888
list_with_messages_to_ignore_ru = ['Назад','000','Завершити чат','0000','В початок меню','00','Новим клієнтам','001','Як отримати кредит?','011','Як сплатити кредит?','012','Який термін кредитування?','013','Наявний кредит','002','Переплата по кредиту','021','  Розмір заборгованості','022','Довідка про закриття кредиту','023','Скарга або пропозиція','003','Докучає реклама','031','  Я не є клієнтом, але мені телефонують','032','Видалити мій Особистий кабінет','033']
list_with_messages_to_ignore_ua = ['Новым клиентам','210','Как получить кредит?','211','Как оплатить кредит','212','Срок кредитования','213','Имеющийся кредит','220','Переплата по кредиту','221','Размер задолженности','222','Справка о закрытии кредита','223','Жалоба или предложение','230','Беспокоит реклама','231','Я не клиент, но мне звонят','232','Удалить Личный кабинет','233']
list_chat_with_operator_ru = ['Связь с оператором','240','214','224','234','333']
list_chat_with_operator_ua = ['Підключити оператора','004','014','024','034','111']
# examples
# send message
#response = c2d.send_message(94212, 'test!!!')

# send question
#response = c2d.send_question(94212, 4321)

# get client info
#response = c2d.get_client_info(94212)

# get operators
#response = c2d.get_operators()

# get online operators
#response = c2d.get_online_operators()

# get list of question
#response = c2d.get_questions(5369, '10-10-2015', '10-10-2016')

# get last question
# response = c2d.get_last_question(5369)

# get unanswered dialogs
#response = c2d.get_unanswered_dialogs(18000)

# transfer dialog
#response = c2d.transfer_dialog(81984, 1899)

# get last message id in dialog
# dialog_id = 100
# type = 2 (1-client, 2-operator, 3-auto, 4-system)
# 2*24*60*60 time ago
#response = c2d.get_last_message_id(100, 2, 2*24*60*60)

# operator groups_ids
# operator_id = 81984
#response = c2d.get_operator_group_ids(81984)

# check if operator in group
# operator_id = 81984
# group_id = 81984
#response = c2d.operator_in_group(81984, 100)

# not send menu in new_message_handler add
# print 'not send menu'
        