echo "running salary scraper"
python3 salary_scraper.py > salary_output.txt

echo "running bbr scraper"
python3 bbr_scraper.py > bbr_output.txt

# echo "running missing bbr scraper"
# python3 bbr_missing_players_scraper.py > bbr_missing_players_output.txt

echo "removing TOTs"
python3 remove_TOTs.py > remove_TOTs_output.txt

sudo mkdir output

sudo mv salary_output.txt output
sudo mv bbr_output.txt output
# sudo mv bbr_missing_players_output.txt output
sudo mv remove_TOTs_output.txt output
sudo mv players.csv output
sudo mv batters.csv output
sudo mv pitchers.csv output
sudo mv salaries.csv output
sudo mv batters_bbr.csv output
sudo mv pitchers_bbr.csv output
# sudo mv batters_bbr_full.csv output
# sudo mv pitchers_bbr_full.csv output
sudo mv batters_bbr_TOTs_removed.csv output
sudo mv pitchers_bbr_TOTs_removed.csv output

zip -r output.zip output
mv output.zip ../


#this code is only necessary if being run on google cloud service as to not run
#up the charge once the code is done. Otherwise can remove.
sudo shutdown