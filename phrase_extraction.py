import data_reader
from collections import defaultdict

# phrase_frequencies = defaultdict()
# phrase_pair_frequencies = defaultdict()

read_actual_data = False

if read_actual_data:
  english_sentences = data_reader.read_english_sentences()
  german_sentences = data_reader.read_german_sentences()
  alignments = data_reader.read_word_alignments()

def phrase_extraction_algorithm(native_sentence, foreign_sentence, A):

  def extract(f_start, f_end, e_start, e_end):
    if f_end <= 0:
      return set()

    for e,f in A:
      if e < e_start or e > e_end:
        return set()

    E = set()
    fs = f_start

    while True:
      fe = f_end

      while True:
        source_phrase = "".join(native_sentence[i] for i in range(e_start, e_end + 1))
        target_phrase = "".join(foreign_sentence[i] for i in range(fs, fe + 1))

        E.add(source_phrase + " – " + target_phrase)
        fe += 1

        print(f)
        if fe in f_aligned or fe == f:
          break

      fs -= 1
      if fs in f_aligned or fs < 0:
        break

    return E

  e = array_of_words_from_string(native_sentence)
  f = array_of_words_from_string(foreign_sentence)

  phrase_pairs = set()

  e_aligned = [e for e,f in A]
  f_aligned = [f for e,f in A]

  for e_start in range(len(e)):
    for e_end in range(e_start, len(e)):
      f_start, f_end = len(f)-1, -1

      for e_pos, f_pos in A:
        if e_start <= e_pos and e_pos <= e_end:
          f_start = min(f_pos, f_start)
          f_end = max(f_pos, f_end)

      phrase_pairs.update(extract(f_start, f_end, e_start, e_end))

  return phrase_pairs

def array_of_words_from_string(sentence):
  return sentence.split(' ');

def main():
  # phrase_extraction_algorithm(english_sentences[0], german_sentences[0], alignments[0])
  srctext = "michael assumes that he will stay in the house"
  trgtext = "michael geht davon aus , dass er im haus bleibt"
  alignment = [(0,0), (1,1), (1,2), (1,3), (2,5), (3,6), (4,9), (5,9), (6,7), (7,7), (8,8)]

  pairs = phrase_extraction_algorithm(srctext, trgtext, alignment)
  for pair in pairs: print(pair)

main()
