"""A script to calculate statistics of spine dynamics from annotation sheets.
Authors: Daniel Müller-Komorowska, Joanna Komorowska-Müller & Anne-Kathrine Gellner"""

import pandas as pd
import os
import pdb
import numpy as np

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'data')
save_path = os.path.join(dirname, 'output')

col_names = ['I' + str(x).zfill(2) for x in range(1,16)]
f_list = []
n_spines_df = pd.DataFrame(columns=col_names)

par_list = ['n_stable',
            'n_spines',
            'n_lost',
            'n_gained',
            'perc_stable',
            'spine_density',
            'perc_lost',
            'perc_gained',
            'gain_by_loss',
            'turnover',
            'gain_density',
            'perc_transient',
            'n_new_persistent_by_all_gained',
            'survival_im5_gained',
            'survival_im3_gained',
            'survival_im11_gained',
            'survival_im12_gained',
            'survival_im1_present',
            'survival_superstable',
            'survival_stable',
            'n_protrusions_2_density',
            'n_protrusions_3_density',
            'n_protrusions_2',
            'n_protrusions_3']

result_dict = {par: pd.DataFrame() for par in par_list}
#[pd.DataFrame() for x in range(len(par_list))], keys=par_list)
total_dend_len_dict = {}
total_dend_len_list = []

for root, dirs, files in os.walk(path):
    for f in files:
        if not '.csv' in f:
            continue
        f_list.append(f)
        data = pd.read_csv(root + '\\' +f,
                           header=3,
                           delimiter=';',
                           skip_blank_lines=True,
                           skipfooter=4,
                           usecols=range(1,16),
                           names = col_names,
                           dtype=float,
                           skipinitialspace=True)

        data_bool = data > 10
        data_bool.any(axis=1)
        dends = data[data_bool.any(axis=1)]
        total_dend_len = dends.mean(axis=1, skipna=True).sum()
        total_dend_len_dict[f] = total_dend_len
        total_dend_len_list.append(total_dend_len)

        spines_size = data[~data_bool.any(axis=1)]
        n_protrusions_2_density = (spines_size > 2).sum(axis=0) / total_dend_len
        n_protrusions_3_density = (spines_size > 3).sum(axis=0) / total_dend_len
        n_protrusions_2 = (spines_size > 2).sum(axis=0)
        n_protrusions_3 = (spines_size > 3).sum(axis=0)

        spines_bin = spines_size > 0
        spines_bin_shifted = spines_bin.shift(1,axis='columns')
        spines_added = spines_bin + spines_bin_shifted
        spines_diff = spines_bin - spines_bin_shifted
        spines_stable = spines_added == 2
        spines_lost = (spines_diff == -1)
        spines_gained = (spines_diff == 1)
        im5_gained = spines_bin[spines_gained[spines_gained.columns[4]]]
        #survival_im5_gained = im5_gained[spines_gained.columns[4:]].sum(axis=0) / im5_gained[spines_gained.columns[4]].sum()
        survival_im5_gained = im5_gained[spines_gained.columns[4:]].sum(axis=0)
        im1_present = spines_bin[spines_bin[spines_gained.columns[0]]]
        #survival_im3_present = im3_present[spines_gained.columns[2:]].sum(axis=0) / im3_present[spines_gained.columns[2]].sum()
        survival_im1_present = im1_present[spines_gained.columns[0:]].sum(axis=0)
        superstable = spines_bin[spines_bin[spines_gained.columns[0:3]].sum(axis=1) == 3]
        #survival_superstable = superstable[spines_gained.columns[2:]].sum(axis=0) / superstable[spines_gained.columns[2]].sum()
        survival_superstable = superstable[spines_gained.columns[2:]].sum(axis=0)
        stable = spines_bin[spines_bin[spines_gained.columns[1:3]].sum(axis=1) == 2]
        survival_stable = stable[spines_gained.columns[2:]].sum(axis=0)
        im3_gained = spines_bin[spines_gained[spines_gained.columns[2]]]
        #survival_im3_gained = im3_gained[spines_gained.columns[2:]].sum(axis=0) / im3_gained[spines_gained.columns[2]].sum()
        survival_im3_gained = im3_gained[spines_gained.columns[2:]].sum(axis=0)
        transient_temp = (spines_gained + spines_bin.shift(-1, axis='columns')) == 1
        transient = transient_temp & spines_gained
        n_transient = transient.sum(axis=0)
        im11_gained = spines_bin[spines_gained[spines_gained.columns[10]]]
        survival_im11_gained = im11_gained[spines_gained.columns[10:]].sum(axis=0)

        im12_gained = spines_bin[spines_gained[spines_gained.columns[11]]]
        survival_im12_gained = im12_gained[spines_gained.columns[11:]].sum(axis=0)

        new_persistent = (spines_gained + spines_bin.shift(-1, axis='columns')) == 2
        n_new_persistent = new_persistent.sum(axis=0)

        total_spines = spines_bin.any(axis=1).sum()
        n_stable = spines_stable.sum()
        n_spines = spines_bin.sum(axis=0)
        n_lost = spines_lost.sum(axis=0)
        n_gained = spines_gained.sum(axis=0)
        perc_stable = (n_stable / n_spines.shift(1)) * 100 #corrected to previous time point 20201118
        spine_density = n_spines / total_dend_len
        perc_lost = (n_lost / n_spines.shift(1)) * 100
        perc_gained = (n_gained / n_spines) * 100
        gain_by_loss = (perc_gained / perc_lost)
        turnover = (n_lost + n_gained) / (n_spines + n_spines.shift(1))
        gain_density = n_gained / total_dend_len
        perc_transient = (n_transient / n_spines) * 100
        n_new_persistent_by_all_gained = n_new_persistent / n_gained

        n_spines_df = n_spines_df.append(n_spines, ignore_index=True)

        for k in result_dict.keys():
            result_dict[k] = result_dict[k].append(eval(k), ignore_index=True)
# n_spines_df.rename(index={n_spines_df.shape[0]-1:f}, inplace=True)

index_dict = {}
for idx, x in enumerate(f_list):
    index_dict[idx] = x

xl_writer = pd.ExcelWriter(os.path.join(save_path, 'CTRL_checked_results_stable corr.xlsx'))
for k in result_dict.keys():
    result_dict[k].rename(index=index_dict, inplace=True)
    result_dict[k].to_excel(xl_writer, sheet_name = k)
xl_writer.close()
