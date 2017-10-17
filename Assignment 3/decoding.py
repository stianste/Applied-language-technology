import data_reader
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

# Initializa some container variables which we will use to calculate useful statistics
phrase_based_reorderings_counter = Counter() # Counts the number of reorderings occurring in the entire corpus per phrase pair (phrase-based)
word_based_reorderings_counter = Counter()   # Counts the number of reorderings occurring in the entire corpus per phrase pair (word-based)
phrase_orderings_counter = Counter() # Counts the total number of reorderings in the corpus (phrase-based)
word_orderings_counter = Counter()   # Counts the total number of reorderings in the corpus (word-based)
ordering_amount_per_f_phrase_length_counter = Counter() # Counts the total number of reorderings in the corpus, per f-phrase length (phrase-based)
ordering_amount_per_e_phrase_length_counter = Counter() # Counts the total number of reorderings in the corpus, per e-phrase length (phrase-based)
phrase_pairs = set() # The set of all encountered (f,e) phrase pairs in the corpus

# Set the maximum length of the phrases extracted (both e and f)
MAX_PHRASE_LEN = 7

# Perform the phrase extraction algorithm for one sentence pair.
# Based on pseudocode from Section 5.2.3 of "Philipp Koehn - Statistical machine translation"
# If either f or e exceeds 'MAX_PHRASE_LEN', the phrase pair is discarded.
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

        if fe < fs + MAX_PHRASE_LEN:
          E.add((foreign_phrase, english_phrase, sub_alignments, (fs, fe), (e_start, e_end)))

        fe += 1

        if fe in f_aligned or fe == len(foreign_sentence_split) or fe > fs + MAX_PHRASE_LEN:
          break

      fs -= 1
      if fs in f_aligned or fs == -1:
        break

    return E

  phrase_pairs_in_sentence = set()

  f_aligned = [f for (e, f) in A]

  for e_start in range(len(english_sentence_split)):
    for e_end in range(e_start, min(e_start + MAX_PHRASE_LEN, len(english_sentence_split))):
      f_start, f_end = len(foreign_sentence_split)-1, -1

      for (e_pos, f_pos) in A:
        if e_start <= e_pos and e_pos <= e_end:
          f_start = min(f_pos, f_start)
          f_end = max(f_pos, f_end)

      phrase_pairs_in_sentence.update(extract(f_start, f_end, e_start, e_end))

  return phrase_pairs_in_sentence

# Count the total number of occurring reorderings for all models (left-to-right, right-to-left and phrase-based, word-based)
def count_reorderings(n, english_sentences, foreign_sentences, global_alignments):
  print("Counting reorderings for {} sentences... (total number of sentences is {})".format(n, len(english_sentences)))

  for i in range(n):
    if i % 1000 == 0:
      print("Processing sentence {}/{}".format(i, n))

    # Extract sentence pair from corpus
    foreign_sentence = foreign_sentences[i]
    english_sentence = english_sentences[i]
    alignments = global_alignments[i]

    foreign_sentence_split = foreign_sentence.split(' ')
    english_sentence_split = english_sentence.split(' ')

    # Extract all phrase pairs for this sentece pair.
    # Output is a list of tuples, where each tuple consists of the following elements:
    # (f, e, sub_alignments, (f_start, f_end), (e_start, e_end))
    phrase_pairs_in_sentence = phrase_extraction_algorithm(foreign_sentence_split, english_sentence_split, alignments)

    # We perform a double for-loop to consider each base-target pair of phrase-pairs.
    for phrase_pair_base in phrase_pairs_in_sentence:
      base_pair_f                         = phrase_pair_base[0]
      base_pair_e                         = phrase_pair_base[1]
      base_pair_f_start, base_pair_f_end  = phrase_pair_base[3]
      base_pair_e_start, base_pair_e_end  = phrase_pair_base[4]
      base_pair_f_len = len(base_pair_f.split(' '))
      base_pair_e_len = len(base_pair_e.split(' '))

      # Add the base phrase-pair to a global collection of all found phrase-pairs in the corpus
      phrase_pairs.update([(base_pair_f, base_pair_e)])

      for phrase_pair_target in phrase_pairs_in_sentence:
        target_pair_f                           = phrase_pair_target[0]
        target_pair_e                           = phrase_pair_target[1]
        target_pair_sub_alignments              = phrase_pair_target[2]
        target_pair_f_start, target_pair_f_end  = phrase_pair_target[3]
        target_pair_e_start, target_pair_e_end  = phrase_pair_target[4]
        target_pair_f_last_index = len(target_pair_f.split(' ')) - 1
        target_pair_e_last_index = len(target_pair_e.split(' ')) - 1

        # First we consider the left-to-right reorderings for both the word-based and phrase-based model.
        # However, since for the phrase-based model there is a symmetric relation between LtR and RtL
        # We can count the right-to-left counts for the phrase-based model at the same time
        # First we check whether the target phrase-pair starts right after the base in the english sentence.
        if target_pair_e_start == base_pair_e_end + 1:

          # We check wether the target starts right after the base in the foreign sentence,
          # making it a monotone reordering
          if target_pair_f_start == base_pair_f_end + 1:
            phrase_based_reorderings_counter.update([('ltr', 'm', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','m', target_pair_f, target_pair_e)])
            phrase_orderings_counter.update(['m'])

            ordering_amount_per_f_phrase_length_counter.update([('m', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('m', base_pair_e_len)])

            # We check wether there is a word-alignment of the first e and f word in the target
            if (0, 0) in target_pair_sub_alignments:
              word_based_reorderings_counter.update([('ltr', 'm', base_pair_f, base_pair_e)])
              word_orderings_counter.update(['m'])
            else:
              word_based_reorderings_counter.update([('ltr', 'dr', base_pair_f, base_pair_e)])
              word_orderings_counter.update(['dr'])

          # Check wether the target comes right before the base in the foreign sentence (making it a swap)
          elif target_pair_f_end == base_pair_f_start - 1:
            phrase_based_reorderings_counter.update([('ltr','s', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','s', target_pair_f, target_pair_e)])
            phrase_orderings_counter.update(['s'])

            ordering_amount_per_f_phrase_length_counter.update([('s', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('s', base_pair_e_len)])

            # Check wether the first english word and last foreign word in target are aligned.
            if (0, target_pair_f_last_index) in target_pair_sub_alignments:
              word_based_reorderings_counter.update([('ltr', 's', base_pair_f, base_pair_e)])
              word_orderings_counter.update(['s'])
            else:
              word_based_reorderings_counter.update([('ltr', 'dl', base_pair_f, base_pair_e)])
              word_orderings_counter.update(['dl'])

          # Check wether the target comes after the base in the foreign sentence (disc. right)
          elif target_pair_f_start > base_pair_f_end:
            phrase_based_reorderings_counter.update([('ltr','dr', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','dr', target_pair_f, target_pair_e)])
            phrase_orderings_counter.update(['dr'])

            word_based_reorderings_counter.update([('ltr', 'dr', base_pair_f, base_pair_e)])
            word_orderings_counter.update(['dr'])

            ordering_amount_per_f_phrase_length_counter.update([('dr', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('dr', base_pair_e_len)])

          # Check wether the target comes before the base in the foreign sentence (disc. left)
          elif target_pair_f_end < base_pair_f_start:
            phrase_based_reorderings_counter.update([('ltr','dl', base_pair_f, base_pair_e)])
            phrase_based_reorderings_counter.update([('rtl','dl', target_pair_f, target_pair_e)])
            phrase_orderings_counter.update(['dl'])

            word_based_reorderings_counter.update([('ltr', 'dl', base_pair_f, base_pair_e)])
            word_orderings_counter.update(['dl'])

            ordering_amount_per_f_phrase_length_counter.update([('dl', base_pair_f_len)])
            ordering_amount_per_e_phrase_length_counter.update([('dl', base_pair_e_len)])

        # Next we count reorderings for the right-to-left model. Since we already did this
        # for the phrase-based model, we only need to consider the word-based model.
        # We consider all target blocks that end where the base block begins
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

  print("All reorderings statistics have been estimated\n")

# Show a bar plot of the average probability of each reorderings
def show_reorderings_probabilities():
  def plot_reorderings_probabilities_per_model(reorderings_counter):
    orderings = ['Mono', 'Swap', 'Disc. l', 'Disc. r']

    m_count = reorderings_counter['m']
    s_count = reorderings_counter['s']
    dl_count = reorderings_counter['dl']
    dr_count = reorderings_counter['dr']
    total_count = sum(reorderings_counter.values())

    # print("m: {}, s: {}, dl: {}, dr: {}".format(m_count/total_count, s_count/total_count, dl_count/total_count, dr_count/total_count))

    x = np.arange(4)
    plt.bar(x, height=[m_count/total_count, s_count/total_count, dl_count/total_count, dr_count/total_count], alpha=0.5)
    plt.xticks(x, orderings);
    plt.xlabel("Orientation type")
    plt.ylabel("Probability of occurring")

  plot_reorderings_probabilities_per_model(phrase_orderings_counter)
  plt.title("Probabilities of orientations for phrase-based")
  plt.show()
  plot_reorderings_probabilities_per_model(word_orderings_counter)
  plt.title("Probabilities of orientations for word-based")
  plt.show()

# Compare the total average reorderings probabilities for the word-based and phrase-based models.
def show_reorderings_comparison_histogram():
  orderings = ['Mono', 'Swap', 'Disc. l', 'Disc. r']

  phrase_m_count = phrase_orderings_counter['m']
  phrase_s_count = phrase_orderings_counter['s']
  phrase_dl_count = phrase_orderings_counter['dl']
  phrase_dr_count = phrase_orderings_counter['dr']
  phrase_total_count = sum(phrase_orderings_counter.values())

  word_m_count = word_orderings_counter['m']
  word_s_count = word_orderings_counter['s']
  word_dl_count = word_orderings_counter['dl']
  word_dr_count = word_orderings_counter['dr']
  word_total_count = sum(word_orderings_counter.values())

  x = [phrase_m_count/phrase_total_count, phrase_s_count/phrase_total_count, phrase_dl_count/phrase_total_count, phrase_dr_count/phrase_total_count]
  y = [word_m_count/word_total_count, word_s_count/word_total_count, word_dl_count/word_total_count, word_dr_count/word_total_count]

  x_range = [i for i in range(0, 4)]
  y_range = [i + 0.2 for i in range(0, 4)] # Add some displacement for easier reading

  plt.bar(x_range, height=x, label='Phrase based', alpha=0.5, color='red')
  plt.bar(y_range, height=y, label='Word based', alpha=0.5)
  plt.xticks(x_range, orderings)
  plt.xlabel("Orientation type")
  plt.ylabel("Probability of occurring")
  plt.legend(loc='upper right')
  plt.title("Comparison of orientation frequencies for word- and phrase based models")
  plt.show()

# Show histograms of average probabilities of reordering orientations split for all possible lenghts of either e or f phrase in the LtR phrase-based model.
def show_histograms_orientation_vs_phrase_length():
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

    ax.hist(x_multi, bins=7, weights=(prob_m, prob_s, prob_dl, prob_dr), histtype='bar', label=('mono', 'swap', 'disc. l', 'disc. r'))

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

# Write the output (reordering probabilities) of the phrase-based model and word-based model to different files.
def output_reordering_statistics():
  def write_statistics_to_file(reorderings_counter, output_filename):
    print("Writing reordering probabilities to {}...".format(output_filename))
    output_file = open(output_filename, 'w')

    for (f, e) in phrase_pairs:
      # First calculate the total amount of reorderings for the phrase pair
      total_ordering_count_rtl = 0
      total_ordering_count_ltr = 0
      for orientation in ['m', 's', 'dl', 'dr']:
        total_ordering_count_rtl += reorderings_counter[('rtl', orientation, f, e)]
        total_ordering_count_ltr += reorderings_counter[('ltr', orientation, f, e)]

      # Calculate the probabilities for each reordering. First for the left-to-right model, then right-to-left
      prob_ltr_m = reorderings_counter['ltr', 'm', f, e] / max(total_ordering_count_ltr, 1)
      prob_ltr_s = reorderings_counter['ltr', 's', f, e] / max(total_ordering_count_ltr, 1)
      prob_ltr_dl = reorderings_counter['ltr', 'dl', f, e] / max(total_ordering_count_ltr, 1)
      prob_ltr_dr = reorderings_counter['ltr', 'dr', f, e] / max(total_ordering_count_ltr, 1)

      prob_rtl_m = reorderings_counter['rtl', 'm', f, e] / max(total_ordering_count_rtl, 1)
      prob_rtl_s = reorderings_counter['rtl', 's', f, e] / max(total_ordering_count_rtl, 1)
      prob_rtl_dl = reorderings_counter['rtl', 'dl', f, e] / max(total_ordering_count_rtl, 1)
      prob_rtl_dr = reorderings_counter['rtl', 'dr', f, e] / max(total_ordering_count_rtl, 1)

      output_string = "{} ||| {} ||| {} {} {} {} {} {} {} {}\n".format(f, e, prob_ltr_m, prob_ltr_s, prob_ltr_dl, \
        prob_ltr_dr, prob_rtl_m, prob_rtl_s, prob_rtl_dl, prob_rtl_dr)

      # print(output_string)
      output_file.write(output_string)

    output_file.close()

  write_statistics_to_file(phrase_based_reorderings_counter, "output_phrase_based_model.txt")
  write_statistics_to_file(word_based_reorderings_counter, "output_word_based_model.txt")

def main():
  # Read the sentences and alignments from files. Note that we swap the alignments.
  english_sentences, foreign_sentences, global_alignments = data_reader.read_data()

  # For all sentences: Extract phrases, count reorderings and collect other useful statistics.
  count_reorderings(len(english_sentences), english_sentences, foreign_sentences, global_alignments)

  # Write the reordering statistics to files
  output_reordering_statistics()

  # Show some insightful graphs
  show_reorderings_probabilities()
  show_reorderings_comparison_histogram()
  show_histograms_orientation_vs_phrase_length()

if __name__ == '__main__':
  main()
