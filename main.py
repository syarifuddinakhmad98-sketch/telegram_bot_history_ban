import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.ext import MessageHandler, filters

TOKEN = "8708411824:AAEiYaB0DYFoiGX-7GlarzENmM-zg6j9wpA"

# =============================
# GOOGLE SHEET CONNECTION
# =============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope)

client = gspread.authorize(creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1K0DuuvuPUWojx0QpmD-3huxEOFj_zSSNj4L44yAEZ1I/edit?resourcekey=&gid=972115993#gid=972115993"
).sheet1

# =============================
# LIST KATEGORI
# =============================

kategori_list = [
    "NOMOR LAMBUNG", "CABANG", "GOLONGAN", "MERK//TYPE", "NOPOL", "PEMAKAI",
    "JENIS KENDARAAN"
]


# =============================
# MENU UTAMA
# =============================
async def start(update, context):

    keyboard = [["NOMOR LAMBUNG", "CABANG"], ["GOLONGAN", "MERK//TYPE"],
                ["NOPOL", "PEMAKAI"], ["JENIS KENDARAAN"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🚚 BOT DATA BAN KENDARAAN\n\n"
        "Silakan pilih kategori pencarian (button kanan bawah) :\n"
        "Filter by Nomor Lambung.\n"
        "Field lain hanya menampilkan data unik\n\n\n",
        reply_markup=reply_markup)


# =============================
# HANDLE PESAN
# =============================


async def reply(update, context):

    text = update.message.text.strip()

    data = sheet.get_all_records()

    # =============================
    # PILIH KATEGORI
    # =============================

    if text in kategori_list:

        daftar = set()

        for row in data:

            value = str(row.get(text, "")).strip()

            if value != "":
                daftar.add(value)

        daftar = sorted(daftar)

        if len(daftar) == 0:

            await update.message.reply_text("❌ Data kategori kosong")

            return

        daftar_text = "\n".join(daftar)

        context.user_data["kategori"] = text

        await update.message.reply_text(f"📋 DAFTAR {text}\n\n"
                                        f"{daftar_text}\n\n"
                                        f"Ketik {text} yang ingin dicari\n\n"
                                        f"Ketik /start untuk kembali ke menu")

        return

    # =============================
    # MODE FILTER DATA
    # =============================

    kategori = context.user_data.get("kategori")

    if kategori:

        hasil = ""

        for row in data:

            value = str(row.get(kategori, "")).strip()

            if value.upper() == text.upper():

                hasil += f"""

🚚 DATA KENDARAAN

Nomor Lambung : {row.get('NOMOR LAMBUNG','')}

Cabang : {row.get('CABANG','')}
Golongan : {row.get('GOLONGAN','')}

Merk : {row.get('MERK//TYPE','')}
Nopol : {row.get('NOPOL','')}


Pemakai :
{row.get('PEMAKAI','')}


Kilometer : {row.get('KILOMETER','')}
Tanggal Ambil : {row.get('TANGGAL AMBIL','')}


Jenis Kendaraan :
{row.get('JENIS KENDARAAN','')}


Nomor Ban : {row.get('NOMOR BAN','')}
Qty : {row.get('QTY','')}


Keterangan :
{row.get('KETERANGAN BAN','')}


----------------------------

"""

        if hasil == "":

            hasil = "❌ Data tidak ditemukan"

        await update.message.reply_text(hasil)

        return

    # =============================
    # DEFAULT
    # =============================

    await update.message.reply_text("Silakan ketik /start untuk memulai")


# =============================
# RUN BOT
# =============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT, reply))

app.run_polling()
