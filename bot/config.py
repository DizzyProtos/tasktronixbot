import os
import dotenv


dotenv.load_dotenv('.env')


NAME, PROJECT, DESCRIPTION, DEADLINE, REMOVE = range(5)

REMOVE_ACTION = 0

HELP_TEXT = 'Help'
LIST_TASKS_TEXT = 'List Tasks'
NEW_TASK_TEXT = 'New Task'
SKIP_DEADLINE_TEXT = 'Skip'
REMOVE_TASK_TEXT = 'Remove'


BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
DATABASE_CONNECTION_STRING = os.environ.get('DATABASE_CONNECTION_STRING', '')
