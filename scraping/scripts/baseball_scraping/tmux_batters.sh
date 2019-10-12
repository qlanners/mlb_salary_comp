echo "running salary scraper"
python3 salary_scraper.py > salary_output.txt

END=2019
pickle_file="None"
for i in $(seq 2000 $END)
do
	echo "Batter BBR Scraping for $i"
	output_file="batters_bbr_output_${i}.txt"
	python3 bbr_scraper.py batters $i $pickle_file > $output_file
	pickle_file="batters_bbr_${i}_players_done.pickle"
	sleep 5m
done


echo "removing TOTs"
python3 remove_TOTs.py batters > batters_remove_TOTs_output.txt

sudo mkdir batters_output

sudo mv batters_bbr_* batters_output


sudo mv salary_output.txt batters_output
sudo mv players.csv batters_output
sudo mv batters.csv batters_output
sudo mv pitchers.csv batters_output
sudo mv salaries.csv batters_output

sudo mv batters_remove_TOTs_output.txt batters_output
sudo mv batters_TOTs_removed.csv batters_output

cd batters_output
sudo mkdir batters_bbr

sudo mv batters_bbr_* batters_bbr

cd ..

zip -r batters_output.zip batters_output
sudo mv batters_output.zip ../

tmux new-session -d -s pitchers \; send-keys "sh tmux_pitchers.sh" Enter