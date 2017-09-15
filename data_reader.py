import requests

english_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.en"
german_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.de"
word_alignment_dataset_url = "https://staff.fnwi.uva.nl/m.fadaee/ALT/file.word_alignment"

english_dataset = requests.get(english_dataset_url).text
german_dataset = requests.get(german_dataset_url).text
english_dataset = requests.get(english_dataset_url).text

def _read_sentences(dataset):
  return dataset.splitlines()

def read_english_sentences():
  return _read_sentences(english_dataset)

def read_german_sentences():
  return _read_sentences(german_dataset)

def read_word_alignment_sentences():
  return _read_sentences(word_alignment_dataset)
