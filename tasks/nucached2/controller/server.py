from kyzylborda_lib.sandbox import start_box
from kyzylborda_lib.secrets import get_flag, validate_token
from kyzylborda_lib.server import http


def init(box):
    with box.open("/flag", "w") as f:
        f.write(get_flag(box.token))


@http.listen
async def handle(request: http.Request):
    token = request.path[1:].partition("/")[0]
    if not validate_token(token):
        return http.respond(404)
    if "X-Forwarded-Host" in request.headers:
        del request.headers["Host"]
        request.headers["Host"] = request.headers["X-Forwarded-Host"]
    return await start_box(token, init=init, pass_secrets=["token"])
