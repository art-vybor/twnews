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


# APPLY
На вход:
    модель и набор текстов.
        модель задаётся: P, wm, dim, lambda, корпус слов.
        набор текстов представляем в виде tfidf матрицы X, где столбцы - тексты, строки - слова из корпуса.
На выход:
    матрица Q
    
Псевдокод:
    PPTE <- P P^T wm
    init Q
    for each column in X:
        i <- индекс колонки
        if в столбце все нули:
            Q[:i] <- [0..0]
        else:
            строим Q[:i] как в случае с трейном модели.
            
           