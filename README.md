# idhar — waitlist landing page

A standalone waitlist page for **idhar**, built to test whether the idea (helping small,
handmade and home-grown businesses get reach, recognition, and counselling) is worth
building out fully.

- **Frontend:** single responsive page, palette pulled directly from the logo
  (maroon `#5C0202`, gold `#F7B61A`, white/paper), Baloo 2 + Inter + JetBrains Mono type,
  scroll reveals, an ambient "ink-stamp" ring motif borrowed from the logo mark, and a
  live waitlist counter.
- **Backend:** a small Flask app. Signups are validated and stored in **Supabase**
  (a hosted Postgres database with a free tier) via its REST API — this works
  identically whether the app runs as a long-lived server (Render) or a serverless
  function (Vercel), which a local CSV file cannot do.

## 1. Set up Supabase (one-time, ~3 minutes)

1. Go to **supabase.com** → sign up → **New project**. Pick any name/region, set a
   database password (you won't need to remember it — the app doesn't use it directly).
2. Once the project is ready, open **SQL Editor → New query**, paste the contents of
   `supabase_schema.sql` from this folder, and run it. This creates one table,
   `waitlist_signups`, with a unique constraint on email so nobody can join twice.
3. Go to **Project Settings → API**. You need two values:
   - **Project URL** → this is `SUPABASE_URL`
   - **service_role key** (under "Project API keys" — NOT the "anon" key) → this is
     `SUPABASE_SERVICE_KEY`

   Keep the service_role key secret — it has full access to your database. It's only
   ever used from your server code (Render/Vercel), never sent to the browser.

## 2. Run it locally

```bash
pip install -r requirements.txt
cp .env.example .env      # then paste in your SUPABASE_URL and SUPABASE_SERVICE_KEY
python app.py
```

Open **http://127.0.0.1:5000**.

## 3. Where the data lives, and how to see it

Every signup becomes a row in the `waitlist_signups` table in your Supabase project.

- **To browse it:** Supabase dashboard → **Table Editor** → `waitlist_signups`. It looks
  and behaves like a spreadsheet — you can filter, sort, and there's an **Export → CSV**
  button whenever you want an actual CSV file to open in Excel/Sheets.
- **To query it in code:** `select * from waitlist_signups order by created_at desc;`
  in the SQL Editor, or pull it into pandas with `supabase-py` / any Postgres client
  using the connection string under Project Settings → Database.

This is the same data regardless of whether the app is deployed on Render, on Vercel,
or running on your laptop — it's one shared database, not something living on whichever
server happened to handle a given request.

## 4. Deploy — Render

1. Push this folder to a GitHub repo.
2. Render dashboard → **New → Web Service** → connect the repo.
3. It should auto-detect Python. Confirm:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   (Both are already captured in `render.yaml` and `Procfile` if you use "New → Blueprint" instead.)
4. Under **Environment**, add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.
5. Deploy. Render gives you a `https://your-app.onrender.com` URL.

No persistent disk needed anymore — the database lives in Supabase, not on Render's
filesystem, so this works fine on Render's free tier.

## 5. Deploy — Vercel

1. Push this folder to a GitHub repo.
2. Vercel dashboard → **Add New → Project** → import the repo. Vercel will detect
   `vercel.json` and use the Python runtime automatically — no build settings to change.
3. Under **Settings → Environment Variables**, add `SUPABASE_URL` and
   `SUPABASE_SERVICE_KEY`.
4. Deploy. Vercel gives you a `https://your-app.vercel.app` URL.

`api/index.py` is the serverless entrypoint Vercel calls; it just imports the same
`app.py` used everywhere else, so there's one codebase, not two.

## Customizing

- **Copy & sections** — edit `templates/index.html`. Section IDs (`#problem`,
  `#solution`, `#counsel`, `#how`, `#join`) match the nav links.
- **Colors & type** — every design token lives at the top of
  `static/css/style.css` under `:root`.
- **Logo** — swap `static/images/logo.jpg` for a higher-res export any time.
- **Base counter offset** — `BASE_OFFSET` in `app.py` (currently 214) pads the "people
  already idhar" counter so it doesn't read "0" on day one. Adjust or remove once you
  have real numbers you're comfortable showing.
