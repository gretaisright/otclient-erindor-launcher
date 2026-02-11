echo.
echo ===============================
echo 2. Building binaries utility...
echo ===============================
python launcher\binaries_build.py

echo.
echo ===============================
echo 3. Generating binaries.json...
echo ===============================
:: Since the files are in launcher/, we point the directory there
python launcher\binaries.py --dir "launcher"

echo.
echo ===============================
echo Done! Check launcher/binaries.json
echo ===============================
pause