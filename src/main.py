from curses import wrapper, error
from editor import Editor
from file import File
from sys import argv, exit


if __name__ == "__main__":
  if len(argv) != 2:
    print("Usage: clx [flags] <file>")
    exit(1)

  file = File(argv[1])
  editor = Editor(file)

  try: wrapper(editor.main, argv[1])
  except KeyboardInterrupt: print("Keyboard interrupt.")
  except error as e:
    match e.args[0]:
      case "no input": print("No input.")
      case "curses function returned NULL": print("Something returned NULL! Terminal may be too small!")
      case _: print("Curses error: %s" %e)

  except Exception as e: print(e)
