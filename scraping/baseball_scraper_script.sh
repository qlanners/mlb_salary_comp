echo "starting setup"


echo "downloading zip, unzip and tmux"
sudo apt-get install unzip

sudo apt-get -f install <<-EOF
yes
EOF

sudo apt-get install unzip

sudo apt-get install zip

sudo apt-get install tmux <<-EOF
yes
EOF


echo "downloading pip and python3"
sudo apt update
sudo apt-get install python3-pip <<-EOF
yes
EOF

echo "downloading google chrome"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb <<-EOF
yes
EOF

sudo dpkg -i google-chrome-stable_current_amd64.deb <<-EOF
yes
EOF

sudo apt-get install -f <<-EOF
yes
EOF

sudo dpkg -i google-chrome-stable_current_amd64.deb <<-EOF
yes
EOF

#Need to have right version of chromedriver
echo "downloading chromedriver"
wget https://chromedriver.storage.googleapis.com/76.0.3809.68/chromedriver_linux64.zip <<-EOF
yes
EOF

unzip chromedriver_linux64.zip


#may need to modify this path to whatever working directory you specify your
#chromedriver is in in the python scraping scripts
sudo mv chromedriver /usr/local/bin

echo "installing necessary python packages"
pip3 install selenium
pip3 install pandas
pip3 install beautifulsoup4
pip3 install lxml

echo "environment setup complete"

echo "unzipping files"
unzip baseball_scraping.zip
cd baseball_scraping

#create tmu session so you can close your terminal while code runs
echo "starting tmux session 'main'"
tmux new-session -d -s main \; send-keys "sh tmux.sh" Enter


