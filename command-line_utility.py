# importing the requests library
import requests
import csv

URL = 'http://127.0.0.1:5000/'


def get(object):
	request = input('Do you want to see all records (Yes/No) ')

	while request.lower() != 'yes' and request.lower() != 'no':
		print('Please enter Yes or No.')
		request = input('Do you want to see all records (Yes/No) ')

	if request.lower() == 'no':
		id = input('Please enter the id of what you are looking for: ')
		get_url = URL + '{}/{}'.format(object, id)
	else:
		get_url = URL + '{}'.format(object)

	response = requests.get(get_url)

	return response


def add_speech_with_csv():
	add_url = URL + "speeches"
	file_input = str(input("Please enter the name of the csv file: "))

	if ".csv" not in file_input:
		file_input += ".csv"

	with open(file_input, encoding='utf-8') as f:
		reader = csv.DictReader(f)
		responses = []
		for row in reader:
			response = requests.post(add_url, row)
			responses.append(response)

	f.close()
	return responses


if __name__ == '__main__':
	purpose = input(
		'Do you want to add or retrieve information? '
		'(add/retrieve).Enter "quit" to exit the program ')

	while purpose.lower() != 'quit':
		if purpose.lower() == 'retrieve':
			user_input = input(
				'What do you want to know about? (speeches/speakers/topics) ')

			while user_input.lower() != 'speeches' \
				and user_input.lower() != 'speakers' \
				and user_input.lower() != 'topics':

				print('Please enter either "speeches", "speakers", or "topics"')
				user_input = input(
					'What do you want to know about? '
					'(speeches/speakers/topics) ')

			response = get(user_input)
			output = response.json()

			if type(output) is list:
				for record in output:
					for field in record:
						print(field, ":", record[field])
					print('---------------------------')
			else:
				for field in output:
					print(field, ":", output[field])

			purpose = input(
				'Do you want to add or retrieve information? (add/retrieve). '
				'Enter "quit" to exit the program ')

		elif purpose.lower() == 'add':
			responses = add_speech_with_csv()
			if 'error' not in responses[0].json():
				print('The following speeches have been added to the database:')
			for response in responses:
				output = response.json()
				for field in output:
					print(field, ":", output[field])
				print('---------------------------')

			print('\n')
			purpose = input(
				'Do you want to add or retrieve information? (add/retrieve). '
				'Enter "quit" to exit the program ')

		else:
			purpose = input('Please enter either "add", "retrieve", or "quit"')
