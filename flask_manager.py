import asyncio
from aiohttp import web
from global_data_phone import PhoneManager

app = web.Application()
phone_manager = PhoneManager()


async def index(request):
    if request.method == 'POST':
        data = await request.post()
        return web.Response(text=f'Received POST data: {data}')
    else:
        params = request.rel_url.query
        if 'номер' in params.get('message', '').lower():
            phone_manager.phone_data[params.get('message').split(' ')[-1]] = params.get('comport')
            # print(phone_manager.phone_data)

        if 'Авито' in params.get('message', ''):
            phone_manager.code_data[params.get('comport')] = params.get('message').split(' ')[-1]
            # print(phone_manager.code_data[params.get('comport')])

        id = request.rel_url.query.get('id', '')
        return web.Response(text=f'{id}', status=200)


# app.router.add_route('*', '/', index)

# if __name__ == '__main__':
#     web.run_app(app)


