WTMF on python https://github.com/kedz/wtmf


Части работы:
    поиск связей текст - текст.
        для твитов и новостей своё
        извлечение хештегов
        извлечение NER
    wtmf:
        на вход множество текстов
        1) Формирование матрицы X
            слова - строки (словарь - все слова всех текстов), тексты столбцы, в ячейках tfidf
        2) Строим матрицу W
            правило в отчёте
        3) строим "случайную модель"
            модель это матрицы P и Q
        4) строим итеративный процеcc приближающий P и Q
        выход P и Q
    wtmf-g:
        меняем итеративный процесс с добавлением связей текст-текст

# install jupiter
http://bikulov.org/blog/2015/11/07/install-jupyter-notebook-and-scientific-environment-in-ubuntu-14-dot-04-with-python-3/

#install ntlk
sudo python -m nltk.downloader -d /usr/local/share/nltk_data stopwords
sudo python -m nltk.downloader -d /usr/local/share/nltk_data punkt
sudo python -m nltk.downloader -d /usr/local/share/nltk_data wordnet