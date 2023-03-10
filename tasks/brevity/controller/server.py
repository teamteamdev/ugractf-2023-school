from kyzylborda_lib.sandbox import start_box
from kyzylborda_lib.secrets import validate_token
from kyzylborda_lib.server import tcp


@tcp.listen
async def handle(conn: tcp.Connection):
    await conn.writeall(b"Vvedite zheton: ")
    token = (await conn.readline()).decode(errors="ignore").strip()
    if not validate_token(token):
        await conn.writeall(b"Zheton nepravilniy!!!\n")
        return
    await conn.writeall(b"Podklyuchayu...\n")
    return await start_box(token, pass_secrets=["flag"])