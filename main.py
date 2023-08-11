import aiohttp, asyncio, json
import urllib.parse

proxy = ''

def get_url_encoded_data(dict_data: dict) -> str:
	return "&".join(
		[urllib.parse.quote_plus(dict_1) + "=" + urllib.parse.quote_plus(dict_data[dict_1]) for dict_1 in dict_data])

async def send_code_qiwi(qiwi_number: str, token_head: str, token_tail: str):
	cookies = {
		'token-tail-web-qw': token_tail,
	}
	
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:110.0) Gecko/20100101 LibreWolf/110.0',
	}

	data = {
		'response_type': 'code',
		'client_id': 'qiwi_wallet_api',
		'client_software': 'WEB v4.96.0',
		'username': qiwi_number,
		'scope': 'read_person_profile read_balance read_payment_history accept_payments get_virtual_cards_requisites write_ip_whitelist',
		'token_head': token_head,
		'token_head_client_id': 'web-qw',
	}

	url = f"https://qiwi.com/oauth/authorize?{get_url_encoded_data(data)}"
	
	async with aiohttp.ClientSession() as session:
		async with session.post(url=url, headers=headers, cookies=cookies, proxy=proxy) as response:
			result = await response.text()
			result = json.loads(result)

			return result

async def confirm_token_creation(send_code: str, sms_code: str, token_tail: str):
	cookies = {
		'token-tail-web-qw': token_tail,
	}

	headers = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:110.0) Gecko/20100101 LibreWolf/110.0',
	}

	data = {
		'grant_type': 'urn:qiwi:oauth:grant-type:vcode',
		'client_id': 'qiwi_wallet_api',
		'code': send_code,
		'vcode': sms_code
	}
	
	url = f"https://qiwi.com/oauth/token?{get_url_encoded_data(data)}"

	async with aiohttp.ClientSession() as session:
		async with session.post(url=url, data=data, headers=headers, cookies=cookies, proxy=proxy) as response:
			result = await response.text()
			result = json.loads(result)

			return result

async def main():
	token_head = input('[?] Введите TOKEN HEAD: ')
	token_tail = input('[?] Введите TOKEN TAIL: ')
	phone = input('[] Номер телефона: ')
	
	send_code = await send_code_qiwi(phone, token_head, token_tail)
	
	if 'error' not in send_code:
		print('[] Запрос СМС: ' + str(send_code))
		
		sms_code = input('[?] Укажите код из СМС: ')
		result = await confirm_token_creation(send_code['code'], sms_code, token_tail)
		print('[] Выпуск токена: ' + str(result))
		print('[✓] Токен выпущен: ' + result['access_token'])
	else:
		print('[X] Произошла ошибка: ' + str(send_code))
		

if __name__ == '__main__':
	asyncio.run(main())