import asyncio
import websockets

async def test_ws():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as ws:
            print('WebSocket соединение установлено')
            await ws.send('ping')
            msg = await ws.recv()
            print('Ответ:', msg)
    except Exception as e:
        print('Ошибка:', e)

if __name__ == '__main__':
    asyncio.run(test_ws()) 