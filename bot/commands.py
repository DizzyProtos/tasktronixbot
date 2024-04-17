import logging
from datetime import datetime
from telegram import Update,  ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler
from bot.database import session, TaskModel
from bot.config import NAME, PROJECT, DESCRIPTION, DEADLINE, REMOVE_ACTION, \
                       HELP_TEXT, LIST_TASKS_TEXT, NEW_TASK_TEXT, SKIP_DEADLINE_TEXT, REMOVE_TASK_TEXT


START_KEYBOARD = ReplyKeyboardMarkup([[KeyboardButton(HELP_TEXT), KeyboardButton(LIST_TASKS_TEXT)],
                                      [KeyboardButton(NEW_TASK_TEXT), KeyboardButton(REMOVE_TASK_TEXT)]],
                                     one_time_keyboard=True)

SKIP_DEADLINE_KEYBOARD = InlineKeyboardMarkup([[InlineKeyboardButton(SKIP_DEADLINE_TEXT, callback_data=0)]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'start cmd from {update.message.from_user.id}')
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text="Hello! I'm your task tracker bot.",
                                   reply_markup=START_KEYBOARD)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'help cmd from {update.message.from_user.id}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="You can use the following commands:\n/start - Start the bot\n/newtask - Add a new task\n/help - Show this help")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logging.info(f'List tasks cmd from user {user_id}')
    tasks = session.query(TaskModel).filter(TaskModel.user_id == user_id).all()
    
    if not tasks:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have no tasks saved.")
        return
    
    tasks_message = "Here are your tasks:\n"
    for task in tasks:
        deadline_str = task.deadline.strftime('%Y-%m-%d') if task.deadline else "No deadline"
        tasks_message += f"Task: {task.name}\nProject: {task.project}\nDeadline: {deadline_str}\nDescription: {task.description}\n\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=tasks_message)


async def start_new_task(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text="Please, enter task's name:")
    return NAME


async def task_name(update: Update, context: CallbackContext):
    user = update.message.from_user
    task_name = update.message.text
    context.user_data['task_name'] = task_name

    reply_keyboard = [['Project Alpha', 'Project Beta', 'Project Gamma']]
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Choose a project:',
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='Select a project'))
    return PROJECT


async def project(update: Update, context: CallbackContext):
    project = update.message.text
    context.user_data['project'] = project
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Please enter the task description:', 
                                   reply_markup=ReplyKeyboardRemove())
    return DESCRIPTION


async def description(update: Update, context: CallbackContext):
    context.user_data['description'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Select the deadline date in DD-MM-YYYY format or skip if there are no deadline:',
                                   reply_markup=SKIP_DEADLINE_KEYBOARD)
    return DEADLINE


async def skip_deadline(update: Update, context: CallbackContext):
    context.user_data['deadline'] = None
    return await end(update, context)


async def repeat_deadline(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                text='Incorrect date format. Please, select the deadline date in DD-MM-YYYY format or skip if there are no deadline:',
                                reply_markup=SKIP_DEADLINE_KEYBOARD)
    return DEADLINE

async def deadline(update: Update, context: CallbackContext):
    try:
        deadline_date = datetime.strptime(update.message.text, "%d-%m-%Y")
    except Exception as e:
        logging.exception(e)
        return await repeat_deadline(update, context)
    
    context.user_data['deadline'] = deadline_date
    return await end(update, context)


async def end(update: Update, context: CallbackContext):
    task_data = context.user_data
    new_task = TaskModel(user_id=update.message.from_user.id,
                         name=task_data['task_name'], 
                         description=task_data['description'], 
                         project=task_data['project'],
                         deadline=task_data.get('deadline'))
    session.add(new_task)
    session.commit()
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=f"Task '{task_data['task_name']}' added successfully!",
                                   reply_markup=START_KEYBOARD)
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Task creation cancelled.',
                                   reply_markup=START_KEYBOARD)
    return ConversationHandler.END


async def remove_task_select(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Please, enter the name of the task to remove.')
    return REMOVE_ACTION


async def remove_task(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    task_name = update.message.text
    
    session.query(TaskModel) \
           .filter(TaskModel.user_id == user_id and TaskModel.name == task_name) \
           .delete(synchronize_session='fetch')
    session.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Task {task_name} deleted.')
    return ConversationHandler.END
