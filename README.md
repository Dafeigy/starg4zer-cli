## Dev setup

```bash
python -m venv .venv

source .venv/Script/activate

pip install -r requirements.txt

```

Next, add `.env.local` and write follows:

```bash
GITHUB_TOKEN="Bearer xxxxxxxxxxxxxxx"
```

then use `source .env.local` to export environmental variables.



