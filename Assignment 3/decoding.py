import data_reader
# TODO: What bout 666.666?
# TODO: Reordering: How to handle first and last phrases?
# TODO: Convert to log probs

def calculate_language_probability(english_phrase):
  return 0

def calculate_translation_probability():
  return 0

def calculate_reordering_probability():
  return 0

def main():
  trace_file = open('Data/testresults.trans.txt.trace', 'r')
  english_file = open('Data/file.test.en', 'r')
  german_file = open('Data/file.test.de', 'r')

  for i in range(1):
    trace_line = trace_file.readline()
    english_line = english_file.readline()
    german_line = german_file.readline()

    trace_phrases = trace_line.split(" ||| ")
    english_words = english_line.split(" ")
    german_line = german_line.split(" ")

    sentence_probability = 0
    for trace_phrase in trace_phrases:
      (german_indices, english_phrase) = trace_phrase.split(":")
      (german_s_index, german_e_index) = map(int, german_indices.split("-"))

      (german_indices_next, english_phrase_next) = trace_phrases[trace_i+1].split(":")
      (german_s_index, german_e_index) = map(int, german_indices.split("-"))

      phrase_probability = 0
      phrase_probability += calculate_language_probability(english_phrase)
      phrase_probability += calculate_translation_probability()
      phrase_probability += calculate_reordering_probability()

      sentence_probability += phrase_probability

    print("Translation probability: {}".format(translation_probability))


if __name__ == '__main__':
  main()
