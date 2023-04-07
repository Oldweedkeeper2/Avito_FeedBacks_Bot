from loguru import logger


async def error_log(data, error_text):
    logger.error(error_text)
    data['errors'].append(error_text)
    print(data)
