import re, sys, time, random, requests, json, hashlib, datetime
# -*- coding: utf-8 -*-
class Handler:
	reload(sys)
	sys.setdefaultencoding('UTF8')
	#
	# new message handler
	#
	def new_message_handler(self, input_data, c2d):
		schedule = c2d.get_company_info()
		messageid = input_data['message']['id']
		dialogid = input_data['message']['dialogID']
		#dialog_unassign = input_data['dialog']['unassigned']
		#channelidint = input_data['channel']['id']
		try:
			idnovaint = input_data['client']['id']
			#c2d.send_message(idnovaint, str(dialog_unassign),'system')
			if (dialogid is None) and (schedule['online'] == True):
				#c2d.send_message(idnovaint, str(dialogid) + ' dialog_id','system')
				#c2d.send_message(idnovaint, 'online: ' + str(schedule['online']),'system')
				c2d.send_message(idnovaint, str(idnovaint) + ' idnovaint','system')
				tags = self.get_tags(idnovaint)
				c2d.send_message(idnovaint, str(tags) + ' tags_id','system')
				group = self.get_group(tags)
				c2d.send_message(idnovaint, str(group) + ' group', 'system')
				operators = self.get_operators(group)
				#c2d.send_message(idnovaint, str(operators) + ' all_operators', 'system')
				online_operator = self.get_online_operators(idnovaint, operators, c2d, messageid, dialogid)
				c2d.send_message(idnovaint, str(online_operator) + ' online_operator','system')
				#c2d.send_message(idnovaint, 'online: ' + str(schedule['online']),'system')
				self.transfer_to_operator(messageid, dialogid, c2d, online_operator)
			elif (dialogid is None) and (schedule['online'] == False): 
				c2d.transfer_message(messageid, bot_id)
			else:
				c2d.send_message(idnovaint, str(dialogid) + ' dialogid','system')
		except Exception:
			pass
		return dialogid
			#if (dialogid is None) and (schedule['online'] == True): 
				#c2d.transfer_message(messageid, bot_id)		
	def get_tags(self, idnovaint):
		tagid = requests.get('https://api.chat24.io/v1/clients/' + str(idnovaint),
			headers={
			'Authorization': api_token,
			'Content-Type': 'application/json'},
			timeout=2
		)
		tags = json.loads(tagid.text)['data']['tags']
		proper_tags = []
		for t in tags:
			if t['id'] == tag_paid or t['id'] == tag_after or t['id'] == tag_markng:
				proper_tags.append(t['id'])
		return proper_tags

	def get_group(self, tags):
		if tag_paid in tags and tag_after and tag_markng not in tags:
			return group_paid
		elif tag_after in tags and tag_paid and tag_markng not in tags:
			return group_calls
		elif tag_markng in tags and tag_after and tag_paid not in tags:
			return group_ad
		elif tag_paid and tag_markng in tags and tag_after not in tags:
			return group_ad
		elif tag_paid and tag_after in tags and tag_markng not in tags:
			return group_paid
		elif tag_after and tag_markng in tags and tag_paid not in tags:
			return group_ad
		else: 
			return group_attendants


	def get_operators(self, group):
		operators_groups_id = requests.get('https://api.chat24.io/v1/operators_groups',
			headers={
			'Authorization': api_token,
			'Content-Type': 'application/json'},
			timeout=2
		)
		group_data_all = json.loads(operators_groups_id.text)['data']
		group_operator_ids = []
		for g in group_data_all:
			if g['id'] == group:
				group_operator_ids.extend(g['operator_ids'])
		return group_operator_ids

	def getKeysByValue(self, dictOfElements, valueToFind):
		listOfItems = dictOfElements.items()
		for item in listOfItems:
			if item[1] == valueToFind:
				Key = item[0]
		return Key

	def get_online_operators(self, idnovaint, operators, c2d, messageid, dialogid):
		operators_ids = requests.get('https://api.chat24.io/v1/operators/?limit=100',
			headers={
			'Authorization': api_token,
			'Content-Type': 'application/json'},
			timeout=2
		)
		operator_data_all = json.loads(operators_ids.text)['data']
		online_ops = []
		dialog_num = []
		for o in operators:
			for each_op in operator_data_all:
				if (each_op['id'] == o) and (each_op['online'] == 1) and (each_op['offline_type'] == None):
					online_ops.append(o)
					dialog_num.append(each_op['opened_dialogs'])
					break
		if online_ops == [] and messageid == 777:
			operators = self.get_operators(group_attendants)
			c2d.send_message(log_id, 'operators_night ' + str(operators),'system')
			online_operator = self.get_online_operators_night(operators, c2d)
			c2d.send_message(log_id, 'online_operator_night ' + str(online_operator),'system')
			self.transfer_dialog(dialogid, online_operator, c2d)

		elif online_ops == []:
			c2d.send_message(idnovaint, 'no operators online','system')
			time.sleep(1) #убрать задержку
			c2d.transfer_message_to_group(messageid, group_attendants)
			
		zip_op = zip(online_ops, dialog_num)
		dict_op = dict(zip_op)

		if len(online_ops) > 0:
			free_operator = dialog_num[0]
			for n in dialog_num:
				if n < free_operator:
					free_operator = n

		available_op = self.getKeysByValue(dict_op,free_operator)
		return available_op
								
	def transfer_to_operator(self, messageid, dialogid, c2d, online_operator):
		if dialogid is None:
			c2d.transfer_message(messageid, online_operator)
		else:
			pass  

	#
	# before sending message handler
	#
	def before_sending_message_handler(self, input_data, c2d):
		return '[before_sending_message] do logic here'

	#
	# after closing dialog handler
	#
	def after_closing_dialog_handler(self, input_data, c2d):
		return '[after_closing_dialog] do logic here'

	#
	# before closing dialog handler
	#
	def before_closing_dialog_handler(self, input_data, c2d):
		return '[after_closing_dialog] do logic here'

	#
	# auto checking handler
	#
	def auto_checking_handler(self, input_data, c2d):
		messageid = 777
		timeisnow = datetime.datetime.now().time().strftime("%H:%M")
		#c2d.send_message(log_id, 'time: ' + str(timeisnow),'system')
		info = c2d.get_company_info()
		#c2d.send_message(log_id, 'online: ' + str(info['online']),'system')
		if (info['online'] == True) and (timeisnow > "08:04" and timeisnow < "22:00"):
			all_bot_chats = requests.get('https://api.chats.novait.com.ua/v1/dialogs?operator_id=38154&limit=100',
				headers={
				'Authorization': api_token,
				'Content-Type': 'application/json'},
				timeout=2
			)
			bot_data = json.loads(all_bot_chats.text)['data']
			all_bot_chats_ids = []
			all_bot_clients_ids = []
			all_bot_message_ids = []
			for g in bot_data:
				all_bot_chats_ids.append(g['last_message']['dialog_id'])
			#c2d.send_message(log_id, 'dialog_ids: ' + str(all_bot_chats_ids),'system')
			for c in bot_data:
				all_bot_clients_ids.append(c['last_message']['client_id'])
			#c2d.send_message(log_id, 'client_ids: ' + str(all_bot_clients_ids),'system')
			for m in bot_data:
				all_bot_message_ids.append(m['last_message']['id'])
			#c2d.send_message(log_id, 'message_ids: ' + str(all_bot_message_ids),'system')
			zip_info = zip(all_bot_chats_ids, all_bot_clients_ids)
			dict_info = dict(zip_info)
			#c2d.send_message(log_id, 'dictionary ' + str(dict_info),'system')
			for key, value in dict_info.iteritems():
				#c2d.send_message(log_id, 'key ' + str(key),'system')
				#c2d.send_message(log_id, 'value ' + str(value),'system')
				tags = self.get_tags(value)
				#c2d.send_message(log_id, 'tags ' + str(tags),'system')
				group = self.get_group(tags)
				#c2d.send_message(log_id, 'group ' + str(group),'system')
				operators = self.get_operators(group)
				#c2d.send_message(log_id, 'operators ' + str(operators),'system')
				online_operator = self.get_online_operators(log_id, operators, c2d, messageid, key)
				#c2d.send_message(log_id, 'online_operator ' + str(online_operator),'system')
				if key is not None:
					try:
						#c2d.send_message(log_id, 'trasfer','system') 
						self.transfer_dialog(key, online_operator, c2d)
					except Exception:
						pass
				else:
					pass

			# all_op_admin_chats = requests.get('https://api.chats.novait.com.ua/v1/dialogs?operator_id=37861&limit=10&state=op'+'en',
			# 	headers={
			# 	'Authorization': api_token,
			# 	'Content-Type': 'application/json'},
			# 	timeout=2
			# )
			# admin_data_chats = json.loads(all_op_admin_chats.text)['data']
			# all_admin_chats_ids = []
			# #c2d.send_message(log_id, 'dialog_ids: ' + str(admin_data_chats),'system')
			# for g in admin_data_chats:
			# 	all_admin_chats_ids.append(g['last_message']['dialog_id'])
			# c2d.send_message(log_id, 'dialog_ids: ' + str(all_admin_chats_ids),'system')
			# for m_id in all_admin_chats_ids:
			# 	c2d.send_message(log_id, m_id,'system')
			# 	try:	
			# 		requests.put('https://api.chats.novait.com.ua/v1/dialogs/' + str(m_id) + '?operator_id=37861&state=closed',
			# 		headers={
			# 	    'Authorization': api_token,
			# 	    'Content-Type': 'application/json'},
			# 	    timeout=2
			# 		)
			# 		#c2d.send_message(log_id, 'done','system')
			# 	except Exception:
			# 		pass
			# all_op_admin_chats = requests.get('https://api.chats.novait.com.ua/v1/dialogs?operator_id=37861&limit=10&state=op'+'en',
			# 	headers={
			# 	'Authorization': api_token,
			# 	'Content-Type': 'application/json'},
			# 	timeout=2
			# )
			# admin_data = json.loads(all_op_admin_chats.text)['data']
			# all_admin_chats_ids = []
			# all_admin_clients_ids = []
			# all_admin_message_ids = []
			# for g in admin_data:
			# 	all_admin_chats_ids.append(g['last_message']['dialog_id'])
			# #c2d.send_message(log_id, 'dialog_ids: ' + str(all_admin_chats_ids),'system')
			# for c in admin_data:
			# 	all_admin_clients_ids.append(c['last_message']['client_id'])
			# c2d.send_message(log_id, 'client_ids: ' + str(all_admin_clients_ids),'system')
			# for m in admin_data:
			# 	all_admin_message_ids.append(m['last_message']['id'])
			# c2d.send_message(log_id, 'message_ids: ' + str(all_admin_message_ids),'system')
			# zip_info_op = zip(all_admin_chats_ids, all_admin_clients_ids)
			# dict_info_op = dict(zip_info_op)
			# c2d.send_message(log_id, 'dictionary ' + str(dict_info_op),'system')
			# for key, value in dict_info_op.iteritems():
			# 	c2d.send_message(log_id, 'key ' + str(key),'system')
			# 	c2d.send_message(log_id, 'value ' + str(value),'system')
			# 	tags = self.get_tags(value)
			# 	c2d.send_message(log_id, 'tags ' + str(tags),'system')
			# 	group = self.get_group(tags)
			# 	c2d.send_message(log_id, 'group ' + str(group),'system')
			# 	operators = self.get_operators(group)
			# 	c2d.send_message(log_id, 'operators ' + str(operators),'system')
			# 	online_operator = self.get_online_operators(log_id, operators, c2d, messageid, key)
			# 	c2d.send_message(log_id, 'online_operator ' + str(online_operator),'system')
			# 	if key is not None:
			# 		try:
			# 			c2d.send_message(log_id, 'trasfer','system')
			# 			time.sleep(1) 
			# 			self.transfer_dialog(key, online_operator, c2d)

			# 		except Exception:
			# 			c2d.send_message(log_id, 'no_online','system')
			# 	else:
			# 		pass
		else:
			pass

	def transfer_dialog(self, dialogid, online_operator, c2d):
		c2d.transfer_dialog(dialogid, online_operator)

	def get_online_operators_night(self, operators, c2d):
		operators_ids = requests.get('https://api.chat24.io/v1/operators/?limit=100',
			headers={
			'Authorization': api_token,
			'Content-Type': 'application/json'},
			timeout=2
		)
		operator_data_all = json.loads(operators_ids.text)['data']
		online_ops = []
		dialog_num = []
		for o in operators:
			for each_op in operator_data_all:
				if (each_op['id'] == o) and (each_op['online'] == 1) and (each_op['offline_type'] == None):
					online_ops.append(o)
					dialog_num.append(each_op['opened_dialogs'])
					break
			
		zip_op = zip(online_ops, dialog_num)
		dict_op = dict(zip_op)

		if len(online_ops) > 0:
			free_operator = dialog_num[0]
			for n in dialog_num:
				if n < free_operator:
					free_operator = n

		available_op = self.getKeysByValue(dict_op,free_operator)
		return available_op

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
tag_paid = 333
tag_after = 444
tag_markng = 555
group_paid = 666
group_calls = 777
group_ad = 888
group_attendants = 999
log_id = 2432
bot_id = '0000'

# examples
# send message
#response = c2d.get_unanswered_dialogs()

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
