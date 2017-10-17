import data_reader
# TODO: What bout 666.666?
# TODO: Reordering: How to handle first and last phrases?
# TODO: Convert to log probs

def calculate_language_probability(english_phrase, language_model):
  return 0

def calculate_translation_probability(german_phrase, english_phrase, language_model):
  return 0

def calculate_reordering_probability(german_phrase, english_phrase, german_indexes, reordering_model):
  # german_indexes = [german_s_index, german_e_index, german_previous_s_index, german_previous_e_index, german_next_s_index, german_next_e_index]
  return 0

def main():
  trace_file = open('Data/testresults.trans.txt.trace', 'r')
  english_file = open('Data/file.test.en', 'r')
  german_file = open('Data/file.test.de', 'r')

  language_model = None
  translation_model = None
  reordering_model = None

  for i in range(1):
    trace_line = trace_file.readline()
    english_line = english_file.readline()
    german_line = german_file.readline()

    trace_phrases = trace_line.split(" ||| ")
    english_words = english_line.split(" ")
    german_words = german_line.split(" ")

    translation_cost = 0

    for trace_i, trace_phrase in enumerate(trace_phrases):
      # Get necessary values
      (german_indices, english_phrase) = trace_phrase.split(":")
      (german_previous_indices, previous_english_phrase) = trace_phrases[max(trace_i - 1, 0)].split(":")
      (german_next_indices, next_english_phrase) = trace_phrases[min(trace_i + 1, len(trace_phrases) - 1)].split(":")

      (german_s_index, german_e_index) = map(int, german_indices.split("-"))
      (german_previous_s_index, german_previous_e_index) = map(int, german_previous_indices.split("-"))
      (german_next_s_index, german_next_e_index) = map(int, german_next_indices.split("-"))

      german_indexes = [german_s_index, german_e_index, german_previous_s_index, german_previous_e_index, german_next_s_index, german_next_e_index]

      # Calculate probabilities
      phrase_probability = 0
      phrase_probability += calculate_language_probability(english_phrase, language_model)

      german_phrase = " ".join(german_words[german_s_index : german_e_index + 1])
      phrase_probability += calculate_translation_probability(german_phrase, english_phrase, language_model)

      phrase_probability += calculate_reordering_probability(german_phrase, english_phrase, german_indexes, reordering_model)

      translation_cost += phrase_probability

    print("Translation cost: {}".format(translation_cost))


if __name__ == '__main__':
  main()
