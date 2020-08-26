# Change prefix key (also useful to map control to caps-lock)
set -g prefix C-a

# update window splitting to something more intuitive
bind / split-window -h -c '#{pane_current_path}'
bind - split-window -v -c '#{pane_current_path}'

# After updates simply prefix-r to update tmux config
bind r source-file ${HOME}/.tmux.conf \; display 'Reloaded!'

# Set scroll-back buffer options
set-option -g history-limit 10000
setw -g mode-keys vi
unbind-key [
bind-key Escape copy-mode

# Increase time for pressing correct key after prefix
set -s escape-time 1

# make tmux respect vim formatting option (experimental)
set -g default-terminal "screen-256color"
set -g terminal-overrides 'xterm:colors=256'

# moving between panes with vim movement keys
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R
