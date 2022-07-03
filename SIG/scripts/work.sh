


python3 sig_parser/work.py --load_path model/sig2joint3/epoch228_batch5996 \
               --test_data data/SIG/ace_sig/test.txt.features.preproc \
               --test_batch_size 6000 \
               --beam_size 8\
               --alpha 0.6\
               --max_time_step 100\
               --output_suffix _test_out

