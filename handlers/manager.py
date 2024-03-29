import states.manager_states as manager_states
from roles import manager, admin, user
from loader import dp


def init_manager_handlers():
    dp.register_message_handler(manager.start_command_handler, commands=['start'], state='*')
    dp.register_callback_query_handler(manager.avito_profile_id, text='add_feedbacks')
    dp.register_message_handler(manager.add_reviews_handler, state=manager_states.AddReviews.profile_id)
    dp.register_message_handler(manager.link_handler, state=manager_states.AddReviews.link)
    dp.register_message_handler(manager.excel_handler, content_types=['document'], state=manager_states.AddReviews.excel)
    dp.register_message_handler(manager.amount_of_days_handler, state=manager_states.AddReviews.count_on_day)
    dp.register_callback_query_handler(manager.confirmation_handler, state=manager_states.AddReviews.confirmation)

    dp.register_callback_query_handler(manager.current_feedback_handler, text='current_feedbacks')
    dp.register_callback_query_handler(manager.order_statistic, lambda call: call.data.startswith('current_order_'))
