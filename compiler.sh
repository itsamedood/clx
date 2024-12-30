#!/bin/bash

compile_clx() {
  echo "Compiling clx..."
  pyinstaller --onefile --distpath bin --name clx src/main.py
  rm -r build
  rm clx.spec

  echo "Done!"
}

compile_clx
