#!/bin/bash

# IMPORTANT: this script assumes .vimrc uses junegunn/vim-plug.
#
# If you use another .vimrc with a different plugin manager, please update this
# script accordingly to match the new plugin manager.
VIMRC_SRC=${1:-https://raw.githubusercontent.com/verdimrc/linuxcfg/master/.vimrc}

VIM_SM_ROOT=/home/ec2-user/SageMaker
VIM_RTP=${VIM_SM_ROOT}/.vim
VIMRC=${VIM_SM_ROOT}/.vimrc

apply_vim_setting() {
    # vimrc
    rm /home/ec2-user/.vimrc
    ln -s ${VIMRC} /home/ec2-user/.vimrc

    echo "Vim initialized"
}

if [[ ! -f ${VIM_RTP}/_SUCCESS ]]; then
    echo "Initializing vim from ${VIMRC_SRC}"

    # vimrc
    cat << EOF > ${VIMRC}
set rtp+=${VIM_RTP}

" Hybrid line numbers (https://github.com/josiahdavis/dotfiles/blob/master/.vimrc)
"
" Prefer built-in over RltvNmbr as the later makes vim even slower on
" high-latency aka. cross-region instance.
:set number relativenumber
:augroup numbertoggle
:  autocmd!
:  autocmd BufEnter,FocusGained,InsertLeave * set relativenumber
:  autocmd BufLeave,FocusLost,InsertEnter   * set norelativenumber
:augroup END

" Relative number only on focused-windoes (see: jeffkreeftmeijer/vim-numbertoggle)
autocmd BufEnter,FocusGained,InsertLeave,WinEnter * if &number | set relativenumber   | endif
autocmd BufLeave,FocusLost,InsertEnter,WinLeave   * if &number | set norelativenumber | endif

" Remap keys to navigate window aka split screens to ctrl-{h,j,k,l}
" See: https://vi.stackexchange.com/a/3815
"
" Vim defaults to ctrl-w-{h,j,k,l}. But, laaa la la la la, ctrl-w on Linux
" (and Windows?) closes browser tab.
"
" NOTE: ctrl-l was "clear and redraw screen". The later can still be invoked
"       with :redr[aw][!]
nmap <C-h> <C-w>h
nmap <C-j> <C-w>j
nmap <C-k> <C-w>k
nmap <C-l> <C-w>l

EOF
    curl -sfL $VIMRC_SRC >> ${VIMRC}
    declare -a SED_SCRIPTS=(
        # Store plugins under ~/SageMaker for reuse on instance restart
        -e "s|^call plug#begin.*$|call plug#begin('$VIM_RTP/plugged')|g"

        # Disabled. Make vim even slower on high-latency aka. cross-region.
        -e "s|^Plug 'vim-scripts/RltvNmbr.vim'|\"Plug 'vim-scripts/RltvNmbr.vim'|g"
    )
    sed -i "${SED_SCRIPTS[@]}" ${VIMRC}

    # plugins
    curl -sfLo ${VIM_RTP}/autoload/plug.vim --create-dirs \
        https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    unset DISPLAY
    vim -u ${VIMRC} -E +PlugUpdate +qall > /dev/null

    touch ${VIM_RTP}/_SUCCESS
fi

apply_vim_setting

