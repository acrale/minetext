# -*- coding: latin-1 -*-
import re
import nltk
from nltk.tag import UnigramTagger
from nltk.corpus.reader import TaggedCorpusReader
from nltk.tokenize import PunktWordTokenizer
from nltk import RegexpParser
from nltk.corpus import stopwords
from nltk.tokenize.regexp import WhitespaceTokenizer
global corpus, sent_tags, tagger

# corpus = TaggedCorpusReader('/root/adail/python/names',r'.*\.txt',word_tokenizer=PunktWordTokenizer(),sep="_") PATH no linux
corpus = TaggedCorpusReader('C:/Users/jose.adail/workspace/TextProcessor/names', r'.*\.txt', word_tokenizer=WhitespaceTokenizer(), sep="_")
name_tags = corpus.tagged_sents()  # Recebe as senten�as marcadas com POS_Tags.
tagger = UnigramTagger(name_tags)  # UnigramTagger � treinado com essas senten�as marcadas que o s�o repassadas.

class RegexpReplacer(object):
   def __init__(self):
      self.replacement_patterns = [(r"'",''),(r'#','hash'),(r'no','no_'),(r'not','not_'),(r'RT ',''),(r'rs[rs]+','rs'),(r'ha[ha]+','haha'),(r's[s]+','sxs'),(r'r[r]+','rxr'),(r'a[a]+','aqa'),(r'e[e]+','eqe'),
                                   (r'o[o]+','oqo'),(r'tt','tqt'),(r'ff','fqf'),(r'dd','dqd'),(r'mm','mqm'),(r'nn','nqn'),(r'pp','pqp'),(r'gg','gqg'),(r'ff','fqf'),(r'll','lql'),
                                   (r'cc','cqc'),(r'[\W\d\_]',' ')]
   # Para cada emoticon e outras express�es mapeadas nas regex encontradas em replacement_patterns, realizar substitui��o.
   def replaceEmoticon(self, text):
      for r, s in self.replacement_patterns:
         text = re.sub(r, s, text)
      return text

class TextCleaner(object):
   def __init__(self):
      self.repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
      self.repl = r'\1\2\3'
      self.tokenizer = WhitespaceTokenizer()
      self.cached_stopwords = stopwords.words('english')
      self.ascii_replace = [('�', 'a'), ('�', 'a'), ('�', 'a'), ('�', 'a'), ('�', 'e'), ('�', 'e'), ('�', 'e'), ('�', 'i'), ('�', 'o'), ('�', 'o'), ('�', 'o'), ('�', 'o'), ('�', 'u'),
                 ('�', 'c'), ('�', 'a'), ('�', 'e'), ('�', 'i'), ('�', 'o'), ('�', 'u'), ('�', 'a'), ('�', 'a'), ('�', 'a'), ('�', 'a'), ('�', 'e'), ('�', 'e'), ('�', 'e'),
                 ('�', 'i'), ('�', 'o'), ('�', 'o'), ('�', 'o'), ('�', 'o'), ('�', 'u'), ('�', 'c')]
      self.link_patterns = [('http'), ('www'), ('w3c')]
      self.digraph = [(r'hash','#'),(r'rxr','rr'),(r'sxs','ss'),(r'aqa','aa'),(r'eqe','ee'),(r'oqo','oo'),(r'fqf','ff'),(r'gqg','gg'),(r'cqc','cc'),(r'dqd','dd'),
          (r'mqm','mm'),(r'nqn','nn'),(r'pqp','pp'),(r'dqd','dd'),(r'tqt','tt'),(r'fqf','ff'),(r'lql','ll')]
      
   # Remover caracteres repetidos seguidamente, para que o modelo n�o seja prejudicado por falta de padr�o na escrita.
   def removeRepChar(self, word):
      repl_word = self.repeat_regexp.sub(self.repl, word)
      if repl_word != word:
         return self.removeRepChar(repl_word)
      else:
         return repl_word


   # Substituir caracateres acentuados por caracteres sem acentos.
   def removeAccent(self, text):
      para = text
      for (lat, asc) in self.ascii_replace:
         para = para.replace(lat, asc)
      return para

   # Remover stopwords dos textos.
   def removeStopwords(self, text):
      text = ' '.join([word for word in text.split() if word not in self.cached_stopwords])
      return text

   # Remover links dos textos.
   def removeLinks(self, text):
      for l in self.link_patterns:
         text = text.split(l, 1)[0]
      return text

   # Reescrever os digrafos na sua forma original. Exemplo: rxr -> rr
   def normalizeDigraph(self, text):
      for a, d in self.digraph:
         text = re.sub(a, d, text)
      return text

   # Reescrever algumas palavras para dar melhor sem�ntica e legibilidade aos resultados do modelo.
   def normalizeText(self, text):
      for a, b in self.normal:
         text = re.sub(a, b, text)
      return text
   
   def removeOneCharacter(self, text):
      text = self.tokenizeWords(text)
      for i in range(len(text)):
         if len(text[i]) <= 2:
            text[i] = ''
      return ' '.join(text)

   def tokenizeWords(self, text):
      text = self.tokenizer.tokenize(text)
      return text
      
class NamedEntity(object):
   def __init__(self):
      self.tokenizer = WhitespaceTokenizer()
        
   # Remover do texto duas ou mais palavras pr�prias em sequ�ncia.
   def removeName(self, text):
      i = 0
      j = 1
      words = text.split()
      lim = len(words) - 1
      while j <= lim:
         if not words[i].isupper() and not words[i].islower():
            if not words[j].isupper() and not words[j].islower():
               words[i] = words[i].replace(words[i], "")
               words[j] = words[j].replace(words[j], "")
         i += 1
         j += 1
      words = ' '.join(words)
      return words

   # Remover nomes pr�prios dos textos. Para isso, recebe o texto, que em seguida � dividido em palavras, que posteriormente recebem POS_Tags.
   # Para cada palavra/tag, � verificado se a tag nao corresponde a de nome proprio 'NPROP'. Ao final, forma-se um texto sem palavras com tags
   # 'NPROP', sendo assim retornado pelo m�todo.
   def removePersonName(self, text):
      final_text = ''
      tokenized_text = self.tokenizeWords(text)
      tagged_text = self.tagWords(tokenized_text)
      for w, t in tagged_text:
         if t != "NPROP":
            final_text = final_text + ''.join(w) + ' '
      return final_text

   # Remover men��es de usu�rios de tweets. Os mesmos s�o identificados pelo caractere '@'. O texto original � repassado ao m�todo e divido em palavras,
   # em seguida. Ap�s isso, � verificado para cada palavra do texto se a mesma se inicia com o caractere '@'. Caso sim, essa palavra � removida do texto.
   # Ao final, o texto � retornado, sem os nomes de usu�rios.
   def removeTwitterUsername(self, text):
      text = text.split()
      for w in text:
         if w[0] == '@':
            text.remove(w)
      return ' '.join(text)

   # Marcar as palavras de uma senten�a tokenizada com POS_Tags. O texto � repassado ao m�todo tag da classe UnigramTagger, que marca as palavras do texto com
   # POS_Tags. Retorna uma lista com palavras/tags. 
   def tagWords(self, tokenized_text):
      tagged_words = tagger.tag(tokenized_text)
      return tagged_words

   # Desenhar arvore que destaca um determinado padr�o gramatical do texto. 
   def drawNamedEntityTree(self, text):
      tokenized_text = tokenizer.tokenize(text)
      tagged_text = self.tagWords(tokenized_text)
      grammar = "ENT: {<PESSOA>*}"
      cp = RegexpParser(grammar)
      res = cp.parse(tagged_text)
      res.draw()

   # Tokenizar senten�as em palavras. Retorna uma lista com as palavras que formam o texto.
   def tokenizeWords(self, text):
      text = self.tokenizer.tokenize(text)
      return text


