# FlipEarn

A marketplace platform for buying and selling social media accounts and channels (YouTube, Instagram, TikTok, and more).

**Live Frontend:** https://socialflip.vercel.app/

---

## Project Structure

```
flipearn/
├── src/          # React frontend
└── backend/      # FastAPI backend
```

---

## Frontend

Built with React + Vite + Tailwind CSS.

```bash
npm install
npm run dev
```

Runs at `http://localhost:5173`

---

## Backend

Built with FastAPI + SQLAlchemy + SQLite.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs at `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

### What the backend covers
- JWT authentication (register, login)
- Listings — create, browse, approve/reject
- Transactions — buy a listing
- Withdrawals — seller payouts with admin review
- Dashboard — live stats (users, revenue, listings)

For full backend documentation see [backend/README.md](backend/README.md).
