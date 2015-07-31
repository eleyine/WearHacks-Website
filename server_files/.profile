# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

mesg n
export PYTHONPATH="${PYTHONPATH}:DJANGO_PROJECT_PATH"
cd DJANGO_PROJECT_PATH