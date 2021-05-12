#!/usr/bin/bash

# See: https://docs.aws.amazon.com/dcv/latest/adminguide/setting-up-installing-linux-prereq.html

# NOTE: not share cpu & gpu build, because cpu pulls in mesa-gl, while gpu should stays with NVIDIA [TO_CONFIRM]
# NOTE: at least, until it's confirmed can share the same build.


################################################################################
# Pre-requisites
################################################################################
sudo amazon-linux-extras install -y epel
sudo yum update -y
sudo yum groupinstall -y Xfce
declare -a FONTS=(
    xorg-x11-fonts-Type1 xorg-x11-fonts-100dpi xorg-x11-fonts-75dpi ghostscript-fonts lyx-fonts
    xorg-x11-fonts-ISO8859-9-100dpi xorg-x11-fonts-ISO8859-9-75dpi
    xorg-x11-fonts-ISO8859-2-100dpi xorg-x11-fonts-ISO8859-2-75dpi open-sans-fonts
    google-droid-sans-fonts google-droid-sans-mono-fonts google-droid-serif-fonts
    gnu-free-fonts-common gnu-free-mono-fonts gnu-free-sans-fonts gnu-free-serif-fonts
    adobe-source-code-pro-fonts dejavu-fonts-common dejavu-lgc-sans-mono-fonts dejavu-lgc-serif-fonts
    dejavu-sans-fonts dejavu-sans-mono-fonts dejavu-serif-fonts google-roboto-condensed-fonts
    google-roboto-fonts google-roboto-mono-fonts google-roboto-slab-fonts roboto-fontface-common roboto-fontface-fonts
    liberation-fonts-common liberation-fonts liberation-mono-fonts liberation-narrow-fonts liberation-sans-fonts
    liberation-serif-fonts linux-libertine-biolinum-fonts linux-libertine-fonts linux-libertine-fonts-common
    freefont mathjax-ams-fonts mathjax-caligraphic-fonts mathjax-fraktur-fonts mathjax-main-fonts mathjax-math-fonts
    mathjax-sansserif-fonts mathjax-script-fonts mathjax-size1-fonts mathjax-size2-fonts mathjax-size3-fonts
    mathjax-size4-fonts mathjax-typewriter-fonts mathjax-winchrome-fonts mathjax-winie6-fonts mathjax
    oxygen-fonts oxygen-fonts-common oxygen-mono-fonts oxygen-sans-fonts terminus-fonts terminus-fonts-console
    texlive-ae texlive-amsfonts texlive-amsfonts-doc texlive-arphic texlive-avantgar texlive-bera texlive-beton
    texlive-bookman texlive-boondox texlive-cbfonts texlive-cbfonts-doc texlive-charter texlive-cm texlive-cm-lgc
    texlive-cm-super texlive-cmcyr texlive-collection-fontsrecommended texlive-courier texlive-cyrillic texlive-ec
    texlive-euenc texlive-euler texlive-eulervm texlive-fontaxes texlive-fontaxes-doc texlive-fontbook
    texlive-fontbook-doc texlive-fontspec texlive-fontspec-doc texlive-fontware texlive-fontware-bin.x86_64
    texlive-fontwrap texlive-fontwrap-doc texlive-fpl texlive-garuda-c90 texlive-gsftopk texlive-helvetic texlive-kerkis
    texlive-kpfonts texlive-kpfonts-doc texlive-latex-fonts texlive-latex-fonts-doc texlive-lato texlive-lcyw texlive-lh
    texlive-lm texlive-lm-math texlive-marvosym texlive-mathdesign texlive-mathspec texlive-metafont
    texlive-metafont-bin texlive-metapost texlive-mflogo texlive-mfnfss texlive-mfware texlive-mnsymbol texlive-ncntrsbk
    texlive-newtx texlive-norasi-c90 texlive-palatino texlive-philokalia texlive-pslatex texlive-psnfss texlive-pxfonts
    texlive-pxfonts-doc texlive-rsfs texlive-sansmath texlive-slantsc texlive-symbol texlive-tex-gyre
    texlive-tex-gyre-math texlive-times texlive-txfonts texlive-txfonts-doc texlive-type1cm texlive-ucharclasses
    texlive-utopia texlive-wadalab texlive-wasy texlive-wasysym texlive-xetexfontinfo texlive-xetexfontinfo-doc
    texlive-zapfchan texlive-zapfding
)
sudo yum install -y dkms xorg-x11-server-Xorg xorg-x11-drivers glx-utils "${FONTS[@]}"


################################################################################
# DCV
################################################################################
DCV_SRC=https://d1uj6qtbmh3dt5.cloudfront.net/2020.2/Servers/nice-dcv-2020.2-9662-el7-x86_64.tgz
DCV_TGZ=$(basename $DCV_SRC)
DCV_DIR=${DCV_TGZ%*.tgz}
sudo rpm --yes --import https://d1uj6qtbmh3dt5.cloudfront.net/NICE-GPG-KEY
curl -O $DCV_SRC
tar -xzf $DCV_TGZ
cd $DCV_DIR
sudo yum install -y nice-dcv-server-*.el7.x86_64.rpm nice-xdcv-*.el7.x86_64.rpm nice-dcv-gl-*.el7.x86_64.rpm nice-dcv-gltest-*.el7.x86_64.rpm
sudo dcvusbdriverinstaller --quiet
cd ..
# Clean installation source
rm -fr $DCV_DIR
rm $DCV_TGZ

# Disable authentication, because we intend to front this single-tenant instance with an ssh tunnel.
sudo sed -i 's/^#authentication.*/authentication="none"/' /etc/dcv/dcv.conf

# Auto-start dcv server on boot
sudo systemctl enable dcvserver

# gdm is not needed for virtual sessions
sudo systemctl disable gdm
# Hotfix for DCV-2068 "dcv-2019.1 and virtual session xfce4 needs gdm to start once"
# NOTE: workaround for  gawk < 4.1.0 which cannot do inplace modif.
awk '!/\[display\]/ {print $0} /\[display\]/ {print $0; print "display-encoders=[\"nvenc\", \"ffmpeg\", \"turbojpeg\", \"lz4\"]"}' /etc/dcv/dcv.conf > /tmp/dcv.conf
sudo cp /tmp/dcv.conf /etc/dcv/dcv.conf
echo 'Ensure hotfix for DCV-2068:'
grep display /etc/dcv/dcv.conf


sudo yum clean all


################################################################################
# Helpful usage message
################################################################################
echo
echo Installation done. Next steps:
echo "1) Ensure this instance's role permits S3 public endpoint, as dcv needs to check for a specific"
echo '   bucket for licensing.'
echo '   - It is still free to use on EC2, just that it needs to ping S3.'
echo '   - See https://docs.aws.amazon.com/dcv/latest/adminguide/setting-up-license.html'
echo '2) Reboot'
echo '3) Start virtual sessions: dcv create-session --type virtual --init /usr/bin/startxfce4 my-session'
echo '   Access by web-browser: https://host:8443/#my-session'
echo ''
echo 'NOTE: You must secure this host behind ah ssh tunnel. This instance is meant for single-tenancey,'
echo '      and thus, disable the authentication and defer it to external mechanisms such as ssh.'
echo ''
echo '      Alternatively, enable authentication in /etc/dcv/dcv.conf'
