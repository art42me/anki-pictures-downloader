# данная программка была написана для работы с эсперанто-русским словарём. она позволяет генерировать задания
# для тестов с выбором количества ответов. так, например, можно выбрать исходный язык и язык перевода,
# указать количество заданий и количество ответов к каждому заданию. программа случайным образом выберет слова для заданий,
# распечатает в первой строке правильный ответ, а в остальных будут неправильные ответы. готовые задания заносятся в тест.

# > D:\work\python\tests\Include>python random_words.py vortoj.txt
# 1 - Russian - Esperanto
# 2 - Esperanto - Russian
# 3 - exit
# Choose a language: > 1
# Write number of questions: > 2
# Write number of answers: > 4
#
# коза; козёл
# kapro (правильный ответ)
# kapo
# fingro
# kolombo
#
# собака
# hundo (правильный ответ)
# emerito
# violino
# fablo

import random
import string
import argparse
parser = argparse.ArgumentParser(description='Write filename')
parser.add_argument('filename', type=str)  # принимаем название файла как аргумент
args = parser.parse_args()
filename = args.filename
esperanto_list = []
russian_list = []
esperanto_dictionary = {}
russian_dictionary = {}


def create_lang_lists(file):  # обрабатываем текстовый файл, разделённый тильдой, в котором язык меняется через строчку
    counter = 0
    strip_rus = '\n .,;~абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    strip_esp = string.ascii_letters + string.digits + '\n .,;~ĝŭĉĥŝŭĵ'
    with open(filename, 'r', encoding="utf-8") as words:
        for line in words:
            counter += 1
            if counter % 2 == 0:  # русско-эсперантская строка (чётная)
                esperanto_word = line.lstrip(strip_rus).rstrip('\n')
                russian_word = line.rstrip(strip_esp).lstrip('\n')
                sort_word(esperanto_word, russian_word)

            elif counter % 2 != 0:  # эсперанто-русская строка (нечётная)
                esperanto_word = line.rstrip(strip_rus).lstrip('\n')
                russian_word = line.lstrip(strip_esp).rstrip('\n')
                sort_word(esperanto_word, russian_word)


def sort_word(esperanto_word, russian_word):
    esperanto_list.append(esperanto_word)
    russian_list.append(russian_word)
    esperanto_dictionary[esperanto_word] = russian_word  # составляем есп-рус словарь
    russian_dictionary[russian_word] = esperanto_word  # составляем рус-есп словарь


def read_commands():  # обработчик команд
    while True:
        choice = int(input('\n1 - Russian - Esperanto\n2 - Esperanto - Russian\n3 - exit\nChoose a language: '))
        number_of_matches = int(input('Write number of questions: '))
        number_of_variants = int(input('Write number of answers: '))
        if choice == 1:
            current_list = esperanto_list
            current_dictionary = esperanto_dictionary
            create_word_matches(number_of_matches, number_of_variants, current_list, current_dictionary)
        elif choice == 2:
            current_list = russian_list
            current_dictionary = russian_dictionary
            create_word_matches(number_of_matches, number_of_variants, current_list, current_dictionary)
        elif choice == 3:
            exit()
        else:
            pass


def create_word_matches(number_of_matches, number_of_variants, current_list, current_dictionary):
    matches_dict = {}
    used_words = []
    for i in range(number_of_matches):
        while True:
            variants = random.choices(current_list, k=number_of_variants)  # список на языке вариантов
            if variants[0] not in used_words:
                used_words.append(variants[0])
                right_translation = current_dictionary[variants[0]]  # ищет по ключам того же языка, но возвращает обратный
                matches_dict[right_translation] = variants  # обратный + варианты
                break
    for k, v in matches_dict.items():
        print(k, *v, sep='\n')
        print()


create_lang_lists(filename)
read_commands()




