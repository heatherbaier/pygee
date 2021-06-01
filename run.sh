ISO="MEX"
ADM="2"
IC="LANDSAT/LT05/C01/T1_TOA"

python3 downloadGB.py $ISO $ADM
python3 save_boxes.py $ISO
python3 download_imagery.py $IC --year_list "2010" --month_list "1" "2" "3" "4" "5" "6" "7" "8" "9" "10" "11" "12"


python3 downloadGB.py "MEX" "2"


conda create --prefix ./caoe_env

python3 download_imagery.py "LANDSAT/LT05/C01/T1" "MEX4" --year_list "2010" --month_list "1" "2" "3" "4" "5" "6" "7" "8" "9" "10" "11" "12"



python3 download_imagery.py "LANDSAT/LT05/C01/T1" "MEX4" --year_list "2010" --month_list "5" 
