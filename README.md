# twnews
BMSTU graduate work

http://techcrunch.com/2013/08/19/twitter-related-headlines/

server: 46.101.228.8
connect: ssh 46.101.228.8

Работа по семантической схожести сообщений твиттера:
https://github.com/cocoxu/SemEval-PIT2015

Код WTMF и Linking tweets to news
http://www.cs.columbia.edu/~weiwei/code.html

LSA: https://ru.wikipedia.org/wiki/%D0%9B%D0%B0%D1%82%D0%B5%D0%BD%D1%82%D0%BD%D0%BE-%D1%81%D0%B5%D0%BC%D0%B0%D0%BD%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7



Идеи для улучшения:
* прикрутить word2vec
* Немного на покопать: Note that there are some false positive named entities detected such as apple. We plan to address removing noisy named entities and hashtags in future work
* mine hashtags (в статье есть ссылка на соответствующую работу)


Изменения для консьюмера:
собирать resolve_url который отдаёт twitter
собирать больше новостных источников
собирать английские твиты
собирать английские новости
собирать хештеги


https://xyclade.github.io/MachineLearning/

#https://pythonprogramming.net/stop-words-nltk-tutorial/?completed=/tokenizing-words-sentences-nltk-tutorial/

Как установить numpy и scipy
https://hunseblog.wordpress.com/2014/09/15/installing-numpy-and-openblas/


Ускорение формулы 4 из статьи WTMF, примерное время за 100 итераций:
В одну итерацию входит перемножение нескольких больших матриц и взятие обратной матрицы.

||что сделали||текущее время||во сколько раз стало быстрее||
|наивная реализация|205с|1|
|перемножение с помощью OpenBlass|55с|3.73|
|вынесение общих множителей|15.15с|3.63|
|переход к работе с sparse матрицами|0.75с|20.2|
|удаление ненужного приведения матрицы к python list|0.63c|1.21|

итого пришли к коду, который работает в 325 раз быстрее наивной реализации
