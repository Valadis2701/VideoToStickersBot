# messages.py

start_message_part1 = "Привет! Я бот, который превращает стикеры в видео."
start_message_part2 = "**Как это работает:**\n\n1. Добавьте меня в групповой чат.\n2. Отправьте мне в личные сообщения команду `/addpair`.\n3. Сначала отправьте видео , а затем видео , которое вы хотите с ним связать.\n4. Когда кто-то отправит этот стикер в групповой чат, я заменю его на видео!"
start_message_part3 = "**Команды:**\n\n* `/addpair` - Добавить пару стикер-видео.\n* `/delpair` - Удалить пару стикер-видео."

add_pair_video_request = "Отправьте мне видео."
add_pair_sticker_request = "Теперь отправьте мне стикер, который вы хотите связать с этим видео."
add_pair_success = "Пара добавлена успешно!"

delete_pair_request = "Отправьте мне стикер, который вы хотите удалить."
delete_pair_success = "Пара удалена успешно!"
delete_pair_unauthorized = "Вы не можете удалить эту пару."
delete_pair_404 = "Пара с этим стикером не найдена"

video_unavailable = "Видео, связанное с этим стикером, больше не доступно. Пара удалена."
sticker_already_paired = "Пара с этим стикером уже существует."

invalid_input_sticker_required = "Не правильно. Отмена..."