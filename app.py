import time
import requests
from fastapi import FastAPI, Query
from byte import Encrypt_ID
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

app = FastAPI(title="Like API")

KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
IV  = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])

LIKE_URL   = "https://clientbp.ppmainecoonghj.com/LikeProfile"
TOKEN_API  = "https://perlextoken.vercel.app/token?uid={uid}&password={pw}"
INFO_API   = "https://perlexinfo.vercel.app/info?uid={uid}"

TOKEN_TTL = 3600

ACCOUNTS = [
    ("8026375043", "SOE5OR0AVDYV0KL4UZRTJTT78W5J45Y6ND54A49PTWNJC40GNOY2KBXSNE6DXBRX"),
    ("8033691787", "7072678XAMMWQRHGMSPPH3X5YF0VKCUSCT43JMF67IYRA161M15J0Z7IJ5IUQZZS"),
    ("8033691789", "GDXHS8UI45PFABVHPDLM81LW67EZXFVZ1JBLJR73SBEI1LEP0JNUGMZ69ESVBHGL"),
    ("8033691814", "E8W8N9Y4ZJ9OG26UTQ5ENLB51HTMT5Y59M0GP0M77Y1NSJFMWEUFO395CLYO5SCO"),
    ("8033692938", "XPALGJ1RSTX2O65Z00JS4IWDIUEM34YV9VFAY7NW4LJN2Q22D34FZ256QL28AY0L"),
    ("8033693038", "LW4395ZXIJRJAM3M0U61KHAIQP8R1STC7L3B03B3CXR5FJFSKIRXRG63JBD8NV9B"),
    ("8033693060", "K9JIQH58SOJF6VTY13E0WMOGXBY326R7IC4804MIK0W690ZE1JDULLDUFHEK6SNR"),
    ("8033693724", "EX02WTB3GS0PUHKKK41NZO2XPNW4RELRNX5VLBX1C698B2Y0U00GTX1Z97LE83SV"),
    ("8033693766", "0X2OH4L6EX1I572S4YW0P9JS0UC1U44255T77X21KNYRGVLE5CH3HSZW9NYT6DJJ"),
    ("8033693874", "ZES2016503IY9VNHH2VQRY2JGYAEX2B1PW5FPJM3SF6O9WPCKYADGQ63I0S9U5E5"),
    ("8033694615", "A0Z8AICHWTL4HH1ZKA4BT045RC4DQ5TDCYTJC22EW91JVQM02K91QQMRLQBF41DA"),
    ("8033694820", "XHVHYC5K2NWDX9R6L0507TW85P5AJJY9BG3TGMO8KKNH8HU2SZ6B2P6JFWZQ0US4"),
    ("8033695370", "4EATFWBFPMJDZ3OV2XG86GP8ODH2U75G6105D54QHRB89JRNGLRY6X5BO2ZL3VQH"),
    ("8033695474", "NBZ0IBIPRJLUOL0RRU037XI8VAMCY8YWLH68BJ1M75JMAD6INNH1W6EQD2SVHO0H"),
    ("8033695576", "7G7C7XK3L9H7SA18AUUU8COLXR5BUY0CJZ3U9PB352Q66LF1982W1FMZGHVRJVDA"),
    ("8033695712", "DQF6CXFYL2V04K6HH418ILIVFGJYQCNB65GW9OFYQT6ZK0AIS1E9FFOE4UZS440C"),
    ("8033695791", "GIRS14QQVGEN1AGKAJLHNMZQGYALVEUYY8A2QORZCOMB9M422VD2Z3KN7HXEUS4T"),
    ("8033695798", "SDA4UY8KJ4P3YZ6HVGCLUXDV8OL332XV2WJS4PONXMNDGIPZ2K6TA5XSM6SJ5XH1"),
    ("8033696167", "L7S3IQ11YEKHA2I8ZGG1LNC7FDVTOCN3OG78KOL0JLVD75BSC2GEA7VIV32MWX46"),
    ("8033696179", "LOYBM1ZDMYY7AIUO335I1XTB57X7O6JZTVRLKKUR1HD9QYALU99F9LO3FFLBLGXH"),
    ("8033697284", "WHWDI8FNYHJ91OY32QCTUHT6UBLIZGURLJCSZYHE7P6BYKJF1D0WLMGIGNKHBAY3"),
    ("8033697372", "ROBZ9J7UWH4HV6UCII7G016I2JOKJNV0S33B5G11AWQUKSJ970GCI01PTTCHH3QM"),
    ("8033697402", "QVFOHXY6I2MMAXWA9O4I8DKU0O8BUT5JTV6H0DFAO1MXVSST7I53499RNWI8HSFL"),
    ("8033697428", "Z188E8VW6EMCOJKE4SKGZG7NCBEJS7SLUOUVNT4Y3DRBZTXH64XY2FA989JIGZSV"),
    ("8033697423", "E5E37S3XTNV8LQXXXBJIAUCLEC5OWJVUYAKEQ5FBOYWCPYBGSLXLA3IYZHJ0ZEOV"),
    ("8033698447", "9BRPHDNLMOLPXYNPR8TD97I8I7JJ28SBAQN58ORA6NU91BQ3PLQ1076RNXO6W76Q"),
    ("8033698440", "CWA9PCW7HMLORQFM49000SOKX74LS2CT481N2KODHSRZFDURH8FJNF6S8ZUCNA66"),
    ("8033698688", "2JGXTFE3I75ZB716VRHA5RW7F3P7SH5S7GWAE7S95117SPP08MPX8TCGJ4GR53AO"),
]

_token_cache: dict = {}


def get_token(uid: str, pw: str) -> str:
    now = time.time()
    cached = _token_cache.get(uid)
    if cached and cached["expires_at"] > now:
        return cached["jwt"]
    r = requests.get(TOKEN_API.format(uid=uid, pw=pw), timeout=30)
    r.raise_for_status()
    jwt = r.json()["jwt"]
    _token_cache[uid] = {"jwt": jwt, "expires_at": now + TOKEN_TTL}
    return jwt


def build_payload(target_uid: str) -> bytes:
    enc = Encrypt_ID(str(target_uid))
    plain = bytes.fromhex(f"08{enc}")
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(plain, AES.block_size))


def fetch_info(uid: str) -> dict:
    r = requests.get(INFO_API.format(uid=uid), timeout=30)
    r.raise_for_status()
    return r.json()


def extract_likes(info: dict) -> int:
    return int(info.get("basicInfo", {}).get("liked", 0))


def send_like(jwt: str, payload: bytes):
    headers = {
        'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
        'Connection': 'Keep-Alive',
        'Accept': '*/*',
        'Accept-Encoding': 'deflate, gzip',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Expect': '100-continue',
        'X-Unity-Version': '2018.4.12f1',
        'X-GA': 'v1 1',
        'X-GA-SV': str(int(time.time())),
        'ReleaseVersion': 'OB55',
        'Authorization': f'Bearer {jwt}',
    }
    return requests.post(LIKE_URL, headers=headers, data=payload, timeout=30)


@app.get("/like")
def like_endpoint(uid: str = Query(..., description="Target UID to like")):
    target_uid = uid
    payload = build_payload(target_uid)

    try:
        before_info = fetch_info(target_uid)
        name  = before_info.get("basicInfo", {}).get("nickname", "Unknown")
        level = before_info.get("basicInfo", {}).get("level", 0)
        likes_before = extract_likes(before_info)
    except Exception as e:
        return {"ok": False, "error": f"failed to fetch info before: {e}"}

    results = []
    success = 0
    failed = 0
    for account_uid, pw in ACCOUNTS:
        try:
            jwt = get_token(account_uid, pw)
            resp = send_like(jwt, payload)
            results.append({
                "uid": account_uid,
                "status_code": resp.status_code,
                "body": resp.text[:200],
            })
            if resp.status_code == 200:
                success += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            results.append({"uid": account_uid, "status": "error", "error": str(e)})
        time.sleep(0.3)

    try:
        after_info = fetch_info(target_uid)
        likes_after = extract_likes(after_info)
    except Exception as e:
        return {"ok": False, "error": f"failed to fetch info after: {e}"}

    return {
        "ok": True,
        "target": {
            "uid": target_uid,
            "name": name,
            "level": level,
            "likes_before": likes_before,
            "likes_after": likes_after,
            "likes_added": likes_after - likes_before,
        },
        "summary": {
            "total": len(ACCOUNTS),
            "success": success,
            "failed": failed,
        },
        "accounts": results,
    }
