import os
import logging
import time
import random
import requests
import csv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Leer variables de entorno
BOT_TOKEN = os.environ.get("8222996356:AAGyj1T-Wthf2R_9GGsIUfhzcttyIMBxKEs")
ADMIN_ID = int(os.environ.get("8191397359"))

BINLIST_URL = "https://lookup.binlist.net/{}"
RATE_DELAY = 0.7  # segundos entre consultas

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin(user_id):
    return user_id == ADMIN_ID

def generate_bin(prefix=None):
    if prefix is None:
        return "".join(str(random.randint(0,9)) for _ in range(6))
    prefix = str(prefix)
    if len(prefix) > 6:
        return None
    return prefix + "".join(str(random.randint(0,9)) for _ in range(6-len(prefix)))

def check_bin(bin6):
    try:
        resp = requests.get(BINLIST_URL.format(bin6), timeout=6, headers={"Accept":"application/json"})
        if resp.status_code == 200:
            d = resp.json()
            bank = (d.get("bank") or {}).get("name") or "N/A"
            country = (d.get("country") or {}).get("name") or "N/A"
            scheme = d.get("scheme") or "N/A"
            typ = d.get("type") or "N/A"
            brand = d.get("brand") or "N/A"
            return f"BIN: {bin6}\nBanco: {bank}\nPaís: {country}\nScheme: {scheme}\nTipo: {typ}\nBrand: {brand}"
        elif resp.status_code == 429:
            return "Rate limit: intenta más tarde."
        else:
            return f"No hay datos (status {resp.status_code})"
    except Exception as e:
        return f"Error: {e}"

# Comandos
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot BIN Checker listo. Solo admin puede generar/consultar.")

def gen(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    if not is_admin(uid):
        update.message.reply_text("Solo el admin puede usar este comando.")
        return
    args = context.args
    prefix = args[0] if args else None
    b = generate_bin(prefix)
    info = check_bin(b)
    update.message.reply_text(info)

def batch(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    if not is_admin(uid):
        update.message.reply_text("Solo el admin puede usar este comando.")
        return
    # ejemplo: /batch 10 4539 -> 10 BINs con prefijo 4539
    try:
        count = int(context.args[0]) if len(context.args) >= 1 else 5
    except:
        count = 5
    prefix = context.args[1] if len(context.args) >= 2 else None
    results = []
    for i in range(count):
        b = generate_bin(prefix)
        info = check_bin(b)
        results.append({"bin":b, "info": info})
        time.sleep(RATE_DELAY)
    # guarda CSV temporal
    fname = "tg_bin_results.csv"
    with open(fname, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bin", "info"])
        for r in results:
            writer.writerow([r["bin"], r["info"]])
    # enviar resumen y adjuntar csv
    summary = "\n\n".join([r["info"] for r in results])
    if len(summary) > 4000:
        summary = "\n\n".join([r["info"] for r in results[:10]]) + "\n\n... (demasiado para mostrar)"
    update.message.reply_text(summary)
    update.message.reply_document(open(fname, "rb"))

# Main
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("gen", gen, pass_args=True))
    dp.add_handler(CommandHandler("batch", batch, pass_args=True))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

        writer = csv.writer(f)
        writer.writerow(["bin", "info"])
        for r in results:
            writer.writerow([r["bin"], r["info"]])
    # enviar resumen y adjuntar csv
    summary = "\n\n".join([r["info"] for r in results])
    if len(summary) > 4000:
        summary = "\n\n".join([r["info"] for r in results[:10]]) + "\n\n... (demasiado para mostrar)"
    update.message.reply_text(summary)
    update.message.reply_document(open(fname, "rb"))

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("gen", gen, pass_args=True))
    dp.add_handler(CommandHandler("batch", batch, pass_args=True))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generar y verificar BINs")
    parser.add_argument("-n", type=int, default=10, help="Cuántos BINs generar")
    parser.add_argument("--prefix", type=str, default=None, help="Prefijo para los BINs (1-6 dígitos)")
    parser.add_argument("--delay", type=float, default=0.6, help="Segundos entre consultas")
    parser.add_argument("--out", type=str, default="bin_results.csv", help="Archivo CSV de salida")
    args = parser.parse_args()

    recs = batch_generate_and_check(n=args.n, prefix=args.prefix, delay=args.delay)
    save_to_csv(recs, args.out)
    print(f"Guardados {len(recs)} registros en {args.out}")
    for r in recs:
        print(r)
