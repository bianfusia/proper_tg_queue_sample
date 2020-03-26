#!/usr/bin/env python3
# encoding=utf-8
#BENJAMIN: Message group limits handle itself in a the group so declaring all limit is sufficient. Use updated updater so that it wont crash on group limit.
'''
MessageQueue usage example with @queuedmessage decorator.
Provide your bot token with `TOKEN` environment variable or list it in
file `token.txt`
'''

import telegram.bot
from telegram.ext import messagequeue as mq


class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)


if __name__ == '__main__':
    from telegram.ext import MessageHandler, Filters, CommandHandler, Updater
    from telegram.utils.request import Request
    import os
    token = '1128954914:AAE6MbS6l3puYb5VtUYRYcxFgTtaEaVL6Dw'
    # for test purposes limit global throughput to 3 messages per 3 seconds
    # 1 message per group per 3 second
    q = mq.MessageQueue(all_burst_limit=30, all_time_limit_ms=1000, group_burst_limit=1)
    # set connection pool size for bot 
    request = Request(con_pool_size=8)
    beeeatanttester = MQBot(token, request=request, mqueue=q)
    updater = Updater(bot=beeeatanttester, use_context=True)

    dispatcher = updater.dispatcher
    def gping(bot, update):
        chat_id = bot.message.chat_id
        for i in range(20):
            message = str(i) + " pong!"
            update.bot.send_message(chat_id=chat_id, text=message)
        
    def pping(bot, update):
        chat_id = bot.message.chat_id
        message = "pong!"
        for i in range(30):
            message = str(i) + " pong!"
            update.bot.send_message(chat_id=chat_id, text=message)

    gping_handler = CommandHandler("gping", gping)
    pping_handler = CommandHandler("pping",pping)
    dispatcher.add_handler(gping_handler)
    dispatcher.add_handler(pping_handler)
    updater.start_polling()
