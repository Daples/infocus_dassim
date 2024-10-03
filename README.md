# infocus_dassim

This repository contains different templates to run data assimilation experiments for
induced seismicity using GARNET + PDAF (links!).

## Troubleshooting

    1. Missing checkpoints in `create_obsnet.py` error: either because there was an
    error running the truth model in Garnet, or the timing was not set correctly in
    `da_exp_setup.yaml` file.

    Check `garnet/path_to_truth/*.err` for possible errors when running Garnet.

    2. (For 2D model) to be solved!
    ``` tau_xy_checkfile=data['chi']['odes']['sigma']['base']['y']['data'][0]['elements']['0']['base']['01']['data']
            ~~~~~~~~~~~~~~~~~~~^^^^^^^^^
        KeyError: 'sigma'
    ```

