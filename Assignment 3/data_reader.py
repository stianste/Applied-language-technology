def read_translation_model():
  with open('Data/phrase-table', 'r') as translation_model_file:
    translation_model_lines = translation_model_file.read().splitlines()

  translation_model = {}
  for translation_model_line in translation_model_lines:
    (german_phrase, english_phrase, probabilities, _, _) = translation_model_line.split(" ||| ")
    (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f, _) = map(float, probabilities.split(" "))

    translation_model[(german_phrase, english_phrase)] = (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f)

  return translation_model

def read_reordering_model():
  with open('Data/dm_fe_0.75', 'r') as reordering_model_file:
    reordering_model_lines = reordering_model_file.read().splitlines()

  reordering_model = {}
  for reordering_model_line in reordering_model_lines:
    (german_phrase, english_phrase, probabilities) = reordering_model_line.split(" ||| ")
    (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr) = map(float, probabilities.split(" "))

    reordering_model[(german_phrase, english_phrase)] = (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr)

  return reordering_model

def get_ngram_model(language_model_lines, start_index, end_index):
  ngram_model = {}

  for i in range(start_index, end_index):
    split_line = language_model_lines[i].split('\t')
    probability = float(split_line[0])
    ngram = split_line[1]
    if len(split_line) == 3:
      backoff_weight = float(split_line[2])
    else:
      backoff_weight = None

    ngram_model[ngram] = (probability, backoff_weight)

  return ngram_model

def read_language_model():
  with open('Data/file.en.lm', 'r') as language_model_file:
    language_model_lines = language_model_file.read().splitlines()

  # Read the number of lines for each ngram model
  ngram_1_n_lines = int(language_model_lines[2].split("=")[1])
  ngram_2_n_lines = int(language_model_lines[3].split("=")[1])
  ngram_3_n_lines = int(language_model_lines[4].split("=")[1])
  ngram_4_n_lines = int(language_model_lines[5].split("=")[1])
  ngram_5_n_lines = int(language_model_lines[6].split("=")[1])

  start_index = 9
  ngram_1_model = get_ngram_model(language_model_lines, start_index, start_index + ngram_1_n_lines)
  start_index = start_index + ngram_1_n_lines + 2
  ngram_2_model = get_ngram_model(language_model_lines, start_index, start_index + ngram_2_n_lines)
  start_index = start_index + ngram_2_n_lines + 2
  ngram_3_model = get_ngram_model(language_model_lines, start_index, start_index + ngram_3_n_lines)
  start_index = start_index + ngram_3_n_lines + 2
  ngram_4_model = get_ngram_model(language_model_lines, start_index, start_index + ngram_4_n_lines)
  start_index = start_index + ngram_4_n_lines + 2
  ngram_5_model = get_ngram_model(language_model_lines, start_index, start_index + ngram_5_n_lines)

  return ngram_1_model, ngram_2_model, ngram_3_model, ngram_4_model, ngram_5_model