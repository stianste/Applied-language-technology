import data_reader
from collections import Counter

def phrase_extraction_algorithm(foreign_sentence_split, english_sentence_split, A):
  def extract(f_start, f_end, e_start, e_end):
    if f_end == -1:
      return set()

    for (e, f) in A:
      if (f >= f_start and f <= f_end) and (e < e_start or e > e_end):
        return set()

    E = set()
    fs = f_start

    while True:
      fe = f_end

      while True:
        english_phrase = " ".join(english_sentence_split[i] for i in range(e_start, e_end + 1))
        foreign_phrase = " ".join(foreign_sentence_split[i] for i in range(fs, fe + 1))

        # For this particular phrase pair, store the relative alignments.
        # We subtract e_start and fs, which are the positions of the first words
        # of these phrases in respectively the english and foreign sentence.
        sub_alignments = [
          (sub_alignment_e - e_start, sub_alignment_f - fs)
          for (sub_alignment_e, sub_alignment_f) in A \
          if (e_start <= sub_alignment_e <= e_end) and (fs <= sub_alignment_f <= fe)
          ]
        sub_alignments = tuple(sub_alignments)

        if fe < fs + 5: # Only make phrases of length five or less
          E.add((foreign_phrase, english_phrase, sub_alignments))

        fe += 1

        if fe in f_aligned or fe == len(foreign_sentence_split) or fe > fs + 5:
          break

      fs -= 1
      if fs in f_aligned or fs == -1:
        break

    return E

  phrase_pairs = set()

  f_aligned = [f for (e, f) in A]

  for e_start in range(len(english_sentence_split)):
    # Only make phrases of length five or less
    for e_end in range(e_start, min(e_start + 5, len(english_sentence_split))):
      f_start, f_end = len(foreign_sentence_split)-1, -1

      for (e_pos, f_pos) in A:
        if e_start <= e_pos and e_pos <= e_end:
          f_start = min(f_pos, f_start)
          f_end = max(f_pos, f_end)

      phrase_pairs.update(extract(f_start, f_end, e_start, e_end))

  return phrase_pairs

def array_of_words_from_string(sentence):
  return sentence.split(' ');

# Returns p(e|f) = count(e, f) / count(f).
# or p(f|e) (depending on input)
def phrase_translation_probabilities(phrase_counter, phrase, phrase_pair_counter, phrase_pair):
  return phrase_pair_counter[phrase_pair] / phrase_counter[phrase]

def update_word_translation_counter(
  word_translation_counter_e_given_f, word_translation_counter_f_given_e,
  foreign_word_counter, english_word_counter,
  foreign_sentence_split, english_sentence_split, alignments):

  # Update word counters and word alignment counters.
  for (e,f) in alignments:
    word_translation_counter_e_given_f.update([(english_sentence_split[e], foreign_sentence_split[f])])
    word_translation_counter_f_given_e.update([(foreign_sentence_split[f], english_sentence_split[e])])
    foreign_word_counter.update([foreign_sentence_split[f]])
    english_word_counter.update([english_sentence_split[e]])

  # Get the words in english that are not translated in the foreign sentence. 
  all_english_words = range(len(english_sentence_split))
  matched_english_words = [alignment[0] for alignment in alignments]
  unmatched_english_words = [english_word for english_word in all_english_words if english_word not in matched_english_words]

  # Increment word translation for all unmmatched words by matching them to 'NULL'
  for unmatched_english_word in unmatched_english_words:
    word_translation_counter_e_given_f.update([(english_sentence_split[unmatched_english_word], 'NULL')])
    foreign_word_counter.update(['NULL'])

  # Do the same thing for foreign words that are not matched to any english words.
  all_foreign_words = range(len(foreign_sentence_split))
  matched_foreign_words = [alignment[1] for alignment in alignments]
  unmatched_foreign_words = [foreign_word for foreign_word in all_foreign_words if foreign_word not in matched_foreign_words]

  for unmatched_foreign_word in unmatched_foreign_words:
    word_translation_counter_f_given_e.update([(foreign_sentence_split[unmatched_foreign_word], 'NULL')])
    english_word_counter.update(['NULL'])

# Count the number of foreign words the english word (index i) is aligned to.
# If this is 0, it is aligned to 'NULL', which would make the count 1.
# Therefore we take count = max(count, 1)
def all_words_aligned_to_word(i, alignment):
  return max(1, sum([1 for a in alignment if a[0] == i]))

def sum_of_all_words_with_alignment(i, e_phrase, f_phrase, alignments, word_translation_probabilities):
  total = 0

  sub_alignments_i = [a for a in alignments if a[0] == i]

  # Unaligned word
  if not len(sub_alignments_i):
    total = word_translation_probabilities[(e_phrase[i], 'NULL')]

  # For all aligned words: add the word translation probability
  for alignment in sub_alignments_i:
    total += word_translation_probabilities[(e_phrase[i], f_phrase[alignment[1]])]

  return total

# Calculates the lexical score Lex(e | f) (or Lex(f | e) if arguments are switched)
def lex(e_phrase, f_phrase, alignments, word_translation_probabilities):
  lexical_score = 1
  for i in range(len(e_phrase)):
    lexical_score *= 1 / all_words_aligned_to_word(i, alignments)
    lexical_score *= sum_of_all_words_with_alignment(i, e_phrase, f_phrase, alignments, word_translation_probabilities)

  return lexical_score

def switch_alignments(alignments):
  return tuple([(b, a) for (a, b) in alignments])

# Calculate the word translation probabilities 
def calculate_word_translation_probabilities(word_translation_counter, word_counter):
  word_translation_probabilities = {}
  for word_translation in word_translation_counter:
    english_word = word_translation[0]
    foreign_word = word_translation[1]

    number_of_translation_occurences = word_translation_counter[word_translation]
    number_of_word_occurences = word_counter[foreign_word]

    word_translation_probabilities[word_translation] = number_of_translation_occurences / number_of_word_occurences

  return word_translation_probabilities

def read_data():
  english_sentences = data_reader.read_english_sentences()
  foreign_sentences = data_reader.read_german_sentences()
  global_alignments = data_reader.read_word_alignments()

  return english_sentences, foreign_sentences, global_alignments

def create_phrase_pairs_and_counts(n, english_sentences, foreign_sentences,
    global_alignments, word_translation_counter_e_given_f, 
    word_translation_counter_f_given_e, foreign_word_counter, english_word_counter,
    phrase_pairs):

  print("Extracting phrases for {} sentences... ({} total)".format(n, len(english_sentences)))
  for i in range(n):
    if i % 1000 == 0 and i > 0:
      print("Extracted phrases for {}/{} sentences".format(i, n))
 
    foreign_sentence = foreign_sentences[i]
    english_sentence = english_sentences[i]
    alignments = global_alignments[i]

    foreign_sentence_split = array_of_words_from_string(foreign_sentence)
    english_sentence_split = array_of_words_from_string(english_sentence)

    phrase_pairs.update(phrase_extraction_algorithm(foreign_sentence_split, english_sentence_split, alignments))

    update_word_translation_counter(word_translation_counter_e_given_f, word_translation_counter_f_given_e,
      foreign_word_counter, english_word_counter,
      foreign_sentence_split, english_sentence_split, alignments)

def main():

  ################################################################
  ### Initialize variables and create phrase pairs with counts ###
  ################################################################

  english_sentences, foreign_sentences, global_alignments = read_data()

  word_translation_counter_e_given_f = Counter()
  word_translation_counter_f_given_e = Counter()
  foreign_word_counter = Counter()
  english_word_counter = Counter()

  phrase_pairs = set()

  # Create phrase pairs and count words and word alignments
  create_phrase_pairs_and_counts(len(english_sentences), english_sentences, foreign_sentences, global_alignments, \
      word_translation_counter_e_given_f, word_translation_counter_f_given_e, \
      foreign_word_counter, english_word_counter, phrase_pairs)

  # Normalize word translation counts to get probabilities
  word_translation_probabilities_e_given_f = calculate_word_translation_probabilities(word_translation_counter_e_given_f, foreign_word_counter)
  word_translation_probabilities_f_given_e = calculate_word_translation_probabilities(word_translation_counter_f_given_e, english_word_counter)

  # Count phrases and phrase pairs
  f_phrase_counter = Counter(f_phrase for (f_phrase, e_phrase, alignment) in phrase_pairs)
  e_phrase_counter = Counter(e_phrase for (f_phrase, e_phrase, alignment) in phrase_pairs)
  phrase_pair_counter = Counter(phrase_pairs)

  ##################################################
  ### Write actual output for each sentence pair ###
  ##################################################

  print("Extracted {} phrase pairs. Writing to 'output.txt'...\n\n".format(len(phrase_pairs)))

  with open('output.txt', 'w') as output_file:
    for phrase_pair in phrase_pairs:
      f_phrase, e_phrase, sub_alignments = phrase_pair
      e_phrase_split = e_phrase.split(' ')
      f_phrase_split = f_phrase.split(' ')
      sub_alignments_switched = switch_alignments(sub_alignments)

      phrase_pair_freq = phrase_pair_counter[phrase_pair]
      f_freq = f_phrase_counter[f_phrase]
      e_freq = e_phrase_counter[e_phrase]
      p_f_e = phrase_translation_probabilities(e_phrase_counter, e_phrase, phrase_pair_counter, phrase_pair)
      p_e_f = phrase_translation_probabilities(f_phrase_counter, f_phrase, phrase_pair_counter, phrase_pair)
      lex_e_f = lex(e_phrase_split, f_phrase_split, sub_alignments, word_translation_probabilities_e_given_f)
      lex_f_e = lex(f_phrase_split, e_phrase_split, sub_alignments_switched, word_translation_probabilities_f_given_e)

      output_string = "{} ||| {} ||| {} {} {} {} ||| {} {} {}\n".format(f_phrase,
        e_phrase, p_f_e, p_e_f, lex_f_e, lex_e_f, f_freq, e_freq, phrase_pair_freq)

      output_file.write(output_string)
      # print(output_string)

if __name__ == '__main__':
  main()
