import os, os.path
import lasio
import pandas


def analyzer(DIR):
    first_file = True
    my_dict = {}
    bad_files = []
    for name in os.listdir(DIR):
        print(name)
        if os.path.isfile(os.path.join(DIR, name)):
            try:
                las = lasio.read(DIR + name)
            except ValueError:
                bad_files.append(name)
                continue
            if first_file:
                my_dict = dict.fromkeys(las.keys(), 0)
                first_file = False
            count_NaN = las.df().isnull().sum()
            percent_good_value = {}
            for item in las.df().keys():
                if item in my_dict:
                    my_dict[item] += 1
                else:
                    my_dict[item] = 1
                percent_good_value[item] = round(count_NaN[item] / las[item].size, 2)
    print(sorted(my_dict.items(), key=lambda x: x[1], reverse=True))
