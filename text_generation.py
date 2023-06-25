import requests

TEXTGEN_HOST = 'localhost:5000'
TEXTGEN_URI = f'http://{TEXTGEN_HOST}/api/v1/chat'

class TextGenerator:
    def generate(self, user, prompt, context = '', history = {'internal': [], 'visible': []}):
        # TODO personality, context, etc
        payload = {
            'user_input': prompt,
            'preset': 'bot',  
            'seed': -1,
            'mode': 'chat', # instruct
            'history': history,
            'character': 'Pepega',
            'instruction_template': 'Alpaca',
            'your_name': user,

            'regenerate': False,
            '_continue': False,
            'stop_at_newline': False,
            'chat_prompt_size': 2048,
            'chat_generation_attempts': 1,
            'chat-instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stopping_strings': [],

            'chat_style': 'cai-chat',
            'context': context,
        }

        print('Fetching text from api')
        response = requests.post(url=TEXTGEN_URI, json=payload)

        if response.status_code == 200:
            result = response.json()['results'][0]['history']
            print(result)
            return result

        raise Exception('Could not generate')
