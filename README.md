# Knowledge Hub Desktop APP Based on PyQt5
---
## Tech Stack
- **python3.8+**
- **PyQt5**

## Features
- db initial with dsn( both local or remote)
- user create
- add note that binding to current user
- email client config/send email
- shortcut support

## TODO
- reset password
- temp note
- syntax highlight
- pyInstaller build

## ScreenShot
- config window
<img src="./assets/config_window.png" width = "400" align=center />
<img src="./assets/config_window_initial.png" width = "400" align=center />

- login window
<img src="./assets/login_window.png" width = "400" align=center />
- registry window
<img src="./assets/registry_window.png" width = "400" align=center />
<img src="./assets/registry_succeed_window.png" width = "400" align=center />

- main window
the left list widget will list new 20 note default.
<img src="./assets/main_window.png" width = "400" align=center />

- create new file
use left corner `File->New File` menu or `Ctrl+n` shortcut both can create new file
<img src="./assets/new_file.png" width = "400" align=center />
<img src="./assets/new_file_window.png" width = "400" align=center />

- new file 
default use markdown syntax, use shortcut `Ctrl+t` will toggle show origin content and render content
<img src="./assets/origin_markdown.png" width = "400" align=center />
<img src="./assets/render_markdown.png" width = "400" align=center />

- and so on...


## Refactor
will refactor this project to Qt5(C++)