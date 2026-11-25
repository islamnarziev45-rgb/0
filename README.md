# Tez VPN Telegram bot

Separate Telegram chat bot for the Tez VPN brand. This repository contains the bot source and deploy configuration for Bothost.

Business settings: trial 2 days with 3 GB; paid plans 1 month — 150 ₽, 3 months — 399 ₽, 6 months — 679 ₽; up to 2 devices; verified referral reward +3 days after the invited user's first paid subscription. Languages: Russian, Tajik, Uzbek, Kyrgyz. Support: @tbworstversion.

## Deployment

Set environment variables from `.env.example` in the hosting control panel. Never commit real tokens or secrets. The bot runs with `python main.py` and uses Telegram long polling.

## Important

Trial, payment, subscription/key provisioning, usage/device reporting, promo redemption and referral rewards require the separate Tez VPN backend and server. Payment is not enabled until a real provider is configured. Do not treat this bot as production-ready until the backend is deployed and connected.

See the full backend API contract and setup notes below in this README or the local project notes before launch.