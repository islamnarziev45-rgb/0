# Tez VPN Telegram chat bot

This is a separate Tez bot for the regular Telegram chat (not the Mini App). It has the agreed chat menu and RU/TJ/UZ/KG text, plan selection, trial request, subscription/status view, referral link, promo entry, gift flow, support link and device/key actions.

## Confirmed business settings

- Trial: 2 days, 3 GB.
- Paid plans: 1 month — 150 ₽; 3 months — 399 ₽; 6 months — 679 ₽.
- Paid traffic: 150 GB per month, shown in subscription status; keep ordinary-location unlimited traffic policy on the backend if the VPN panel supports that distinction.
- Device cap: 2.
- Referral: +3 days to the inviter after a newly referred user makes their first verified payment. The bot displays verified invite counts and awarded days from the backend only.

## Run

Requires Python 3.10+ and no third-party Python packages.

1. Revoke the bot token previously shared in chat and create a replacement in BotFather.
2. Set the values from `.env.example` as environment variables on a private server. Never put a real token in GitHub, this folder, a Mini App, or a message.
3. Set `TEZ_BACKEND_URL` and `TEZ_BACKEND_SECRET` only after the Tez VPN API is deployed.
4. Run `python bot.py`.

The bot uses long polling, so it can start without a public webhook URL. It still needs to run on an always-on server to answer users.

## Backend contract

All backend requests use `Authorization: Bearer <TEZ_BACKEND_SECRET>`.

- `POST /api/trial` with `{telegram_id, days: 2, limit_gb: 3}`. The backend must enforce one trial per eligible user and return `{subscription: {...}}` only after the VPN user/key was created.
- `GET /api/me?telegram_id=...` returns `{subscription: null}` or a subscription with `status`, `expires_at`, `remaining`, `used_gb`, `limit_gb`, `devices`, `subscription_url`, and optional `happ_url`/`incy_url`.
- `GET /api/referrals?telegram_id=...` returns verified counts and applied bonus days. The front end never awards the bonus itself.
- `POST /api/referrals/register` records a referral candidate. The backend must reject existing users, self-referrals and duplicates; award +3 days only after the referred user's first verified payment.
- `POST /api/payments` with `{telegram_id, plan, method, gift}` returns `checkout_url` only when a real provider is configured. Payment is granted only after a signed provider webhook.
- `POST /api/promos/redeem` with `{telegram_id, code}` validates and applies a promo code.
- `POST /api/subscription/renew-key` rotates the VPN key only after the VPN panel confirms the operation.

## Important launch limit

The Telegram menu and conversations can run, but trial activation, payments, VPN key issuance, traffic/device reporting, promo redemption and verified referral rewards remain unavailable until the Tez backend and server are connected. The bot deliberately reports this instead of showing a fake successful payment or key.

