def read_translation_model():
  translation_model_file = open('Data/phrase-table', 'r')
  translation_model_lines = translation_model_file.read().splitlines()

  translation_model = {}
  for translation_model_line in translation_model_lines:
    (german_phrase, english_phrase, probabilities, _, _) = translation_model_line.split(" ||| ")
    (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f, _) = probabilities.split(" ")

    translation_model[(german_phrase, english_phrase)] = (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f)

  return translation_model

def read_reordering_model():
  reordering_model_file = open('Data/dm_fe_0.75', 'r')
  reordering_model_lines = reordering_model_file.read().splitlines()

  reordering_model = {}
  for reordering_model_line in reordering_model_lines:
    (german_phrase, english_phrase, probabilities) = reordering_model_line.split(" ||| ")
    (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr) = probabilities.split(" ")

    reordering_model[(german_phrase, english_phrase)] = (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr)

  return reordering_model

def read_language_model():
  language_model_file = open('Data/file.en.lm', 'r')

  return 0