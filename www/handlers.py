__author__='xiaoer'

'url handlers'


import re, time, json, logging, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError

from models import User, Comment, Blog, next_id
from config import configs

COOKIE_NAME='xiaoersession'
_COOKIE_KEY='configs.session.secret'


def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError()

def get_page_index(page_str):
	p=1
	try:
		p=int(page_str)
	except ValueError as e:
		raise e
		pass
	if p<1:
		p=1
	return p

def user2cookie(user,max_age):
	expires=str(int(time.time()+max_age))
	s='%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L=[user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
	return ''.join(lines)

@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
		return None

"""
@get('/')
async def index(request):
	'''
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
    '''
    summary='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs=[
    	Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
		Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

"""
@asyncio.coroutine
@get('/')
def index(request):
	summary='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
	blogs=[
		Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
	    Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
		Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
	    ]
	return {
	    '__template__': 'blogs.html',
	    'blogs': blogs
	}


# @get('/api/users')
# def api_get_users():
# 	users=yield from User.findAll(orderBy='created_at desc')
# 	for u in users:
# 		u.passd='******'
# 	return dict(users=users)


# 注册
@get('/register')
def register():
	return {
		'__template__':'register.html'
	}

# 登录
@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
	}



_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
def api_register_user(*,email,name,):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not email.strip():
		raise APIValueError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users=yield from User.findAll('email=?', [email])
	if len(users)>0:
		raise APIError('register:failed','email','Email is already in use.')
	uid=next_id()
	sha1_passwd='%s:%s' % (uid,passwd)
	user=User(id=uid,name=name.strip(),email=email,passwd=hashlib.sha1_passwd.encode('utf-8').hexigest(),image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	yield from user.save()
	r.web.Pesponse()
	r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=96400,httponly=True)
