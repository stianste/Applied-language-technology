import data_reader
from collections import Counter

phrase_length = 7

def read_data():
  english_sentences = data_reader.read_english_sentences()
  foreign_sentences = data_reader.read_german_sentences()
  global_alignments = data_reader.read_word_alignments()

  return english_sentences, foreign_sentences, global_alignments

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
        e_first_alignment = min([e_index for (e_index, f_index) in sub_alignments])
        e_last_alignment = max([e_index for (e_index, f_index) in sub_alignments])
        f_first_alignment = min([f_index for (e_index, f_index) in sub_alignments])
        f_last_alignment = max([f_index for (e_index, f_index) in sub_alignments])


        if fe < fs + phrase_length: # Only make phrases of length five or less
          E.add((foreign_phrase, english_phrase, sub_alignments, (fs, fe), (e_start, e_end)))

        fe += 1

        if fe in f_aligned or fe == len(foreign_sentence_split) or fe > fs + phrase_length:
          break

      fs -= 1
      if fs in f_aligned or fs == -1:
        break

    return E

  phrase_pairs = set()

  f_aligned = [f for (e, f) in A]

  for e_start in range(len(english_sentence_split)):
    # Only make phrases of length five or less
    for e_end in range(e_start, min(e_start + phrase_length, len(english_sentence_split))):
      f_start, f_end = len(foreign_sentence_split)-1, -1

      for (e_pos, f_pos) in A:
        if e_start <= e_pos and e_pos <= e_end:
          f_start = min(f_pos, f_start)
          f_end = max(f_pos, f_end)

      phrase_pairs.update(extract(f_start, f_end, e_start, e_end))

  return phrase_pairs

def count_reorderings(n, english_sentences, foreign_sentences, global_alignments):
  phrase_based_reorderings_counter = Counter()
  word_based_phrase_based_reorderings_counter = Counter()
  global_phrase_pairs = set()

  for i in range(n):
    foreign_sentence = foreign_sentences[i]
    english_sentence = english_sentences[i]
    alignments = global_alignments[i]

    foreign_sentence_split = foreign_sentence.split(' ')
    english_sentence_split = english_sentence.split(' ')

    # f, e, sub_alignments, (f_start, f_end), (e_start, e_end)
    phrase_pairs = phrase_extraction_algorithm(foreign_sentence_split, english_sentence_split, alignments)

    for phrase_pair_base in phrase_pairs:
      base_pair_f                         = phrase_pair_base[0]
      base_pair_e                         = phrase_pair_base[1]
      base_pair_f_start, base_pair_f_end  = phrase_pair_base[3]
      base_pair_e_start, base_pair_e_end  = phrase_pair_base[4]

      global_phrase_pairs.update([(base_pair_f, base_pair_e)])

      for phrase_pair_target in phrase_pairs:
        target_pair_f                           = phrase_pair_target[0]
        target_pair_e                           = phrase_pair_target[1]
        target_pair_sub_alignments              = phrase_pair_target[2]
        target_pair_f_start, target_pair_f_end  = phrase_pair_target[3]
        target_pair_e_start, target_pair_e_end  = phrase_pair_target[4]
        target_pair_f_last_index = len(target_pair_f.split(' ')) - 1
        target_pair_e_last_index = len(target_pair_e.split(' ')) - 1

        # Phrase-based (left-to-right and right-to-left) and word-based (left-to-right)
        if target_pair_e_start == base_pair_e_end + 1:

          if target_pair_f_start == base_pair_f_end + 1:
            phrase_based_reorderings_counter.update([('ltr', 'm', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','m', target_pair_f, target_pair_e)])

            if (0, 0) in target_pair_sub_alignments:
              word_based_phrase_based_reorderings_counter.update(['ltr', 'm', base_pair_f, base_pair_e])
            else:
              word_based_phrase_based_reorderings_counter.update(['ltr', 'dr', base_pair_f, base_pair_e])

          elif target_pair_f_start == base_pair_f_end - 1:
            phrase_based_reorderings_counter.update([('ltr','s', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','s', target_pair_f, target_pair_e)])

            if (0, target_pair_f_last_index) in target_pair_sub_alignments:
              word_based_phrase_based_reorderings_counter.update(['ltr', 's', base_pair_f, base_pair_e])
            else:
              word_based_phrase_based_reorderings_counter.update(['ltr', 'dl', base_pair_f, base_pair_e])

          elif target_pair_f_start > base_pair_f_end:
            # TODO: Figure out the difference between discontinuous right and left
            phrase_based_reorderings_counter.update([('ltr','dr', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','dr', target_pair_f, target_pair_e)])

            word_based_phrase_based_reorderings_counter.update(['ltr', 'dr', base_pair_f, base_pair_e])

          elif target_pair_f_end < base_pair_f_start:
            phrase_based_reorderings_counter.update([('ltr','dl', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','dl', target_pair_f, target_pair_e)])

            word_based_phrase_based_reorderings_counter.update(['ltr', 'dr', base_pair_f, base_pair_e])

        # Word-based (right-to-left)
        # Check whether the target block ends where the base block begins
        if target_pair_e_end == base_pair_e_start - 1:
          # Check whether the target block is monotone
          if target_pair_f_end == base_pair_f_start - 1:
            # Check whether an alignment in this block is monotone
            if (target_pair_e_last_index, target_pair_f_last_index) in target_pair_sub_alignments:
              phrase_based_reorderings_counter.update(['rtl', 'm', base_pair_f, base_pair_e])
            else:
              phrase_based_reorderings_counter.update(['rtl', 'dr', base_pair_f, base_pair_e])

          # Check whether the target block is on the left side of the base block
          # (which makes it discontinuous right for the right-to-left model)
          elif (target_pair_f_end < base_pair_f_start):
            phrase_based_reorderings_counter.update(['rtl', 'dr', base_pair_f, base_pair_e])

          # Check wether the block is swapped
          elif target_pair_f_start == base_pair_f_end + 1:
            # Check wether there is also a word alignment that is swapped
            if (target_pair_e_last_index, 0) in target_pair_sub_alignments:
              phrase_based_reorderings_counter.update(['rtl', 's', base_pair_f, base_pair_e])
            else:
              phrase_based_reorderings_counter.update(['rtl', 'dl', base_pair_f, base_pair_e])
          
          # Check wether the target block is on the right side of the base block (making it discontinuous left in the rtl model)
          elif (target_pair_f_start > base_pair_f_end):
            phrase_based_reorderings_counter.update(['rtl', 'dl', base_pair_f, base_pair_e])            

  return phrase_based_reorderings_counter, global_phrase_pairs

def main():

  ################################################################
  ### Initialize variables and create phrase pairs with counts ###
  ################################################################

  english_sentences, foreign_sentences, global_alignments = read_data()

  english_sentences = ["en1 en2 en3 en4 en5 en6"]
  foreign_sentences = ["f1 f2 f3 f4 f5 f6 f7"]
  global_alignments = [[(0, 0), (1, 1), (2, 1), (3, 4), (3, 5), (4, 2), (4, 3), (5, 6)]]

  phrase_based_reorderings_counter, phrase_pairs = count_reorderings(1, english_sentences, foreign_sentences, global_alignments)

  for (f, e) in phrase_pairs:
    ordering_count_sum_right = 0
    ordering_count_sum_left = 0

    for o in ['m', 's', 'dl', 'dr']:
      ordering_count_sum_right += phrase_based_reorderings_counter[('rtl', o, f, e)]
      ordering_count_sum_left += phrase_based_reorderings_counter[('ltr', o, f, e)]

    if not ordering_count_sum_right == 0 and not ordering_count_sum_left == 0:
      p_l_r_m = phrase_based_reorderings_counter['ltr', 'm', f, e] / ordering_count_sum_left
      p_l_r_s = phrase_based_reorderings_counter['ltr', 's', f, e] / ordering_count_sum_left
      p_l_r_dl = phrase_based_reorderings_counter['ltr', 'dl', f, e] / ordering_count_sum_left
      p_l_r_dr = phrase_based_reorderings_counter['ltr', 'dr', f, e] / ordering_count_sum_left

      p_r_l_m = phrase_based_reorderings_counter['rtl', 'm', f, e] / ordering_count_sum_right
      p_r_l_s = phrase_based_reorderings_counter['rtl', 's', f, e] / ordering_count_sum_right
      p_r_l_dl = phrase_based_reorderings_counter['rtl', 'dl', f, e] / ordering_count_sum_right
      p_r_l_dr = phrase_based_reorderings_counter['rtl', 'dr', f, e] / ordering_count_sum_right

      print("{} ||| {} ||| {} {} {} {} {} {} {} {}".format(f, e, p_l_r_m, p_l_r_s, p_l_r_dl, p_l_r_dr, p_r_l_m, p_r_l_s, p_r_l_dl, p_r_l_dr))

if __name__ == '__main__':
  main()
