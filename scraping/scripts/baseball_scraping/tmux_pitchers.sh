END=2019
pickle_file="None"
for i in $(seq 2000 $END)
do
	echo "Pitcher BBR Scraping for $i"
	output_file="pitchers_bbr_output_${i}.txt"
	python3 bbr_scraper.py pitchers $i $pickle_file > $output_file
	pickle_file="pitchers_bbr_${i}_players_done.pickle"
	sleep 5m
done


echo "removing TOTs"
python3 remove_TOTs.py pitchers > pitchers_remove_TOTs_output.txt

sudo mkdir pitchers_output

sudo mv pitchers_bbr_* pitchers_output


sudo mv salary_output.txt pitchers_output
sudo mv players.csv pitchers_output
sudo mv pitchers.csv pitchers_output
sudo mv pitchers.csv pitchers_output
sudo mv salaries.csv pitchers_output

sudo mv pitchers_remove_TOTs_output.txt pitchers_output
sudo mv pitchers_TOTs_removed.csv pitchers_output

cd pitchers_output
sudo mkdir pitchers_bbr

sudo mv pitchers_bbr_* pitchers_bbr

cd ..

zip -r pitchers_output.zip pitchers_output
sudo mv pitchers_output.zip ../


#this code is only necessary if being run on google cloud service as to not run
#up the charge once the code is done. Otherwise can remove.
sudo shutdown