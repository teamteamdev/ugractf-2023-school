import requests
from tqdm import trange

sess = requests.Session()

url = input('Enter url: ')
base_url = input('Enter base url: ')
answer = input('Enter answer: ')


sess.get(base_url)
for i in trange(500):
    resp = sess.post(url, data={'answer': answer}, allow_redirects=False)
    resp.raise_for_status()

resp = sess.get(base_url)
print(resp.text)

