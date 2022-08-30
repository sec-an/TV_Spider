# -*- coding:utf-8 -*-
import asyncio
import hmac
import json
from hashlib import sha256

from Crypto.Cipher import AES
from websockets import connect
import urllib3


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None

KEY = b"55ca5c48a943afdc"
IV = b"d11424dcecfe16c0"


def AesDecrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    text_decrypted = cipher.decrypt(data)
    unpad = lambda s: s[0:-s[-1]]
    text_decrypted = unpad(text_decrypted)
    return text_decrypted.decode("utf-8")


def AesEncrypt(data):
    pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    data = pad(data)
    rawdata = ConvertBytes(data)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(rawdata)


def HmacHash256(data):
    rawdata = ConvertBytes(data)
    key = b"55ca5c4d11424dcecfe16c08a943afdc"
    return hmac.new(key, rawdata, digestmod=sha256).digest().hex()


def ConvertBytes(data):
    if type(data) == str:
        return data.encode("utf-8")
    else:
        return data


def EncryptData(url):
    data = {
        "type": "getUrl",
        "url": url,
        "sign": HmacHash256(url)
    }
    encryptdata = AesEncrypt(json.dumps(data, separators=(',', ':')))
    return encryptdata.hex().upper().encode("utf-8")


async def SendData(data):
    async with connect("wss://player2.lscsfw.com:6723/wss") as ws:
        await ws.send(data)
        return await ws.recv()


def GetPlayUrl(data):
    if type(data) == str:
        rawdata = bytes.fromhex(data)
    else:
        rawdata = data
    dataText = AesDecrypt(rawdata)
    jsondata = json.loads(dataText)
    return jsondata


def get_m3u8(url):
    encryptdata = EncryptData(url)
    rawdata = asyncio.run(SendData(encryptdata))
    return GetPlayUrl(rawdata)
