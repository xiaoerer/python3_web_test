import sys
import orm, asyncio
from models import User, Blog, Comment

async def test(loop):
    
    await orm.create_pool(loop=loop, user='root', password='123456', db='python_jun')

    u = User(name='Test2', email='xiaoer@example.com', passwd='123456', image='aaabout:blank')

    await u.save()



if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete( asyncio.wait([test( loop )]) )  
    loop.close()
    if loop.is_closed():
        sys.exit(0)
