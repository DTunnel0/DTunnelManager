from scripts.socks import WebsocketParseResponse, WS_DEFAULT_RESPONSE


def test_websocket_parse_response():
    body = b'GET / HTTP/1.1\r\nHost: w.dutra01.xyz\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nAccept-Encoding: gzip\r\nX-Forwarded-For: 189.40.100.187\r\nCF-RAY: 774ecb7eb97d1a99-GRU\r\nX-Forwarded-Proto: https\r\nCF-Visitor: {"scheme":"https"}\r\nCF-Connecting-IP: 189.40.100.187\r\nCF-IPCountry: BR\r\nCDN-Loop: cloudflare\r\n\r\n'

    parser = WebsocketParseResponse()
    status = parser.parse(body)

    assert status == WS_DEFAULT_RESPONSE
