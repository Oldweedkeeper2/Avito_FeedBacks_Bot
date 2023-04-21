import asyncio
from aiohttp import web
from global_data_phone import PhoneManager

app = web.Application()
phone_manager = PhoneManager()


async def index(request):
    if request.method == 'GET':
        param = request.rel_url.query
        print(param)
        id = param.get('id')
        sender = param.get('from')
        to = param.get('to')
        message = param.get('message')
        imsi = param.get('imsi')
        imei = param.get('imei')
        comport = param.get('comport')
        simno = param.get('simno')
        if 'Авито' in message:
            phone_manager.phone_data[simno] = message.split(' ')[-1]
    return web.Response(text=' ', status=200)


# app.router.add_route('*', '/', index)

# if __name__ == '__main__':
#     web.run_app(app)


