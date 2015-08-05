# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

mesg n
git config --global core.filemode false
export PYTHONPATH="${PYTHONPATH}:DJANGO_PROJECT_PATH"
cd DJANGO_PROJECT_PATH