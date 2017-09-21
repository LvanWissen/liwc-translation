#  An Electronic Translation of the LIWC Dictionary into Dutch

## Abstract

LIWC (Linguistic Inquiry and Word Count) is a text analysis tool developed by social psychologists but now widely used outside of psychology. The tool counts words in certain categories, as defined in an accompanying (English-language) dictionary. The most recent version of the dictionary was published in 2015. We present a pipeline for the automatic translation of LIWC dictionaries into Dutch. We first make an automated translation of the LIWC 2007 version and compare it to the manually translated version of this dictionary. Then we use the pipeline to translate the LIWC 2015 dictionary. We also present the provisional Dutch LIWC 2015 dictionary that results from the pipeline. Although a number of categories require further work, the dictionary should be usable for most research purposes. 

The full paper can be found in the proceeding of eLex2017:

Van Wissen, Leon and Peter Boot (2017). "An Electronic Translation of the LIWC Dictionary into Dutch". In: Proceedings of eLex 2017 conference, Electronic lexicography in the 21st century, 19-21 September 2017, Leiden. ([pdf](https://elex.link/elex2017/wp-content/uploads/2017/09/paper43.pdf))

## Contact
We invite researchers in psychology, digital humanities and other fields to validate the
usability of the dictionary in the context of practical research. If you would like to use this dictionary for your own research, please contact [Peter Boot](mailto:peter.boot@huygens.knaw.nl).

---

## Pipeline

#### Python packages

see `requirements.txt`, or:

* scipy
* pandas
* nltk
* requests
* matplotlib
* docopt
* numpy
* treetaggerwrapper
* LIWCtools
