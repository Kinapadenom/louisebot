# Louisebot

Manage who eat and when :)

## Requirements

Python3, Mysql

## Installation

1. Create virtualenv & clone

```
git clone https://github.com/Kinapadenom/louisebot.git
virtualenv -p python3 ~/venv/louisebot
source ~/venv/louisebot/bin/activate
cd louisebot
pip install -r requirements.txt
```

2. Edit rtmbot.conf

```
cp rtmbot.conf.example rtmbot.conf
vim rtmbot.conf
```

3. Edit plugins to enable our plugin

```
vim hubcommander/command_plugins/enabled_plugins.py
```

Here is a quicklook of `cat hubcommander/command_plugins/enabled_plugins.py`:

```python
from hubcommander.command_plugins.repeat.plugin import RepeatPlugin
from plugins.cocotte import CocottePlugin

COMMAND_PLUGINS = {
    "repeat": RepeatPlugin(),
    "cocotte": CocottePlugin(),
}
```

4. Create ~/.louisebot.conf

```
cp louisebot.conf.example louisebot.conf
vim louisebot.conf
```
