import asyncio
import random


#

# без интерполяции
# async def emulate_mouse_movement(page, duration):
#     start_time = asyncio.get_event_loop().time()
#     while (asyncio.get_event_loop().time() - start_time) < duration:
#         x = random.randint(0, page.viewport_size['width'])
#         y = random.randint(0, page.viewport_size['height'])
#         await page.mouse.move(x, y)
#         await asyncio.sleep(random.uniform(0.5, 1))

# с интерполяцией
# async def emulate_mouse_movement(page, duration, n_points=100):
#     start_time = asyncio.get_event_loop().time()
#     x0, y0 = await page.evaluate('''() => {
#                                         const { x, y } = window.scrollY ?
#                                             { x: window.scrollX + window.innerWidth / 2, y: window.scrollY + window.innerHeight / 2 } :
#                                             { x: window.screenX + window.innerWidth / 2, y: window.screenY + window.innerHeight / 2 };
#                                         return [x, y];
#                                     }''')
#     x1 = random.randint(0, page.viewport_size['width'])
#     y1 = random.randint(0, page.viewport_size['height'])
#     delta_t = 1 / (n_points - 1)
#     for i in range(n_points):
#         t = i * delta_t
#         x = x0 + (x1 - x0) * t
#         y = y0 + (y1 - y0) * t + math.sin(t * math.pi) * 50  # добавить синусоидальное движение
#         await page.mouse.move(x, y)
#         # елси нужно посмотреть, что мышь двигается по экрану, вруби (клики+координаты)
#         # await page.mouse.click(x, y)
#         print(x, y)
#         await asyncio.sleep(duration / (n_points - 1))

# по кривым Безье (более плавно) v.2
async def emulate_mouse_movement(page, duration, n_points=100, pause_time=1):
    x0, y0 = await page.evaluate('''() => {
                                        const { x, y } = window.scrollY ?
                                            { x: window.scrollX + window.innerWidth / 2, y: window.scrollY + window.innerHeight / 2 } :
                                            { x: window.screenX + window.innerWidth / 2, y: window.screenY + window.innerHeight / 2 };
                                        return [x, y];
                                    }''')
    # Определяем точки контроля для кривой Безье
    points = [(x0, y0)]
    for i in range(n_points):
        x = random.randint(0, page.viewport_size['width'])
        y = random.randint(0, page.viewport_size['height'])
        points.append((x, y))
    points.append((x0, y0))

    # Вычисляем кривую Безье для заданных точек контроля
    curve_points = []
    for i in range(len(points) - 3):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        x3, y3 = points[i + 2]
        x4, y4 = points[i + 3]
        for j in range(n_points):
            t = j / n_points
            x = (1 - t) ** 3 * x1 + 3 * (1 - t) ** 2 * t * x2 + 3 * (1 - t) * t ** 2 * x3 + t ** 3 * x4
            y = (1 - t) ** 3 * y1 + 3 * (1 - t) ** 2 * t * y2 + 3 * (1 - t) * t ** 2 * y3 + t ** 3 * y4
            curve_points.append((x, y))
    # Считаем, сколько времени прошло с начала выполнения функции
    start_time = asyncio.get_event_loop().time()

    # Двигаем мышь по кривой Безье
    for i, point in enumerate(curve_points):
        # Проверяем, не истекло ли время выполнения функции
        if asyncio.get_event_loop().time() - start_time > duration:
            break
        x, y = point
        await page.mouse.move(x, y)
        # Обновляем позицию элемента-следа мыши
        await page.evaluate(f'''
            const div = document.querySelector('div');
            div.style.left = '{x}px';
            div.style.top = '{y}px';
        ''')
        await asyncio.sleep(duration / (n_points - 1))

        if (i + 1) % 40 == 0:
            await asyncio.sleep(random.uniform(pause_time, pause_time + 1))
            await page.mouse.move(x, y)
