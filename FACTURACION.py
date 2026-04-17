import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = "8796156269:AAF0gf1fWZ6o6MZVAl9ve7jhQUOjo66Ftwc"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ==============================
# ESTADO SIMPLE
# ==============================

user_states = {}

# ==============================
# MENÚ PRINCIPAL
# ==============================

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 100 Stars", callback_data="pay_100")],
        [InlineKeyboardButton(text="💳 300 Stars", callback_data="pay_300")],
        [InlineKeyboardButton(text="💳 500 Stars", callback_data="pay_500")],
        [InlineKeyboardButton(text="🧾 Personalizado", callback_data="custom")]
    ])

# ==============================
# START
# ==============================

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "📊 <b>Sistema de Facturación</b>\n\nSelecciona el monto:",
        reply_markup=menu()
    )

# ==============================
# ENVIAR FACTURA
# ==============================

async def enviar_factura(chat_id, amount, servicio="Servicio general"):
    prices = [LabeledPrice(label=servicio, amount=amount)]

    await bot.send_invoice(
        chat_id=chat_id,
        title="Factura de Servicio",
        description=f"{servicio} - {amount} Stars",
        payload=f"{servicio}_{amount}",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="factura"
    )

# ==============================
# BOTONES
# ==============================

@dp.callback_query()
async def botones(call: types.CallbackQuery):

    if call.data.startswith("pay_"):
        amount = int(call.data.split("_")[1])
        user_states[call.from_user.id] = {"amount": amount}
        await call.message.answer("🧾 Escribe el servicio (ej: Netflix, Spotify, Diseño web):")

    elif call.data == "custom":
        user_states[call.from_user.id] = {"custom": True}
        await call.message.answer("💰 Escribe el monto:")

    await call.answer()

# ==============================
# MENSAJES (FLUJO)
# ==============================

@dp.message()
async def flujo(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_states:
        return

    data = user_states[user_id]

    # Si está poniendo monto personalizado
    if "custom" in data:
        try:
            amount = int(message.text)

            if amount <= 0:
                await message.answer("❌ Monto inválido")
                return

            user_states[user_id] = {"amount": amount}
            await message.answer("🧾 Ahora escribe el servicio:")

        except:
            await message.answer("❌ Escribe un número válido")
        return

    # Si ya tiene monto, ahora pide servicio
    if "amount" in data:
        servicio = message.text
        amount = data["amount"]

        await enviar_factura(message.chat.id, amount, servicio)

        user_states.pop(user_id)

# ==============================
# PRE-CHECKOUT
# ==============================

@dp.pre_checkout_query()
async def pre_checkout(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

# ==============================
# CONFIRMACIÓN DE PAGO
# ==============================

@dp.message(lambda m: m.successful_payment)
async def pago_exitoso(message: types.Message):
    amount = message.successful_payment.total_amount
    user_id = message.from_user.id

    factura_id = f"FAC-{user_id}-{int(datetime.datetime.now().timestamp())}"

    with open("pagos.txt", "a", encoding="utf-8") as f:
        f.write(f"{factura_id} | Usuario: {user_id} | Monto: {amount} Stars\n")

    await message.answer(
        f"✅ <b>Pago recibido</b>\n\n"
        f"🧾 Factura: {factura_id}\n"
        f"💰 Monto: {amount} Stars\n"
        f"📌 Estado: Confirmado\n\n"
        f"Gracias por su pago."
    )

    print(f"✔ {factura_id} - {amount} Stars")

# ==============================
# MAIN
# ==============================

async def main():
    print("Sistema de facturación corriendo...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())