from chat_downloader import ChatDownloader

url = 'https://www.youtube.com/watch?v=d0h_1JW2hV0'
chat = ChatDownloader().get_chat(url, output='test.json')

for message in chat:
    print(chat.print_formatted(message))
