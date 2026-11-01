#python3 -m venv .venv
source .venv/bin/activate

export DATABASE_URL="postgresql://mtguser:dev@localhost:5432/mtgdb"
python importer.py

