" Setting the leader
let mapleader="\<Space>"

" Easier writing/quitting
nnoremap <Leader>w :w<CR>
nnoremap <Leader>x :x<CR>
nnoremap <Leader>q :q<CR>
nnoremap <Leader>e :e<CR>

" Use better code folding
let g:SimpylFold_docstring_preview = 1

" Nerdtree open/close toggle
map <C-n> :NERDTreeToggle<CR>

" Vim pane switching
map <C-j> <C-W>j
map <C-k> <C-W>k
map <C-h> <C-W>h
map <C-l> <C-W>l

" Hybrid line numbers
:set number relativenumber

filetype plugin indent on

:augroup numbertoggle
:  autocmd!
:  autocmd BufEnter,FocusGained,InsertLeave * set relativenumber
:  autocmd BufLeave,FocusLost,InsertEnter   * set norelativenumber
:augroup END

" Searching within a file
set hlsearch  " highlight search results
set incsearch " show search results as you type
nnoremap <silent> <CR> :nohlsearch<Bar>:echo<CR> " Clear search results with enter

" Color
let g:gruvbox_contrast_dark = 'hard'
if exists('+termguicolors')
    let &t_8f = "\<Esc>[38;2;%lu;%lu;%lum"
    let &t_8b = "\<Esc>[48;2;%lu;%lu;%lum"
endif
let g:gruvbox_invert_selection='0'
syntax enable
colorscheme gruvbox
set background=dark

" Tab spacing
set tabstop=4
set softtabstop=4
set shiftwidth=4
set smarttab
set expandtab

" Additional vim options
set encoding=utf-8                       " Set encoding
set ruler                                " Show line, column number
set viminfo='20,<1000                    " Increase the copy/paste-buffer
set noerrorbells visualbell t_vb=        " Get rid of bell sound on error
set nowrap                               " Turn off text wrapping
set colorcolumn=100                       " Column number for vertical line
set cursorline                           " Highlight the line of the cursor
set t_Co=256                             " Required for vim colorscheme show up in tmux
