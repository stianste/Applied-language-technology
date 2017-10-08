import requests
import os

### Parameters: 
read_locally = True # Either read files locally or from the internet


english_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.en"
german_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.de"
word_alignment_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.aligned"

dataset_directory = 'data'
english_dataset_filename = os.path.join(dataset_directory, 'file.en')
german_dataset_filename = os.path.join(dataset_directory, 'file.de')
word_alignment_dataset_filename = os.path.join(dataset_directory, 'file.aligned')

def read_german_sentences():
  if read_locally:
    german_dataset = _read_file(german_dataset_filename)
  else:
    german_dataset = _read_online_file(german_dataset_url)
  
  german_dataset = german_dataset.splitlines()
  return german_dataset

def read_english_sentences():
  if read_locally:
    english_dataset = _read_file(english_dataset_filename)
  else:
    english_dataset = _read_online_file(english_dataset_url)
  
  english_dataset = english_dataset.splitlines()
  return english_dataset

def read_word_alignments():
  if read_locally:
    word_alignment_dataset = _read_file(word_alignment_dataset_filename)
  else:
    word_alignment_dataset = _read_online_file(word_alignment_dataset_url)

  word_alignment_dataset = word_alignment_dataset.splitlines()
  word_alignment_dataset = [[_string_to_tupple(x) for x in alignment.split()] for alignment in word_alignment_dataset]

  return word_alignment_dataset

def read_data():
  english_sentences = read_english_sentences()
  foreign_sentences = read_german_sentences()
  global_alignments = read_word_alignments()

  return english_sentences, foreign_sentences, global_alignments

def _read_file(filename):
  with open(filename, 'r') as f:
    data = f.read()
  return data

def _read_online_file(url):
  data = requests.get(url).text
  return data

# Convert string 'a-b' to tuple (b, a)
# So we switch around the order
def _string_to_tupple(s):
  numbers = s.split('-')
  return (int(numbers[1]), int(numbers[0]))
