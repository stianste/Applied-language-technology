import numpy as np

# Read in the translation model file and return the translation model object.
# Returns a dictionary with the tuple (german_phrase, english_phrase) as key
# and the tuple (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f) as value
# The probabilities are in log10
def read_translation_model():
  with open('Data/phrase-table', 'r') as translation_model_file:
    translation_model_lines = translation_model_file.read().splitlines()

  translation_model = {}
  for translation_model_line in translation_model_lines:
    (german_phrase, english_phrase, probabilities, _, _) = translation_model_line.split(" ||| ")
    (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f, _) = map(np.log10, map(float, probabilities.split()))

    translation_model[(german_phrase, english_phrase)] = (p_f_given_e, lex_f_given_e, p_e_given_f, lex_e_given_f)

  return translation_model

# Read in the reordering model file and return the reordering model object.
# Returns a dictionary with the tuple (german_phrase, english_phrase) as key
# and the tuple (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr) as value
# The probabilities are in log10
def read_reordering_model():
  with open('Data/dm_fe_0.75', 'r') as reordering_model_file:
    reordering_model_lines = reordering_model_file.read().splitlines()

  reordering_model = {}
  for reordering_model_line in reordering_model_lines:
    (german_phrase, english_phrase, probabilities) = reordering_model_line.split(" ||| ")
    (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr) = map(np.log10, map(float, probabilities.split()))

    reordering_model[(german_phrase, english_phrase)] = (mono_rtl, swap_rtl, disc_rtl, mono_ltr, swap_ltr, disc_ltr)

  return reordering_model

# Read a certain number of lines and add the values into a dict (ngram-model)
def _get_ngram_model(language_model_lines, start_index, end_index):
  ngram_model = {}

  for i in range(start_index, end_index):
    split_line = language_model_lines[i].split('\t')
    probability = float(split_line[0])
    ngram = split_line[1]
    if len(split_line) == 3:
      backoff_weight = float(split_line[2])
    else:
      # If there is no back-off we can backoff with no cost.
      # Thus we use a backoff weight of log(1) = 0
      backoff_weight = 0

    ngram_model[ngram] = (probability, backoff_weight)

  return ngram_model

# Returns the 5 n-gram models.
# Each model is a dictionary with the ngram as key and the tuple: (probability, backoff_weight) as value
# Both the probability and backoff_weight are log10
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
  ngram_1_model = _get_ngram_model(language_model_lines, start_index, start_index + ngram_1_n_lines)
  start_index = start_index + ngram_1_n_lines + 2
  ngram_2_model = _get_ngram_model(language_model_lines, start_index, start_index + ngram_2_n_lines)
  start_index = start_index + ngram_2_n_lines + 2
  ngram_3_model = _get_ngram_model(language_model_lines, start_index, start_index + ngram_3_n_lines)
  start_index = start_index + ngram_3_n_lines + 2
  ngram_4_model = _get_ngram_model(language_model_lines, start_index, start_index + ngram_4_n_lines)
  start_index = start_index + ngram_4_n_lines + 2
  ngram_5_model = _get_ngram_model(language_model_lines, start_index, start_index + ngram_5_n_lines)

  ngram_1_model.update(ngram_2_model)
  ngram_1_model.update(ngram_3_model)
  ngram_1_model.update(ngram_4_model)
  ngram_1_model.update(ngram_5_model)

  return ngram_1_model
