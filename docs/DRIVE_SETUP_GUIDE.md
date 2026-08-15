# Google Drive Setup — A to Z

**For:** Zane (MD) · **No coding required** · ~15 minutes
**What you get:** every proposal, plan and document ZYNTH produces lands in your
Google Drive automatically, filed by sector, at the moment it is created.

---

## Before you start

You are already in the right place in the screenshot — Railway → your service →
**Variables** tab. Keep that tab open; you will come back to it in Part C.

You need two things that do not exist yet:

1. A **service account** — a robot Google account that belongs to ZYNTH, not to
   you personally. This is what lets the bot write to Drive at 3am without you
   being logged in.
2. Its **key file** — a JSON file you download once and paste into Railway.

> **Why not just use your own Google login?** Because the bot runs unattended.
> A personal login expires and needs a human to click "allow". A service account
> does not. It is also safer: you can revoke it without touching your own account.

---

## PART A — Create the service account (Google Cloud, ~7 min)

Do this on a laptop if you can. It is possible on iPad but the Cloud Console is
cramped.

### A1. Open Google Cloud Console
Go to **https://console.cloud.google.com** and sign in as **zane@zynth.asia**.

### A2. Create a project
- Top of the page there is a project dropdown (it may say "Select a project").
- Click it → **New Project**.
- Name: `ZYNTH Brain`
- Click **Create**. Wait ~10 seconds, then make sure the dropdown now says
  **ZYNTH Brain**.

> If you already have a project you use for ZYNTH, use that instead.

### A3. Turn on the Drive API
- In the search bar at the top, type **Google Drive API**.
- Click the result, then click the blue **Enable** button.
- Wait for it to finish. If it already says "Manage", it is already on — fine.

### A4. Create the service account
- Search bar → type **Service Accounts** → open it.
- Click **+ Create Service Account** at the top.
- **Service account name:** `zynth-drive`
- The **Service account ID** fills in automatically. Leave it.
- Click **Create and Continue**.
- On the "Grant this service account access" step: **skip it**, click **Continue**.
- On the last step: **skip it**, click **Done**.

### A5. Download the key
- You are now back on the Service Accounts list. Click the account you just made
  (`zynth-drive@...`).
- Go to the **Keys** tab.
- **Add Key** → **Create new key** → choose **JSON** → **Create**.
- A `.json` file downloads. **This file is a password.** Do not email it, do not
  put it in a group chat, do not commit it to GitHub.

### A6. Copy the robot's email address
Still on that page, copy the service account's email. It looks like:

```
zynth-drive@zynth-brain-123456.iam.gserviceaccount.com
```

You need it in Part B. Paste it somewhere safe for a minute.

---

## PART B — Give the robot access to your Drive folder (~2 min)

The service account starts with access to **nothing**. You have to invite it,
exactly like inviting a colleague.

### B1. Open the proposals folder
https://drive.google.com/drive/folders/1e8-n4Tm2GjzsmJW3O53HuqtNuQIxP3lX

(That is your existing **ZYNTH-Proposals** folder.)

### B2. Share it with the robot
- Click the folder name at the top → **Share**.
- Paste the service account email from step A6.
- Set the role to **Editor** (not Viewer — it needs to create files).
- **Untick "Notify people"** (the robot has no inbox).
- Click **Share**.

That is the whole of Part B. If you skip it, everything else will look correct
and nothing will ever appear in Drive.

---

## PART C — Add the two variables in Railway (~5 min)

Back to the tab in your screenshot: Railway → service → **Variables**.

### C1. `DRIVE_DELIVERABLES_FOLDER`

- **VARIABLE_NAME:** `DRIVE_DELIVERABLES_FOLDER`
- **VALUE:** `1e8-n4Tm2GjzsmJW3O53HuqtNuQIxP3lX`
- Click **Add**.

> That long string is the folder ID — the part of the Drive URL after
> `/folders/`. It is already correct for your ZYNTH-Proposals folder.

### C2. `GOOGLE_SERVICE_ACCOUNT_JSON`

- **VARIABLE_NAME:** `GOOGLE_SERVICE_ACCOUNT_JSON`
- **VALUE:** open the `.json` file you downloaded in A5 in a text editor,
  **select all**, copy, and paste the whole thing into the value box.
- Click **Add**.

**Three things people get wrong here:**

| Mistake | What happens | Fix |
|---|---|---|
| Pasting only part of the file | Bot cannot read the key | Paste from the first `{` to the last `}` |
| Retyping instead of copying | One wrong character breaks it | Always copy-paste |
| Opening the JSON on iPad and it "prettifies" | Usually still fine | If it fails, do this step on a laptop |

The value will be long (about 2,300 characters) and full of random-looking
letters. That is correct — most of it is the private key.

### C3. Redeploy
Railway usually redeploys by itself after a variable change. If it does not:
**Deployments** tab → **⋮** on the newest one → **Redeploy**.

---

## PART D — Check it actually worked (~1 min)

**Do not trust the setup. Check it.**

In Telegram, send:

```
/connections
```

Look for the **Google Drive mirror** line:

| What you see | Meaning |
|---|---|
| 🟢 **Google Drive mirror** — Both secrets set | Working |
| 🟡 Off — Missing: `GOOGLE_SERVICE_ACCOUNT_JSON` | C2 did not save — redo it |
| 🟡 Off — Missing: `DRIVE_DELIVERABLES_FOLDER` | C1 did not save — redo it |

Then send:

```
/deliverables
```

and confirm new items say they saved to Drive as well as GitHub.

**If `/connections` is green but nothing appears in Drive**, the cause is almost
always **Part B** — the folder was never shared with the robot. Go back and check
the folder's Share list contains the `...iam.gserviceaccount.com` address.

---

## What this does NOT do

Being straight with you so you are not surprised:

- **It does not backfill.** The 75 proposals already in the pool stay where they
  are. This applies to everything produced *from now on*. Backfilling them is a
  separate job — ask and I will run it.
- **It does not create the sector folders for you.** The first upload of a new
  sector creates its folder. `01 Fintech and Banking` already exists.
- **It is one-way.** ZYNTH writes to Drive. It does not read your Drive or sync
  changes back. If you edit a document in Drive, ZYNTH will not know.

---

## Safety notes

- The JSON key is a **password**. If it ever leaks: Google Cloud → Service
  Accounts → `zynth-drive` → Keys → delete the old key, create a new one, update
  Railway. Takes two minutes.
- The robot can only touch folders you explicitly shared with it. It cannot see
  the rest of your Drive.
- Never put the JSON in the repo. `backend/.env` is gitignored for this reason.

---

## Quick reference — the two variables

```
DRIVE_DELIVERABLES_FOLDER = 1e8-n4Tm2GjzsmJW3O53HuqtNuQIxP3lX

GOOGLE_SERVICE_ACCOUNT_JSON = {"type":"service_account","project_id":"...",
                               ...the entire downloaded file...}
```

---

*Last updated: 12 August 2026. If a Google screen looks different from this
guide, Google moved it — search the Cloud Console for the bold term and it will
be there.*
