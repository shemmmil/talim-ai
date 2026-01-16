# Настройка Python по умолчанию

## Вариант 1: Использование pyenv (рекомендуется, если у вас pyenv)

Если у вас установлен pyenv, установите Python 3.11 глобально:

```bash
# Установить Python 3.11 (если еще не установлен)
pyenv install 3.11.3

# Установить как глобальную версию
pyenv global 3.11.3

# Перезагрузить shell
exec $SHELL

# Проверить
python --version  # Должно показать Python 3.11.3
```

## Вариант 2: Alias в .zshrc (простой способ)

Добавьте в файл `~/.zshrc`:

```bash
# Добавить в конец файла ~/.zshrc
alias python=python3
alias pip=pip3
```

Затем перезагрузите shell:
```bash
source ~/.zshrc
```

## Вариант 3: Обновление PATH

Добавьте в `~/.zshrc` (если Python 3 установлен через Homebrew):

```bash
# Добавить в конец файла ~/.zshrc
export PATH="/usr/local/bin:$PATH"
# или если Python установлен в другом месте:
# export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"
```

## Проверка

После настройки проверьте:
```bash
python --version   # Должно быть Python 3.11.x
pip --version      # Должно использовать Python 3
which python       # Покажет путь к Python 3
```
