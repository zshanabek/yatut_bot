require 'telegram/bot'
require 'rest-client'
require 'byebug'
token = '350061682:AAE4xRrjpgNi31Vp9ld2A34MEqpqJLrains'

subjects = 'https://tendybook.herokuapp.com/subjects.json'
response = RestClient.get subjects
RestClient.post subjects, {'name' => 'second'}.to_json, {content_type: :json, accept: :json}
subjects_array = JSON.parse(response.body)
# byebug
Telegram::Bot::Client.run(token) do |bot|
  bot.listen do |message|
    case message.text
    when '/start'
      bot.api.sendMessage(chat_id: message.chat.id, text: "Hello, #{message.from.first_name}")
      bot.api.sendMessage(chat_id: message.chat.id, text: "#{subjects_array[0]}")      
    end
  end
end