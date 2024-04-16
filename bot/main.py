from telegram.ext import ApplicationBuilder, CommandHandler, \
                         ConversationHandler, MessageHandler, filters
from bot import commands
from bot.config import BOT_TOKEN, HELP_TEXT, LIST_TASKS_TEXT, NEW_TASK_TEXT, SKIP_DEADLINE_TEXT, REMOVE_TASK_TEXT
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def main():
    logging.info(f'Building application')
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', commands.start))
    application.add_handler(CommandHandler('help', commands.help_command))
    application.add_handler(CommandHandler('listtasks', commands.list_tasks))

    application.add_handler(MessageHandler(filters.Text([HELP_TEXT]), commands.help_command))
    application.add_handler(MessageHandler(filters.Text([LIST_TASKS_TEXT]), commands.list_tasks))

    new_task_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('newtask', commands.start_new_task),
                      MessageHandler(filters.Text([NEW_TASK_TEXT]), commands.start_new_task)],
        states={
            commands.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, commands.task_name)],
            commands.PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, commands.project)],
            commands.DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, commands.description)],
            commands.DEADLINE: [MessageHandler(filters.Regex(r'^\d{2}-\d{2}-\d{4}$'), commands.deadline),
                                CommandHandler('skip', commands.skip_deadline),
                                MessageHandler(filters.Text([SKIP_DEADLINE_TEXT]), commands.skip_deadline)]
        },
        fallbacks=[CommandHandler('cancel', commands.cancel)]
    )
    application.add_handler(new_task_conversation_handler)

    remove_task_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('remove', commands.remove_task_select),
                      MessageHandler(filters.Text([REMOVE_TASK_TEXT]), commands.remove_task_select)],
        states={
            commands.REMOVE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, commands.remove_task)],
        },
        fallbacks=[CommandHandler('cancel', commands.cancel)]
    )
    application.add_handler(remove_task_conversation_handler)


    logging.info(f'Starting polling')
    application.run_polling()


if __name__ == '__main__':
    main()
