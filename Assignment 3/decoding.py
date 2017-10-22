import data_reader

lambda_language_model = 1
lambda_translation_model = 1
lambda_reordering_model = 1

# Calculate language probability of english phrase with the highest order n-gram possible.
# Otherwise, back-off recursively
def calculate_language_probability(english_phrase, language_model):
  english_words = english_phrase.split()

  # Base case
  if not english_words:
    return 0

  # Return (log) probability if in language model
  if english_phrase in language_model:
    return language_model[english_phrase][0]

  # Else, recursively backoff to lower n-gram models
  # If the history is not in the language model, we use a backoff weight of 0
  else:
    history = " ".join(english_words[:-1])
    backoff_weight = language_model.get(history, [0,0])[1]

    lower_order_ngram = " ".join(english_words[1:])
    lower_order_ngram_prob = calculate_language_probability(lower_order_ngram, language_model)

    return backoff_weight + lower_order_ngram_prob

# Calculate translation probability of phrase pair (e,f) by:
# p(e|f) * p(f|e) * lex(e|f) * lex(f|e)
def calculate_translation_probability(german_phrase, english_phrase, translation_model):
  if (german_phrase, english_phrase) in translation_model:
    return sum([log_prob for log_prob in translation_model[(german_phrase, english_phrase)]])
  else:
    return 0

# Calculate reordering probability. See our report for more info on how we did this
def calculate_reordering_probability(german_phrase, english_phrase, german_indexes, german_sentence_len, reordering_model):
  # Unpack indices variable into multiple single variables.
  german_start_index, german_end_index = german_indexes[0], german_indexes[1]
  german_previous_start_index, german_previous_end_index = german_indexes[2], german_indexes[3]
  german_next_start_index, german_next_end_index = german_indexes[4], german_indexes[5]

  log_sum = 0
  if (german_phrase, english_phrase) not in reordering_model:
    return 0


  ### Right-to-left model ###

  # Case for the first english phrase
  if german_previous_start_index == -1:
    if german_start_index == 0:
      log_sum += reordering_model[(german_phrase, english_phrase)][0] # Monotone
    else:
      log_sum += reordering_model[(german_phrase, english_phrase)][2] # Discontinuous

  # Any other english phrase
  else:
    if german_start_index - 1 == german_previous_end_index:
      log_sum += reordering_model[(german_phrase, english_phrase)][0] # Monotone
    elif german_end_index + 1 == german_previous_start_index:
      log_sum += reordering_model[(german_phrase, english_phrase)][1] # Swap
    else:
      log_sum += reordering_model[(german_phrase, english_phrase)][2] # Discont

  ### Left-to-right ###

  # Case for the last english phrase
  if german_next_start_index == -1:
    if german_end_index == german_sentence_len - 1:
      log_sum += reordering_model[(german_phrase, english_phrase)][3] # Monotone
    else:
      log_sum += reordering_model[(german_phrase, english_phrase)][5] # Discontinuous

  # Any other english phrase
  else:
    if german_end_index + 1 == german_next_start_index:
      log_sum += reordering_model[(german_phrase, english_phrase)][3] # Monotone
    elif german_start_index - 1 == german_next_end_index:
      log_sum += reordering_model[(german_phrase, english_phrase)][4] # Swap
    else:
      log_sum += reordering_model[(german_phrase, english_phrase)][5] # Disct

  return log_sum

def main():
  trace_file = open('Data/testresults.trans.txt.trace', 'r')
  english_file = open('Data/file.test.en', 'r')
  german_file = open('Data/file.test.de', 'r')

  print("Loading language model in memory...")
  language_model = data_reader.read_language_model()
  print("Loading translation model in memory...")
  translation_model = data_reader.read_translation_model()
  print("Loading reordering model in memory...")
  reordering_model = data_reader.read_reordering_model()

  sentence_i = 1
  while True:
    # Load one line at a time and strip trailing whitespace
    trace_line = trace_file.readline().strip()
    english_line = english_file.readline().strip()
    german_line = german_file.readline().strip()

    # EOF reached
    if not trace_line:
      break

    # Split lines into array of words or phrases.
    trace_phrases = trace_line.split(" ||| ")
    english_words = english_line.split()
    german_words = german_line.split()
    german_sentence_len = len(german_words)

    sentence_translation_probability = 0
    for phrase_i, trace_phrase in enumerate(trace_phrases):
      # Get necessary values
      (german_indices, english_phrase) = trace_phrase.split(":", 1)
      (german_start_index, german_end_index) = map(int, german_indices.split("-"))
      german_phrase = " ".join(german_words[german_start_index : german_end_index + 1])
      english_phrase_split = english_phrase.split()

      # Get start and end indices of the previous translated phrase. If this is the first English phrase,
      # indicate this edge case with indices -1
      if (phrase_i - 1 > 0):
        (german_previous_indices, previous_english_phrase) = trace_phrases[max(phrase_i - 1, 0)].split(":", 1)
        (german_previous_start_index, german_previous_end_index) = map(int, german_previous_indices.split("-"))
      else:
        (german_previous_start_index, german_previous_end_index) = (-1, -1)

      # Get start and end indices of the next translated phrase. If this is the last English phrase,
      # indicate this edge case with indices -1
      if (phrase_i + 1 < len(trace_phrases)):
        (german_next_indices, next_english_phrase) = trace_phrases[phrase_i + 1].split(":", 1)
        (german_next_start_index, german_next_end_index) = map(int, german_next_indices.split("-"))
      else:
        (german_next_start_index, german_next_end_index) = (-1, -1)

      # Combine the six start and end indices into just one variable
      german_indexes = [german_start_index, german_end_index, german_previous_start_index, german_previous_end_index, german_next_start_index, german_next_end_index]

      # Get all (up-to) 5-grams in this phrase and add the language probability of this n-gram
      phrase_language_probability = 0
      for english_word_index in range(1, len(english_phrase_split) + 1):
        n_gram = " ".join(english_phrase_split[max(0, english_word_index - 5) : english_word_index])
        phrase_language_probability += calculate_language_probability(n_gram, language_model)

      # Calculate probabilities
      phrase_probability = 0
      phrase_probability += lambda_language_model    * phrase_language_probability
      phrase_probability += lambda_translation_model * calculate_translation_probability(german_phrase, english_phrase, translation_model)
      phrase_probability += lambda_reordering_model  * calculate_reordering_probability(german_phrase, english_phrase, german_indexes, german_sentence_len, reordering_model)


      sentence_translation_probability += phrase_probability

    print("Translation cost of sentence {}/{}: {}".format(sentence_i, 500, sentence_translation_probability))
    sentence_i += 1

  trace_file.close()
  english_file.close()
  german_file.close()

if __name__ == '__main__':
  main()
