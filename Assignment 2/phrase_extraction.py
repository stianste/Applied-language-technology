import data_reader
from collections import Counter
import matplotlib.pyplot as plt

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
        # of these phrases in respectively the English and foreign sentence.
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
  word_based_reorderings_counter = Counter()
  ordering_amount_per_f_phrase_length_counter = Counter()
  ordering_amount_per_e_phrase_length_counter = Counter()

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
      base_pair_f_len = len(base_pair_f.split(' '))
      base_pair_e_len = len(base_pair_e.split(' '))

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

            ordering_amount_per_f_phrase_length_counter.update([('m', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('m', base_pair_e_len)])

            if (0, 0) in target_pair_sub_alignments:
              word_based_reorderings_counter.update([('ltr', 'm', base_pair_f, base_pair_e)])
            else:
              word_based_reorderings_counter.update([('ltr', 'dr', base_pair_f, base_pair_e)])

          elif target_pair_f_end == base_pair_f_start - 1:
            phrase_based_reorderings_counter.update([('ltr','s', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','s', target_pair_f, target_pair_e)])

            ordering_amount_per_f_phrase_length_counter.update([('s', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('s', base_pair_e_len)])

            if (0, target_pair_f_last_index) in target_pair_sub_alignments:
              word_based_reorderings_counter.update([('ltr', 's', base_pair_f, base_pair_e)])
            else:
              word_based_reorderings_counter.update([('ltr', 'dl', base_pair_f, base_pair_e)])

          elif target_pair_f_start > base_pair_f_end:
            phrase_based_reorderings_counter.update([('ltr','dr', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','dr', target_pair_f, target_pair_e)])

            ordering_amount_per_f_phrase_length_counter.update([('dr', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('dr', base_pair_e_len)])

            word_based_reorderings_counter.update([('ltr', 'dr', base_pair_f, base_pair_e)])

          elif target_pair_f_end < base_pair_f_start:
            phrase_based_reorderings_counter.update([('ltr','dl', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','dl', target_pair_f, target_pair_e)])

            ordering_amount_per_f_phrase_length_counter.update([('dl', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('dl', base_pair_e_len)])

            word_based_reorderings_counter.update([('ltr', 'dl', base_pair_f, base_pair_e)])

        # Word-based (right-to-left)
        # Check whether the target block ends where the base block begins
        if target_pair_e_end == base_pair_e_start - 1:
          # Check whether the target block is monotone
          if target_pair_f_end == base_pair_f_start - 1:
            # Check whether an alignment in this block is monotone
            if (target_pair_e_last_index, target_pair_f_last_index) in target_pair_sub_alignments:
              word_based_reorderings_counter.update([('rtl', 'm', base_pair_f, base_pair_e)])
            else:
              word_based_reorderings_counter.update([('rtl', 'dr', base_pair_f, base_pair_e)])

          # Check whether the target block is on the left side of the base block
          # (which makes it discontinuous right for the right-to-left model)
          elif (target_pair_f_end < base_pair_f_start):
            word_based_reorderings_counter.update([('rtl', 'dr', base_pair_f, base_pair_e)])

          # Check wether the block is swapped
          elif target_pair_f_start == base_pair_f_end + 1:
            # Check wether there is also a word alignment that is swapped
            if (target_pair_e_last_index, 0) in target_pair_sub_alignments:
              word_based_reorderings_counter.update([('rtl', 's', base_pair_f, base_pair_e)])
            else:
              word_based_reorderings_counter.update([('rtl', 'dl', base_pair_f, base_pair_e)])

          # Check wether the target block is on the right side of the base block (making it discontinuous left in the rtl model)
          elif (target_pair_f_start > base_pair_f_end):
            word_based_reorderings_counter.update([('rtl', 'dl', base_pair_f, base_pair_e)])

  return phrase_based_reorderings_counter, word_based_reorderings_counter, ordering_amount_per_f_phrase_length_counter, ordering_amount_per_e_phrase_length_counter, global_phrase_pairs

def plot_histograms_orientation_vs_phrase_length(ordering_amount_per_f_phrase_length_counter, ordering_amount_per_e_phrase_length_counter):
  def plot_subplot(ordering_amount_per_phrase_length_counter, ax):
    x_multi = ([1,2,3,4,5,6,7], [1,2,3,4,5,6,7], [1,2,3,4,5,6,7], [1,2,3,4,5,6,7])

    counts_m = [ordering_amount_per_phrase_length_counter['m', i] for i in range(1, 8)]
    counts_s = [ordering_amount_per_phrase_length_counter['s', i] for i in range(1, 8)]
    counts_dl = [ordering_amount_per_phrase_length_counter['dl', i] for i in range(1, 8)]
    counts_dr = [ordering_amount_per_phrase_length_counter['dr', i] for i in range(1, 8)]

    list_of_counts = [counts_m, counts_s, counts_dl, counts_dr]

    counts1_total = sum([count[0] for count in list_of_counts])
    counts2_total = sum([count[1] for count in list_of_counts])
    counts3_total = sum([count[2] for count in list_of_counts])
    counts4_total = sum([count[3] for count in list_of_counts])
    counts5_total = sum([count[4] for count in list_of_counts])
    counts6_total = sum([count[5] for count in list_of_counts])
    counts7_total = sum([count[6] for count in list_of_counts])

    ws =[counts1_total, counts2_total, counts3_total, counts4_total, counts5_total, counts6_total, counts7_total]
    prob_m = [counts_m[i] / ws[i] for i in range(7)]
    prob_s = [counts_s[i] / ws[i] for i in range(7)]
    prob_dl = [counts_dl[i] / ws[i] for i in range(7)]
    prob_dr = [counts_dr[i] / ws[i] for i in range(7)]

    ax.hist(x_multi, bins=range(1,8), weights=(prob_m, prob_s, prob_dl, prob_dr), histtype='bar', label=('mono', 'swap', 'disc. l', 'disc. r'))

  fig, (ax1, ax2) = plt.subplots(1, 2)
  plot_subplot(ordering_amount_per_f_phrase_length_counter, ax1)
  ax1.set_xlabel('Foreign phrase length')
  ax1.set_ylabel(r'$p_{l \rightarrow r}(o | len_f)$')
  ax1.set_title(r'$p_{l \rightarrow r}(o)$ vs. foreign phrase length')
  plot_subplot(ordering_amount_per_e_phrase_length_counter, ax2)
  ax2.set_xlabel('English phrase length')
  ax2.set_ylabel(r'$p_{l \rightarrow r}(o | len_e)$')
  ax2.set_title(r'$p_{l \rightarrow r}(o)$ vs. English phrase length')
  ax2.legend()
  plt.show()

def main():

  ################################################################
  ### Initialize variables and create phrase pairs with counts ###
  ################################################################

  english_sentences, foreign_sentences, global_alignments = read_data()

  # english_sentences = ["en1 en2 en3 en4 en5 en6"]
  # foreign_sentences = ["f1 f2 f3 f4 f5 f6 f7"]
  # global_alignments = [[(0, 0), (1, 1), (2, 1), (3, 4), (3, 5), (4, 2), (4, 3), (5, 6)]]

  phrase_based_reorderings_counter, word_based_reorderings_counter, \
    ordering_amount_per_f_phrase_length_counter, ordering_amount_per_e_phrase_length_counter, phrase_pairs = \
      count_reorderings(10, english_sentences, foreign_sentences, global_alignments)

  plot_histograms_orientation_vs_phrase_length(ordering_amount_per_f_phrase_length_counter, ordering_amount_per_e_phrase_length_counter)

  for (f, e) in phrase_pairs:
    phrase_ordering_count_sum_right = 0
    phrase_ordering_count_sum_left = 0
    word_ordering_count_sum_right = 0
    word_ordering_count_sum_left = 0

    for o in ['m', 's', 'dl', 'dr']:
      phrase_ordering_count_sum_right += phrase_based_reorderings_counter[('rtl', o, f, e)]
      phrase_ordering_count_sum_left += phrase_based_reorderings_counter[('ltr', o, f, e)]
      word_ordering_count_sum_right += word_based_reorderings_counter[('rtl', o, f, e)]
      word_ordering_count_sum_left += word_based_reorderings_counter[('ltr', o, f, e)]

    phrase_p_l_r_m = phrase_based_reorderings_counter['ltr', 'm', f, e] / max(phrase_ordering_count_sum_left, 1)
    phrase_p_l_r_s = phrase_based_reorderings_counter['ltr', 's', f, e] / max(phrase_ordering_count_sum_left, 1)
    phrase_p_l_r_dl = phrase_based_reorderings_counter['ltr', 'dl', f, e] / max(phrase_ordering_count_sum_left, 1)
    phrase_p_l_r_dr = phrase_based_reorderings_counter['ltr', 'dr', f, e] / max(phrase_ordering_count_sum_left, 1)

    phrase_p_r_l_m = phrase_based_reorderings_counter['rtl', 'm', f, e] / max(phrase_ordering_count_sum_right, 1)
    phrase_p_r_l_s = phrase_based_reorderings_counter['rtl', 's', f, e] / max(phrase_ordering_count_sum_right, 1)
    phrase_p_r_l_dl = phrase_based_reorderings_counter['rtl', 'dl', f, e] / max(phrase_ordering_count_sum_right, 1)
    phrase_p_r_l_dr = phrase_based_reorderings_counter['rtl', 'dr', f, e] / max(phrase_ordering_count_sum_right, 1)

    # print("### Phrase based ###")
    # print("{} ||| {} ||| {} {} {} {} {} {} {} {}\n".format(f, e, phrase_p_l_r_m, phrase_p_l_r_s, phrase_p_l_r_dl, \
    #     phrase_p_l_r_dr, phrase_p_r_l_m, phrase_p_r_l_s, phrase_p_r_l_dl, phrase_p_r_l_dr))

    word_p_l_r_m = word_based_reorderings_counter['ltr', 'm', f, e] / max(word_ordering_count_sum_left, 1)
    word_p_l_r_s = word_based_reorderings_counter['ltr', 's', f, e] / max(word_ordering_count_sum_left, 1)
    word_p_l_r_dl = word_based_reorderings_counter['ltr', 'dl', f, e] / max(word_ordering_count_sum_left, 1)
    word_p_l_r_dr = word_based_reorderings_counter['ltr', 'dr', f, e] / max(word_ordering_count_sum_left, 1)

    word_p_r_l_m = word_based_reorderings_counter['rtl', 'm', f, e] / max(word_ordering_count_sum_right, 1)
    word_p_r_l_s = word_based_reorderings_counter['rtl', 's', f, e] / max(word_ordering_count_sum_right, 1)
    word_p_r_l_dl = word_based_reorderings_counter['rtl', 'dl', f, e] / max(word_ordering_count_sum_right, 1)
    word_p_r_l_dr = word_based_reorderings_counter['rtl', 'dr', f, e] / max(word_ordering_count_sum_right, 1)

    # print("### Word based ###")
    # print("{} ||| {} ||| {} {} {} {} {} {} {} {}\n".format(f, e, word_p_l_r_m, word_p_l_r_s, word_p_l_r_dl, \
    #     word_p_l_r_dr, word_p_r_l_m, word_p_r_l_s, word_p_r_l_dl, word_p_r_l_dr))

if __name__ == '__main__':
  main()
