# Setup and Deployment Guide

Step-by-step instructions for deploying the inflation expectations experiment to Heroku. Written for researchers and instructors who are comfortable with basic command-line use but have no prior Heroku or DevOps experience.

---

## Before You Start

You will need:

- A [Heroku account](https://signup.heroku.com/) (free to create; deployment costs ~$10–15/month for a typical classroom run of a few days)
- A credit card on file with Heroku (required for paid dynos and the PostgreSQL add-on)
- [Git](https://git-scm.com/downloads) installed
- Python 3.11 installed (only needed to test the experiment on your own computer first)

Clone this repository and move into it:

```bash
git clone https://github.com/letsgoexploring/teaching-inflation-expectations.git
cd teaching-inflation-expectations
```

All commands below are run from this folder, the root of the repository. The oTree app itself is in the `otree/` subfolder.

Estimated time: 20–30 minutes for a first deployment.

---

## Optional: Test the Experiment Locally

Before deploying, you can run the experiment on your own computer:

```bash
cd otree
pip install -r requirements.txt
otree devserver
```

Open `http://localhost:8000` in a browser, click **Inflation Forecasting** under Demo, and play through it. Press `Ctrl+C` to stop the server, then `cd ..` to return to the repository root.

---

## Step 1: Install the Heroku CLI

The Heroku CLI is a command-line tool for managing your app. Download and install it from:

https://devcenter.heroku.com/articles/heroku-cli

Verify the installation:

```bash
heroku --version
```

---

## Step 2: Log in to Heroku

```bash
heroku login
```

This opens a browser window. Log in with your Heroku account credentials. When complete, your terminal is authenticated.

---

## Step 3: Create a Heroku App

From the root of the repository:

```bash
heroku create your-app-name
```

Replace `your-app-name` with a short, memorable name (e.g., `inflation-forecast-2025`). This name becomes part of your app's URL:

```
https://your-app-name.herokuapp.com
```

If the name is taken, Heroku will tell you — try a variation. If you omit the name entirely, Heroku assigns one automatically.

---

## Step 4: Add a PostgreSQL Database

oTree requires a PostgreSQL database in production. Add Heroku's lowest-cost plan:

```bash
heroku addons:create heroku-postgresql:essential-0
```

Heroku automatically provides a `DATABASE_URL` environment variable that oTree reads. You do not need to configure the database connection manually.

**Expected output:**

```
Creating heroku-postgresql:essential-0 on your-app-name... ~$5/month
Database has been created and is available
```

---

## Step 5: Set Environment Variables

oTree needs four environment variables for production:

```bash
heroku config:set OTREE_ADMIN_PASSWORD=yourpassword OTREE_PRODUCTION=1 OTREE_AUTH_LEVEL=STUDY OTREE_SECRET_KEY=yoursecretkey
```

- **`OTREE_ADMIN_PASSWORD`** — the password for the oTree admin panel. Choose something secure. You will use this to log in at `https://your-app-name.herokuapp.com/`.
- **`OTREE_AUTH_LEVEL=STUDY`**: password-protects the admin panel and only lets people take part through a participant link. **Do not skip this.** Without it, oTree leaves the admin panel, including the data export, open to anyone who finds your app's URL, even if you set a password.
- **`OTREE_PRODUCTION=1`** — switches oTree from development to production mode, enabling PostgreSQL and disabling debug output.
- **`OTREE_SECRET_KEY`** — a secret key used by oTree for cryptographic signing. Generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

You can verify all four were set:

```bash
heroku config
```

**Security note:** None of these values should ever appear in `settings.py` or be committed to the repository. The `settings.py` in this project reads all of them from the environment:

```python
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = environ.get('OTREE_SECRET_KEY')
```

---

## Step 6: Push the Code to Heroku

Heroku deploys via Git. Because the oTree app is in the `otree/` subfolder, push only that folder to Heroku:

```bash
git subtree push --prefix otree heroku main
```

Run this from the repository root. (A plain `git push heroku main` would send the whole repository, and Heroku would fail to find `requirements.txt` and the `Procfile`, which are inside `otree/`.)

If you have edited any files, commit them first (`git add .` then `git commit -m "describe what changed"`), since only committed changes are pushed.

Heroku will:
1. Detect that this is a Python app
2. Read `.python-version` and install Python 3.11
3. Install dependencies from `requirements.txt`
4. Run `otree prodserver` as specified in `Procfile`

This takes 1–3 minutes. You will see build output in your terminal. A successful deployment ends with:

```
remote: -----> Launching...
remote:        Released v5
remote:        https://your-app-name.herokuapp.com/ deployed to Heroku
```

---

## Step 7: Open the App

```bash
heroku open
```

This opens `https://your-app-name.herokuapp.com` in your browser. Log in with:

- **Username:** `admin`
- **Password:** the `OTREE_ADMIN_PASSWORD` you set in Step 5

---

## Step 8: Create a Session

1. In the admin panel, click **Sessions** → **Create new session**
2. Under **Config**, select **Inflation Forecasting**
3. Set **Number of participants** (create at least as many as your expected enrollment, plus a buffer)
4. Optionally change `time_limit_seconds` (default 1200 = 20 minutes)
5. Click **Create**

---

## Step 9: Get Participant Links

After the session is created, click on it to open the session detail page. Go to the **Links** tab to download a list of participant links.

Each link looks like:

```
https://your-app-name.herokuapp.com/InitializeParticipant/abc123xyz
```

Each link is unique and single-use. Distribute one per student.

---

## Redeploying After Changes

Whenever you edit files locally:

```bash
git add .
git commit -m "describe what changed"
git subtree push --prefix otree heroku main
```

Heroku redeploys automatically. Active sessions are not interrupted by redeployment, but it's best to redeploy before a session starts.

---

## Exporting Data

After the session closes, log in to the admin panel and open the **Data** tab. Download the CSV for the `inflation_forecast` app. It has one row per participant per round, with the forecast, actual inflation, forecast error, squared error, a timeout flag, and the post-experiment survey responses. Export the data before scaling down or removing the database.

---

## Scaling Down After the Experiment

To avoid ongoing charges after your experiment is complete, you can scale down the dyno and remove the database:

```bash
heroku ps:scale web=0           # Turns off the dyno (stops billing for compute)
heroku addons:destroy heroku-postgresql:essential-0  # Removes the database
```

**Warning:** Destroying the database is permanent. Export your data first (see [Exporting Data](#exporting-data) below).

---

## Troubleshooting

### View live logs

```bash
heroku logs --tail
```

This streams all log output in real time. Press `Ctrl+C` to stop.

### Check dyno status

```bash
heroku ps
```

You should see one `web` dyno with state `up`.

### Common errors

| Symptom | Likely cause | Fix |
|---|---|---|
| App shows "Application Error" | Crash on startup | Check `heroku logs --tail` for the Python traceback |
| Admin password not accepted | `OTREE_ADMIN_PASSWORD` not set | Run `heroku config` to verify; re-run Step 5 if missing |
| Database connection error | `DATABASE_URL` not set | Verify the Postgres add-on was created (`heroku addons`) |
| Build fails with "No default language could be detected" | The whole repository was pushed instead of the `otree/` folder | Deploy with `git subtree push --prefix otree heroku main` (Step 6) |
| Anyone can open the admin panel | `OTREE_AUTH_LEVEL` not set | Run `heroku config:set OTREE_AUTH_LEVEL=STUDY` |
| `ModuleNotFoundError: psycopg2` | Wrong psycopg2 package | Ensure `requirements.txt` has `psycopg2-binary`, not `psycopg2` |
| Python version error | Wrong Python installed | Confirm `.python-version` contains `3.11` |

### Reset the database (for testing)

If you need to wipe all session data and start fresh during testing:

```bash
heroku pg:reset DATABASE_URL --confirm your-app-name
heroku run otree resetdb
```

**This permanently deletes all data.** Do not run this during or after a real experiment.
