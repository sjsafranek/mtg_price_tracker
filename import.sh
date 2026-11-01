source .venv/bin/activate

export DATABASE_URL="postgresql://mtguser:dev@localhost:5432/mtgdb"
python3 importer.py

