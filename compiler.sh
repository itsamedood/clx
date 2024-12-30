compile_clx() {
  echo "Compiling clx..."
  pyinstaller --onefile --distpath bin --name clx src/main.py
  echo "Done!"
}

compile_clx
