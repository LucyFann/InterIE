# -*- coding:utf-8 -*-
# Author: hankcs
# Date: 2020-05-21 20:26

_UD_23_HOME = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz?sequence=1&isAllowed=y"
_UD_24_HOME = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz?sequence=4&isAllowed=y"


def _list_dir(path, home):
    prefix = home.lstrip('_').replace('_HOME', '')

    from elit.utils.io_util import get_resource
    import glob
    import os
    path = get_resource(path)
    with open('ud23.py', 'a') as out:
        for f in sorted(glob.glob(path + '/UD_*')):
            basename = os.path.basename(f)
            name = basename[len('UD_'):]
            name = name.upper().replace('-', '_')
            for split in 'train', 'dev', 'test':
                sp = glob.glob(f + f'/*{split}.conllu')
                if not sp:
                    continue
                sp = os.path.basename(sp[0])
                out.write(f'{prefix}_{name}_{split.upper()} = {home} + "#{basename}/{sp}"\n')


def main():
    _list_dir(_UD_23_HOME, '_UD_23_HOME')
    pass


if __name__ == '__main__':
    main()

UD_23_AFRIKAANS_AFRIBOOMS_TRAIN = _UD_23_HOME + "#UD_Afrikaans-AfriBooms/af_afribooms-ud-train.conllu"
UD_23_AFRIKAANS_AFRIBOOMS_DEV = _UD_23_HOME + "#UD_Afrikaans-AfriBooms/af_afribooms-ud-dev.conllu"
UD_23_AFRIKAANS_AFRIBOOMS_TEST = _UD_23_HOME + "#UD_Afrikaans-AfriBooms/af_afribooms-ud-test.conllu"
UD_23_AKKADIAN_PISANDUB_TEST = _UD_23_HOME + "#UD_Akkadian-PISANDUB/akk_pisandub-ud-test.conllu"
UD_23_AMHARIC_ATT_TEST = _UD_23_HOME + "#UD_Amharic-ATT/am_att-ud-test.conllu"
UD_23_ANCIENT_GREEK_PROIEL_TRAIN = _UD_23_HOME + "#UD_Ancient_Greek-PROIEL/grc_proiel-ud-train.conllu"
UD_23_ANCIENT_GREEK_PROIEL_DEV = _UD_23_HOME + "#UD_Ancient_Greek-PROIEL/grc_proiel-ud-dev.conllu"
UD_23_ANCIENT_GREEK_PROIEL_TEST = _UD_23_HOME + "#UD_Ancient_Greek-PROIEL/grc_proiel-ud-test.conllu"
UD_23_ANCIENT_GREEK_PERSEUS_TRAIN = _UD_23_HOME + "#UD_Ancient_Greek-Perseus/grc_perseus-ud-train.conllu"
UD_23_ANCIENT_GREEK_PERSEUS_DEV = _UD_23_HOME + "#UD_Ancient_Greek-Perseus/grc_perseus-ud-dev.conllu"
UD_23_ANCIENT_GREEK_PERSEUS_TEST = _UD_23_HOME + "#UD_Ancient_Greek-Perseus/grc_perseus-ud-test.conllu"
UD_23_ARABIC_NYUAD_TRAIN = _UD_23_HOME + "#UD_Arabic-NYUAD/ar_nyuad-ud-train.conllu"
UD_23_ARABIC_NYUAD_DEV = _UD_23_HOME + "#UD_Arabic-NYUAD/ar_nyuad-ud-dev.conllu"
UD_23_ARABIC_NYUAD_TEST = _UD_23_HOME + "#UD_Arabic-NYUAD/ar_nyuad-ud-test.conllu"
UD_23_ARABIC_PADT_TRAIN = _UD_23_HOME + "#UD_Arabic-PADT/ar_padt-ud-train.conllu"
UD_23_ARABIC_PADT_DEV = _UD_23_HOME + "#UD_Arabic-PADT/ar_padt-ud-dev.conllu"
UD_23_ARABIC_PADT_TEST = _UD_23_HOME + "#UD_Arabic-PADT/ar_padt-ud-test.conllu"
UD_23_ARABIC_PUD_TEST = _UD_23_HOME + "#UD_Arabic-PUD/ar_pud-ud-test.conllu"
UD_23_ARMENIAN_ARMTDP_TRAIN = _UD_23_HOME + "#UD_Armenian-ArmTDP/hy_armtdp-ud-train.conllu"
UD_23_ARMENIAN_ARMTDP_TEST = _UD_23_HOME + "#UD_Armenian-ArmTDP/hy_armtdp-ud-test.conllu"
UD_23_BAMBARA_CRB_TEST = _UD_23_HOME + "#UD_Bambara-CRB/bm_crb-ud-test.conllu"
UD_23_BASQUE_BDT_TRAIN = _UD_23_HOME + "#UD_Basque-BDT/eu_bdt-ud-train.conllu"
UD_23_BASQUE_BDT_DEV = _UD_23_HOME + "#UD_Basque-BDT/eu_bdt-ud-dev.conllu"
UD_23_BASQUE_BDT_TEST = _UD_23_HOME + "#UD_Basque-BDT/eu_bdt-ud-test.conllu"
UD_23_BELARUSIAN_HSE_TRAIN = _UD_23_HOME + "#UD_Belarusian-HSE/be_hse-ud-train.conllu"
UD_23_BELARUSIAN_HSE_DEV = _UD_23_HOME + "#UD_Belarusian-HSE/be_hse-ud-dev.conllu"
UD_23_BELARUSIAN_HSE_TEST = _UD_23_HOME + "#UD_Belarusian-HSE/be_hse-ud-test.conllu"
UD_23_BRETON_KEB_TEST = _UD_23_HOME + "#UD_Breton-KEB/br_keb-ud-test.conllu"
UD_23_BULGARIAN_BTB_TRAIN = _UD_23_HOME + "#UD_Bulgarian-BTB/bg_btb-ud-train.conllu"
UD_23_BULGARIAN_BTB_DEV = _UD_23_HOME + "#UD_Bulgarian-BTB/bg_btb-ud-dev.conllu"
UD_23_BULGARIAN_BTB_TEST = _UD_23_HOME + "#UD_Bulgarian-BTB/bg_btb-ud-test.conllu"
UD_23_BURYAT_BDT_TRAIN = _UD_23_HOME + "#UD_Buryat-BDT/bxr_bdt-ud-train.conllu"
UD_23_BURYAT_BDT_TEST = _UD_23_HOME + "#UD_Buryat-BDT/bxr_bdt-ud-test.conllu"
UD_23_CANTONESE_HK_TEST = _UD_23_HOME + "#UD_Cantonese-HK/yue_hk-ud-test.conllu"
UD_23_CATALAN_ANCORA_TRAIN = _UD_23_HOME + "#UD_Catalan-AnCora/ca_ancora-ud-train.conllu"
UD_23_CATALAN_ANCORA_DEV = _UD_23_HOME + "#UD_Catalan-AnCora/ca_ancora-ud-dev.conllu"
UD_23_CATALAN_ANCORA_TEST = _UD_23_HOME + "#UD_Catalan-AnCora/ca_ancora-ud-test.conllu"
UD_23_CHINESE_CFL_TEST = _UD_23_HOME + "#UD_Chinese-CFL/zh_cfl-ud-test.conllu"
UD_23_CHINESE_GSD_TRAIN = _UD_23_HOME + "#UD_Chinese-GSD/zh_gsd-ud-train.conllu"
UD_23_CHINESE_GSD_DEV = _UD_23_HOME + "#UD_Chinese-GSD/zh_gsd-ud-dev.conllu"
UD_23_CHINESE_GSD_TEST = _UD_23_HOME + "#UD_Chinese-GSD/zh_gsd-ud-test.conllu"
UD_23_CHINESE_HK_TEST = _UD_23_HOME + "#UD_Chinese-HK/zh_hk-ud-test.conllu"
UD_23_CHINESE_PUD_TEST = _UD_23_HOME + "#UD_Chinese-PUD/zh_pud-ud-test.conllu"
UD_23_COPTIC_SCRIPTORIUM_TRAIN = _UD_23_HOME + "#UD_Coptic-Scriptorium/cop_scriptorium-ud-train.conllu"
UD_23_COPTIC_SCRIPTORIUM_DEV = _UD_23_HOME + "#UD_Coptic-Scriptorium/cop_scriptorium-ud-dev.conllu"
UD_23_COPTIC_SCRIPTORIUM_TEST = _UD_23_HOME + "#UD_Coptic-Scriptorium/cop_scriptorium-ud-test.conllu"
UD_23_CROATIAN_SET_TRAIN = _UD_23_HOME + "#UD_Croatian-SET/hr_set-ud-train.conllu"
UD_23_CROATIAN_SET_DEV = _UD_23_HOME + "#UD_Croatian-SET/hr_set-ud-dev.conllu"
UD_23_CROATIAN_SET_TEST = _UD_23_HOME + "#UD_Croatian-SET/hr_set-ud-test.conllu"
UD_23_CZECH_CAC_TRAIN = _UD_23_HOME + "#UD_Czech-CAC/cs_cac-ud-train.conllu"
UD_23_CZECH_CAC_DEV = _UD_23_HOME + "#UD_Czech-CAC/cs_cac-ud-dev.conllu"
UD_23_CZECH_CAC_TEST = _UD_23_HOME + "#UD_Czech-CAC/cs_cac-ud-test.conllu"
UD_23_CZECH_CLTT_TRAIN = _UD_23_HOME + "#UD_Czech-CLTT/cs_cltt-ud-train.conllu"
UD_23_CZECH_CLTT_DEV = _UD_23_HOME + "#UD_Czech-CLTT/cs_cltt-ud-dev.conllu"
UD_23_CZECH_CLTT_TEST = _UD_23_HOME + "#UD_Czech-CLTT/cs_cltt-ud-test.conllu"
UD_23_CZECH_FICTREE_TRAIN = _UD_23_HOME + "#UD_Czech-FicTree/cs_fictree-ud-train.conllu"
UD_23_CZECH_FICTREE_DEV = _UD_23_HOME + "#UD_Czech-FicTree/cs_fictree-ud-dev.conllu"
UD_23_CZECH_FICTREE_TEST = _UD_23_HOME + "#UD_Czech-FicTree/cs_fictree-ud-test.conllu"
UD_23_CZECH_PDT_TRAIN = _UD_23_HOME + "#UD_Czech-PDT/cs_pdt-ud-train.conllu"
UD_23_CZECH_PDT_DEV = _UD_23_HOME + "#UD_Czech-PDT/cs_pdt-ud-dev.conllu"
UD_23_CZECH_PDT_TEST = _UD_23_HOME + "#UD_Czech-PDT/cs_pdt-ud-test.conllu"
UD_23_CZECH_PUD_TEST = _UD_23_HOME + "#UD_Czech-PUD/cs_pud-ud-test.conllu"
UD_23_DANISH_DDT_TRAIN = _UD_23_HOME + "#UD_Danish-DDT/da_ddt-ud-train.conllu"
UD_23_DANISH_DDT_DEV = _UD_23_HOME + "#UD_Danish-DDT/da_ddt-ud-dev.conllu"
UD_23_DANISH_DDT_TEST = _UD_23_HOME + "#UD_Danish-DDT/da_ddt-ud-test.conllu"
UD_23_DUTCH_ALPINO_TRAIN = _UD_23_HOME + "#UD_Dutch-Alpino/nl_alpino-ud-train.conllu"
UD_23_DUTCH_ALPINO_DEV = _UD_23_HOME + "#UD_Dutch-Alpino/nl_alpino-ud-dev.conllu"
UD_23_DUTCH_ALPINO_TEST = _UD_23_HOME + "#UD_Dutch-Alpino/nl_alpino-ud-test.conllu"
UD_23_DUTCH_LASSYSMALL_TRAIN = _UD_23_HOME + "#UD_Dutch-LassySmall/nl_lassysmall-ud-train.conllu"
UD_23_DUTCH_LASSYSMALL_DEV = _UD_23_HOME + "#UD_Dutch-LassySmall/nl_lassysmall-ud-dev.conllu"
UD_23_DUTCH_LASSYSMALL_TEST = _UD_23_HOME + "#UD_Dutch-LassySmall/nl_lassysmall-ud-test.conllu"
UD_23_ENGLISH_ESL_TRAIN = _UD_23_HOME + "#UD_English-ESL/en_esl-ud-train.conllu"
UD_23_ENGLISH_ESL_DEV = _UD_23_HOME + "#UD_English-ESL/en_esl-ud-dev.conllu"
UD_23_ENGLISH_ESL_TEST = _UD_23_HOME + "#UD_English-ESL/en_esl-ud-test.conllu"
UD_23_ENGLISH_EWT_TRAIN = _UD_23_HOME + "#UD_English-EWT/en_ewt-ud-train.conllu"
UD_23_ENGLISH_EWT_DEV = _UD_23_HOME + "#UD_English-EWT/en_ewt-ud-dev.conllu"
UD_23_ENGLISH_EWT_TEST = _UD_23_HOME + "#UD_English-EWT/en_ewt-ud-test.conllu"
UD_23_ENGLISH_GUM_TRAIN = _UD_23_HOME + "#UD_English-GUM/en_gum-ud-train.conllu"
UD_23_ENGLISH_GUM_DEV = _UD_23_HOME + "#UD_English-GUM/en_gum-ud-dev.conllu"
UD_23_ENGLISH_GUM_TEST = _UD_23_HOME + "#UD_English-GUM/en_gum-ud-test.conllu"
UD_23_ENGLISH_LINES_TRAIN = _UD_23_HOME + "#UD_English-LinES/en_lines-ud-train.conllu"
UD_23_ENGLISH_LINES_DEV = _UD_23_HOME + "#UD_English-LinES/en_lines-ud-dev.conllu"
UD_23_ENGLISH_LINES_TEST = _UD_23_HOME + "#UD_English-LinES/en_lines-ud-test.conllu"
UD_23_ENGLISH_PUD_TEST = _UD_23_HOME + "#UD_English-PUD/en_pud-ud-test.conllu"
UD_23_ENGLISH_PARTUT_TRAIN = _UD_23_HOME + "#UD_English-ParTUT/en_partut-ud-train.conllu"
UD_23_ENGLISH_PARTUT_DEV = _UD_23_HOME + "#UD_English-ParTUT/en_partut-ud-dev.conllu"
UD_23_ENGLISH_PARTUT_TEST = _UD_23_HOME + "#UD_English-ParTUT/en_partut-ud-test.conllu"
UD_23_ERZYA_JR_TEST = _UD_23_HOME + "#UD_Erzya-JR/myv_jr-ud-test.conllu"
UD_23_ESTONIAN_EDT_TRAIN = _UD_23_HOME + "#UD_Estonian-EDT/et_edt-ud-train.conllu"
UD_23_ESTONIAN_EDT_DEV = _UD_23_HOME + "#UD_Estonian-EDT/et_edt-ud-dev.conllu"
UD_23_ESTONIAN_EDT_TEST = _UD_23_HOME + "#UD_Estonian-EDT/et_edt-ud-test.conllu"
UD_23_FAROESE_OFT_TEST = _UD_23_HOME + "#UD_Faroese-OFT/fo_oft-ud-test.conllu"
UD_23_FINNISH_FTB_TRAIN = _UD_23_HOME + "#UD_Finnish-FTB/fi_ftb-ud-train.conllu"
UD_23_FINNISH_FTB_DEV = _UD_23_HOME + "#UD_Finnish-FTB/fi_ftb-ud-dev.conllu"
UD_23_FINNISH_FTB_TEST = _UD_23_HOME + "#UD_Finnish-FTB/fi_ftb-ud-test.conllu"
UD_23_FINNISH_PUD_TEST = _UD_23_HOME + "#UD_Finnish-PUD/fi_pud-ud-test.conllu"
UD_23_FINNISH_TDT_TRAIN = _UD_23_HOME + "#UD_Finnish-TDT/fi_tdt-ud-train.conllu"
UD_23_FINNISH_TDT_DEV = _UD_23_HOME + "#UD_Finnish-TDT/fi_tdt-ud-dev.conllu"
UD_23_FINNISH_TDT_TEST = _UD_23_HOME + "#UD_Finnish-TDT/fi_tdt-ud-test.conllu"
UD_23_FRENCH_FTB_TRAIN = _UD_23_HOME + "#UD_French-FTB/fr_ftb-ud-train.conllu"
UD_23_FRENCH_FTB_DEV = _UD_23_HOME + "#UD_French-FTB/fr_ftb-ud-dev.conllu"
UD_23_FRENCH_FTB_TEST = _UD_23_HOME + "#UD_French-FTB/fr_ftb-ud-test.conllu"
UD_23_FRENCH_GSD_TRAIN = _UD_23_HOME + "#UD_French-GSD/fr_gsd-ud-train.conllu"
UD_23_FRENCH_GSD_DEV = _UD_23_HOME + "#UD_French-GSD/fr_gsd-ud-dev.conllu"
UD_23_FRENCH_GSD_TEST = _UD_23_HOME + "#UD_French-GSD/fr_gsd-ud-test.conllu"
UD_23_FRENCH_PUD_TEST = _UD_23_HOME + "#UD_French-PUD/fr_pud-ud-test.conllu"
UD_23_FRENCH_PARTUT_TRAIN = _UD_23_HOME + "#UD_French-ParTUT/fr_partut-ud-train.conllu"
UD_23_FRENCH_PARTUT_DEV = _UD_23_HOME + "#UD_French-ParTUT/fr_partut-ud-dev.conllu"
UD_23_FRENCH_PARTUT_TEST = _UD_23_HOME + "#UD_French-ParTUT/fr_partut-ud-test.conllu"
UD_23_FRENCH_SEQUOIA_TRAIN = _UD_23_HOME + "#UD_French-Sequoia/fr_sequoia-ud-train.conllu"
UD_23_FRENCH_SEQUOIA_DEV = _UD_23_HOME + "#UD_French-Sequoia/fr_sequoia-ud-dev.conllu"
UD_23_FRENCH_SEQUOIA_TEST = _UD_23_HOME + "#UD_French-Sequoia/fr_sequoia-ud-test.conllu"
UD_23_FRENCH_SPOKEN_TRAIN = _UD_23_HOME + "#UD_French-Spoken/fr_spoken-ud-train.conllu"
UD_23_FRENCH_SPOKEN_DEV = _UD_23_HOME + "#UD_French-Spoken/fr_spoken-ud-dev.conllu"
UD_23_FRENCH_SPOKEN_TEST = _UD_23_HOME + "#UD_French-Spoken/fr_spoken-ud-test.conllu"
UD_23_GALICIAN_CTG_TRAIN = _UD_23_HOME + "#UD_Galician-CTG/gl_ctg-ud-train.conllu"
UD_23_GALICIAN_CTG_DEV = _UD_23_HOME + "#UD_Galician-CTG/gl_ctg-ud-dev.conllu"
UD_23_GALICIAN_CTG_TEST = _UD_23_HOME + "#UD_Galician-CTG/gl_ctg-ud-test.conllu"
UD_23_GALICIAN_TREEGAL_TRAIN = _UD_23_HOME + "#UD_Galician-TreeGal/gl_treegal-ud-train.conllu"
UD_23_GALICIAN_TREEGAL_TEST = _UD_23_HOME + "#UD_Galician-TreeGal/gl_treegal-ud-test.conllu"
UD_23_GERMAN_GSD_TRAIN = _UD_23_HOME + "#UD_German-GSD/de_gsd-ud-train.conllu"
UD_23_GERMAN_GSD_DEV = _UD_23_HOME + "#UD_German-GSD/de_gsd-ud-dev.conllu"
UD_23_GERMAN_GSD_TEST = _UD_23_HOME + "#UD_German-GSD/de_gsd-ud-test.conllu"
UD_23_GERMAN_PUD_TEST = _UD_23_HOME + "#UD_German-PUD/de_pud-ud-test.conllu"
UD_23_GOTHIC_PROIEL_TRAIN = _UD_23_HOME + "#UD_Gothic-PROIEL/got_proiel-ud-train.conllu"
UD_23_GOTHIC_PROIEL_DEV = _UD_23_HOME + "#UD_Gothic-PROIEL/got_proiel-ud-dev.conllu"
UD_23_GOTHIC_PROIEL_TEST = _UD_23_HOME + "#UD_Gothic-PROIEL/got_proiel-ud-test.conllu"
UD_23_GREEK_GDT_TRAIN = _UD_23_HOME + "#UD_Greek-GDT/el_gdt-ud-train.conllu"
UD_23_GREEK_GDT_DEV = _UD_23_HOME + "#UD_Greek-GDT/el_gdt-ud-dev.conllu"
UD_23_GREEK_GDT_TEST = _UD_23_HOME + "#UD_Greek-GDT/el_gdt-ud-test.conllu"
UD_23_HEBREW_HTB_TRAIN = _UD_23_HOME + "#UD_Hebrew-HTB/he_htb-ud-train.conllu"
UD_23_HEBREW_HTB_DEV = _UD_23_HOME + "#UD_Hebrew-HTB/he_htb-ud-dev.conllu"
UD_23_HEBREW_HTB_TEST = _UD_23_HOME + "#UD_Hebrew-HTB/he_htb-ud-test.conllu"
UD_23_HINDI_HDTB_TRAIN = _UD_23_HOME + "#UD_Hindi-HDTB/hi_hdtb-ud-train.conllu"
UD_23_HINDI_HDTB_DEV = _UD_23_HOME + "#UD_Hindi-HDTB/hi_hdtb-ud-dev.conllu"
UD_23_HINDI_HDTB_TEST = _UD_23_HOME + "#UD_Hindi-HDTB/hi_hdtb-ud-test.conllu"
UD_23_HINDI_PUD_TEST = _UD_23_HOME + "#UD_Hindi-PUD/hi_pud-ud-test.conllu"
UD_23_HINDI_ENGLISH_HIENCS_TRAIN = _UD_23_HOME + "#UD_Hindi_English-HIENCS/qhe_hiencs-ud-train.conllu"
UD_23_HINDI_ENGLISH_HIENCS_DEV = _UD_23_HOME + "#UD_Hindi_English-HIENCS/qhe_hiencs-ud-dev.conllu"
UD_23_HINDI_ENGLISH_HIENCS_TEST = _UD_23_HOME + "#UD_Hindi_English-HIENCS/qhe_hiencs-ud-test.conllu"
UD_23_HUNGARIAN_SZEGED_TRAIN = _UD_23_HOME + "#UD_Hungarian-Szeged/hu_szeged-ud-train.conllu"
UD_23_HUNGARIAN_SZEGED_DEV = _UD_23_HOME + "#UD_Hungarian-Szeged/hu_szeged-ud-dev.conllu"
UD_23_HUNGARIAN_SZEGED_TEST = _UD_23_HOME + "#UD_Hungarian-Szeged/hu_szeged-ud-test.conllu"
UD_23_INDONESIAN_GSD_TRAIN = _UD_23_HOME + "#UD_Indonesian-GSD/id_gsd-ud-train.conllu"
UD_23_INDONESIAN_GSD_DEV = _UD_23_HOME + "#UD_Indonesian-GSD/id_gsd-ud-dev.conllu"
UD_23_INDONESIAN_GSD_TEST = _UD_23_HOME + "#UD_Indonesian-GSD/id_gsd-ud-test.conllu"
UD_23_INDONESIAN_PUD_TEST = _UD_23_HOME + "#UD_Indonesian-PUD/id_pud-ud-test.conllu"
UD_23_IRISH_IDT_TRAIN = _UD_23_HOME + "#UD_Irish-IDT/ga_idt-ud-train.conllu"
UD_23_IRISH_IDT_TEST = _UD_23_HOME + "#UD_Irish-IDT/ga_idt-ud-test.conllu"
UD_23_ITALIAN_ISDT_TRAIN = _UD_23_HOME + "#UD_Italian-ISDT/it_isdt-ud-train.conllu"
UD_23_ITALIAN_ISDT_DEV = _UD_23_HOME + "#UD_Italian-ISDT/it_isdt-ud-dev.conllu"
UD_23_ITALIAN_ISDT_TEST = _UD_23_HOME + "#UD_Italian-ISDT/it_isdt-ud-test.conllu"
UD_23_ITALIAN_PUD_TEST = _UD_23_HOME + "#UD_Italian-PUD/it_pud-ud-test.conllu"
UD_23_ITALIAN_PARTUT_TRAIN = _UD_23_HOME + "#UD_Italian-ParTUT/it_partut-ud-train.conllu"
UD_23_ITALIAN_PARTUT_DEV = _UD_23_HOME + "#UD_Italian-ParTUT/it_partut-ud-dev.conllu"
UD_23_ITALIAN_PARTUT_TEST = _UD_23_HOME + "#UD_Italian-ParTUT/it_partut-ud-test.conllu"
UD_23_ITALIAN_POSTWITA_TRAIN = _UD_23_HOME + "#UD_Italian-PoSTWITA/it_postwita-ud-train.conllu"
UD_23_ITALIAN_POSTWITA_DEV = _UD_23_HOME + "#UD_Italian-PoSTWITA/it_postwita-ud-dev.conllu"
UD_23_ITALIAN_POSTWITA_TEST = _UD_23_HOME + "#UD_Italian-PoSTWITA/it_postwita-ud-test.conllu"
UD_23_JAPANESE_BCCWJ_TRAIN = _UD_23_HOME + "#UD_Japanese-BCCWJ/ja_bccwj-ud-train.conllu"
UD_23_JAPANESE_BCCWJ_DEV = _UD_23_HOME + "#UD_Japanese-BCCWJ/ja_bccwj-ud-dev.conllu"
UD_23_JAPANESE_BCCWJ_TEST = _UD_23_HOME + "#UD_Japanese-BCCWJ/ja_bccwj-ud-test.conllu"
UD_23_JAPANESE_GSD_TRAIN = _UD_23_HOME + "#UD_Japanese-GSD/ja_gsd-ud-train.conllu"
UD_23_JAPANESE_GSD_DEV = _UD_23_HOME + "#UD_Japanese-GSD/ja_gsd-ud-dev.conllu"
UD_23_JAPANESE_GSD_TEST = _UD_23_HOME + "#UD_Japanese-GSD/ja_gsd-ud-test.conllu"
UD_23_JAPANESE_MODERN_TEST = _UD_23_HOME + "#UD_Japanese-Modern/ja_modern-ud-test.conllu"
UD_23_JAPANESE_PUD_TEST = _UD_23_HOME + "#UD_Japanese-PUD/ja_pud-ud-test.conllu"
UD_23_KAZAKH_KTB_TRAIN = _UD_23_HOME + "#UD_Kazakh-KTB/kk_ktb-ud-train.conllu"
UD_23_KAZAKH_KTB_TEST = _UD_23_HOME + "#UD_Kazakh-KTB/kk_ktb-ud-test.conllu"
UD_23_KOMI_ZYRIAN_IKDP_TEST = _UD_23_HOME + "#UD_Komi_Zyrian-IKDP/kpv_ikdp-ud-test.conllu"
UD_23_KOMI_ZYRIAN_LATTICE_TEST = _UD_23_HOME + "#UD_Komi_Zyrian-Lattice/kpv_lattice-ud-test.conllu"
UD_23_KOREAN_GSD_TRAIN = _UD_23_HOME + "#UD_Korean-GSD/ko_gsd-ud-train.conllu"
UD_23_KOREAN_GSD_DEV = _UD_23_HOME + "#UD_Korean-GSD/ko_gsd-ud-dev.conllu"
UD_23_KOREAN_GSD_TEST = _UD_23_HOME + "#UD_Korean-GSD/ko_gsd-ud-test.conllu"
UD_23_KOREAN_KAIST_TRAIN = _UD_23_HOME + "#UD_Korean-Kaist/ko_kaist-ud-train.conllu"
UD_23_KOREAN_KAIST_DEV = _UD_23_HOME + "#UD_Korean-Kaist/ko_kaist-ud-dev.conllu"
UD_23_KOREAN_KAIST_TEST = _UD_23_HOME + "#UD_Korean-Kaist/ko_kaist-ud-test.conllu"
UD_23_KOREAN_PUD_TEST = _UD_23_HOME + "#UD_Korean-PUD/ko_pud-ud-test.conllu"
UD_23_KURMANJI_MG_TRAIN = _UD_23_HOME + "#UD_Kurmanji-MG/kmr_mg-ud-train.conllu"
UD_23_KURMANJI_MG_TEST = _UD_23_HOME + "#UD_Kurmanji-MG/kmr_mg-ud-test.conllu"
UD_23_LATIN_ITTB_TRAIN = _UD_23_HOME + "#UD_Latin-ITTB/la_ittb-ud-train.conllu"
UD_23_LATIN_ITTB_DEV = _UD_23_HOME + "#UD_Latin-ITTB/la_ittb-ud-dev.conllu"
UD_23_LATIN_ITTB_TEST = _UD_23_HOME + "#UD_Latin-ITTB/la_ittb-ud-test.conllu"
UD_23_LATIN_PROIEL_TRAIN = _UD_23_HOME + "#UD_Latin-PROIEL/la_proiel-ud-train.conllu"
UD_23_LATIN_PROIEL_DEV = _UD_23_HOME + "#UD_Latin-PROIEL/la_proiel-ud-dev.conllu"
UD_23_LATIN_PROIEL_TEST = _UD_23_HOME + "#UD_Latin-PROIEL/la_proiel-ud-test.conllu"
UD_23_LATIN_PERSEUS_TRAIN = _UD_23_HOME + "#UD_Latin-Perseus/la_perseus-ud-train.conllu"
UD_23_LATIN_PERSEUS_TEST = _UD_23_HOME + "#UD_Latin-Perseus/la_perseus-ud-test.conllu"
UD_23_LATVIAN_LVTB_TRAIN = _UD_23_HOME + "#UD_Latvian-LVTB/lv_lvtb-ud-train.conllu"
UD_23_LATVIAN_LVTB_DEV = _UD_23_HOME + "#UD_Latvian-LVTB/lv_lvtb-ud-dev.conllu"
UD_23_LATVIAN_LVTB_TEST = _UD_23_HOME + "#UD_Latvian-LVTB/lv_lvtb-ud-test.conllu"
UD_23_LITHUANIAN_HSE_TRAIN = _UD_23_HOME + "#UD_Lithuanian-HSE/lt_hse-ud-train.conllu"
UD_23_LITHUANIAN_HSE_DEV = _UD_23_HOME + "#UD_Lithuanian-HSE/lt_hse-ud-dev.conllu"
UD_23_LITHUANIAN_HSE_TEST = _UD_23_HOME + "#UD_Lithuanian-HSE/lt_hse-ud-test.conllu"
UD_23_MALTESE_MUDT_TRAIN = _UD_23_HOME + "#UD_Maltese-MUDT/mt_mudt-ud-train.conllu"
UD_23_MALTESE_MUDT_DEV = _UD_23_HOME + "#UD_Maltese-MUDT/mt_mudt-ud-dev.conllu"
UD_23_MALTESE_MUDT_TEST = _UD_23_HOME + "#UD_Maltese-MUDT/mt_mudt-ud-test.conllu"
UD_23_MARATHI_UFAL_TRAIN = _UD_23_HOME + "#UD_Marathi-UFAL/mr_ufal-ud-train.conllu"
UD_23_MARATHI_UFAL_DEV = _UD_23_HOME + "#UD_Marathi-UFAL/mr_ufal-ud-dev.conllu"
UD_23_MARATHI_UFAL_TEST = _UD_23_HOME + "#UD_Marathi-UFAL/mr_ufal-ud-test.conllu"
UD_23_NAIJA_NSC_TEST = _UD_23_HOME + "#UD_Naija-NSC/pcm_nsc-ud-test.conllu"
UD_23_NORTH_SAMI_GIELLA_TRAIN = _UD_23_HOME + "#UD_North_Sami-Giella/sme_giella-ud-train.conllu"
UD_23_NORTH_SAMI_GIELLA_TEST = _UD_23_HOME + "#UD_North_Sami-Giella/sme_giella-ud-test.conllu"
UD_23_NORWEGIAN_BOKMAAL_TRAIN = _UD_23_HOME + "#UD_Norwegian-Bokmaal/no_bokmaal-ud-train.conllu"
UD_23_NORWEGIAN_BOKMAAL_DEV = _UD_23_HOME + "#UD_Norwegian-Bokmaal/no_bokmaal-ud-dev.conllu"
UD_23_NORWEGIAN_BOKMAAL_TEST = _UD_23_HOME + "#UD_Norwegian-Bokmaal/no_bokmaal-ud-test.conllu"
UD_23_NORWEGIAN_NYNORSK_TRAIN = _UD_23_HOME + "#UD_Norwegian-Nynorsk/no_nynorsk-ud-train.conllu"
UD_23_NORWEGIAN_NYNORSK_DEV = _UD_23_HOME + "#UD_Norwegian-Nynorsk/no_nynorsk-ud-dev.conllu"
UD_23_NORWEGIAN_NYNORSK_TEST = _UD_23_HOME + "#UD_Norwegian-Nynorsk/no_nynorsk-ud-test.conllu"
UD_23_NORWEGIAN_NYNORSKLIA_TRAIN = _UD_23_HOME + "#UD_Norwegian-NynorskLIA/no_nynorsklia-ud-train.conllu"
UD_23_NORWEGIAN_NYNORSKLIA_TEST = _UD_23_HOME + "#UD_Norwegian-NynorskLIA/no_nynorsklia-ud-test.conllu"
UD_23_OLD_CHURCH_SLAVONIC_PROIEL_TRAIN = _UD_23_HOME + "#UD_Old_Church_Slavonic-PROIEL/cu_proiel-ud-train.conllu"
UD_23_OLD_CHURCH_SLAVONIC_PROIEL_DEV = _UD_23_HOME + "#UD_Old_Church_Slavonic-PROIEL/cu_proiel-ud-dev.conllu"
UD_23_OLD_CHURCH_SLAVONIC_PROIEL_TEST = _UD_23_HOME + "#UD_Old_Church_Slavonic-PROIEL/cu_proiel-ud-test.conllu"
UD_23_OLD_FRENCH_SRCMF_TRAIN = _UD_23_HOME + "#UD_Old_French-SRCMF/fro_srcmf-ud-train.conllu"
UD_23_OLD_FRENCH_SRCMF_DEV = _UD_23_HOME + "#UD_Old_French-SRCMF/fro_srcmf-ud-dev.conllu"
UD_23_OLD_FRENCH_SRCMF_TEST = _UD_23_HOME + "#UD_Old_French-SRCMF/fro_srcmf-ud-test.conllu"
UD_23_PERSIAN_SERAJI_TRAIN = _UD_23_HOME + "#UD_Persian-Seraji/fa_seraji-ud-train.conllu"
UD_23_PERSIAN_SERAJI_DEV = _UD_23_HOME + "#UD_Persian-Seraji/fa_seraji-ud-dev.conllu"
UD_23_PERSIAN_SERAJI_TEST = _UD_23_HOME + "#UD_Persian-Seraji/fa_seraji-ud-test.conllu"
UD_23_POLISH_LFG_TRAIN = _UD_23_HOME + "#UD_Polish-LFG/pl_lfg-ud-train.conllu"
UD_23_POLISH_LFG_DEV = _UD_23_HOME + "#UD_Polish-LFG/pl_lfg-ud-dev.conllu"
UD_23_POLISH_LFG_TEST = _UD_23_HOME + "#UD_Polish-LFG/pl_lfg-ud-test.conllu"
UD_23_POLISH_SZ_TRAIN = _UD_23_HOME + "#UD_Polish-SZ/pl_sz-ud-train.conllu"
UD_23_POLISH_SZ_DEV = _UD_23_HOME + "#UD_Polish-SZ/pl_sz-ud-dev.conllu"
UD_23_POLISH_SZ_TEST = _UD_23_HOME + "#UD_Polish-SZ/pl_sz-ud-test.conllu"
UD_23_PORTUGUESE_BOSQUE_TRAIN = _UD_23_HOME + "#UD_Portuguese-Bosque/pt_bosque-ud-train.conllu"
UD_23_PORTUGUESE_BOSQUE_DEV = _UD_23_HOME + "#UD_Portuguese-Bosque/pt_bosque-ud-dev.conllu"
UD_23_PORTUGUESE_BOSQUE_TEST = _UD_23_HOME + "#UD_Portuguese-Bosque/pt_bosque-ud-test.conllu"
UD_23_PORTUGUESE_GSD_TRAIN = _UD_23_HOME + "#UD_Portuguese-GSD/pt_gsd-ud-train.conllu"
UD_23_PORTUGUESE_GSD_DEV = _UD_23_HOME + "#UD_Portuguese-GSD/pt_gsd-ud-dev.conllu"
UD_23_PORTUGUESE_GSD_TEST = _UD_23_HOME + "#UD_Portuguese-GSD/pt_gsd-ud-test.conllu"
UD_23_PORTUGUESE_PUD_TEST = _UD_23_HOME + "#UD_Portuguese-PUD/pt_pud-ud-test.conllu"
UD_23_ROMANIAN_NONSTANDARD_TRAIN = _UD_23_HOME + "#UD_Romanian-Nonstandard/ro_nonstandard-ud-train.conllu"
UD_23_ROMANIAN_NONSTANDARD_DEV = _UD_23_HOME + "#UD_Romanian-Nonstandard/ro_nonstandard-ud-dev.conllu"
UD_23_ROMANIAN_NONSTANDARD_TEST = _UD_23_HOME + "#UD_Romanian-Nonstandard/ro_nonstandard-ud-test.conllu"
UD_23_ROMANIAN_RRT_TRAIN = _UD_23_HOME + "#UD_Romanian-RRT/ro_rrt-ud-train.conllu"
UD_23_ROMANIAN_RRT_DEV = _UD_23_HOME + "#UD_Romanian-RRT/ro_rrt-ud-dev.conllu"
UD_23_ROMANIAN_RRT_TEST = _UD_23_HOME + "#UD_Romanian-RRT/ro_rrt-ud-test.conllu"
UD_23_RUSSIAN_GSD_TRAIN = _UD_23_HOME + "#UD_Russian-GSD/ru_gsd-ud-train.conllu"
UD_23_RUSSIAN_GSD_DEV = _UD_23_HOME + "#UD_Russian-GSD/ru_gsd-ud-dev.conllu"
UD_23_RUSSIAN_GSD_TEST = _UD_23_HOME + "#UD_Russian-GSD/ru_gsd-ud-test.conllu"
UD_23_RUSSIAN_PUD_TEST = _UD_23_HOME + "#UD_Russian-PUD/ru_pud-ud-test.conllu"
UD_23_RUSSIAN_SYNTAGRUS_TRAIN = _UD_23_HOME + "#UD_Russian-SynTagRus/ru_syntagrus-ud-train.conllu"
UD_23_RUSSIAN_SYNTAGRUS_DEV = _UD_23_HOME + "#UD_Russian-SynTagRus/ru_syntagrus-ud-dev.conllu"
UD_23_RUSSIAN_SYNTAGRUS_TEST = _UD_23_HOME + "#UD_Russian-SynTagRus/ru_syntagrus-ud-test.conllu"
UD_23_RUSSIAN_TAIGA_TRAIN = _UD_23_HOME + "#UD_Russian-Taiga/ru_taiga-ud-train.conllu"
UD_23_RUSSIAN_TAIGA_TEST = _UD_23_HOME + "#UD_Russian-Taiga/ru_taiga-ud-test.conllu"
UD_23_SANSKRIT_UFAL_TEST = _UD_23_HOME + "#UD_Sanskrit-UFAL/sa_ufal-ud-test.conllu"
UD_23_SERBIAN_SET_TRAIN = _UD_23_HOME + "#UD_Serbian-SET/sr_set-ud-train.conllu"
UD_23_SERBIAN_SET_DEV = _UD_23_HOME + "#UD_Serbian-SET/sr_set-ud-dev.conllu"
UD_23_SERBIAN_SET_TEST = _UD_23_HOME + "#UD_Serbian-SET/sr_set-ud-test.conllu"
UD_23_SLOVAK_SNK_TRAIN = _UD_23_HOME + "#UD_Slovak-SNK/sk_snk-ud-train.conllu"
UD_23_SLOVAK_SNK_DEV = _UD_23_HOME + "#UD_Slovak-SNK/sk_snk-ud-dev.conllu"
UD_23_SLOVAK_SNK_TEST = _UD_23_HOME + "#UD_Slovak-SNK/sk_snk-ud-test.conllu"
UD_23_SLOVENIAN_SSJ_TRAIN = _UD_23_HOME + "#UD_Slovenian-SSJ/sl_ssj-ud-train.conllu"
UD_23_SLOVENIAN_SSJ_DEV = _UD_23_HOME + "#UD_Slovenian-SSJ/sl_ssj-ud-dev.conllu"
UD_23_SLOVENIAN_SSJ_TEST = _UD_23_HOME + "#UD_Slovenian-SSJ/sl_ssj-ud-test.conllu"
UD_23_SLOVENIAN_SST_TRAIN = _UD_23_HOME + "#UD_Slovenian-SST/sl_sst-ud-train.conllu"
UD_23_SLOVENIAN_SST_TEST = _UD_23_HOME + "#UD_Slovenian-SST/sl_sst-ud-test.conllu"
UD_23_SPANISH_ANCORA_TRAIN = _UD_23_HOME + "#UD_Spanish-AnCora/es_ancora-ud-train.conllu"
UD_23_SPANISH_ANCORA_DEV = _UD_23_HOME + "#UD_Spanish-AnCora/es_ancora-ud-dev.conllu"
UD_23_SPANISH_ANCORA_TEST = _UD_23_HOME + "#UD_Spanish-AnCora/es_ancora-ud-test.conllu"
UD_23_SPANISH_GSD_TRAIN = _UD_23_HOME + "#UD_Spanish-GSD/es_gsd-ud-train.conllu"
UD_23_SPANISH_GSD_DEV = _UD_23_HOME + "#UD_Spanish-GSD/es_gsd-ud-dev.conllu"
UD_23_SPANISH_GSD_TEST = _UD_23_HOME + "#UD_Spanish-GSD/es_gsd-ud-test.conllu"
UD_23_SPANISH_PUD_TEST = _UD_23_HOME + "#UD_Spanish-PUD/es_pud-ud-test.conllu"
UD_23_SWEDISH_LINES_TRAIN = _UD_23_HOME + "#UD_Swedish-LinES/sv_lines-ud-train.conllu"
UD_23_SWEDISH_LINES_DEV = _UD_23_HOME + "#UD_Swedish-LinES/sv_lines-ud-dev.conllu"
UD_23_SWEDISH_LINES_TEST = _UD_23_HOME + "#UD_Swedish-LinES/sv_lines-ud-test.conllu"
UD_23_SWEDISH_PUD_TEST = _UD_23_HOME + "#UD_Swedish-PUD/sv_pud-ud-test.conllu"
UD_23_SWEDISH_TALBANKEN_TRAIN = _UD_23_HOME + "#UD_Swedish-Talbanken/sv_talbanken-ud-train.conllu"
UD_23_SWEDISH_TALBANKEN_DEV = _UD_23_HOME + "#UD_Swedish-Talbanken/sv_talbanken-ud-dev.conllu"
UD_23_SWEDISH_TALBANKEN_TEST = _UD_23_HOME + "#UD_Swedish-Talbanken/sv_talbanken-ud-test.conllu"
UD_23_SWEDISH_SIGN_LANGUAGE_SSLC_TRAIN = _UD_23_HOME + "#UD_Swedish_Sign_Language-SSLC/swl_sslc-ud-train.conllu"
UD_23_SWEDISH_SIGN_LANGUAGE_SSLC_DEV = _UD_23_HOME + "#UD_Swedish_Sign_Language-SSLC/swl_sslc-ud-dev.conllu"
UD_23_SWEDISH_SIGN_LANGUAGE_SSLC_TEST = _UD_23_HOME + "#UD_Swedish_Sign_Language-SSLC/swl_sslc-ud-test.conllu"
UD_23_TAGALOG_TRG_TEST = _UD_23_HOME + "#UD_Tagalog-TRG/tl_trg-ud-test.conllu"
UD_23_TAMIL_TTB_TRAIN = _UD_23_HOME + "#UD_Tamil-TTB/ta_ttb-ud-train.conllu"
UD_23_TAMIL_TTB_DEV = _UD_23_HOME + "#UD_Tamil-TTB/ta_ttb-ud-dev.conllu"
UD_23_TAMIL_TTB_TEST = _UD_23_HOME + "#UD_Tamil-TTB/ta_ttb-ud-test.conllu"
UD_23_TELUGU_MTG_TRAIN = _UD_23_HOME + "#UD_Telugu-MTG/te_mtg-ud-train.conllu"
UD_23_TELUGU_MTG_DEV = _UD_23_HOME + "#UD_Telugu-MTG/te_mtg-ud-dev.conllu"
UD_23_TELUGU_MTG_TEST = _UD_23_HOME + "#UD_Telugu-MTG/te_mtg-ud-test.conllu"
UD_23_THAI_PUD_TEST = _UD_23_HOME + "#UD_Thai-PUD/th_pud-ud-test.conllu"
UD_23_TURKISH_IMST_TRAIN = _UD_23_HOME + "#UD_Turkish-IMST/tr_imst-ud-train.conllu"
UD_23_TURKISH_IMST_DEV = _UD_23_HOME + "#UD_Turkish-IMST/tr_imst-ud-dev.conllu"
UD_23_TURKISH_IMST_TEST = _UD_23_HOME + "#UD_Turkish-IMST/tr_imst-ud-test.conllu"
UD_23_TURKISH_PUD_TEST = _UD_23_HOME + "#UD_Turkish-PUD/tr_pud-ud-test.conllu"
UD_23_UKRAINIAN_IU_TRAIN = _UD_23_HOME + "#UD_Ukrainian-IU/uk_iu-ud-train.conllu"
UD_23_UKRAINIAN_IU_DEV = _UD_23_HOME + "#UD_Ukrainian-IU/uk_iu-ud-dev.conllu"
UD_23_UKRAINIAN_IU_TEST = _UD_23_HOME + "#UD_Ukrainian-IU/uk_iu-ud-test.conllu"
UD_23_UPPER_SORBIAN_UFAL_TRAIN = _UD_23_HOME + "#UD_Upper_Sorbian-UFAL/hsb_ufal-ud-train.conllu"
UD_23_UPPER_SORBIAN_UFAL_TEST = _UD_23_HOME + "#UD_Upper_Sorbian-UFAL/hsb_ufal-ud-test.conllu"
UD_23_URDU_UDTB_TRAIN = _UD_23_HOME + "#UD_Urdu-UDTB/ur_udtb-ud-train.conllu"
UD_23_URDU_UDTB_DEV = _UD_23_HOME + "#UD_Urdu-UDTB/ur_udtb-ud-dev.conllu"
UD_23_URDU_UDTB_TEST = _UD_23_HOME + "#UD_Urdu-UDTB/ur_udtb-ud-test.conllu"
UD_23_UYGHUR_UDT_TRAIN = _UD_23_HOME + "#UD_Uyghur-UDT/ug_udt-ud-train.conllu"
UD_23_UYGHUR_UDT_DEV = _UD_23_HOME + "#UD_Uyghur-UDT/ug_udt-ud-dev.conllu"
UD_23_UYGHUR_UDT_TEST = _UD_23_HOME + "#UD_Uyghur-UDT/ug_udt-ud-test.conllu"
UD_23_VIETNAMESE_VTB_TRAIN = _UD_23_HOME + "#UD_Vietnamese-VTB/vi_vtb-ud-train.conllu"
UD_23_VIETNAMESE_VTB_DEV = _UD_23_HOME + "#UD_Vietnamese-VTB/vi_vtb-ud-dev.conllu"
UD_23_VIETNAMESE_VTB_TEST = _UD_23_HOME + "#UD_Vietnamese-VTB/vi_vtb-ud-test.conllu"
UD_23_WARLPIRI_UFAL_TEST = _UD_23_HOME + "#UD_Warlpiri-UFAL/wbp_ufal-ud-test.conllu"
UD_23_YORUBA_YTB_TEST = _UD_23_HOME + "#UD_Yoruba-YTB/yo_ytb-ud-test.conllu"
