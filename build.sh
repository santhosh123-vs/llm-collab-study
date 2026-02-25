#!/usr/bin/env bash
set -e

pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..

python -m src.generate_sample_data
